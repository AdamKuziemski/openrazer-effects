import math
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

# Disable daemon effect syncing.
# Without this, the daemon will try to set the lighting effect to every device.
device_manager.sync_effects = False
device_manager.turn_off_on_screensaver = False

def gradient_linear(start, end, n):
    colors = []

    for color in range(n):
        new_color = (int(start[j] + (float(color) / (n - 1)) * (end[j] - start[j])) for j in range(3))
        colors.append(tuple(new_color))

    return colors

beer_color = (242, 142, 28)
foam_color = (246, 246, 227)
dark_color = (166, 166, 154)

class Bubble:
    def __init__(self, rows, cols):
        self.x = random.randint(0, cols - 1)
        self.y = rows - 1
        self.radius = random.choices([0, 1, 2], [0.5, 0.4, 0.1], k = 1)[0]
        self.colors = gradient_linear(foam_color, dark_color, self.radius + 1) if self.radius > 0 else foam_color

        # print(self.x, self.y, self.radius)

    def draw(self, device):
        if self.radius == 0:
            device.fx.advanced.matrix[self.y, self.x] = foam_color
            return

        for p in self.circle(device):
            device.fx.advanced.matrix[p['y'], p['x']] = p['c']

    def update(self):
        self.y = self.y - 1

    def circle(self, device):
        # print(self.x, self.y)
        rows = device.fx.advanced.rows
        cols = device.fx.advanced.cols
        step = 60 / self.radius
        theta = 0
        points = []

        while theta < 360:
            px = int(round(self.x + self.radius * math.cos(theta)))
            py = int(round(self.y + self.radius * math.sin(theta)))
            
            if px >= 0 and px < cols and py >= 0 and py < rows:
                # print('adding', px, py)
                points.append({
                    'x': px,
                    'y': py,
                    'c': self.colors[abs(py - self.y) if px == self.x else abs(px - self.x)]
                })
            
            theta = theta + step

        return points

    def is_dead(self):
        return self.y <= 2

for device in devices:
    rows = device.fx.advanced.rows
    cols = device.fx.advanced.cols
    foam = rows // 3

    device.brightness = 40
    device.fx.advanced.matrix.reset()

    bubbles = []

    for b in range(6):
        bubbles.append(Bubble(rows, cols))

    while True:
        for r in range(foam):
            for c in range(cols):
                device.fx.advanced.matrix[r, c] = foam_color

        for r in range(foam, rows):
            for c in range(cols):
                device.fx.advanced.matrix[r, c] = beer_color

        for b in bubbles:
            b.draw(device)
            b.update()

            if (b.is_dead()):
                bubbles.remove(b)
                bubbles.append(Bubble(rows, cols))

        time.sleep(1 / 4)

        device.fx.advanced.draw()