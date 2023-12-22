#include <functional>

#include "rclcpp/rclcpp.hpp"
#include "image_transport/image_transport.hpp"
#include <cv_bridge/cv_bridge.h>
#include "sensor_msgs/image_encodings.hpp"

#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

class ImageConverter : public rclcpp::Node {
private:
    const std::string OPENCV_WINDOW = "Image window";
    image_transport::Subscriber sub_;
    image_transport::Publisher pub_;

    void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr &msg) {
        cv_bridge::CvImagePtr cv_ptr;
        try
        {
            cv_ptr = cv_bridge::toCvCopy(msg, msg->encoding);
        }
        catch (cv_bridge::Exception& e)
        {
            RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
            return;
        }

        RCLCPP_INFO(this->get_logger(), "Rows: %d, Cols: %d, Channels: %d", cv_ptr->image.rows, cv_ptr->image.cols, cv_ptr->image.channels());

        // For some reason removing this line causes a segmenation fault
        // I really wish I knew why
        cv_ptr->image.clone();

        // Convert to grayscale and resize
        cv::cvtColor(cv_ptr->image, cv_ptr->image, CV_BGR2GRAY);
        cv::resize(cv_ptr->image, cv_ptr->image, cv::Size(752, 480));

        // Display
        cv::imshow(OPENCV_WINDOW, cv_ptr->image);
        cv::waitKey(3);

        // Publish
        pub_.publish(cv_ptr->toImageMsg());
    }

public:
    ImageConverter() : Node("image_converter") {

        // Open demo window that will show output image
        cv::namedWindow(OPENCV_WINDOW);

        rmw_qos_profile_t custom_qos = rmw_qos_profile_default;
        pub_ = image_transport::create_publisher(this, "test_output_image", custom_qos);
        sub_ = image_transport::create_subscription(this, "camera/image_raw",
                std::bind(&ImageConverter::imageCallback, this, std::placeholders::_1), "raw", custom_qos);

        RCLCPP_INFO(this->get_logger(), "ImageConverter initialized");

    }

    ~ImageConverter()
    {
        cv::destroyWindow(OPENCV_WINDOW);
    }
};

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ImageConverter>());
    rclcpp::shutdown();
    return 0;
}
