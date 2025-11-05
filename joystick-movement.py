from colorama import Style, Fore
from throttle import get_current_throttle, throttle_precision
import pydirectinput
import pyautogui
import threading
import pyglet

BRIGHT = Style.BRIGHT
NORMAL = Style.NORMAL
DIM = Style.DIM
BLACK = Fore.LIGHTBLACK_EX
RED = Fore.LIGHTRED_EX
DARK_RED = Fore.RED
GREEN = Fore.LIGHTGREEN_EX
DARK_GREEN = Fore.GREEN
YELLOW = Fore.LIGHTYELLOW_EX
BLUE = Fore.LIGHTBLUE_EX
DARK_BLUE = Fore.BLUE
MAGENTA = Fore.LIGHTMAGENTA_EX
DARK_MAGENTA = Fore.MAGENTA
CYAN = Fore.LIGHTCYAN_EX
DARK_CYAN = Fore.CYAN
WHITE = Fore.LIGHTWHITE_EX
RESET = Style.RESET_ALL

joysticks = pyglet.input.get_joysticks()

joystick = list(filter(lambda joystick: joystick.device.name == "T.A320 Copilot", joysticks))[0]
quadrant = list(filter(lambda joystick: joystick.device.name == "TCA Q-Eng 1&2", joysticks))[0]

joystick.open()
quadrant.open()

default_x = 1920 // 2
min_x = 120
max_x = 1800
default_y = 580
min_y = 80
max_y = 1000

x = default_x
y = default_y

joystick_name = "T.A320 Copilot"
quadrant_name = "TCA Q-Eng 1&2"
state = "Ground"
ground_rudder = "Joystick"
current_flap_configuration = 0
current_spoiler_configuration = 0
throttle_1_percentage = 0
throttle_2_percentage = 0
external = False
camera = False
camera_hat = (0, 0)

rev_throttle = (-0.06, -0.5)
ground_throttle = (0.44, 0.07)
clb_lvr = (0.94, 0.56)
flex_detent = (1.5, 1.06)

"""
Airliners:
- landing speed: 50%
- taxi speed: 15%
Jets:
- landing speed: 35%
- taxi speed: 9%
"""

############################################################
max_pushback = 32
max_ground_taxi = 20
throttle_detents = [55, 80, 100] # A320
# throttle_detents = [52, 80, 100] # A380
# throttle_detents = [35, 60, 100]
############################################################

needed_throttle = 0
current_throttle = 0
ignition = False
engines = [False, False]
autopilot = False
twin_engine = True
pushback = False
parking_brake = True

stop_event = threading.Event()
third_event = threading.Event()
secondary_event = threading.Event()
event = threading.Event()

def camera_thread():
    global camera_hat
    while not stop_event.is_set():
        if camera_hat != (0, 0):
            pydirectinput.mouseDown(button="right", _pause=False)
            value1 = 5 if camera_hat[0] == 1 else -5 if camera_hat[0] == -1 else 0
            value2 = 5 if camera_hat[1] == 1 else -5 if camera_hat[1] == -1 else 0
            if external is False:
                if value2 > 0:
                    value2 = -value2
                else:
                    value2 = abs(value2)
            pydirectinput.moveRel(value1, value2, _pause=False, relative=True)

        if not camera:
            third_event.wait(0.2)
        else:
            third_event.wait(0.005)

