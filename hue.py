from openrazer.client import DeviceManager

device_manager = DeviceManager()

print("Found {} Razer devices".format(len(device_manager.devices)))

devices = device_manager.devices
for device in devices:
    if not device.fx.advanced:
        print("Skipping device " + device.name + " (" + device.serial + ")")
        devices.remove(device)

# disable turning rgb off
device_manager.turn_off_on_screensaver = False

def gradient_linear(start, end, n):
    colors = []

    for color in range(n):
        new_color = (int(start[j] + (float(color) / (n - 1)) * (end[j] - start[j])) for j in range(3))
        colors.append(tuple(new_color))

    return colors

def gradient_2d(top_left, bottom_left, top_right, bottom_right, rows, cols):
    first_col = gradient_linear(top_left, bottom_left, rows)
    last_col = gradient_linear(top_right, bottom_right, rows)

    return [gradient_linear(first_col[r], last_col[r], cols) for r in range(rows)]

for device in devices:
    x1 = (0, 232, 62)
    y1 = (232, 0, 162)

    x2 = (235, 114, 0)
    y2 = (0, 223, 235)

    rows = device.fx.advanced.rows
    cols = device.fx.advanced.cols

    hue = gradient_2d(x1, y1, x2, y2, rows, cols)
    # print(hue)

    device.fx.advanced.matrix.reset()

    for r in range(rows):
        for c in range(cols):
            device.fx.advanced.matrix[r, c] = hue[r][c]

    device.fx.advanced.draw()
