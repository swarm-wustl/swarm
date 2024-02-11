#include <functional>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "opencv2/opencv.hpp"

// std::vector<std::vector<int>> bresenham(int x1, int y1, int x2, int y2)
// { 
//     int m_new = 2 * (y2 - y1); 
//     int slope_error_new = m_new - (x2 - x1); 
//     for (int x = x1, y = y1; x <= x2; x++) { 
//         cout << "(" << x << "," << y << ")\n"; 
//   
//         // Add slope to increment angle formed 
//         slope_error_new += m_new; 
//   
//         // Slope error reached limit, time to 
//         // increment y and update slope error. 
//         if (slope_error_new >= 0) { 
//             y++; 
//             slope_error_new -= 2 * (x2 - x1); 
//         } 
//     } 
// }

void create_grid_map(std::vector<std::vector<float>> points, std::vector<float> pose, cv::Mat img) {
  if (points.size() == 0) {
    return;
  }
  int IMG_SIZE = 1000;
  int SCALE_FACTOR = 250;
  int grid_size_cm = 1000;
  int grid_resolution_cm = 1;
  int grid_size = grid_size_cm / grid_resolution_cm;

  std::vector<std::vector<int>> grid_map(grid_size, std::vector<int>(grid_size, 0));
  
  img.setTo(cv::Scalar(255, 255, 255));

  std::vector<float> y_values;

  for (auto point : points) {
    float x = point[0];
    float y = -point[1];
    float z = -point[2];

    y_values.push_back(y);

    int display_x = x*SCALE_FACTOR + IMG_SIZE/2;
    int display_z = z*SCALE_FACTOR + IMG_SIZE/2;

    if (display_x < 0 || display_x >= IMG_SIZE || display_z < 0 || display_z >= IMG_SIZE) {
      continue;
    }

    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "display_x: %d, display_z: %d", display_x, display_z);

    cv::Scalar color = y > 0.1 ? cv::Scalar(0, 0, 255) : cv::Scalar(0, 255, 0);
    cv::circle(img, cv::Point(display_x, display_z), 12, color, y > 0.1 ? 1 : cv::FILLED);

    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "x: %f, y: %f, z: %f", x, y, z);

    // Cast ray from robot to point using Breseham's line algorithm and update grid map
    int x0 = (pose[0] - 777)*SCALE_FACTOR + IMG_SIZE/2;
    int z0 = (pose[2] - 777)*SCALE_FACTOR + IMG_SIZE/2;
    int x1 = display_x;
    int z1 = display_z;

    // TODO
  }

  // sort y values
  // std::sort(y_values.begin(), y_values.end());
  // float min_y = y_values[0];
  // float quarter_y = y_values[y_values.size() / 4];
  // float mid_y = y_values[y_values.size() / 2];
  // float three_quarter_y = y_values[y_values.size() * 3 / 4];
  // float max_y = y_values[y_values.size() - 1];
  // RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "min_y: %f, quarter_y: %f, mid_y: %f, three_quarter_y: %f, max_y: %f", min_y, quarter_y, mid_y, three_quarter_y, max_y);

  // Draw robot pose
  int display_x = (pose[0] - 777)*SCALE_FACTOR + IMG_SIZE/2;
  int display_z = (pose[2] - 777)*SCALE_FACTOR + IMG_SIZE/2;
  cv::circle(img, cv::Point(display_x, display_z), 25, cv::Scalar(255, 0, 0), cv::FILLED);
  // RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "pose: %f, %f, %f", pose[0] - 777, pose[1] - 777, pose[2] - 777);
}

class GridMapperNode : public rclcpp::Node {
  private:
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr point_cloud_sub_;
    // rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr pose_sub_;

    // float pose_x = 0;
    // float pose_y = 0;
    // float pose_z = 0;

    cv::Mat img = cv::Mat::zeros(1000, 1000, CV_8UC3);

    // void pose_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg) 
    // {
    //   // RCLCPP_INFO(this->get_logger(), "Received pose");
    //   // RCLCPP_INFO(this->get_logger(), "pose: %f, %f, %f", msg->pose.position.x, msg->pose.position.y, msg->pose.position.z);
    //
    //   pose_x = msg->pose.position.x;
    //   pose_y = msg->pose.position.y;
    //   pose_z = msg->pose.position.z;
    // }

    void point_cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) 
    {
      RCLCPP_INFO(this->get_logger(), "Received point cloud");
      // RCLCPP_INFO(this->get_logger(), "pose: %f, %f, %f", pose_x, pose_y, pose_z);
      sensor_msgs::PointCloud2Iterator<float> iter_x(*msg, "x");
      sensor_msgs::PointCloud2Iterator<float> iter_y(*msg, "y");
      sensor_msgs::PointCloud2Iterator<float> iter_z(*msg, "z");

      std::vector<std::vector<float>> points;
      std::vector<float> pose;

      int msg_size = msg->height * msg->width;
      for (size_t i = 0; i < msg_size; ++i, ++iter_x, ++iter_y, ++iter_z) {
        float x = *iter_x;
        float y = *iter_y;
        float z = *iter_z;

        if (x == 0 && y == 0 && z == 0) {
          continue;
        }

        bool is_robot_pose_point = i == msg_size - 1;
        if (is_robot_pose_point) {
          pose = {x, y, z};
        } else {
          std::vector<float> point = {x, y, z};
          points.push_back(point);
        }
        // if (i == 0)
        // RCLCPP_INFO(this->get_logger(), "coords: %f, %f, %f", x, y, z);
      }

      RCLCPP_INFO(this->get_logger(), "points size: %d", points.size());
      create_grid_map(points, pose, img);
      cv::imshow("Grid", img);
      cv::waitKey(1);
    }

  public:
    GridMapperNode() : Node("grid_mapper")
  {
    point_cloud_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>("vslam/point_cloud", 10, std::bind(&GridMapperNode::point_cloud_callback, this, std::placeholders::_1));
    // pose_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>("vslam/estimated_pose", 10, std::bind(&GridMapperNode::pose_callback, this, std::placeholders::_1));

  }
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GridMapperNode>());
  rclcpp::shutdown();
  return 0;
}