def throttle_thread():
    global current_throttle, pushback
    while not stop_event.is_set():
        if (not twin_engine) or (twin_engine and all(engines)):
            if needed_throttle >= 0: # Forward Thrust

                if current_throttle < needed_throttle:
                    throttle_difference = abs(current_throttle - needed_throttle)
                    duration = throttle_precision[throttle_difference]

                    event.clear()
                    while not event.is_set():
                        pydirectinput.keyDown("w", _pause=False)
                        event.wait(duration)
                        break

                    pydirectinput.keyUp("w", _pause=False)
                    event.clear()
                    secondary_event.wait(0.10)
                    current_throttle = get_current_throttle()
                    continue

                if current_throttle > needed_throttle:
                    throttle_difference = abs(current_throttle - needed_throttle)
                    duration = throttle_precision[throttle_difference]

                    event.clear()
                    while not event.is_set():
                        pydirectinput.keyDown("s", _pause=False)
                        event.wait(duration)
                        break

                    pydirectinput.keyUp("s", _pause=False)
                    event.clear()
                    secondary_event.wait(0.10)
                    current_throttle = get_current_throttle()
                    continue

                if pushback:
                    pushback = False
                    pydirectinput.press("p", _pause=False)
                    secondary_event.wait(0.10)
                    print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{YELLOW}Pushback Disengaged.{RESET}")

            elif needed_throttle < 0: # Reverse Thrust
                if not pushback:
                    pushback = True
                    pydirectinput.press("p", _pause=False)
                    secondary_event.wait(0.10)
                    print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{YELLOW}Pushback Engaged.{RESET}")

                if current_throttle < abs(needed_throttle):
                    throttle_difference = abs(current_throttle - abs(needed_throttle))
                    duration = throttle_precision[throttle_difference]

                    event.clear()
                    while not event.is_set():
                        pydirectinput.keyDown("w", _pause=False)
                        event.wait(duration)
                        break

                    pydirectinput.keyUp("w", _pause=False)
                    event.clear()
                    secondary_event.wait(0.10)
                    current_throttle = get_current_throttle()
                    continue

                if current_throttle > abs(needed_throttle):
                    throttle_difference = abs(current_throttle - abs(needed_throttle))
                    duration = throttle_precision[throttle_difference]

                    event.clear()
                    while not event.is_set():
                        pydirectinput.keyDown("s", _pause=False)
                        event.wait(duration)
                        break

                    pydirectinput.keyUp("s", _pause=False)
                    event.clear()
                    secondary_event.wait(0.10)
                    current_throttle = get_current_throttle()
                    continue

        secondary_event.wait(0.1)

def get_overall_throttle(throttle_1, throttle_2):
    return (throttle_1 + throttle_2) // 2

@quadrant.event
def on_joybutton_press(joystick, button):
    global ignition, twin_engine, parking_brake, needed_throttle
    if button == 2: # Engine 1 start
        if ignition:
            engines[0] = True
            print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{GREEN}Engine 1 ignition.{RESET}")
            if (not twin_engine) or (twin_engine and all(engines)): # Engine START
                pydirectinput.press("e", _pause=False)
                print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{MAGENTA}Engine start.{RESET}")
        else:
            print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{RED}Failed to start Engine 1.{RESET}")

    elif button == 3: # Engine 2 start
        if ignition:
            engines[1] = True
            if not twin_engine:
                engines[1] = False
                print(f"{RED}For {YELLOW}twin engine mode{RED}, engine 1 must be active ONLY.{RESET}")
            else:
                print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{GREEN}Engine 2 ignition.{RESET}")
                if twin_engine and all(engines): # Engine START
                    pydirectinput.press("e", _pause=False)
                    print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{MAGENTA}Engine start.{RESET}")
        else:
            print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{RED}Failed to start Engine 2.{RESET}")

    elif button == 4:
        if twin_engine:
            print(f"{CYAN}Twin engine mode {RED}disabled{CYAN}.{RESET}")
            twin_engine = False
        else:
            print(f"{CYAN}Twin engine mode {GREEN}enabled{CYAN}.{RESET}")
            twin_engine = True

    elif button == 7: # IGN/START
        print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{GREEN}IGN/START.{RESET}")
        ignition = True

    elif button == 19: # Parking Brake On
        print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Parking brake ON.{RESET}")
        parking_brake = True

        if state == "Ground":
            if needed_throttle > max_ground_taxi:
                needed_throttle -= max_ground_taxi
            elif needed_throttle >= 0:
                needed_throttle = 0
            elif needed_throttle < 0:
                needed_throttle = -round((8 / max_pushback) * abs(needed_throttle))

    elif button == 20:  # Landing Gear Up
        print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Landing gear UP.{RESET}")
        pydirectinput.press("g", _pause=False)

