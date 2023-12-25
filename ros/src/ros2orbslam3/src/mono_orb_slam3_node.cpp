#include <functional>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/image_encodings.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"
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

    image_transport::Subscriber sub_;
    image_transport::Publisher pub_;
    
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr point_cloud_publisher_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odometry_publisher_;

    ORB_SLAM3::System* SLAM;

    void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr &msg) {
      // Throttle to 10 FPS
      auto now = std::chrono::high_resolution_clock::now();
      if (now - last_callback < std::chrono::milliseconds(1000 / 10)) {
        RCLCPP_INFO(this->get_logger(), "Throttling");
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
      RCLCPP_INFO(this->get_logger(), "tframe: %f", tframe);
      SLAM->TrackMonocular(cv_ptr->image, tframe);

      Sophus::SE3f pose = SLAM->TrackMonocular(cv_ptr->image, tframe);
      int state = SLAM->GetTrackingState();
      vector<ORB_SLAM3::MapPoint*> vMPs = SLAM->GetTrackedMapPoints();
      vector<cv::KeyPoint> vKeys = SLAM->GetTrackedKeyPointsUn();

      // Get position
      Eigen::Vector3f position = pose.translation();
      Eigen::Quaternionf orientation = pose.unit_quaternion();

      RCLCPP_INFO(this->get_logger(), "position: %f, %f, %f", position.x(), position.y(), position.z());
      RCLCPP_INFO(this->get_logger(), "orientation: %f, %f, %f, %f", orientation.x(), orientation.y(), orientation.z(), orientation.w());

      // Publish odometry (don't think this is working)
      nav_msgs::msg::Odometry::SharedPtr odometry_msg = std::make_shared<nav_msgs::msg::Odometry>();
      odometry_msg->header.frame_id = "map";
      odometry_msg->header.stamp = this->now();
      odometry_msg->child_frame_id = "camera_link";
      odometry_msg->pose.pose.position.x = position.x();
      odometry_msg->pose.pose.position.y = position.y();
      odometry_msg->pose.pose.position.z = position.z();
      odometry_msg->pose.pose.orientation.x = orientation.x();
      odometry_msg->pose.pose.orientation.y = orientation.y();
      odometry_msg->pose.pose.orientation.z = orientation.z();
      odometry_msg->pose.pose.orientation.w = orientation.w();

      odometry_publisher_->publish(*odometry_msg);


      // for (int i = 0; i < vMPs.size(); i++) {
      //   Eigen::Vector3f world_pos = vMPs[i]->GetWorldPos();
      //   RCLCPP_INFO(this->get_logger(), "vMPs[%d]: %f, %f, %f", i, world_pos.x(), world_pos.y(), world_pos.z());
      // }

      // Create PointCloud2
      // sensor_msgs::msg::PointCloud2::SharedPtr point_cloud_msg = std::make_shared<sensor_msgs::msg::PointCloud2>();
      // point_cloud_msg->header.frame_id = "map";
      // point_cloud_msg->header.stamp = this->now();
      // point_cloud_msg->height = 1;
      // point_cloud_msg->width = vMPs.size();
      // point_cloud_msg->is_bigendian = false;
      // point_cloud_msg->is_dense = false;
      //
      // sensor_msgs::PointCloud2Modifier modifier(*point_cloud_msg);
      // modifier.setPointCloud2Fields(3, "x", 1, sensor_msgs::msg::PointField::FLOAT32,
      //     "y", 1, sensor_msgs::msg::PointField::FLOAT32,
      //     "z", 1, sensor_msgs::msg::PointField::FLOAT32);
      //
      // sensor_msgs::PointCloud2Iterator<float> iter_x(*point_cloud_msg, "x");
      // sensor_msgs::PointCloud2Iterator<float> iter_y(*point_cloud_msg, "y");
      // sensor_msgs::PointCloud2Iterator<float> iter_z(*point_cloud_msg, "z");
      //
      // // Fill message
      // for (int i = 0; i < vMPs.size(); i++) {
      //   *iter_x = vMPs[i]->GetWorldPos().x();
      //   *iter_y = vMPs[i]->GetWorldPos().y();
      //   *iter_z = vMPs[i]->GetWorldPos().z();
      //   ++iter_x; ++iter_y; ++iter_z;
      // }

      // Publish
      // point_cloud_publisher_->publish(*point_cloud_msg);

      // RCLCPP_INFO(this->get_logger(), "pose: %f, %f, %f, %f, %f, %f, %f, %f, %f", pose[0], pose[1], pose[2], pose[3], pose[4], pose[5], pose[6], pose[7], pose[8]);

      // RCLCPP_INFO(this->get_logger(), "pose: %f", pose);
      // RCLCPP_INFO(this->get_logger(), "state: %d", state);
      // RCLCPP_INFO(this->get_logger(), "vMPs.size(): %d", vMPs.size());
      // RCLCPP_INFO(this->get_logger(), "vKeys.size(): %d", vKeys.size());

      // for (int i = 0; i < vKeys.size(); i++) {
      //   RCLCPP_INFO(this->get_logger(), "vKeys[%d]: %f, %f", i, vKeys[i].pt.x, vKeys[i].pt.y);
      // }

      // Convert back to ROS message


      // Display
      cv::imshow(OPENCV_WINDOW, cv_ptr->image);
      cv::waitKey(3);

      // Publish
      pub_.publish(cv_ptr->toImageMsg());
    }

  public:
    MonoOrbSlam3Node() : Node("image_converter")
  {
    // Open demo window that will show output image
    cv::namedWindow(OPENCV_WINDOW);

    rmw_qos_profile_t custom_qos = rmw_qos_profile_default;
    pub_ = image_transport::create_publisher(this, "test_output_image", custom_qos);
    sub_ = image_transport::create_subscription(this, "camera/image_raw",
        std::bind(&MonoOrbSlam3Node::imageCallback, this, std::placeholders::_1), "raw", custom_qos);

    point_cloud_publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("test_output_point_cloud", 10);
    odometry_publisher_ = this->create_publisher<nav_msgs::msg::Odometry>("test_output_odometry", 10);

    RCLCPP_INFO(this->get_logger(), "MonoOrbSlam3Node initialized");
    RCLCPP_INFO(this->get_logger(), "ORB_SMAM3::System::MONOCULAR: %d", ORB_SLAM3::System::MONOCULAR);

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

