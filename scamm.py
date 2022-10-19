# import pyautogui
# import time
# time.sleep(4)
# count=0
# while count<=5:
#     pyautogui.typewrite('Hello'+str(count))
#     pyautogui.press("enter")
#     count+=1

import pywhatkit
count=0
while count<10:
    pywhatkit.sendwhatmsg('+9647828963228','auto message'+str(count),18,38)
    count+=1