@quadrant.event
def on_joybutton_release(joystick, button):
    global ignition, parking_brake, needed_throttle, throttle_1_percentage, throttle_2_percentage, pushback
    if button == 2: # Engine 1 cutoff
        if engines[0] is True:
            engines[0] = False
            print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{RED}Engine 1 cutoff.{RESET}")

            if twin_engine and not any(engines): # Engine STOP
                pydirectinput.press("e", _pause=False)
                print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{DARK_RED}Engine shutdown.{RESET}")
                if pushback:
                    pushback = False
                    pydirectinput.press("p", _pause=False)
                    print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{YELLOW}Pushback Disengaged.{RESET}")

            elif not twin_engine:
                pydirectinput.press("e", _pause=False)
                print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{RED}Engine cutoff.{RESET}")
                if pushback:
                    pushback = False
                    pydirectinput.press("p", _pause=False)
                    print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{YELLOW}Pushback Disengaged.{RESET}")
            else:
                throttle_1_percentage = 0
                if twin_engine:
                    throttle = get_overall_throttle(throttle_1_percentage, throttle_2_percentage)
                else:
                    throttle = throttle_1_percentage

                if throttle < 0:
                    throttle = -round((max_pushback / 100) * abs(throttle))

    elif button == 3: # Engine 2 cutoff
        if engines[1] is True:
            engines[1] = False
            print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{RED}Engine 2 cutoff.{RESET}")

            if twin_engine and not any(engines): # Engine STOP
                pydirectinput.press("e", _pause=False)
                print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{DARK_RED}Engine shutdown.{RESET}")
                if pushback:
                    pushback = False
                    pydirectinput.press("p", _pause=False)
                    print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{YELLOW}Pushback Disengaged.{RESET}")
            else:
                throttle_2_percentage = 0
                if twin_engine:
                    throttle = get_overall_throttle(throttle_1_percentage, throttle_2_percentage)
                else:
                    throttle = throttle_1_percentage

                if throttle < 0:
                    throttle = -round((max_pushback / 100) * abs(throttle))

    elif button == 7: # MODE NORM
        print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{CYAN}MODE NORM.{RESET}")
        ignition = False

    elif button == 19: # Parking Brake Off
        print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Parking brake OFF.{RESET}")
        parking_brake = False

        if state == "Ground":

            if twin_engine:
                throttle = get_overall_throttle(throttle_1_percentage, throttle_2_percentage)
            else:
                throttle = throttle_1_percentage

            if throttle < 0:
                throttle = -round((max_pushback / 100) * abs(throttle))

            if throttle >= 0 and throttle <= max_ground_taxi:
                throttle = max_ground_taxi

            needed_throttle = throttle

    elif button == 20: # Landing Gear Down
        print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Landing gear DOWN.{RESET}")
        pydirectinput.press("g", _pause=False)

