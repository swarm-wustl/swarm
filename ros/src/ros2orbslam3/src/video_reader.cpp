#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

using namespace cv;
using namespace std::chrono_literals;

using std::string;

class VideoReaderNode : public rclcpp::Node {
    private:
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
        size_t count_;

        void timer_callback()
        {
            auto message = std_msgs::msg::String();
            message.data = "Hello, world! " + std::to_string(count_++);
            RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
            publisher_->publish(message);
        }

    public:
        VideoReaderNode() : Node("video_reader"), count_(0)
        {
            publisher_ = this->create_publisher<std_msgs::msg::String>("camera/image_raw", 10);
            timer_ = this->create_wall_timer(
                500ms, 
                std::bind(&VideoReaderNode::timer_callback, this
                )
            );
        }
};

int main(int argc, char * argv[])
{
  string filename = "IMG_3762.mov";
  VideoCapture capture(filename);
  Mat frame;

  

  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<VideoReaderNode>());
  rclcpp::shutdown();
  return 0;
}

/*
*MAKE SURE YOU ARE IN ros DIRECTORY, NOT NESTED IN src
source install/setup.bash
ros2 run ros2orbslam3 video_reader

https://stackoverflow.com/questions/13709274/reading-video-from-file-opencv
https://stackoverflow.com/questions/27080085/how-to-convert-a-cvmat-into-a-sensor-msgs-in-ros
*/