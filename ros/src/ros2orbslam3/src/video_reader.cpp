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

using namespace cv;
using namespace cv_bridge;
using namespace std::chrono_literals;

using std::string;

class VideoReaderNode : public rclcpp::Node {
    private:
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr publisher_;
        size_t count_;

        string filename;
        VideoCapture capture;
        unsigned int frame_number;
        Mat frame;

        /*void timer_callback()
        {
            auto message = std_msgs::msg::String();
            message.data = "Hello, world! " + std::to_string(count_++);
            RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
            publisher_->publish(message);
        }*/

        void something()
        {
            if (!capture.isOpened()){
                RCLCPP_INFO(this->get_logger(), "Capture failed -- returning from callback...");
                return;
            }

            capture >> frame;

            if (frame.empty()) {
                RCLCPP_INFO(this->get_logger(), "Empty frame -- returning from callback...");
                return;
            }

            CvImage frame_bridge;
            sensor_msgs::msg::Image frame_msg;

            std_msgs::msg::Header header;
            header.stamp = this->now();
            header.frame_id = std::to_string(frame_number);

            frame_number++;

            frame_bridge = cv_bridge::CvImage(header, sensor_msgs::image_encodings::RGB8, frame);
            frame_bridge.toImageMsg(frame_msg);

            RCLCPP_INFO(this->get_logger(), "Publishing frame %d", frame_number);

            publisher_->publish(frame_msg);
        }

    public:
        VideoReaderNode() : Node("video_reader"), count_(0)
        {
            filename = "./src/ros2orbslam3/src/IMG_3762.mov";
            capture = VideoCapture(filename);
            frame_number = 0;

            publisher_ = this->create_publisher<sensor_msgs::msg::Image>("camera/image_raw", 10);
            timer_ = this->create_wall_timer(
                500ms, 
                std::bind(&VideoReaderNode::something, this
                )
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

/*
*MAKE SURE YOU ARE IN ros DIRECTORY, NOT NESTED IN src
source install/setup.bash
ros2 run ros2orbslam3 video_reader

ros2 topic echo camera/image_raw

colcon build --symlink-install --packages-select ros2orbslam3

https://stackoverflow.com/questions/13709274/reading-video-from-file-opencv
https://stackoverflow.com/questions/27080085/how-to-convert-a-cvmat-into-a-sensor-msgs-in-ros
*/