@quadrant.event
def on_joyaxis_motion(joystick, axis, value):
    global current_flap_configuration, current_spoiler_configuration,  throttle_1_percentage, throttle_2_percentage, current_throttle, needed_throttle, pushback
    if axis == "z": # Flaps
        if value < -0.82: # Flaps 0
            if current_flap_configuration == 0:
                return
            if 0 > current_flap_configuration:
                pydirectinput.press("h", _pause=False) # Extend Flap
            else:
                pydirectinput.press("y", _pause=False) # Retract Flap
            current_flap_configuration = 0
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Flaps set to 0.{RESET}")

        elif -0.62 < value < -0.38: # Flaps 1
            if current_flap_configuration == 1:
                return
            if 1 > current_flap_configuration:
                pydirectinput.press("h", _pause=False) # Extend Flap
            else:
                pydirectinput.press("y", _pause=False) # Retract Flap
            current_flap_configuration = 1
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Flaps set to 1.{RESET}")

        elif -0.12 < value < 0.12: # Flaps 2
            if current_flap_configuration == 2:
                return
            if 2 > current_flap_configuration:
                pydirectinput.press("h", _pause=False) # Extend Flap
            else:
                pydirectinput.press("y", _pause=False) # Retract Flap
            current_flap_configuration = 2
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Flaps set to 2.{RESET}")

        elif 0.38 < value < 0.62: # Flaps 3
            if current_flap_configuration == 3:
                return
            if 3 > current_flap_configuration:
                pydirectinput.press("h", _pause=False) # Extend Flap
            else:
                pydirectinput.press("y", _pause=False) # Retract Flap
            current_flap_configuration = 3
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Flaps set to 3.{RESET}")

        elif value > 0.82: # Flaps 4
            if current_flap_configuration == 4:
                return
            if 4 > current_flap_configuration:
                pydirectinput.press("h", _pause=False) # Extend Flap
            else:
                pydirectinput.press("y", _pause=False) # Retract Flap
            current_flap_configuration = 4
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Flaps set to 4.{RESET}")

    elif axis == "rz": # Spoilers
        if value < -0.82: # Spoilers 0%
            if current_spoiler_configuration == 0:
                return
            current_spoiler_configuration = 0
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Spoilers set to 0%.{RESET}")

        elif -0.62 < value < -0.38: # Spoilers 25%
            if current_spoiler_configuration == 25:
                return
            current_spoiler_configuration = 25
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Spoilers set to 25%.{RESET}")

        elif -0.12 < value < 0.12: # Spoilers 50%
            if current_spoiler_configuration == 50:
                return
            current_spoiler_configuration = 50
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Spoilers set to 50%.{RESET}")

        elif 0.38 < value < 0.62: # Spoilers 75%
            if current_spoiler_configuration == 75:
                return
            current_spoiler_configuration = 75
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Spoilers set to 75%.{RESET}")

        elif value > 0.82: # Spoilers 100%
            if current_spoiler_configuration == 100:
                return
            current_spoiler_configuration = 100
            print(f"{WHITE}[{YELLOW}CONFIG{WHITE}] {BRIGHT}{CYAN}Spoilers set to 100%.{RESET}")

    elif axis == "x": # Throttle 1
        if all(engines) or (not twin_engine and engines[0] is True):
            real_value = round(1.5 - (value + 1), 2)

            if real_value < -0.05: # Reverse Thrust
                throttle_1_percentage = round((round(real_value, 2)/0.5) * 100)
            elif real_value >= -0.05 and real_value <= 0.06: # Idle Thrust
                throttle_1_percentage = 0
            elif real_value >= 0.45 and real_value <= 0.55: # CLB (LANDING)
                throttle_1_percentage = throttle_detents[0]
            elif real_value >= 0.95 and real_value <= 1.05: # CLB
                throttle_1_percentage = throttle_detents[1]
            else:
                minimum = 0
                if real_value >= flex_detent[0]:
                    minimum = throttle_detents[2]
                elif real_value >= clb_lvr[0]:
                    minimum = throttle_detents[1]
                elif real_value >= ground_throttle[0]:
                    minimum = throttle_detents[0]

                if ground_throttle[1] < real_value < ground_throttle[0]:
                    percent = round(((0.5 - abs(real_value - ground_throttle[0])) / 0.5) * 100, 2)
                    throttle_1_percentage = round(minimum + ((throttle_detents[0] / 100) * percent))
                elif clb_lvr[1] < real_value < clb_lvr[0]:
                    percent = round(((0.5 - abs(real_value - clb_lvr[0])) / 0.5) * 100, 2)
                    throttle_1_percentage = round(minimum + ((abs(throttle_detents[0] - throttle_detents[1]) / 100) * percent))
                elif flex_detent[1] < real_value < flex_detent[0]:
                    percent = round(((0.5 - abs(real_value - flex_detent[0])) / 0.5) * 100, 2)
                    throttle_1_percentage = round(minimum + ((abs(throttle_detents[1] - throttle_detents[2]) / 100) * percent))
                else:
                    throttle_1_percentage = minimum

    elif axis == "y": # Throttle 2
        if all(engines):
            real_value = round(1.5 - (value + 1), 2)

            if real_value < -0.05: # Reverse Thrust
                throttle_2_percentage = round((round(real_value, 2) / 0.5) * 100)
            elif real_value >= -0.05 and real_value <= 0.06: # Idle Thrust
                throttle_2_percentage = 0
            elif real_value >= 0.45 and real_value <= 0.55: # CLB (LANDING)
                throttle_2_percentage = throttle_detents[0]
            elif real_value >= 0.95 and real_value <= 1.05: # CLB
                throttle_2_percentage = throttle_detents[1]
            else:
                minimum = 0
                if real_value >= flex_detent[0]:
                    minimum = throttle_detents[2]
                elif real_value >= clb_lvr[0]:
                    minimum = throttle_detents[1]
                elif real_value >= ground_throttle[0]:
                    minimum = throttle_detents[0]

                if ground_throttle[1] < real_value < ground_throttle[0]:
                    percent = round(((0.5 - abs(real_value - ground_throttle[0])) / 0.5) * 100, 2)
                    throttle_2_percentage = round(minimum + ((throttle_detents[0] / 100) * percent))
                elif clb_lvr[1] < real_value < clb_lvr[0]:
                    percent = round(((0.5 - abs(real_value - clb_lvr[0])) / 0.5) * 100, 2)
                    throttle_2_percentage = round(minimum + ((abs(throttle_detents[0] - throttle_detents[1]) / 100) * percent))
                elif flex_detent[1] < real_value < flex_detent[0]:
                    percent = round(((0.5 - abs(real_value - flex_detent[0])) / 0.5) * 100, 2)
                    throttle_2_percentage = round(minimum + ((abs(throttle_detents[1] - throttle_detents[2]) / 100) * percent))
                else:
                    throttle_2_percentage = minimum

    if twin_engine:
        throttle = get_overall_throttle(throttle_1_percentage, throttle_2_percentage)
    else:
        throttle = throttle_1_percentage

    if state == "Ground":
        if parking_brake:
            if throttle > max_ground_taxi:
                throttle -= max_ground_taxi
            elif throttle >= 0:
                throttle = 0
            elif throttle < 0:
                throttle = -round((8 / max_pushback) * abs(throttle))
        else:
            if throttle >= 0 and throttle <= max_ground_taxi:
                throttle = max_ground_taxi
            elif throttle < 0:
                throttle = -round((max_pushback / 100) * abs(throttle))
    elif state == "Airborne":
        if throttle > 0 and throttle <= 10:
            throttle -= round((throttle/100) * current_spoiler_configuration)
        elif throttle > 10:
            throttle -= round((10 / 100) * current_spoiler_configuration)
        elif throttle < 0:
            pushback_value = max_pushback

            pushback_value += round((68 / 100) * current_spoiler_configuration)

            throttle = -round((pushback_value / 100) * abs(throttle))

    event.set()
    needed_throttle = throttle

