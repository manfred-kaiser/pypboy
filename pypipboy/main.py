import pygame
import config
import os

# Init framebuffer/touchscreen environment variables
#os.putenv('SDL_VIDEODRIVER', 'fbcon')
#os.putenv('SDL_FBDEV'      , '/dev/fb1')
#os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
#os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    config.GPIO_AVAILABLE = True
except Exception as e:
    print("GPIO UNAVAILABLE ({})".format(e))
    config.GPIO_AVAILABLE = False

from pypboy.core import Pypboy

try:
    pygame.mixer.init(44100, -16, 2, 2048)
    config.SOUND_ENABLED = True
except:
    config.SOUND_ENABLED = False

if __name__ == "__main__":
    boy = Pypboy('Pip-Boy 3000', config.WIDTH, config.HEIGHT)
    print("RUN")
    boy.run()
