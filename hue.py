from openrazer.client import DeviceManager
from razer_utils import gradient_2d, rgb_devices

device_manager = DeviceManager()

device_manager.sync_effects = False
device_manager.turn_off_on_screensaver = False

for device in rgb_devices(device_manager):
    x1 = (0, 232, 62)
    y1 = (232, 0, 162)

    x2 = (235, 114, 0)
    y2 = (0, 223, 235)

    rows = device.fx.advanced.rows
    cols = device.fx.advanced.cols

    hue = gradient_2d(x1, y1, x2, y2, rows, cols)

    device.fx.advanced.matrix.reset()

    for r in range(rows):
        for c in range(cols):
            device.fx.advanced.matrix[r, c] = hue[r][c]

    device.fx.advanced.draw()
