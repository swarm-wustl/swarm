#include <memory>
#include <string>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "ball_capture/msg/detected_ball.hpp"

using namespace std;

class CaptureBall : public rclcpp::Node
{
  private:
    rclcpp::Subscription<ball_capture::msg::DetectedBall>::SharedPtr ball_sub_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    unsigned int frame_width;
    unsigned int frame_height;
    unsigned int radius_threshold;

    // keep track of when we started opening/closing the mandibles
    chrono::time_point<chrono::system_clock> last_mandible_change;

    void ballCallback(const ball_capture::msg::DetectedBall::SharedPtr msg) {
      RCLCPP_INFO(this->get_logger(), "Ball detected at (%d, %d) with radius %f", msg->x, msg->y, msg->r);
      geometry_msgs::msg::Twist cmd_vel;

      // Turn towards the ball (map 0-width to -1-1)
      cmd_vel.angular.z = -1 + 2/((float)frame_width) * (float)msg->x;

      // Move forward if the ball is far away
      // use roll as a way to open/close mandibles
      if (msg->r < radius_threshold) {
        cmd_vel.linear.x = 0.5;
        if (chrono::duration_cast<chrono::milliseconds>(chrono::system_clock::now() - last_mandible_change).count() > 1000) {
          last_mandible_change = chrono::system_clock::now();
          cmd_vel.angular.x = 0.5;
        } else {
          cmd_vel.angular.x = 0;
        }
      } else {
        cmd_vel.linear.x = 0;
        if (chrono::duration_cast<chrono::milliseconds>(chrono::system_clock::now() - last_mandible_change).count() > 1000) {
          last_mandible_change = chrono::system_clock::now();
          cmd_vel.angular.x = -0.5;
        } else {
          cmd_vel.angular.x = 0;
        }
      }

      cmd_vel_pub_->publish(cmd_vel);
    }

  public:
    CaptureBall()
    : Node("capture_ball")
    {
      ball_sub_ = this->create_subscription<ball_capture::msg::DetectedBall>("ball_capture/ball", 10, bind(&CaptureBall::ballCallback, this, placeholders::_1));
      cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);

      frame_width = 640;
      frame_height = 480;
      radius_threshold = 50;
    }
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CaptureBall>());
  rclcpp::shutdown();
  return 0;
}
