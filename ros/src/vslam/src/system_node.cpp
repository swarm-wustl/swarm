#include <functional>
#include <chrono>
#include <string>
#include <vector>
#include <set>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/image_encodings.hpp"

#include "vslam/msg/map.hpp"
#include "vslam/msg/key_frame.hpp"
#include "vslam/msg/map_point.hpp"

#include "image_transport/image_transport.hpp"
#include <cv_bridge/cv_bridge.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <Eigen/Core>
#include "System.h" // ORB_SLAM3

using namespace std;

void throttleCallback(const chrono::time_point<chrono::high_resolution_clock>& last_callback) {
  int FPS = 10;
  auto now = chrono::high_resolution_clock::now();
  if (now - last_callback < chrono::milliseconds(1000 / FPS)) {
    return;
  }
  return;
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

class VSLAMSystemNode : public rclcpp::Node {
  private:
    const string OPENCV_WINDOW = "Camera Feed";
    chrono::time_point<chrono::high_resolution_clock> last_callback;

    image_transport::Subscriber image_sub_;
    rclcpp::Publisher<vslam::msg::Map>::SharedPtr map_publisher_;

    ORB_SLAM3::System* SLAM;

    void processKeyFrame(ORB_SLAM3::KeyFrame* keyframe, vslam::msg::Map::SharedPtr& map_msg) {
      Sophus::SE3f keyframe_pose = keyframe->GetPose();
      Eigen::Vector3f position = keyframe_pose.translation();
      Eigen::Quaternionf orientation = keyframe_pose.unit_quaternion();
      vslam::msg::KeyFrame keyframe_msg;
      keyframe_msg.id = keyframe->mnId;
      keyframe_msg.pose.position.x = position.x();
      keyframe_msg.pose.position.y = position.y();
      keyframe_msg.pose.position.z = position.z();
      keyframe_msg.pose.orientation.x = orientation.x();
      keyframe_msg.pose.orientation.y = orientation.y();
      keyframe_msg.pose.orientation.z = orientation.z();
      keyframe_msg.pose.orientation.w = orientation.w();

      set<ORB_SLAM3::MapPoint*> keyframe_map_points = keyframe->GetMapPoints();
      for (ORB_SLAM3::MapPoint* map_point : keyframe_map_points) {
        keyframe_msg.map_point_ids.push_back(map_point->mnId);
      }

      map_msg->key_frames.push_back(keyframe_msg);
    }

    void processMapPoint(ORB_SLAM3::MapPoint* map_point, vslam::msg::Map::SharedPtr& map_msg) {
      vslam::msg::MapPoint map_point_msg;
      Eigen::Vector3f position = map_point->GetWorldPos();
      map_point_msg.id = map_point->mnId;
      map_point_msg.world_pos.x = position.x();
      map_point_msg.world_pos.y = position.y();
      map_point_msg.world_pos.z = position.z();
      map_msg->map_points.push_back(map_point_msg);
    }

    void publishMap(const Sophus::SE3f& pose) {
      ORB_SLAM3::Atlas* atlas = SLAM->GetAtlas();
      ORB_SLAM3::Map* map = atlas->GetCurrentMap();
      vector<ORB_SLAM3::KeyFrame*> keyframes = map->GetAllKeyFrames();
      vector<ORB_SLAM3::MapPoint*> all_map_points = map->GetAllMapPoints();

      vslam::msg::Map::SharedPtr map_msg = std::make_shared<vslam::msg::Map>();
      map_msg->header.stamp = this->now();
      map_msg->header.frame_id = "map";
      map_msg->id = map->GetId();

      Eigen::Vector3f camera_position = pose.translation();
      Eigen::Quaternionf camera_orientation = pose.unit_quaternion();
      map_msg->camera_pose.position.x = camera_position.x();
      map_msg->camera_pose.position.y = camera_position.y();
      map_msg->camera_pose.position.z = camera_position.z();
      map_msg->camera_pose.orientation.x = camera_orientation.x();
      map_msg->camera_pose.orientation.y = camera_orientation.y();
      map_msg->camera_pose.orientation.z = camera_orientation.z();
      map_msg->camera_pose.orientation.w = camera_orientation.w();

      for (ORB_SLAM3::KeyFrame* keyframe : keyframes) {
        processKeyFrame(keyframe, map_msg);
      }

      for (ORB_SLAM3::MapPoint* map_point : all_map_points) {
        processMapPoint(map_point, map_msg);
      }

      map_publisher_->publish(*map_msg);
    }

    void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr& msg) {
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

      publishMap(pose);

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

    map_publisher_ = this->create_publisher<vslam::msg::Map>("vslam/map", 10);

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

