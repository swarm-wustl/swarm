#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <sensor_msgs/image_encodings.hpp>
#include <cv_bridge/cv_bridge.h>

using namespace std;
using namespace std::chrono;

class VideoReaderNode : public rclcpp::Node {
    private:
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr publisher_;
        size_t count_;

        string filename;
        unsigned int frame_number = 0;
        cv::VideoCapture capture;
        cv::Mat frame;

        void timer_callback()
        {
            capture >> frame;

            if (frame.empty()) {
                RCLCPP_WARN(this->get_logger(), "Empty frame -- returning from callback...");
                return;
            }

            cv_bridge::CvImage frame_bridge;
            sensor_msgs::msg::Image frame_msg;

            std_msgs::msg::Header header;
            header.stamp = this->now();
            header.frame_id = std::to_string(frame_number);

            frame_number++;

            frame_bridge = cv_bridge::CvImage(header, sensor_msgs::image_encodings::BGR8, frame);
            frame_bridge.toImageMsg(frame_msg);

            RCLCPP_INFO(this->get_logger(), "Publishing frame %d", frame_number);

            publisher_->publish(frame_msg);
        }

    public:
        VideoReaderNode() : Node("video_reader"), count_(0)
        {
            auto filename_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
            filename_param_desc.description = "Name of the video file to read";
            this->declare_parameter<string>("video_file_name", "null", filename_param_desc);

            auto frame_rate_multiplier_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
            frame_rate_multiplier_param_desc.description = "Multiplier for the frame rate. 0.5 -> half frame rate";
            this->declare_parameter<double>("frame_rate_multiplier", 1.0, frame_rate_multiplier_param_desc);

            auto topic_name_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
            topic_name_param_desc.description = "Name of the topic to publish the frames to";
            this->declare_parameter<string>("topic_name", "camera/image_raw", topic_name_param_desc);

            // Get filename and open it
            filename = "./src/vslam/samples/" + this->get_parameter("video_file_name").as_string();

            if (access(filename.c_str(), F_OK) == -1) {
                RCLCPP_FATAL(this->get_logger(), "File does not exist: %s", filename.c_str());
                return;
            }

            capture = cv::VideoCapture(filename);
            if (!capture.isOpened()) {
                RCLCPP_FATAL(this->get_logger(), "Failed to open video file: %s", filename.c_str());
                return;
            }
            
            // Convert float (1 / frame_rate) into std::chrono::milliseconds
            int frame_rate = capture.get(cv::CAP_PROP_FPS) * this->get_parameter("frame_rate_multiplier").as_double();
            duration<float> dur = round<nanoseconds>(duration<float>{1.0f / frame_rate});
            milliseconds delay = duration_cast<milliseconds>(dur);

            publisher_ = this->create_publisher<sensor_msgs::msg::Image>(this->get_parameter("topic_name").as_string(), 10);
            timer_ = this->create_wall_timer(
                delay, 
                std::bind(&VideoReaderNode::timer_callback, this)
            );
        }
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<VideoReaderNode>());
  rclcpp::shutdown();
  return 0;
}

