#include <functional>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"

using std::placeholders::_1;

class GridMapperNode : public rclcpp::Node {
  private:
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr point_cloud_sub_;

    void pointCloudCallback(const sensor_msgs::msg::PointCloud2::ConstSharedPtr &msg) {
      RCLCPP_INFO(this->get_logger(), "Received point cloud");
    }

  public:
    GridMapperNode() : Node("grid_mapper")
  {
    point_cloud_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>("test_output_point_cloud", 10, std::bind(&GridMapperNode::pointCloudCallback, this, std::placeholders::_1));
  }
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GridMapperNode>());
  rclcpp::shutdown();
  return 0;
}

