import pkg_resources
import pygame

try:
    import RPi.GPIO as GPIO
except ImportError:
    pass

from pypipboy import config
from pypipboy import game

from pypipboy.pypboy.modules import data
from pypipboy.pypboy.modules import items
from pypipboy.pypboy.modules import stats

from pypipboy.pypboy.ui import Header, Border, Scanlines


class Pypboy(game.core.Engine):

    def __init__(self, *args, **kwargs):
        super(Pypboy, self).__init__(*args, **kwargs)

        self.active = None
        self.header = Header()
        self.border = Border()
        self.scanlines = [
            Scanlines(800, 480, 3, 1, [(0, 13, 3, 50), (6, 42, 22, 100), (0, 13, 3, 50)]),
            Scanlines(800, 480, 8, 40, [(0, 10, 1, 0), (21, 62, 42, 90), (61, 122, 82, 100), (21, 62, 42, 90)] + [(0, 10, 1, 0) for x in range(50)], True)
        ]
        self.background = pygame.image.load(pkg_resources.resource_filename('pypipboy', 'data/images/overlay.png'))

        self.modules = {
            "data": data.Module(self),
            "items": items.Module(self),
            "stats": stats.Module(self)
        }

        self._init_modules()

        self.gpio_actions = {}
        self._init_gpio_controls()

    def _init_modules(self):
        self.root_children.add(self.header)
        self.root_children.add(Border())
        for scanline in self.scanlines:
            self.root_children.add(scanline)

        for module in self.modules.values():
            module.move(4, 40)
        self.switch_module("stats")

    def _init_gpio_controls(self):
        if not config.GPIO_AVAILABLE:
            return
        for pin in config.GPIO_ACTIONS.keys():
            print("Intialising pin {} as action '{}'".format(pin, config.GPIO_ACTIONS[pin]))
            GPIO.setup(pin, GPIO.IN)
            self.gpio_actions[pin] = config.GPIO_ACTIONS[pin]

    def check_gpio_input(self):
        for pin in self.gpio_actions.keys():
            if not GPIO.input(pin):
                self.handle_action(self.gpio_actions[pin])

    def set_title(self, headline, title):
        self.header.headline = headline
        self.header.title = title

    def update(self):
        if self.active:
            self.active.update()
        super(Pypboy, self).update()

    def render(self):
        interval = super(Pypboy, self).render()
        if self.active:
            self.active.render(interval)

    def switch_module(self, module):
        if module in self.modules:
            if self.active:
                self.active.handle_action("pause")
                self.remove(self.active)
            self.active = self.modules[module]
            self.active.parent = self
            self.active.handle_action("resume")
            self.add(self.active)
        else:
            pass
            print("Module '{}' not implemented.".format(module))

    def handle_action(self, action):
        if action.startswith('module_'):
            self.switch_module(action[7:])
        else:
            if self.active:
                self.active.handle_action(action)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                self.running = False
            else:
                if event.key in config.ACTIONS:
                    self.handle_action(config.ACTIONS[event.key])
        elif event.type == pygame.QUIT:
            self.running = False
        elif event.type == config.EVENTS['SONG_END']:
            if config.radio:
                config.radio.handle_event(event)
        else:
            if self.active:
                self.active.handle_event(event)

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.render()
            self.check_gpio_input()
            pygame.time.wait(10)

        try:
            pygame.mixer.quit()
        except Exception:
            pass
