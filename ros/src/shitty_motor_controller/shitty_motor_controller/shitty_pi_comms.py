import RPi.GPIO as GPIO

class ShittyPiComms:
    def __init__(self):
        GPIO.setwarnings(True)

        # Set up GPIO pins
        GPIO.setmode(GPIO.BCM)

        IN1 = 12
        IN2 = 16
        IN3 = 20
        IN4 = 21

        pins = [IN1, IN2, IN3, IN4]

        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        # Set up PWM
        self.pwm = GPIO.PWM(IN1, 100)

    def __del__(self):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 0)
        self.pwm.stop()
        GPIO.cleanup()

    def forward(self, speed):
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        self.pwm.ChangeDutyCycle(speed)

    def backward(self, speed):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        self.pwm.ChangeDutyCycle(speed)

    def left(self, speed):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        self.pwm.ChangeDutyCycle(speed)

    def right(self, speed):
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        self.pwm.ChangeDutyCycle(speed)

    def stop(self):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 0)
        self.pwm.stop()
        GPIO.cleanup()

