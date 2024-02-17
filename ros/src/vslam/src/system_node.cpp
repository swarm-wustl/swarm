#include <functional>
#include <chrono>
#include <string>
#include <vector>

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

using namespace std;

void throttleCallback(const chrono::time_point<chrono::high_resolution_clock>& last_callback) {
  auto now = chrono::high_resolution_clock::now();
  if (now - last_callback < chrono::milliseconds(1000 / 10)) {
    return;
  }
}

cv_bridge::CvImagePtr getImageFromMessage(const sensor_msgs::msg::Image::ConstSharedPtr &msg) {
  cv_bridge::CvImagePtr cv_ptr;
  try {
    cv_ptr = cv_bridge::toCvCopy(msg, msg->encoding);
  } catch (cv_bridge::Exception& e) {
    cerr << "cv_bridge exception: " << e.what() << endl;
    return nullptr;
  }
  return cv_ptr;
}

void processImage(cv::Mat& image) {
  cv::cvtColor(image, image, cv::COLOR_BGR2GRAY);
  cv::cvtColor(image, image, cv::COLOR_GRAY2RGB); // needs 3 channels for rviz
  cv::resize(image, image, cv::Size(752, 480));
}

geometry_msgs::msg::PoseStamped::SharedPtr createPoseMessage(const Sophus::SE3f& pose, rclcpp::Time& current_time) {
  Eigen::Vector3f position = pose.translation();
  Eigen::Quaternionf orientation = pose.unit_quaternion();

  auto pose_msg = std::make_shared<geometry_msgs::msg::PoseStamped>();
  pose_msg->header.frame_id = "map";
  pose_msg->header.stamp = current_time;
  pose_msg->pose.position.x = position.x();
  pose_msg->pose.position.y = position.y();
  pose_msg->pose.position.z = position.z();
  pose_msg->pose.orientation.x = orientation.x();
  pose_msg->pose.orientation.y = orientation.y();
  pose_msg->pose.orientation.z = orientation.z();
  pose_msg->pose.orientation.w = orientation.w();

  return pose_msg;
}

sensor_msgs::msg::PointCloud2::SharedPtr createPointCloudMessage(const vector<ORB_SLAM3::MapPoint*>& map_points, rclcpp::Time& current_time) {
  int num_points = map_points.size();

  auto point_cloud_msg = std::make_shared<sensor_msgs::msg::PointCloud2>();
  point_cloud_msg->header.frame_id = "map";
  point_cloud_msg->header.stamp = current_time;
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

  return point_cloud_msg;
}

int processMapPoints(const vector<ORB_SLAM3::MapPoint*>& map_points, sensor_msgs::msg::PointCloud2::SharedPtr& point_cloud_msg) {
  sensor_msgs::PointCloud2Iterator<float> iter_x(*point_cloud_msg, "x");
  sensor_msgs::PointCloud2Iterator<float> iter_y(*point_cloud_msg, "y");
  sensor_msgs::PointCloud2Iterator<float> iter_z(*point_cloud_msg, "z");

  int num_points_published = 0;
  for (const auto& mp : map_points) {
    if (mp == nullptr || mp->isBad()) {
      continue;
    }

    Eigen::Vector3f world_pos = mp->GetWorldPos();
    *iter_x = world_pos.x();
    *iter_y = world_pos.y();
    *iter_z = world_pos.z();

    ++iter_x;
    ++iter_y;
    ++iter_z;
    ++num_points_published;
  }

  return num_points_published;
}

class VSLAMSystemNode : public rclcpp::Node {
  private:
    const string OPENCV_WINDOW = "Camera Feed";
    chrono::time_point<chrono::high_resolution_clock> last_callback;

    image_transport::Subscriber image_sub_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr point_cloud_publisher_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr pose_publisher_;

    ORB_SLAM3::System* SLAM;

    void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr &msg) {
      throttleCallback(last_callback);

      cv_bridge::CvImagePtr cv_ptr = getImageFromMessage(msg);
      if (!cv_ptr) {
        RCLCPP_ERROR(this->get_logger(), "Failed to convert image message to cv_bridge");
        return;
      }

      cv_ptr->image.empty(); // required to prevent segfault

      processImage(cv_ptr->image);

      double tframe = msg->header.stamp.sec + msg->header.stamp.nanosec / 1000000000.0;
      Sophus::SE3f pose = SLAM->TrackMonocular(cv_ptr->image, tframe);
      vector<ORB_SLAM3::MapPoint*> map_points = SLAM->GetTrackedMapPoints();

      rclcpp::Time current_time = this->now();

      geometry_msgs::msg::PoseStamped::SharedPtr pose_msg = createPoseMessage(pose, current_time);
      pose_publisher_->publish(*pose_msg);

      sensor_msgs::msg::PointCloud2::SharedPtr point_cloud_msg = createPointCloudMessage(map_points, current_time);
      int num_points_published = processMapPoints(map_points, point_cloud_msg);
      point_cloud_publisher_->publish(*point_cloud_msg);
      RCLCPP_INFO(this->get_logger(), "Published %d points", num_points_published);

      cv::imshow(OPENCV_WINDOW, cv_ptr->image);
      cv::waitKey(3);
    }

  public:
    VSLAMSystemNode() : Node("vslam_system_node")
  {
    auto vocab_path_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    vocab_path_param_desc.description = "Path to the ORB vocabulary";
    this->declare_parameter<string>("vocab_path", "./src/vslam/orbslam/ORBvoc.txt", vocab_path_param_desc);

    auto settings_path_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    settings_path_param_desc .description = "Path to the ORB vocabulary";
    this->declare_parameter<string>("settings_path", "./src/vslam/orbslam/mono_settings.yaml", settings_path_param_desc );

    auto display_visual_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    display_visual_param_desc.description = "Display the visual output of the SLAM system";
    this->declare_parameter<bool>("display_visual", true, display_visual_param_desc);

    auto video_topic_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    video_topic_param_desc.description = "Name of the topic to subscribe to for the video feed";
    this->declare_parameter<string>("video_topic", "camera/image_raw", video_topic_param_desc);

    cv::namedWindow(OPENCV_WINDOW);

    rmw_qos_profile_t custom_qos = rmw_qos_profile_default;
    image_sub_ = image_transport::create_subscription(
        this,
        this->get_parameter("video_topic").as_string(),
        bind(&VSLAMSystemNode::imageCallback, this, placeholders::_1),
        "raw",
        custom_qos
    );

    point_cloud_publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("vslam/point_cloud", 10);
    pose_publisher_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("vslam/estimated_pose", 10);

    string vocab_path = this->get_parameter("vocab_path").as_string();
    if (access(vocab_path.c_str(), F_OK) == -1) {
      RCLCPP_FATAL(this->get_logger(), "Vocabulary file does not exist at %s", vocab_path.c_str());
      return;
    }

    string settings_path = this->get_parameter("settings_path").as_string();
    if (access(settings_path.c_str(), F_OK) == -1) {
      RCLCPP_FATAL(this->get_logger(), "Settings file does not exist at %s", settings_path.c_str());
      return;
    }

    SLAM = new ORB_SLAM3::System(
      vocab_path,
      settings_path,
      ORB_SLAM3::System::MONOCULAR,
      this->get_parameter("display_visual").as_bool()
    );

    RCLCPP_INFO(this->get_logger(), "VSLAMSystemNode initialized");
  }

    ~VSLAMSystemNode()
    {
      cv::destroyWindow(OPENCV_WINDOW);
      SLAM->Shutdown();
    }

  private:
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<VSLAMSystemNode>());
  rclcpp::shutdown();
  return 0;
}

