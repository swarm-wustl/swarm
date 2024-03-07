#include <functional>
#include <chrono>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/image_encodings.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"

#include "vslam/msg/point_cloud_and_pose.hpp"

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
  cv::resize(image, image, cv::Size(752, 480));
}

vslam::msg::PointCloudAndPose::SharedPtr createPointCloudAndPoseMessage(
  const vector<ORB_SLAM3::MapPoint*>& map_points,
  const Sophus::SE3f& pose,
  rclcpp::Time& current_time
) {
  vslam::msg::PointCloudAndPose::SharedPtr point_cloud_and_pose_msg = std::make_shared<vslam::msg::PointCloudAndPose>();

  Eigen::Vector3f position = pose.translation();
  Eigen::Quaternionf orientation = pose.unit_quaternion();

  point_cloud_and_pose_msg->pose.position.x = position.x();
  point_cloud_and_pose_msg->pose.position.y = position.y();
  point_cloud_and_pose_msg->pose.position.z = position.z();
  point_cloud_and_pose_msg->pose.orientation.x = orientation.x();
  point_cloud_and_pose_msg->pose.orientation.y = orientation.y();
  point_cloud_and_pose_msg->pose.orientation.z = orientation.z();
  point_cloud_and_pose_msg->pose.orientation.w = orientation.w();

  sensor_msgs::PointCloud2Modifier modifier(point_cloud_and_pose_msg->pointcloud);
  modifier.setPointCloud2Fields(
    3,
    "x", 1, sensor_msgs::msg::PointField::FLOAT32,
    "y", 1, sensor_msgs::msg::PointField::FLOAT32,
    "z", 1, sensor_msgs::msg::PointField::FLOAT32
  );

  vector<int> indicies_to_publish;
  for (unsigned int i = 0; i < map_points.size(); i++) {
    auto mp = map_points[i];
    if (mp == nullptr || mp->isBad()) {
      continue;
    }

    indicies_to_publish.push_back(i);
  }

  int num_points_to_publish = indicies_to_publish.size();
  point_cloud_and_pose_msg->pointcloud.header.frame_id = "map";
  point_cloud_and_pose_msg->pointcloud.header.stamp = current_time;
  point_cloud_and_pose_msg->pointcloud.height = 1;
  point_cloud_and_pose_msg->pointcloud.width = num_points_to_publish;
  point_cloud_and_pose_msg->pointcloud.is_bigendian = false;
  point_cloud_and_pose_msg->pointcloud.is_dense = true;

  modifier.resize(num_points_to_publish);
  sensor_msgs::PointCloud2Iterator<float> iter_x(point_cloud_and_pose_msg->pointcloud, "x");
  sensor_msgs::PointCloud2Iterator<float> iter_y(point_cloud_and_pose_msg->pointcloud, "y");
  sensor_msgs::PointCloud2Iterator<float> iter_z(point_cloud_and_pose_msg->pointcloud, "z");

  for (int index : indicies_to_publish) {
    auto mp = map_points[index];
    Eigen::Vector3f world_pos = mp->GetWorldPos();
    *iter_x = world_pos.x();
    *iter_y = world_pos.y();
    *iter_z = world_pos.z();

    ++iter_x;
    ++iter_y;
    ++iter_z;
  }

  return point_cloud_and_pose_msg;
}

class VSLAMSystemNode : public rclcpp::Node {
  private:
    const string OPENCV_WINDOW = "Camera Feed";
    chrono::time_point<chrono::high_resolution_clock> last_callback;

    image_transport::Subscriber image_sub_;
    rclcpp::Publisher<vslam::msg::PointCloudAndPose>::SharedPtr point_cloud_and_pose_publisher_;

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

      vslam::msg::PointCloudAndPose::SharedPtr point_cloud_and_pose_msg = createPointCloudAndPoseMessage(map_points, pose, current_time);
      point_cloud_and_pose_publisher_->publish(*point_cloud_and_pose_msg);

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
    settings_path_param_desc .description = "Path to the camera settings file";
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

    point_cloud_and_pose_publisher_ = this->create_publisher<vslam::msg::PointCloudAndPose>("vslam/point_cloud_and_pose", 10);

    string vocab_path = this->get_parameter("vocab_path").as_string();
    if (access(vocab_path.c_str(), F_OK) == -1) {
      RCLCPP_FATAL(this->get_logger(), "Vocabulary file does not exist at %s. Try running `cp ~/Dev/ORB_SLAM3/Vocabulary/ORBvoc.txt %s`", vocab_path.c_str(), vocab_path.c_str());
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

