#include <string>
#include <sstream>
#include <iostream>
#include <pigpio.h>
#include <vector>

class PiComms {
  int PIN_FORWARD = 17;
  int PIN_BACKWARD = 23;
  int PIN_LEFT = 27;
  int PIN_RIGHT = 22;
  std::vector<int> pins = {PIN_FORWARD, PIN_BACKWARD, PIN_LEFT, PIN_RIGHT};

  public:
    PiComms();
    ~PiComms();
    
    void connect() {
      std::cout << "Connecting to Pi" << std::endl;
      int status = gpioInitialise();
      if (status < 0) {
        std::cout << "Failed to connect to Pi" << std::endl;
      }

      for (int pin : pins) {
        gpioSetMode(pin, PI_OUTPUT);
      }

      is_connected = true;
      std::cout << "Connected to Pi" << std::endl;
    }

    void disconnect() {
      std::cout << "Disconnecting from Pi" << std::endl;
      gpioTerminate();
      is_connected = false;
      std::cout << "Disconnected from Pi" << std::endl;
    }

    bool get_is_connected() {
      return is_connected;
    }

  private:
    bool is_connected = false;
};

