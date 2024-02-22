#include <functional>
#include <chrono>
#include <vector>
#include <string>

#include "rclcpp/rclcpp.hpp"

#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "vslam/msg/point_cloud_and_pose.hpp"
#include "vslam/msg/map.hpp"
#include "vslam/msg/map_point.hpp"
#include "vslam/msg/key_frame.hpp"

#include "opencv2/opencv.hpp"

using namespace std;

struct Point {
  int x;
  int y;
};

struct GridCell {
  int nOccupied;
  int nVisited;
};

// Adapted from https://www.geeksforgeeks.org/bresenhams-line-generation-algorithm/
vector<Point> bresenham(int x1, int y1, int x2, int y2) {
  vector<Point> points;
  int m_new = 2 * (y2 - y1); 
  int slope_error_new = m_new - (x2 - x1); 
  for (int x = x1, y = y1; x <= x2; x++) { 
    points.push_back({x, y});

    // Add slope to increment angle formed 
    slope_error_new += m_new; 

    // Slope error reached limit, time to 
    // increment y and update slope error. 
    if (slope_error_new >= 0) { 
      y++; 
      slope_error_new -= 2 * (x2 - x1); 
    } 
  }
  return points;
}

Point xzToGrid(float x, float z, float MAX_XZ, int grid_size) {
  int grid_x = (x + MAX_XZ) / (2*MAX_XZ) * grid_size;
  int grid_z = (z + MAX_XZ) / (2*MAX_XZ) * grid_size;
  grid_x = min(max(grid_x, 0), grid_size - 1);
  grid_z = min(max(grid_z, 0), grid_size - 1);
  return {grid_x, grid_z};
}

void display_grid_map(vector<vector<GridCell>> &grid_map, cv::Mat img, vector<float> pose) {
  int MAX_XZ = 10; // made up number
  int DISPLAY_GRID_MIN = 3; // made up number (number of points a cell needs to be visible at all)

  img.setTo(cv::Scalar(255, 255, 255));
  int img_size = img.size().width;
  int pixels_per_cell = img_size / grid_map.size();

  int grid_size = grid_map.size();
  Point pose_grid_point = xzToGrid(pose[0], pose[2], MAX_XZ, grid_size);

  for (int i = 0; i < grid_size; i++) {
    for (int j = 0; j < grid_size; j++) {
      cv::Scalar color;
      if (i == pose_grid_point.x && j == pose_grid_point.y) {
        color = cv::Scalar(0, 0, 255);
      } else if (grid_map[i][j].nVisited < DISPLAY_GRID_MIN) {
        color = cv::Scalar(255, 120, 120);
      } else {
        GridCell cell = grid_map[i][j];
        int color_value = (1 - ((float)cell.nOccupied / (cell.nVisited + 1))) * 255;
        cout << "nOccupied: " << cell.nOccupied << " nVisited: " << cell.nVisited << " color_value: " << color_value << endl;
        color = cv::Scalar(color_value, color_value, color_value);
      }
      cv::rectangle(img, cv::Rect(i*pixels_per_cell, j*pixels_per_cell, pixels_per_cell, pixels_per_cell), color, cv::FILLED);
    }
  }
}

class GridMapperNode : public rclcpp::Node {
  private:
    rclcpp::Subscription<vslam::msg::PointCloudAndPose>::SharedPtr point_cloud_and_pose_sub_;
    rclcpp::Subscription<vslam::msg::Map>::SharedPtr map_sub_;

    cv::Mat img;
    vector<vector<GridCell>> grid_map;

    void map_callback(const vslam::msg::Map::SharedPtr msg)
    {
      vector<vslam::msg::MapPoint> map_points = msg->map_points;
      vector<vslam::msg::KeyFrame> key_frames = msg->key_frames;
      geometry_msgs::msg::Pose pose = msg->camera_pose;
      for (auto key_frame : key_frames) {
        // Get corresponding map points for this key frame
        vector<vslam::msg::MapPoint> key_frame_map_points;
        for (auto map_point_id : key_frame.map_point_ids) {
          for (auto map_point : map_points) {
            if (map_point.id == map_point_id) {
              key_frame_map_points.push_back(map_point);
              break;
            }
          }
        }

        // Update grid map by drawing lines between key frame and its map points
        Point key_frame_grid_point = xzToGrid(key_frame.pose.position.x, key_frame.pose.position.z, 10, grid_map.size());
        for (auto map_point : key_frame_map_points) {
          Point map_point_grid_point = xzToGrid(map_point.world_pos.x, map_point.world_pos.z, 10, grid_map.size());
          // Just ignore points that are outside the grid map
          if (key_frame_grid_point.x > grid_map.size() || key_frame_grid_point.y > grid_map.size() || map_point_grid_point.x > grid_map.size() || map_point_grid_point.y > grid_map.size()) {
            continue;
          }
          vector<Point> visited_points = bresenham(key_frame_grid_point.x, key_frame_grid_point.y, map_point_grid_point.x, map_point_grid_point.y);
          for (auto point : visited_points) {
            grid_map[point.x][point.y].nVisited++;
          }
          grid_map[map_point_grid_point.x][map_point_grid_point.y].nOccupied++;
        }
      }

      // Display grid map
      vector<float> vPose = {pose.position.x, pose.position.y, pose.position.z, pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w};
      display_grid_map(grid_map, img, vPose);
      cv::imshow("Grid", img);
      cv::waitKey(1);
    }

  public:
    GridMapperNode() : Node("grid_mapper")
  {
    map_sub_ = this->create_subscription<vslam::msg::Map>("vslam/map", 10, bind(&GridMapperNode::map_callback, this, placeholders::_1));

    int GRID_SIZE_CM = 3*100;
    int GRID_RESOLUTION_CM = 1;
    int PIXELS_PER_CELL = 4;

    int img_size = GRID_SIZE_CM / GRID_RESOLUTION_CM * PIXELS_PER_CELL;
    img = cv::Mat::zeros(img_size, img_size, CV_8UC3);

    grid_map.resize(GRID_SIZE_CM / GRID_RESOLUTION_CM, vector<GridCell>(GRID_SIZE_CM / GRID_RESOLUTION_CM, {0, 0}));
    for (size_t i = 0; i < grid_map.size(); i++) {
      for (size_t j = 0; j < grid_map[i].size(); j++) {
        grid_map[i][j] = {0, 0};
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

