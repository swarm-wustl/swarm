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

class GridMapperNode : public rclcpp::Node {
  private:
    rclcpp::Subscription<vslam::msg::PointCloudAndPose>::SharedPtr point_cloud_and_pose_sub_;
    rclcpp::Subscription<vslam::msg::Map>::SharedPtr map_sub_;

    cv::Mat img;
    vector<vector<GridCell>> grid_map;

    int n_prev_keyframes = 0;

    int GRID_SIZE_CM;
    int GRID_RESOLUTION_CM;
    int PIXELS_PER_CELL;
    int MAX_XZ;
    int DISPLAY_GRID_MIN;

    int IMG_SIZE;
    int GRID_SIZE;

    Point xzToGrid(float x, float z) {
      int grid_x = (x + MAX_XZ) / (2*MAX_XZ) * GRID_SIZE;
      int grid_z = (z + MAX_XZ) / (2*MAX_XZ) * GRID_SIZE;
      grid_x = min(max(grid_x, 0), GRID_SIZE - 1);
      grid_z = min(max(grid_z, 0), GRID_SIZE - 1);
      return {grid_x, grid_z};
    }

    void update_grid_map(vector<vslam::msg::MapPoint> map_points, vector<vslam::msg::KeyFrame> key_frames) {
      // Create a map for quick lookup of map points by their IDs
      unordered_map<int, vslam::msg::MapPoint> map_points_map;
      for (const auto& map_point : map_points) {
        map_points_map[map_point.id] = map_point;
      }

      for (const auto& key_frame : key_frames) {
        // Calculate grid point for key frame once
        Point key_frame_grid_point = xzToGrid(key_frame.pose.position.x, key_frame.pose.position.z);

        // Update grid map by drawing lines between key frame and its map points
        for (auto map_point_id : key_frame.map_point_ids) {
          auto it = map_points_map.find(map_point_id);
          if (it != map_points_map.end()) {
            const auto& map_point = it->second;
            // Calculate grid point for map point once
            Point map_point_grid_point = xzToGrid(map_point.world_pos.x, map_point.world_pos.z);

            // Check if points are outside the grid map
            if (key_frame_grid_point.x >= GRID_SIZE || key_frame_grid_point.y >= GRID_SIZE || 
                map_point_grid_point.x >= GRID_SIZE || map_point_grid_point.y >= GRID_SIZE) {
              continue;
            }

            // Calculate Bresenham line only for points inside the grid map
            vector<Point> visited_points = bresenham(key_frame_grid_point.x, key_frame_grid_point.y, map_point_grid_point.x, map_point_grid_point.y);
            for (const auto& point : visited_points) {
              grid_map[point.x][point.y].nVisited++;
            }
            grid_map[map_point_grid_point.x][map_point_grid_point.y].nOccupied++;
          }
        }
      }
    }

    void display_grid_map(geometry_msgs::msg::Pose pose) {
      img.setTo(cv::Scalar(255, 255, 255));
      int grid_size = grid_map.size();
      Point pose_grid_point = xzToGrid(pose.position.x, pose.position.z);

      for (int i = 0; i < grid_size; i++) {
        for (int j = 0; j < grid_size; j++) {
          cv::Scalar color;

          // Check if the current cell corresponds to the pose
          if (i == pose_grid_point.x && j == pose_grid_point.y) {
            color = cv::Scalar(0, 0, 255);
          } else {
            GridCell cell = grid_map[i][j];
            // Calculate color value based on occupancy
            int color_value = (1 - ((float)cell.nOccupied / (cell.nVisited + 1))) * 255;

            // Adjust color if below minimum display threshold
            if (cell.nVisited < DISPLAY_GRID_MIN) {
              color = cv::Scalar(255, 120, 120);
            } else {
              color = cv::Scalar(color_value, color_value, color_value);
            }
          }

          // Draw rectangle with appropriate color
          cv::rectangle(img, cv::Rect(i * PIXELS_PER_CELL, j * PIXELS_PER_CELL, PIXELS_PER_CELL, PIXELS_PER_CELL), color, cv::FILLED);
        }
      }
    }

    void map_callback(const vslam::msg::Map::SharedPtr msg)
    {
      vector<vslam::msg::MapPoint> map_points = msg->map_points;
      vector<vslam::msg::KeyFrame> key_frames = msg->key_frames;
      geometry_msgs::msg::Pose pose = msg->camera_pose;
      
      int n_keyframes = key_frames.size();
      if (n_keyframes == n_prev_keyframes) {
        return;
      }
      n_prev_keyframes = n_keyframes;

      update_grid_map(map_points, key_frames);

      if (this->get_parameter("display_grid").as_bool()) {
        display_grid_map(pose);
        cv::imshow("Grid", img);
        cv::waitKey(1);
      }
    }

  public:
    GridMapperNode() : Node("grid_mapper")
  {
    auto display_grid_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    display_grid_param_desc.description = "Display grid map?";
    this->declare_parameter<bool>("display_grid", true, display_grid_param_desc);

    auto map_topic_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    map_topic_param_desc.description = "Name of the topic to subscribe to for the map";
    this->declare_parameter<string>("map_topic", "vslam/map", map_topic_param_desc);

    auto grid_size_cm_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    grid_size_cm_param_desc.description = "Size of the grid in centimeters";
    this->declare_parameter<int>("grid_size_cm", 300, grid_size_cm_param_desc);

    auto grid_resolution_cm_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    grid_resolution_cm_param_desc.description = "Resolution of the grid in centimeters";
    this->declare_parameter<int>("grid_resolution_cm", 1, grid_resolution_cm_param_desc);

    auto pixels_per_cell_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    pixels_per_cell_param_desc.description = "Number of pixels per cell for image display";
    this->declare_parameter<int>("pixels_per_cell", 4, pixels_per_cell_param_desc);

    auto max_xz_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    max_xz_param_desc.description = "Maximum value of x and z in the world";
    this->declare_parameter<int>("max_xz", 10, max_xz_param_desc);

    auto display_grid_min_param_desc = rcl_interfaces::msg::ParameterDescriptor{};
    display_grid_min_param_desc.description = "Minimum number of points a cell needs to be visible at all";
    this->declare_parameter<int>("display_grid_min", 3, display_grid_min_param_desc);

    GRID_SIZE_CM = this->get_parameter("grid_size_cm").as_int();
    GRID_RESOLUTION_CM = this->get_parameter("grid_resolution_cm").as_int();
    PIXELS_PER_CELL = this->get_parameter("pixels_per_cell").as_int();
    MAX_XZ = this->get_parameter("max_xz").as_int();
    DISPLAY_GRID_MIN = this->get_parameter("display_grid_min").as_int();
    IMG_SIZE = GRID_SIZE_CM / GRID_RESOLUTION_CM * PIXELS_PER_CELL;
    GRID_SIZE = GRID_SIZE_CM / GRID_RESOLUTION_CM;

    // Subscribe to point cloud and pose
    string map_topic = this->get_parameter("map_topic").as_string();
    map_sub_ = this->create_subscription<vslam::msg::Map>(map_topic, 10, bind(&GridMapperNode::map_callback, this, placeholders::_1));
    img = cv::Mat::zeros(IMG_SIZE, IMG_SIZE, CV_8UC3);

    // Initialize grid map
    grid_map.resize(GRID_SIZE, vector<GridCell>(GRID_SIZE, {0, 0}));
    for (int i = 0; i < GRID_SIZE; i++) {
      for (int j = 0; j < GRID_SIZE; j++) {
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