@joystick.event
def on_joybutton_press(joystick, button):
    global ground_rudder, state, autopilot, external, camera, camera_hat, needed_throttle
    if button == 0: # Switch between Rudder control on the ground (ONLY) and airborne mode meaning full joystick rotation & rudder control.
        if state == "Airborne":
            state = "Ground"
        else:
            state = "Airborne"

        if state == "Ground":
            if parking_brake:
                if needed_throttle > max_ground_taxi:
                    needed_throttle -= max_ground_taxi
                elif needed_throttle >= 0:
                    needed_throttle = 0
                elif needed_throttle < 0:
                    needed_throttle = -round((8 / max_pushback) * abs(needed_throttle))
            else:
                if needed_throttle >= 0 and needed_throttle <= max_ground_taxi:
                    needed_throttle = max_ground_taxi
                elif needed_throttle < 0:
                    needed_throttle = -round((max_pushback / 100) * abs(needed_throttle))

        print(f"{BLUE}Switching to aircraft control state: {MAGENTA}{state}{RESET}")
    elif button == 1:
        if ground_rudder == "Rudder":
            ground_rudder = "Joystick"
        else:
            ground_rudder = "Rudder"
        print(f"{BLUE}Switching to Ground Rudder Control: {MAGENTA}{ground_rudder}{RESET}")
    elif button == 2: # External Camera
        if external:
            external = False
            camera = False
            camera_hat = (0, 0)
            for i in range(7):
                pyautogui.scroll(777, _pause=False)
                third_event.wait(0.1)
            pydirectinput.mouseUp(button="right", _pause=False)
            print(f"{BLUE}External Camera: {RED}INACTIVE{RESET}")
        else:
            external = True
            camera = True
            pydirectinput.mouseDown(button="right", _pause=False)
            third_event.wait(0.1)
            for i in range(7):
                pyautogui.scroll(-777, _pause=False)
                third_event.wait(0.1)
            print(f"{BLUE}External Camera: {MAGENTA}ACTIVE{RESET}")
    elif button == 3: # Altitude Hold (autopilot)
        if autopilot:
            print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{RED}Autopilot disconnected.{RESET}")
            autopilot = False
        else:
            print(f"{WHITE}[{DARK_RED}IMPORTANT{WHITE}] {BRIGHT}{GREEN}Autopilot connected.{RESET}")
            autopilot = True
        pydirectinput.press("r", _pause=False)

