import time
import os
import sys
import json
up_dir = os.path.dirname(os.path.abspath(__file__))+'/../'
sys.path.append(up_dir)
from display.lcd import LCD as LCD
from ubo_keypad import * # Might have to revisit this form of import

result = True
#initialize LCD and Keypad
lcd = LCD()


class state_machine(KEYPAD):
    def __init__(self, *args, **kwargs):
        super(state_machine, self).__init__(*args, **kwargs)
        self.state_index = 0
        self.repeat_counter = 0
        self.num_retries = 1
        self.test_result  = False
        self.test_report = {"qrcode":False, "green":False, "red":False, "blue":False }


    def key_press_cb(self, channel):
        #read inputs
        inputs = self.aw.inputs
        print("Inputs: {:016b}".format(inputs))
        inputs = 127 - inputs & 0x7F
        if inputs < 1:
            return
        index = (int)(math.log2(inputs))
        print("index is " + str(index))
        if inputs > -1:
            print("Key side = " + BUTTONS[index])
            print("state = " + str(self.state_index))
            print("BUTTONS[index]= ", BUTTONS[index])
            if self.state_index == 0:
                if BUTTONS[index]=="1": #YES
                    self.test_report["qrcode"] = True # record test result
                    self.state_index = 1 # move to next state
                    self.repeat_counter = 0 # reset repeat counter
                    self.show_color_and_prompt("red") # show next screen
                if BUTTONS[index]=="2": #RETRY
                    # show QR code for 5 seconds then promot
                    # increment counter
                    self.repeat_counter += 1
                    if (self.repeat_counter > self.num_retries):
                       self.test_report["qrcode"] = False
                       # move to next test/state
                       self.state_index = 1
                       self.repeat_counter = 0
                       self.show_color_and_prompt("red")
                    else:
                        self.show_color_and_prompt("qrcode")
            elif self.state_index == 1:
                if BUTTONS[index]=="1": #YES
                    self.test_report["red"] = True # record test result
                    self.state_index = 2 # move to next state
                    self.repeat_counter = 0 # reset repeat counter
                    self.show_color_and_prompt("green") # show next screen
                if BUTTONS[index]=="2": #RETRY
                    # increment counter
                    self.repeat_counter += 1
                    if (self.repeat_counter > self.num_retries):
                       self.test_report["red"] = False
                       # move to next test/state
                       self.state_index = 2
                       self.repeat_counter = 0
                       self.show_color_and_prompt("green")
                    else:
                        self.show_color_and_prompt("red")
            elif self.state_index == 2:
                print("state = " + str(self.state_index))
                if BUTTONS[index]=="1": #YES
                    self.test_report["green"] = True # record test result
                    self.state_index = 3 # move to next state
                    self.repeat_counter = 0 # reset repeat counter
                    self.show_color_and_prompt("blue") # show next screen
                if BUTTONS[index]=="2": #RETRY
                    # increment counter
                    self.repeat_counter += 1
                    if (self.repeat_counter > self.num_retries):
                       self.test_report["green"] = False
                       # move to next test/state
                       self.state_index = 3
                       self.repeat_counter = 0 # reset repeat counter
                       self.show_color_and_prompt("blue")
                    else:
                        self.show_color_and_prompt("green")
            elif self.state_index == 3:
                if BUTTONS[index]=="1": #YES
                    self.test_report["blue"] = True # record test result
                    # go to final state
                    self.state_index = 4 # move to next state
                    self.repeat_counter = 0 # reset repeat counter
                if BUTTONS[index]=="2": #RETRY
                    # increment counter
                    self.repeat_counter += 1
                    if (self.repeat_counter > self.num_retries):
                       self.test_report["blue"] = False
                       # move to next test/state
                       self.repeat_counter = 0
                       self.state_index = 4
                    else:
                        self.show_color_and_prompt("blue")
            if self.state_index == 4:
                #show test result
                if (self.test_report["qrcode"] and \
                    self.test_report["blue"] and \
                    self.test_report["green"] and \
                    self.test_report["red"]):
                    # Display Test Result on LCD
                    lcd.display([(1,"LCD Test",0,"white"), (2, "Result:", 0, "white"), (3,"Passed",0,"green"), (4,chr(56),1,"green")], 30)
                    self.test_result = True
                else:
                    lcd.display([(1,"LCD Test",0,"white"), (2, "Result:", 0, "white"), (3,"Failed",0,"red"), (4,chr(50),1,"red")], 30)
                    self.test_result = False
                time.sleep(2)
                self.state_index = 5
    def show_color_and_prompt(self, content):
        if content == "qrcode":
            lcd.display([(1,"Title:",0,"white"), (2,"some text",0,"red"), (3,"zxcvbnmmm,./asdfghjkl;qwertyuiop",2,"green")], 20)
            time.sleep(2)
            if self.repeat_counter == self.num_retries:
                lcd.show_prompt("Did you see text & QR code?", [{"text": "Yes", "color": "green"},{"text": "No", "color": "red"}] )
            else:
                lcd.show_prompt("Did you see text & QR code?", [{"text": "Yes", "color": "green"},{"text": "Retry", "color": "red"}] )
        if content in ["green", "red", "blue"]:
            color = content
            image = Image.new("RGB", (240, 240), color)
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, 240,240), outline=0, fill=color)
            lcd.show_image(image)
            time.sleep(0.5)
            message = "Did you see a " + color + " screen?"
            if self.repeat_counter == self.num_retries:
                lcd.show_prompt(message, [{"text": "Yes", "color": "green"},{"text": "No", "color": "red"}] )
            else:
                lcd.show_prompt(message, [{"text": "Yes", "color": "green"},{"text": "Retry", "color": "red"}] )

def main():
    lcd.display([(1,"Starting",0,"white"), (2,"LCD Display",0,"white"), (3,"Test", 0,"white")], 25)
    S = state_machine()
    S.show_color_and_prompt("qrcode")
    print(S.state_index)
    while (S.state_index != 5): # check state machine state 
        time.sleep(1)
    print(S.test_result)
    if S.test_result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)



