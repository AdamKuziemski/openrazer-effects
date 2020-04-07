import colorsys
import random
import time

from openrazer.client import DeviceManager

device_manager = DeviceManager()

print("Found {} Razer devices".format(len(device_manager.devices)))

devices = device_manager.devices
for device in devices:
    if not device.fx.advanced:
        print("Skipping device " + device.name + " (" + device.serial + ")")
        devices.remove(device)

# disable daemon effect syncing.
# without this, the daemon will try to set the lighting effect to every device.
device_manager.sync_effects = False
# disable turning the effect off when screensaver is active
device_manager.turn_off_on_screensaver = False

def gradient_linear(start, end, n):
    colors = []

    for color in range(n):
        new_color = (int(start[j] + (float(color) / (n - 1)) * (end[j] - start[j])) for j in range(3))
        colors.append(tuple(new_color))

    return colors

class Line:
    def __init__(self, max_row, layer):
        base_colors = [
            colorsys.rgb_to_hls(36, 205, 0), # 0, 199, 10
            colorsys.rgb_to_hls(16, 85, 0),
            colorsys.rgb_to_hls(8, 55, 0),
        ]
        speed_modifier = [0.6, 0.8, 1]

        self.length = random.randint(6, 10)
        self.speed = random.uniform(0.32, 1) * speed_modifier[layer]
        self.delay = random.randint(0, 6)

        self.x = -self.length
        self.y = random.randint(0, max_row - 1)
        self.z = layer

        self.gradient = gradient_linear((4, 32, 0), colorsys.hls_to_rgb(*base_colors[layer]), self.length)

    def move(self):
        if (self.delay > 0):
            self.delay = self.delay - 1
        else:
            self.x = self.x + self.speed

    def draw(self, device):
        for pos in range(self.length):
            if (self.x + pos >= 0 and self.x + pos < device.fx.advanced.cols):
                device.fx.advanced.matrix[self.y, int(self.x) + pos] = self.gradient[pos]

    def is_out_of_bounds(self, device):
        return self.x - self.length > device.fx.advanced.cols

for device in devices:
    rows = device.fx.advanced.rows
    layer_count = 3

    lines = []
    layers = []

    device.brightness = 80

    for z in range(layer_count):
        line_count = random.randint(4, 6)
        layers.append([])

        for line in range(line_count):
            fall = Line(rows, z)
            lines.append(fall)
            layers[z].append(fall)

    while True:
        device.fx.advanced.matrix.reset()

        for r in range(rows):
            for c in range(device.fx.advanced.cols):
                device.fx.advanced.matrix[r, c] = (0, 6, 0)

        for layer in range(layer_count):
            for line in range(len(layers[layer])):
                layers[layer][line].draw(device)

        device.fx.advanced.draw()
        dead = []

        for i in range(len(lines)):
            lines[i].move()

            if (lines[i].is_out_of_bounds(device)):
                dead.append(lines[i])

        for i in range(len(dead)):
            lines.remove(dead[i])
            layers[dead[i].z].remove(dead[i])

            replacement = Line(rows, dead[i].z)
            lines.append(replacement)
            layers[replacement.z].append(replacement)

        time.sleep(1 / 16)
