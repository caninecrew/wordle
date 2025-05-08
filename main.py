from kivy.config import Config
# Configure window size before importing any other Kivy modules
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', True)

from src.ui.app import WordleApp

if __name__ == '__main__':
    WordleApp().run()

