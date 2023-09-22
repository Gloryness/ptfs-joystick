import cv2 as cv
import numpy as np
from mss import mss

sct = mss()

templates = []
for i in range(0, 101):
    templates.append(cv.imread(f'templates/{i:02}.png')[:, :, 0])

def get_current_throttle():
    sct_img = sct.grab((898, 89, 987, 102))
    npimg = np.array(sct_img)[:, :, 0]
    thresh = cv.adaptiveThreshold(npimg, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 9, -40)
    thresh[:, :30] = 0
    thresh[:, 61:] = 0

    results = [np.count_nonzero(cv.bitwise_xor(thresh, template)) for template in templates]

    return results.index(min(results))

throttle_precision = {
    1: 0.0375,
    2: 0.0610,
    3: 0.1030,
    4: 0.1350,
    5: 0.1640,
    6: 0.1880,
    7: 0.2220,
    8: 0.2620,
    9: 0.29475,
    10: 0.3245,
    11: 0.371,
    12: 0.404,
    13: 0.430,
    14: 0.462,
    15: 0.4961070,
    16: 0.543,
    17: 0.575,
    18: 0.596,
    19: 0.613,
    20: 0.660,
    21: 0.690,
    22: 0.720,
    23: 0.762,
    24: 0.798,
    25: 0.8225,
    26: 0.854,
    27: 0.895,
    28: 0.930,
    29: 0.9625,
    30: 0.995,
    31: 1.020,
    32: 1.062,
    33: 1.096,
    34: 1.125,
    35: 1.162,
    36: 1.19525,
    37: 1.215,
    38: 1.252,
    39: 1.294,
    40: 1.328,
    41: 1.364,
    42: 1.396,
    43: 1.4275,
    44: 1.462,
    45: 1.4925,
    46: 1.526,
    47: 1.558,
    48: 1.596,
    49: 1.628,
    50: 1.66311,
    51: 1.700,
    52: 1.731,
    53: 1.752,
    54: 1.794,
    55: 1.828,
    56: 1.862,
    57: 1.894,
    58: 1.926,
    59: 1.960,
    60: 1.985,
    61: 2.029,
    62: 2.062,
    63: 2.095,
    64: 2.119,
    65: 2.156,
    66: 2.196,
    67: 2.228,
    68: 2.252,
    69: 2.294,
    70: 2.328,
    71: 2.362,
    72: 2.386,
    73: 2.426,
    74: 2.462,
    75: 2.496,
    76: 2.529,
    77: 2.562,
    78: 2.590,
    79: 2.617,
    80: 2.664,
    81: 2.6875,
    82: 2.728,
    83: 2.755,
    84: 2.795,
    85: 2.820,
    86: 2.867,
    87: 2.900,
    88: 2.929,
    89: 2.962,
    90: 2.995,
    91: 3.029,
    92: 3.055,
    93: 3.101,
    94: 3.120,
    95: 3.158,
    96: 3.190,
    97: 3.229,
    98: 3.252,
    99: 3.296,
    100: 3.335
}

import pydirectinput
import threading
import time

event = threading.Event()
current = 0

def increase_throttle(value):
    duration = throttle_precision[value]
    while not event.is_set():
        pydirectinput.keyDown("w", _pause=False)
        event.wait(duration)
        break

    pydirectinput.keyUp("w", _pause=False)
    print("All done!")
    # perform any cleanup here
    event.clear()
    time.sleep(0.1)
    print(f"Current Throttle: {get_current_throttle()}%")

def interrupt_throttle():
    import time
    time.sleep(throttle_precision[10])
    event.set()

if __name__ == '__main__':
    time.sleep(1.5)

    thread = threading.Thread(target=interrupt_throttle)
    thread.start()
    increase_throttle(10)
