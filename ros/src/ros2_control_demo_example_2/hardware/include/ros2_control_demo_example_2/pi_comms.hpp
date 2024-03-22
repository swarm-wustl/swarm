#ifndef ROS2_CONTROL_DEMO_EXAMPLE_2__PI_COMMS_HPP_
#define ROS2_CONTROL_DEMO_EXAMPLE_2__PI_COMMS_HPP_

#include <string>
#include <sstream>
#include <iostream>
#include <pigpiod_if2.h>
#include <ros2_control_demo_example_2/encoder.hpp>
#include <vector>
#include "rclcpp/rclcpp.hpp"

class PiComms {
  private:
    int pi_code = -1;

    const int MOTOR_FWD = 17;
    const int MOTOR_REV = 22;

    const int ENC_1_A = 5;
    const int ENC_1_B = 6;

    const int ENC_2_A = 7;
    const int ENC_2_B = 8;

    Encoder enc1;
    Encoder enc2;
    
  public:
    PiComms() = default;
    
    void connect() {
      std::cout << "Connecting to Pi... " << std::flush;

      pi_code = pigpio_start(NULL, NULL);
      if (pi_code < 0) {
        std::cout << "ERROR: Failed to connect to Pi" << std::endl;
        return;
      }

      std::cout << "past starting..." << std::flush;

      set_mode(pi_code, MOTOR_FWD, PI_OUTPUT);
      set_mode(pi_code, MOTOR_REV, PI_OUTPUT);

      std::cout << "past modes..." << std::flush;

      enc1 = Encoder(pi_code, ENC_1_A, ENC_1_B);
      enc2 = Encoder(pi_code, ENC_2_A, ENC_2_B);

      std::cout << "past encoders..." << std::flush;
      std::cout << "wtf..." << std::flush;
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set pin modes");

      std::cout << "done!" << std::endl;
    }

    void disconnect() {
      std::cout << "Disconnecting from Pi... " << std::flush;

      pigpio_stop(pi_code);
      pi_code = -1;

      std::cout << "done!" << std::endl;
    }

    bool connected() const {
      return pi_code >= 0;
    }

    void read_encoder_values(int &val_1, int &val_2)
    {
      val_1 = enc1.read();
      val_2 = enc2.read();
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Read encoder values");
    }

    void set_motor_values(int val_1, int val_2)
    {
      // TODO: change this to integrate with PID
      set_PWM_dutycycle(pi_code, MOTOR_FWD, val_1);
      set_PWM_dutycycle(pi_code, MOTOR_REV, val_2);
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set motor values");
    }

    void set_pid_values(int k_p, int k_d, int k_i, int k_o)
    {
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set PID constants");
    }
};

#endif