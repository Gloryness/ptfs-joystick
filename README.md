# ptfs-joystick
A project dedicated for the Throttlemaster Airbus Edition Captain Pack that lets you control PTFS (Pilot Training Flight Simulator) using no other than the joystick aswell as the throttle, along with other features.

# The journey
### 11th September 2023
This is the day I got the Throttlemaster Airbus Edition Captain Pack. Later that day I was playing PTFS and stumbled across a thought of "maybe I could make it work with PTFS"

Did a little testing of trying to get the hardware to show up in Python, but I couldn't find anything yet. I tried the `inputs` libary but, well.. that's 7 years out of date and doesn't work for me.

### 12th September 2023
This is also very inconveniently my first day back at College. Throughout the day I thought of ways I could detect the hardware.<br/>
Did a bit of research throughout the day I was there, and came across **[pyglet](https://github.com/pyglet/pyglet)**, an actively maintained multimedia libary for Python. Perfect!

Later that day when I got home, I tried it out, and successfully detected the joystick and throttle!<br/>
The rest of the day went like this:
- 18:15 - detected the joystick & throttle using pyglet.
- 18:30 - successfully detected joystick axis movements for both UP, DOWN, LEFT, RIGHT and also the rudder.
- 18:40 - alot of ideas sparked into my brain at this point. Altitude Hold for the red button on the joystick? Reverse thrust for pushback?
- 19:00 - me testing in-game where the cursor should be to represent an idle joystick. (center of screen roughly)
- 19:50 - Huh! PyAutoGui doesn't work?!?!? What's going on wtf!??!
  - Yeah. Did some research on "pyautogui move not working for game", turns out it's some complicated stuff to do with DirectX and etc.
  - BUT DO NOT FEAR! FOR **[pydirectinput](https://github.com/learncodebygaming/pydirectinput)** IS HERE!
    - It's a fork of pyautogui, however supports DirectX mouse movements. Perfect! It works!
- 20:40 - Successfully made mouse movements react to my joystick. WOOHOO!
- 21:00 - Around here I was probably implementing gound VS airborne state.
  - Airborne for full joystick and rudder control, and ground for only rudder control - with this being a toggleable mode by a button on my joystick.
