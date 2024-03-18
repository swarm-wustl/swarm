#include <memory>
#include <sstream>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "image_transport/image_transport.hpp"
#include <cv_bridge/cv_bridge.h>
#include "sensor_msgs/image_encodings.hpp"
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

#include "ball_capture/msg/detected_ball.hpp"

using namespace std;

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


class DetectBall : public rclcpp::Node
{
  private:
    image_transport::Subscriber image_sub_;
    rclcpp::Publisher<ball_capture::msg::DetectedBall>::SharedPtr ball_pub_;

    unsigned int hsv_lower[3];
    unsigned int hsv_upper[3];

    void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr& msg) {
      cv_bridge::CvImagePtr cv_ptr = getImageFromMessage(msg);
      if (!cv_ptr) {
        RCLCPP_ERROR(this->get_logger(), "Failed to convert image message to cv_bridge");
        return;
      }

      cv_ptr->image.empty(); // required to prevent segfault (maybe)

      cv::Mat processed;
      cv::GaussianBlur(cv_ptr->image, processed, cv::Size(11, 11), 0);
      cv::cvtColor(processed, processed, cv::COLOR_BGR2HSV);
      inRange(processed, cv::Scalar(29, 86, 6), cv::Scalar(64, 255, 255), processed);
      erode(processed, processed, cv::Mat(), cv::Point(-1, -1), 2);
      dilate(processed, processed, cv::Mat(), cv::Point(-1, -1), 2);
      cv::imshow("Foo", processed);
      cv::waitKey(1);

      // Find contours
      vector<vector<cv::Point>> contours;
      findContours(processed.clone(), contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
      cv::Point center;
      float radius;

      if (!contours.empty()) {
        // Find the largest contour in the mask
        vector<cv::Point> largestContour = *max_element(contours.begin(), contours.end(),
            [](const vector<cv::Point>& a, const vector<cv::Point>& b) {
            return contourArea(a) < contourArea(b);
            });

        // Compute the minimum enclosing circle and centroid
        cv::Point2f centerCircle;
        minEnclosingCircle(largestContour, centerCircle, radius);
        cv::Moments M = moments(largestContour);
        center = cv::Point(int(M.m10 / M.m00), int(M.m01 / M.m00));

        // Publish the detected ball
        ball_capture::msg::DetectedBall::SharedPtr detected_ball_msg = std::make_shared<ball_capture::msg::DetectedBall>();
        detected_ball_msg->header.stamp = this->now();
        detected_ball_msg->header.frame_id = "camera";
        detected_ball_msg->x = center.x;
        detected_ball_msg->y = center.y;
        detected_ball_msg->r = radius;
        ball_pub_->publish(*detected_ball_msg);
        RCLCPP_INFO(this->get_logger(), "center: %d, %d, r=%f", detected_ball_msg->x, detected_ball_msg->y, detected_ball_msg->r);
      } else {
        RCLCPP_INFO(this->get_logger(), "No ball detected");
      }
    }

  public:
    DetectBall()
    : Node("detect_ball")
    {
      auto hsv_lower_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
      hsv_lower_param_desc .description = "HSV lower bounds in format: H,S,V";
      this->declare_parameter<string>("hsv_lower", "29,86,6", hsv_lower_param_desc);

      auto hsv_upper_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
      hsv_upper_param_desc .description = "HSV upper bounds in format: H,S,V";
      this->declare_parameter<string>("hsv_upper", "74,255,255", hsv_upper_param_desc);

      stringstream ss_lower(this->get_parameter("hsv_lower").as_string());
      stringstream ss_upper(this->get_parameter("hsv_upper").as_string());
      string token;
      int index = 0;
      while (getline(ss_lower, token, ',')) {
        hsv_lower[index++] = stoi(token);
      }
      index = 0;
      while (getline(ss_upper, token, ',')) {
        hsv_upper[index++] = stoi(token);
      }

      RCLCPP_INFO(this->get_logger(), "HSV Lower: %d %d %d, Upper: %d %d %d", hsv_lower[0], hsv_lower[1], hsv_lower[2], hsv_upper[0], hsv_upper[1], hsv_upper[2]);

      rmw_qos_profile_t custom_qos = rmw_qos_profile_default;
      image_sub_ = image_transport::create_subscription(
          this,
          "camera/image_raw",
          bind(&DetectBall::imageCallback, this, placeholders::_1),
          "raw",
          custom_qos
      );
      ball_pub_ = this->create_publisher<ball_capture::msg::DetectedBall>("ball_capture/ball", 10);
    }
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DetectBall>());
  rclcpp::shutdown();
  return 0;
}
