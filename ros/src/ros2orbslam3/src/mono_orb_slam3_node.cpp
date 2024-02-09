#include <functional>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/image_encodings.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"

#include "image_transport/image_transport.hpp"
#include <cv_bridge/cv_bridge.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <Eigen/Core>
#include "System.h" // ORB_SLAM3

class MonoOrbSlam3Node : public rclcpp::Node {
  private:
    const std::string OPENCV_WINDOW = "Image window";
    std::chrono::time_point<std::chrono::high_resolution_clock> last_callback;

    image_transport::Subscriber image_sub_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr point_cloud_publisher_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr pose_publisher_;

    ORB_SLAM3::System* SLAM;

    void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr &msg) {
      // Throttle to 10 FPS
      auto now = std::chrono::high_resolution_clock::now();
      if (now - last_callback < std::chrono::milliseconds(1000 / 10)) {
        return;
      }
      last_callback = now;

      // Get image from message
      cv_bridge::CvImagePtr cv_ptr;
      try
      {
        cv_ptr = cv_bridge::toCvCopy(msg, msg->encoding);
      }
      catch (cv_bridge::Exception& e)
      {
        RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
        return;
      }

      // For some reason removing this line causes a segmentation fault
      // I really wish I knew why
      cv_ptr->image.empty();

      // Convert to grayscale and resize
      cv::cvtColor(cv_ptr->image, cv_ptr->image, CV_BGR2GRAY);
      cv::cvtColor(cv_ptr->image, cv_ptr->image, CV_GRAY2BGR); // convert back to 3 channels because rviz wants it
      cv::resize(cv_ptr->image, cv_ptr->image, cv::Size(752, 480));

      // Feed image to ORB_SLAM3
      double tframe = msg->header.stamp.sec + msg->header.stamp.nanosec / 1000000000.0;
      Sophus::SE3f pose = SLAM->TrackMonocular(cv_ptr->image, tframe);
      vector<ORB_SLAM3::MapPoint*> vMPs = SLAM->GetTrackedMapPoints();

      // Get position
      Eigen::Vector3f position = pose.translation();
      Eigen::Quaternionf orientation = pose.unit_quaternion();

      // Publish pose as geometry_msgs/PoseStamped Message
      geometry_msgs::msg::PoseStamped::SharedPtr pose_msg = std::make_shared<geometry_msgs::msg::PoseStamped>();
      pose_msg->header.frame_id = "map";
      pose_msg->header.stamp = this->now();
      pose_msg->pose.position.x = position.x();
      pose_msg->pose.position.y = position.y();
      pose_msg->pose.position.z = position.z();
      pose_msg->pose.orientation.x = orientation.x();
      pose_msg->pose.orientation.y = orientation.y();
      pose_msg->pose.orientation.z = orientation.z();
      pose_msg->pose.orientation.w = orientation.w();

      // Publish pose
      pose_publisher_->publish(*pose_msg);

      // Publish sensor_msgs/PointCloud2 Message
      std::vector<ORB_SLAM3::MapPoint*> vpMPs = SLAM->GetTrackedMapPoints();

      int num_points = vMPs.size();
      sensor_msgs::msg::PointCloud2::SharedPtr point_cloud_msg = std::make_shared<sensor_msgs::msg::PointCloud2>();
      point_cloud_msg->header.frame_id = "map";
      point_cloud_msg->header.stamp = this->now();
      point_cloud_msg->height = 1;
      point_cloud_msg->width = num_points;
      point_cloud_msg->is_bigendian = false;
      point_cloud_msg->is_dense = false;

      sensor_msgs::PointCloud2Modifier modifier(*point_cloud_msg);
      modifier.setPointCloud2Fields(3,
          "x", 1, sensor_msgs::msg::PointField::FLOAT32,
          "y", 1, sensor_msgs::msg::PointField::FLOAT32,
          "z", 1, sensor_msgs::msg::PointField::FLOAT32
      );

      // Need to get the map points that are not bad and not outliers
      // Must be done first so that we can resize the point cloud message
      int num_points_published = 0;
      std::vector<ORB_SLAM3::MapPoint*> map_points_to_publish;
      int num_map_points = vpMPs.size();
      for (int i = 0; i < num_map_points; i++) {
        ORB_SLAM3::MapPoint* mp = vpMPs[i];
        if (mp == NULL) {
          continue;
        }

        bool is_bad = mp->isBad();
        if (is_bad) {
          RCLCPP_INFO(this->get_logger(), "is_bad: %d", is_bad);
          continue;
        }

        // if (vbOutliers[i]) {
        //   RCLCPP_INFO(this->get_logger(), "is_outlier: %d", vbOutliers[i]);
        //   continue;
        // }

        map_points_to_publish.push_back(mp);
      }

      // We are incresing the size of the point cloud by 1 BECAUSE we are adding the camera position to the point cloud
      // TODO: make into compound message that includes both camera position (pose) and map points
      modifier.resize(map_points_to_publish.size() + 1);

      sensor_msgs::PointCloud2Iterator<float> iter_x(*point_cloud_msg, "x");
      sensor_msgs::PointCloud2Iterator<float> iter_y(*point_cloud_msg, "y");
      sensor_msgs::PointCloud2Iterator<float> iter_z(*point_cloud_msg, "z");

      int num_points_to_publish = map_points_to_publish.size();
      for (int i = 0; i < num_points_to_publish; i++) {
        ORB_SLAM3::MapPoint* mp = map_points_to_publish[i];
        Eigen::Vector3f world_pos = mp->GetWorldPos();

        *iter_x = world_pos.x();
        *iter_y = world_pos.y();
        *iter_z = world_pos.z();
        ++iter_x;
        ++iter_y;
        ++iter_z;
        num_points_published++;
      }
      RCLCPP_INFO(this->get_logger(), "num_points_published: %d", num_points_published);

      // This is the hack that we are using to publish pose information along with the point cloud
      // We add 777 to make sure that we don't accidentally use this as a map point elsewhere (it's really bad)
      // TODO: write this as a composite message
      *iter_x = position.x() + 777;
      *iter_y = position.y() + 777;
      *iter_z = position.z() + 777;

      point_cloud_publisher_->publish(*point_cloud_msg);

      // double roll, pitch, yaw;
      // Eigen::Matrix3f rotation_matrix = pose.rotationMatrix();
      // Eigen::Vector3f euler_angles = rotation_matrix.eulerAngles(1, 2, 3);
      // yaw = euler_angles[0];
      // pitch = euler_angles[1];
      // roll = euler_angles[2];
      // RCLCPP_INFO(this->get_logger(), "yaw: %f, pitch: %f, roll: %f", yaw, pitch, roll);
      // RCLCPP_INFO(this->get_logger(), "position: %f, %f, %f", position.x(), position.y(), position.z());
      // RCLCPP_INFO(this->get_logger(), "orientation: %f, %f, %f, %f", orientation.x(), orientation.y(), orientation.z(), orientation.w());

      // Display
      cv::imshow(OPENCV_WINDOW, cv_ptr->image);
      cv::waitKey(3);
    }

  public:
    MonoOrbSlam3Node() : Node("mono_orb_slam3_node")
  {
    // Open demo window that will show output image
    cv::namedWindow(OPENCV_WINDOW);

    rmw_qos_profile_t custom_qos = rmw_qos_profile_default;
    image_sub_ = image_transport::create_subscription(this, "camera/image_raw",
        std::bind(&MonoOrbSlam3Node::imageCallback, this, std::placeholders::_1), "raw", custom_qos);

    point_cloud_publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("test_output_point_cloud", 10);
    pose_publisher_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("test_output_pose", 10);

    RCLCPP_INFO(this->get_logger(), "MonoOrbSlam3Node initialized");

    // TODO: get vocabulary_path and settings_path from ROS2 parameters
    // For now, manually edit these paths to be your username
    std::string vocabulary_path = "/home/sebtheiler/Dev/ORB_SLAM3/Vocabulary/ORBvoc.txt";
    std::string settings_path = "/home/sebtheiler/Dev/ORB_SLAM3/Examples/Monocular/EuRoC.yaml";
    SLAM = new ORB_SLAM3::System(vocabulary_path, settings_path, ORB_SLAM3::System::MONOCULAR, true);

  }

    ~MonoOrbSlam3Node()
    {
      cv::destroyWindow(OPENCV_WINDOW);
      SLAM->Shutdown();
    }

  private:
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MonoOrbSlam3Node>());
  rclcpp::shutdown();
  return 0;
}

