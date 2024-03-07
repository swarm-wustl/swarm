#include <functional>
#include <chrono>
#include <vector>
#include <string>
#include <stdlib.h>

#include "rclcpp/rclcpp.hpp"

#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "vslam/msg/point_cloud_and_pose.hpp"

#include "opencv2/opencv.hpp"

using namespace std;

void update_grid_map(vector<vector<int>> &grid_map, vector<vector<float>> points, vector<float> pose) {
  int MAX_XZ = 10; // made up number
  int BELOW_ROBOT_THRESHOLD = 0.7;
  int ABOVE_ROBOT_THRESHOLD = 1.3;

  for (auto point : points) {
    float x = point[0];
    float y = -point[1];
    float z = -point[2];

    if (y < pose[1]*0.7 || y > pose[1]*1.3) {
      continue;
    }

    int grid_x = (x + MAX_XZ) / (2*MAX_XZ) * grid_map.size();
    int grid_z = (z + MAX_XZ) / (2*MAX_XZ) * grid_map.size();
    grid_x = min(max(grid_x, 0), (int)grid_map.size() - 1);
    grid_z = min(max(grid_z, 0), (int)grid_map.size() - 1);

    grid_map[grid_x][grid_z]++;
  }
}

void display_grid_map(vector<vector<int>> &grid_map, cv::Mat img, vector<float> pose) {
  int MAX_XZ = 10; // made up number
  int DISPLAY_GRID_MAX = 100; // made up number (number of points a cell needs to be fully black)

  img.setTo(cv::Scalar(255, 255, 255));
  int img_size = img.size().width;
  int pixels_per_cell = img_size / grid_map.size();

  int pose_grid_x = (pose[0] + MAX_XZ) / (2*MAX_XZ) * grid_map.size();
  int pose_grid_z = (pose[2] + MAX_XZ) / (2*MAX_XZ) * grid_map.size();

  for (int i = 0; i < grid_map.size(); i++) {
    for (int j = 0; j < grid_map[i].size(); j++) {
      cv::Scalar color;
      if (i == pose_grid_x && j == pose_grid_z) {
        color = cv::Scalar(0, 0, 255);
      } else {
        int value = grid_map[i][j];
        int color_value = 255 - value*255/DISPLAY_GRID_MAX;
        color = cv::Scalar(color_value, color_value, color_value);
      }
      cv::rectangle(img, cv::Rect(i*pixels_per_cell, j*pixels_per_cell, pixels_per_cell, pixels_per_cell), color, cv::FILLED);
    }
  }
}

class GridMapperNode : public rclcpp::Node {
  private:
    rclcpp::Subscription<vslam::msg::PointCloudAndPose>::SharedPtr point_cloud_and_pose_sub_;

    cv::Mat img;
    vector<vector<int>> grid_map = std::vector<std::vector<int>>();

    void point_cloud_and_pose_callback(const vslam::msg::PointCloudAndPose::SharedPtr msg)
    {
      sensor_msgs::PointCloud2Iterator<float> iter_x(msg->pointcloud, "x");
      sensor_msgs::PointCloud2Iterator<float> iter_y(msg->pointcloud, "y");
      sensor_msgs::PointCloud2Iterator<float> iter_z(msg->pointcloud, "z");

      vector<vector<float>> points;
      vector<float> pose = {msg->pose.position.x, msg->pose.position.y, msg->pose.position.z};

      size_t msg_size = msg->pointcloud.height * msg->pointcloud.width;
      for (size_t i = 0; i < msg_size; ++i, ++iter_x, ++iter_y, ++iter_z) {
        float x = *iter_x;
        float y = *iter_y;
        float z = *iter_z;

        if (x == 0 && y == 0 && z == 0) {
          continue;
        }

        vector<float> point = {x, y, z};
        points.push_back(point);
      }

      update_grid_map(grid_map, points, pose);
      display_grid_map(grid_map, img, pose);
      cv::imshow("Grid", img);
      cv::waitKey(1);
    }

  public:
    GridMapperNode() : Node("grid_mapper")
  {
    point_cloud_and_pose_sub_ = this->create_subscription<vslam::msg::PointCloudAndPose>("vslam/point_cloud_and_pose", 10, bind(&GridMapperNode::point_cloud_and_pose_callback, this, placeholders::_1));

    int GRID_SIZE_CM = 10*100;
    int GRID_RESOLUTION_CM = 5;
    int PIXELS_PER_CELL = 5;

    int img_size = GRID_SIZE_CM / GRID_RESOLUTION_CM * PIXELS_PER_CELL;
    img = cv::Mat::zeros(img_size, img_size, CV_8UC3);

    grid_map.resize(GRID_SIZE_CM / GRID_RESOLUTION_CM, vector<int>(GRID_SIZE_CM / GRID_RESOLUTION_CM, 0));
    for (size_t i = 0; i < grid_map.size(); i++) {
      for (size_t j = 0; j < grid_map[i].size(); j++) {
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

