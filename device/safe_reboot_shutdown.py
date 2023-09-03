# -----------------------------------------------------------------------------
#                 Raspberry Pi Safe Restart and Shutdown Python Script
# -----------------------------------------------------------------------------
# Based on code from the following blog and tutorials:
#
#    Kevin Godden
#    https://www.ridgesolutions.ie/index.php/2013/02/22/raspberry-pi-restart-shutdown-your-pi-from-python-code/
#
#    Pete Lewis
#    https://learn.sparkfun.com/tutorials/raspberry-pi-stand-alone-programmer#resources-and-going-further
#
#    Shawn Hymel
#    https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-1-digital-input-and-output
#
#    Ben Croston raspberry-gpio-python module
#    https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
#
# ==================== DESCRIPTION ====================
#
# This python script takes advantage of the Qwiic pHat v2.0's
# built-in general purpose button to safely reboot/shutdown you Pi:
#
#    1.) If you press the button momentarily, the Pi will reboot.
#    2.) Holding down the button for about 3 seconds the Pi will shutdown.
#
# This example also takes advantage of interrupts so that it uses a negligible
# amount of CPU. This is more efficient since it isn't taking up all of the Pi's
# processing power.
#
# LICENSE: This code is released under the MIT License (http://opensource.org/licenses/MIT)
# Distributed as-is; no warranty is given
# -----------------------------------------------------------------------------

import time
import RPi.GPIO as GPIO #Python Package Reference: https://pypi.org/project/RPi.GPIO/
import os
import sys

SDK_HOME_PATH = os.path.dirname(os.path.abspath(__file__)) + '/../'
sys.path.append(SDK_HOME_PATH)

from display.lcd import LCD
from ubo_keypad.ubo_keypad import Keypad 
from rgb_ring.rgb_ring_client import LEDClient
from audio.audio_manager import AudioManager

# Pin definition
bus_isolation_pin = 17
reset_shutdown_pin = 27
led_backlight = 26


# Suppress warnings
GPIO.setwarnings(False)

# Use "GPIO" pin numbering
GPIO.setmode(GPIO.BCM)

# Use built-in internal pullup resistor so the pin is not floating
# if using a momentary push button without a resistor.
#GPIO.setup(reset_shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Use Qwiic pHAT's pullup resistor so that the pin is not floating
GPIO.setup(reset_shutdown_pin, GPIO.IN)
GPIO.setup(bus_isolation_pin, GPIO.OUT)
GPIO.setup(led_backlight, GPIO.OUT)

GPIO.output(bus_isolation_pin, GPIO.HIGH)
GPIO.output(led_backlight, GPIO.HIGH)


# modular function to restart Pi
def restart():
    print("restarting Pi")
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)

# modular function to shutdown Pi
def shut_down():
    print("shutting down")
    command = "/usr/bin/sudo /sbin/shutdown -h now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)


while True:
    #short delay, otherwise this code will take up a lot of the Pi's processing power
    time.sleep(0.5)

    # wait for a button press with switch debounce on the falling edge so that this script
    # is not taking up too many resources in order to shutdown/reboot the Pi safely
    channel = GPIO.wait_for_edge(reset_shutdown_pin, GPIO.FALLING, bouncetime=200)

    if channel is None:
        print('Timeout occurred')
    else:
        print('Edge detected on channel', channel)

        # For troubleshooting, uncomment this line to output button status on command line
        #print('GPIO state is = ', GPIO.input(reset_shutdown_pin))
        counter = 0
        lcd = LCD()
        led_ring = LEDClient()
        # audio = AudioManager()

        while GPIO.input(reset_shutdown_pin) == False:
            # For troubleshooting, uncomment this line to view the counter. If it reaches a value above 4, we will restart.
            #print(counter)

            counter += 1
            time.sleep(0.5)

            # long button press
            if counter > 4:
                lcd.display([(1,"Shutting down",0,"white"), (2, "in 5 seconds" ,0,"white")], 19)
                led_ring.set_all(color=(255,255,0))
                shut_down()

        #if short button press, restart!
        lcd.display([(1,"Restarting",0,"white"), (2, "Ubo Pod..." ,0,"white")], 19)
        led_ring.set_all(color=(255,255,0))
        restart()
