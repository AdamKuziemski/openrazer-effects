import colorsys
# import random
import time
# import threading
# import numpy as np
from opensimplex import OpenSimplex

from openrazer.client import DeviceManager
from openrazer.client import constants as c

device_manager = DeviceManager()
simplex = OpenSimplex()

print("Found {} Razer devices".format(len(device_manager.devices)))

devices = device_manager.devices
for device in devices:
    if not device.fx.advanced:
        print("Skipping device " + device.name + " (" + device.serial + ")")
        devices.remove(device)

# Disable daemon effect syncing.
# Without this, the daemon will try to set the lighting effect to every device.
device_manager.sync_effects = False
device_manager.turn_off_on_screensaver = False

def avg(sources, index):
    return int(sum(map(lambda color: color[index], sources)) / len(sources))

def neighboring_keys(device, row, col):
    return [
        device.fx.advanced.matrix[row, col + 1],
        device.fx.advanced.matrix[row, col - 1],
        device.fx.advanced.matrix[row + 1, col],
        device.fx.advanced.matrix[row - 1, col]
    ]

def fabulous(device, rows, cols):
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            neighbors = neighboring_keys(device, r, c)
            average = (avg(neighbors, 0), avg(neighbors, 1), avg(neighbors, 2))
            hue = colorsys.rgb_to_hsv(*average)
            noise = abs(simplex.noise2d(r, c)) * 255

            device.fx.advanced.matrix[r, c] = colorsys.hsv_to_rgb(hue[0], hue[1] - noise, hue[2])
    device.fx.advanced.draw()

for device in devices:
    rows = device.fx.advanced.rows
    cols = device.fx.advanced.cols

    device.fx.advanced.matrix.reset()
    device.fx.advanced.draw()

    for c in range(cols):
        device.fx.advanced.matrix[rows - 1, c] = (0, 1, 255)

    while True:
        fabulous(device, rows, cols)
        time.sleep(1/8)