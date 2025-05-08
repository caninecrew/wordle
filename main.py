from kivy.config import Config
# Configure window size before importing any other Kivy modules
Config.set('graphics', 'width', '400')  # Set a reasonable default width
Config.set('graphics', 'height', '650')  # Set a reasonable default height that fits all elements
Config.set('graphics', 'minimum_width', '350')  # Prevent window from being too narrow
Config.set('graphics', 'minimum_height', '600')  # Prevent window from being too short
Config.set('graphics', 'resizable', True)

from src.ui.app import WordleApp

if __name__ == '__main__':
    WordleApp().run()

