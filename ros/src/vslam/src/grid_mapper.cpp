#include <functional>
#include <chrono>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "opencv2/opencv.hpp"

using namespace std;

void create_grid_map(vector<vector<int>> &grid_map, vector<vector<float>> points, vector<float> pose, cv::Mat img) {
  if (points.size() == 0) {
    return;
  }
  int IMG_SIZE = 1000;
  int SCALE_FACTOR = 250;
  int GRID_SCALE_FACTOR = 5;
  int POINT_RADIUS = 10;
  int grid_size_cm = 1000;
  int grid_resolution_cm = 1;
  int grid_size = grid_size_cm / grid_resolution_cm;

  img.setTo(cv::Scalar(255, 255, 255));

  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "num points: %d", points.size());

  for (auto point : points) {
    float x = point[0];
    float y = -point[1];
    float z = -point[2];

    int display_x = x*SCALE_FACTOR + IMG_SIZE/2;
    int display_z = z*SCALE_FACTOR + IMG_SIZE/2;

    if (display_x < 0 || display_x >= IMG_SIZE || display_z < 0 || display_z >= IMG_SIZE) {
      continue;
    }

    // RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "display_x: %d, display_z: %d", display_x, display_z);

    cv::Scalar color = y > 0.1 ? cv::Scalar(0, 0, 255) : cv::Scalar(0, 255, 0);
    cv::circle(img, cv::Point(display_x, display_z), 12, color, y > 0.1 ? 1 : cv::FILLED);

    // RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "x: %f, y: %f, z: %f", x, y, z);

    // int point_grid_x = x*GRID_SCALE_FACTOR + grid_map.size()/2;
    // for (int i = 0; i < grid_map.size(); i++) {
    //   for (int j = 0; j < grid_map[i].size(); j++) {
    //     // Check if the grid cell is within the radius of the point
    //     int dx = i - point_grid_x;
    //     int dz = j - display_z;
    //     if (dx*dx + dz*dz < POINT_RADIUS*POINT_RADIUS) {
    //       grid_map[i][j]++;
    //     }
    //   }
    // }

    // Cast ray from robot to point using Breseham's line algorithm and update grid map
    // int x0 = (pose[0] - 777)*SCALE_FACTOR + IMG_SIZE/2;
    // int z0 = (pose[2] - 777)*SCALE_FACTOR + IMG_SIZE/2;
    // int x1 = display_x;
    // int z1 = display_z;

    // TODO
  }

  // Display grid map
  int GRID_DISPLAY_SCALE_FACTOR = 5;
  for (int i = 0; i < grid_map.size(); i++) {
    for (int j = 0; j < grid_map[i].size(); j++) {
      // Color grid cell based on its value (0 -> 255, 100 -> 0; linear interpolation)
      int value = grid_map[i][j];
      cv::Scalar color = cv::Scalar(255 - value*255/100, 255 - value*255/100, 255 - value*255/100);
      int display_x = i*GRID_DISPLAY_SCALE_FACTOR;
      int display_z = j*GRID_DISPLAY_SCALE_FACTOR;
      if (display_x < 0 || display_x >= IMG_SIZE || display_z < 0 || display_z >= IMG_SIZE) {
        continue;
      }
      cv::rectangle(img, cv::Rect(display_x, display_z, GRID_DISPLAY_SCALE_FACTOR, GRID_DISPLAY_SCALE_FACTOR), color, cv::FILLED);
    }
  }

  // Draw robot pose
  // int display_x = (pose[0] - 777)*SCALE_FACTOR + IMG_SIZE/2;
  // int display_z = (pose[2] - 777)*SCALE_FACTOR + IMG_SIZE/2;
  // cv::circle(img, cv::Point(display_x, display_z), 25, cv::Scalar(255, 0, 0), cv::FILLED);
}

class GridMapperNode : public rclcpp::Node {
  private:
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr point_cloud_sub_;

    cv::Mat img = cv::Mat::zeros(1000, 1000, CV_8UC3);
    vector<vector<int>> grid_map = std::vector<std::vector<int>>();

    void point_cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) 
    {
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
      }

      create_grid_map(grid_map, points, pose, img);
      cv::imshow("Grid", img);
      cv::waitKey(1);
    }

  public:
    GridMapperNode() : Node("grid_mapper")
  {
    point_cloud_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>("vslam/point_cloud", 10, std::bind(&GridMapperNode::point_cloud_callback, this, std::placeholders::_1));
    // pose_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>("vslam/estimated_pose", 10, std::bind(&GridMapperNode::pose_callback, this, std::placeholders::_1));

    int GRID_SIZE_CM = 20*100;
    int GRID_RESOLUTION_CM = 1;

    grid_map.resize(GRID_SIZE_CM / GRID_RESOLUTION_CM, std::vector<int>(GRID_SIZE_CM / GRID_RESOLUTION_CM, 0));
    for (int i = 0; i < grid_map.size(); i++) {
      for (int j = 0; j < grid_map[i].size(); j++) {
        grid_map[i][j] = 0;
      }
    }

    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "GridMapperNode initialized");
  }
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GridMapperNode>());
  rclcpp::shutdown();
  return 0;
}

