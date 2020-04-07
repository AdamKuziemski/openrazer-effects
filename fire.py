import time

from colorsys import rgb_to_hsv
from opensimplex import OpenSimplex
from openrazer.client import DeviceManager

device_manager = DeviceManager()
simplex = OpenSimplex()
noise_step = 0.16

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

def clamp(color):
    c = int(color)
    return c if c >= 0 else 0

# returns n colors between start (tuple) and end (tuple)
def gradient_linear(start, end, n):
    colors = []

    for color in range(n):
        new_color = (int(start[j] + (float(color) / (n - 1)) * (end[j] - start[j])) for j in range(3))
        colors.append(tuple(new_color))

    return colors

# generate a gradient between the colors
# then spread it into two dimensions to reach black
def gradient_2d(start, end, n):
    color_grid = list(map(
        lambda color: gradient_linear(color, (0, 0, 0), n),
        gradient_linear(start, end, n)
    ))

    # remove black
    for i in range(n):
        color_grid[i].pop()

    # print('gradient colors')
    # for r in range(n):
    #     for c in range(len(color_grid[r])):
    #         print('#%02x%02x%02x' % color_grid[r][c])

    return color_grid

def neighboring_keys(device, row, col):
    return [
        device.fx.advanced.matrix[row, col + 1],
        device.fx.advanced.matrix[row, col - 1],
        device.fx.advanced.matrix[row + 1, col],
        device.fx.advanced.matrix[row - 1, col]
    ]

def cooling_map(rows, cols, start):
    global noise_step
    cooling = [[0] * cols] * rows
    x_offset = 0.0

    for x in range(rows):
        x_offset = x_offset + noise_step
        y_offset = start
        for y in range(cols):
            y_offset = y_offset + noise_step
            noise = simplex.noise2d(x_offset, y_offset)
            cooling[x][y] = (noise ** 3) * 255
    
    return cooling

def draw_fire(device, fire_grid, cool):
    rows = device.fx.advanced.rows
    cols = device.fx.advanced.cols
    cooling = cooling_map(rows, cols, cool)

    for c in range(cols):
        device.fx.advanced.matrix[0, c] = fire_grid[0][-1]

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            colors = list(map(sum, zip(*neighboring_keys(device, r, c))))

            new_rgb = (
                clamp((colors[0] * 0.25) - cooling[r][c]),
                clamp((colors[1] * 0.25) - cooling[r][c]),
                clamp((colors[2] * 0.25) - cooling[r][c])
            )

            cooled_color = int(rgb_to_hsv(*new_rgb)[2] / cols)
            gradient_row = cooled_color % len(fire_grid)
            gradient_col = cooled_color % len(fire_grid[0])

            device.fx.advanced.matrix[r, c] = fire_grid[gradient_row][gradient_col]

    device.fx.advanced.draw()

for device in devices:
    # any pair of colors will do:
    # hot_color = (255, 123, 0) # orange
    # cold_color = (255, 0, 0) # red
    hot_color = (160, 160, 160) # light gray
    cold_color = (0, 255, 255) # light blue
    # hot_color = (243, 130, 255) # light pink
    # cold_color = (75, 0, 156) # dark purple

    rows = device.fx.advanced.rows
    cols = device.fx.advanced.cols
    cooling_offset = 0

    # full brightness is hard on the eyes
    device.brightness = 35

    fire_grid = gradient_2d(hot_color, cold_color, rows)

    device.fx.advanced.matrix.reset()
    device.fx.advanced.draw()

    for c in range(cols):
        device.fx.advanced.matrix[rows - 1, c] = fire_grid[rows - 1][0]
    device.fx.advanced.draw()

    while True:
        draw_fire(device, fire_grid, cooling_offset)
        cooling_offset = cooling_offset + noise_step
        time.sleep(1 / 8)
