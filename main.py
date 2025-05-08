from kivy.config import Config
# Configure window size before importing any other Kivy modules
Config.set('graphics', 'width', '500')  # Slightly wider to prevent cramping
Config.set('graphics', 'height', '800')  # Taller to ensure keyboard fits
Config.set('graphics', 'minimum_width', '400')  # Prevent window from being too narrow
Config.set('graphics', 'minimum_height', '600')  # Prevent window from being too short
Config.set('graphics', 'resizable', True)

from src.ui.app import WordleApp

# Removed redundant mobile_main.py functionality and consolidated into main.py

if __name__ == '__main__':
    WordleApp().run()