@joystick.event
def on_joyhat_motion(joystick, hat_x, hat_y):
    global camera, camera_hat
    if external is True:
        camera = True
        if hat_x == 0 and hat_y == 0:
            camera = False
            pydirectinput.mouseDown(button="right", _pause=False)

        camera_hat = (hat_x, hat_y)

@joystick.event
def on_joyaxis_motion(joystick, axis, value):
    global x, y
    if state == "Airborne" and camera is False:
        if axis == "x":
            if value in [1.5259021896696368e-05, -1.5259021896696368e-05]: # Idle
                pydirectinput.moveTo(default_x, y, _pause=False)
                x = default_x
            else:

                if 0 < value < 1:  # Yaw Right
                    joystick_percentage = (value / 1) * 100
                    x_rel = ((max_x - default_x) / 100) * joystick_percentage

                    x = round(default_x + x_rel)
                elif -1 < value < 0:  # Yaw Left
                    joystick_percentage = (value / -1) * 100
                    x_rel = ((default_x - min_x) / 100) * joystick_percentage

                    x = round(default_x - x_rel)

                pydirectinput.moveTo(x, y, _pause=False)

        elif axis == "y":
            if value in [1.5259021896696368e-05, -1.5259021896696368e-05]: # Idle
                pydirectinput.moveTo(x, default_y, _pause=False)
                y = default_y
            else:
                if 0 < value < 1: # Pitch Up
                    joystick_percentage = (value / 1) * 100
                    y_rel = ((max_y - default_y) / 100) * joystick_percentage

                    y = round(default_y - y_rel)
                elif -1 < value < 0: # Pitch Down
                    joystick_percentage = (value / -1) * 100
                    y_rel = ((default_y - min_y) / 100) * joystick_percentage

                    y = round(default_y + y_rel)

                pydirectinput.moveTo(x, y, _pause=False)

        elif axis == "rz":
            if value in [1.5259021896696368e-05, -1.5259021896696368e-05]: # Idle
                pydirectinput.keyUp("a", _pause=False)
                pydirectinput.keyUp("d", _pause=False)

            elif 0 < value < 1: # Rudder Right
                pydirectinput.keyDown("d", _pause=False)

            elif -1 < value < 0: # Rudder Left
                pydirectinput.keyDown("a", _pause=False)
    else:
        pydirectinput.mouseUp(button="right", _pause=False)
        if ground_rudder == "Rudder":
            if axis == "rz":
                if value in [1.5259021896696368e-05, -1.5259021896696368e-05]: # Idle
                    pydirectinput.moveTo(default_x, default_y, _pause=False)
                    x = default_x
                else:

                    if 0 < value < 1:  # Rudder Right
                        joystick_percentage = (value / 1) * 100
                        x_rel = ((max_x - default_x) / 100) * joystick_percentage

                        x = round(default_x + x_rel)
                    elif -1 < value < 0:  # Rudder Left
                        joystick_percentage = (value / -1) * 100
                        x_rel = ((default_x - min_x) / 100) * joystick_percentage

                        x = round(default_x - x_rel)

                    pydirectinput.moveTo(x, y, _pause=False)
        else:
            if axis == "x":
                if value in [1.5259021896696368e-05, -1.5259021896696368e-05]: # Idle
                    pydirectinput.moveTo(default_x, default_y, _pause=False)
                    x = default_x
                else:

                    if 0 < value < 1:  # Rudder Right
                        joystick_percentage = (value / 1) * 100
                        x_rel = ((max_x - default_x) / 100) * joystick_percentage

                        x = round(default_x + x_rel)
                    elif -1 < value < 0:  # Rudder Left
                        joystick_percentage = (value / -1) * 100
                        x_rel = ((default_x - min_x) / 100) * joystick_percentage

                        x = round(default_x - x_rel)

                    pydirectinput.moveTo(x, y, _pause=False)

thread = threading.Thread(target=throttle_thread)
thread.start()

cam_thread = threading.Thread(target=camera_thread)
cam_thread.start()

try:
    pyglet.app.run()
except KeyboardInterrupt:
    print("\nKeyboardInterrupt received — exiting cleanly...")
    stop_event.set()
    thread.join()
    cam_thread.join()
    pyglet.app.exit()
