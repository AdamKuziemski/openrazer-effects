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

def rgb_devices(device_manager):
    devices = device_manager.devices
    for device in devices:
        if not device.fx.advanced:
            print("Skipping device " + device.name + " (" + device.serial + ")")
            devices.remove(device)
    return devices

def neighboring_keys(device, row, col):
    return [
        device.fx.advanced.matrix[row, col + 1],
        device.fx.advanced.matrix[row, col - 1],
        device.fx.advanced.matrix[row + 1, col],
        device.fx.advanced.matrix[row - 1, col]
    ]
