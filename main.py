import time
import network
import urequests as requests
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
from pngdec import PNG
from pimoroni import Button

# set up the hardware
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, rotate=0)
led = RGBLED(6, 7, 8)

# set the display backlight to 50%
display.set_backlight(0.5)

# set up constants for drawing
WIDTH, HEIGHT = display.get_bounds()

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)

ssid = '_SSID_'
password = '_PASSWORD_'
wlan = None
status = None


def wifi_connector():
    global wlan, status
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(2)

    # Handle connection error
    if wlan.status() != 3:
        return None
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        return True


def show_img(x, y):
    res = requests.get(
        url=f'http://192.168.1.212:8501/png?x={str(x)}&y={str(y)}')
    with open('img.png', 'wb') as fd:
        fd.write(res.content)
    res.close()

    display.clear()
    png = PNG(display)
    png.open_file("img.png")
    png.decode(0, 0)
    display.update()


class Btn:
    def __init__(self):
        self.state = {'A': {'state': False, 'upd': False, 'dur': 0}, 'X': {'state': False, 'upd': False, 'dur': 0},
                      'B': {'state': False, 'upd': False, 'dur': 0}, 'Y': {'state': False, 'upd': False, 'dur': 0}}
        self.is_changed = False
        self.start = time.ticks_ms()
        self.minstep = 10

        self.button_a = Button(12)
        self.button_b = Button(13)
        self.button_x = Button(14)
        self.button_y = Button(15)

    def update_state(self):
        diff = time.ticks_diff(time.ticks_ms(), self.start)
        self.state['A']['dur'] = diff
        self.state['X']['dur'] = diff
        self.state['B']['dur'] = diff
        self.state['Y']['dur'] = diff

        if diff < self.minstep:
            return

        a = self.button_a.raw()
        x = self.button_x.raw()
        b = self.button_b.raw()
        y = self.button_y.raw()

        self.state['A']['upd'] = self.state['A']['state'] != a
        self.state['A']['state'] = a

        self.state['X']['upd'] = self.state['X']['state'] != x
        self.state['X']['state'] = x

        self.state['B']['upd'] = self.state['B']['state'] != b
        self.state['B']['state'] = b

        self.state['Y']['upd'] = self.state['Y']['state'] != y
        self.state['Y']['state'] = y

        self.start = time.ticks_ms()

    def is_pressed(self, btn):
        return self.state[btn]['state'] and self.state[btn]['dur'] >= self.minstep

    def is_all_unpressed(self):
        if (self.state['A']['state'] == self.state['X']['state'] == self.state['B']['state'] == self.state['Y']['state'] == False):
            if (self.state['A']['upd'] or self.state['X']['upd'] or self.state['B']['upd'] or self.state['Y']['upd']):
                self.state['A']['upd'] = False
                self.state['X']['upd'] = False
                self.state['B']['upd'] = False
                self.state['Y']['upd'] = False
                return True
        return False


xc = 2605
yc = 1645
stp = 1
stp_gain_inc = 0.35
stp_gain = 0
if __name__ == '__main__':
    btn = Btn()

    led.set_rgb(10, 100, 10)
    if wifi_connector():
        led.set_rgb(0, 0, 0)
        show_img(xc, yc)

        while True:
            btn.update_state()
            old_x = xc
            old_y = yc

            if btn.is_pressed('A'):
                if xc >= stp + int(stp_gain):
                    xc = xc - (stp + int(stp_gain))
            if btn.is_pressed('X'):
                if xc <= 6000 - (stp + int(stp_gain)):
                    xc = xc + stp + int(stp_gain)
            if btn.is_pressed('B'):
                if yc >= stp + int(stp_gain):
                    yc = yc - (stp + int(stp_gain))
            if btn.is_pressed('Y'):
                if yc <= 4000 - (stp + int(stp_gain)):
                    yc = yc + stp + int(stp_gain)

            if old_x != xc or old_y != yc:
                display.set_pen(BLACK)
                display.rectangle(0, 0, 135, 15)
                display.set_pen(WHITE)
                display.text(f"x:{str(xc)}, y:{str(yc)}", 1, 1, scale=2)
                display.update()
                stp_gain = stp_gain + stp_gain_inc

            if (btn.is_all_unpressed()):
                show_img(xc, yc)
                stp_gain = 0

            time.sleep(0.01)
    else:
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.text("Wifi error code:" + str(status), 1, 1, scale=1)
        display.update()
