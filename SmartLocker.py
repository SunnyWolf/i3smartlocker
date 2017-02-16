from PIL import Image, ImageOps, ImageDraw, ImageFont
import subprocess
import os.path as Path
import re

class ScreenLocker:
    b_out = '/tmp/lockscreen.png'
    b_main = {
        'background': 'wallpaper.jpg',
        'lock': 'lock.png'
    }
    b_weather = {
        'w_sun': 'wheather_sun.png',
        'w_sun_rain': 'wheather_sun_rain.png',
        'w_cloud': 'wheather_cloud.png',
        'w_snow': 'wheather_snow.png',
    }

    font_hello = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"
    font_hello_size = 40

    t_hello = "Please enter password\nto unlock"
    t_err_not_configured = "Error: Not configured!"

    resolution = [0, 0]

    color_background = (30, 30, 50, 255)
    color_text = (200, 200, 200, 255)
    color_lock = (100, 150, 170, 255)
    color_border = (30, 30, 40, 255)

    i_background = ''

    configured = False

    @staticmethod
    def get_screen_resolution():
        import subprocess
        output = subprocess.Popen('xrandr | grep "Screen 0" | cut -d" " -f8,10 | cut -d"," -f1',
                                  shell=True,
                                  stdout=subprocess.PIPE
                                  ).communicate()[0]
        if not re.match(r'^\d+ \d+', output):
            return [0, 0]
        width = int(output.split()[0])
        height = int(output.split()[1])
        return [width, height]

    @staticmethod
    def get_home_path():
        import os
        return os.getenv("HOME")

    @staticmethod
    def check_files_list(flist):
        for param in flist:
            if not Path.isfile(flist[param]):
                return False
        return True

    def __init__(self):
        pass

    def configure(self):
        self.resolution = self.get_screen_resolution()
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            raise Exception('Error: Wrong dimension of screen - ' + str(self.resolution))

        if not self.check_files_list(self.b_main):
            raise Exception('Error: Not found some files of: ' + str(self.b_main))

        self.i_background = Image.open(self.b_main['background'])

        self.configured = True

    @staticmethod
    def resize_image(image, resolution):
        return ImageOps.fit(image, resolution, Image.ANTIALIAS)

    def draw_text_hello(self):
        if not self.configured:
            raise Exception(self.t_err_not_configured)

        draw = ImageDraw.Draw(self.i_background)

        fnt = ImageFont.truetype(self.font_hello, self.font_hello_size)
        txt = self.t_hello.splitlines()
        txt_lines = len(txt)
        txt_size_x = fnt.getsize(max(txt, key=len))[0]
        txt_size_y = fnt.getsize(self.t_hello)[1] * txt_lines
        fnt_size = (txt_size_x, txt_size_y)

        # draw background
        start_pos_x = (self.resolution[0] - fnt_size[0]) / 2 - fnt_size[0]*0.05
        start_pos_y = self.resolution[1] / 5 + fnt_size[1] * 1.05
        start_pos = (start_pos_x, start_pos_y)

        end_pos_x = (self.resolution[0] + fnt_size[0]) / 2 + fnt_size[0]*0.05
        end_pos_y = self.resolution[1] / 5 - fnt_size[1] * 0.05
        end_pos = (end_pos_x, end_pos_y)
        draw.rectangle((start_pos, end_pos),
                       fill=self.color_background)

        draw.multiline_text(((self.resolution[0] - fnt_size[0]) / 2, self.resolution[1] / 5),
                            self.t_hello,
                            font=fnt,
                            fill=self.color_text,
                            align="center")

        del draw

    def draw_lock(self):
        if not self.configured:
            raise Exception(self.t_err_not_configured)

        lock_dimentios = 135
        radius = 90

        draw = ImageDraw.Draw(self.i_background)
        # bitmap_lock = Image.open(self.b_main['lock'])
        bitmap_lock = self.resize_image(
            Image.open(self.b_main['lock']),
            [lock_dimentios] * 2
        )

        # Draw round
        start_pos_y = self.resolution[1] / 2 - radius
        end_pos_y = self.resolution[1] / 2 + radius
        start_pos_x = self.resolution[0] / 2 - radius
        end_pos_x = self.resolution[0] / 2 + radius

        start_pos = (start_pos_x, start_pos_y)
        end_pos = (end_pos_x, end_pos_y)
        draw.ellipse((start_pos, end_pos),
                     fill=self.color_background,
                     outline=self.color_border)

        # Draw lock
        start_pos_x = (self.resolution[0] - bitmap_lock.size[0]) / 2
        start_pos_y = (self.resolution[1] - bitmap_lock.size[1]) / 2
        start_pos = (start_pos_x, start_pos_y)

        draw.bitmap(start_pos, bitmap_lock)

        del draw

    def lock(self):
        if not self.configured:
            raise Exception(self.t_err_not_configured)

        self.i_background.save(self.b_out, 'PNG')

        # subprocess.Popen(['feh', self.b_out])
        subprocess.Popen(['i3lock', '-f', '-n', '-i', self.b_out])

    def draw_weather(self, state):
        pass

#   --- MAIN PART HERE ---
if __name__ == "__main__":
    sl = ScreenLocker()
    try:
        sl.configure()

        sl.i_background = sl.resize_image(sl.i_background, sl.resolution)
        sl.draw_text_hello()
        sl.draw_lock()
        # sl.draw_weather(1)
        sl.lock()

    except Exception as e:
        print e.args
        exit(1)
