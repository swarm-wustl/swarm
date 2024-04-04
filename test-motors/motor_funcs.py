# Straight from ESE 205 :)

import RPi.GPIO as GPIO          
GPIO.setmode(GPIO.BOARD)

def motor_init (in1, in2, en, freq, dutycycle):
   GPIO.setup(in1,GPIO.OUT)
   GPIO.setup(in2,GPIO.OUT)
   GPIO.setup(en,GPIO.OUT)
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.LOW)
   pwm_pin=GPIO.PWM(en,freq)
   pwm_pin.start(dutycycle)
   return pwm_pin

def motor_pwm_change(pwm_pin, dutycycle):
   pwm_pin.start(dutycycle)

def motor_direction(in1, in2, direction, debug=False):     
   # direction -1 -backwards, 0 - stop, 1 - forward
   if (direction < 0):
      if debug: print ('Set backward')
      GPIO.output(in1,GPIO.LOW)
      GPIO.output(in2,GPIO.HIGH)
   elif ( direction == 0 ):
      if debug: print ('stopped')
      GPIO.output(in1,GPIO.LOW)
      GPIO.output(in2,GPIO.LOW)
   else: 
      if debug: print ('Set forward')
      GPIO.output(in1,GPIO.HIGH)
      GPIO.output(in2,GPIO.LOW)

def movingAvg(arr, position, numvals=3, wrap=1):
    # default to 3 pt moving average with wrap around on getting values 
    # arr       - array
    # posistion - start from this point on averages
    # numvals   - Number of values in moving average, default of 3
    # wrap      - wrap around to top or bottom of array if 1 (default), no if 0
    sumvals    = 0
    count      = 0    
    array_size = len(arr)
    # if less than numvals data, then just use what is available
    for i in range(numvals):
        # add an item to the list
        if (position - i >= 0 and position - 1 < array_size):
            sumvals = sumvals + arr[(position - i)]
            count   = count + 1
        # wrap backwards, goes to top of array, works in python
        elif (position - i < 0 and wrap == 1): 
            sumvals = sumvals + arr[(position - i)]
            count   = count + 1
        # wrap around to bottom of array with mod
        elif (position - i > array_size and wrap == 1):
            sumvals = sumvals + arr[(position - i)%array_size]
            count   = count + 1
    return sumvals/count