from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class OnScreenKeyboard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=10, spacing=5, size_hint=(1, 0.2), **kwargs)
        self.keys = {}
        self.create_keys()

    def create_keys(self):
        for letter in "QWERTYUIOPASDFGHJKLZXCVBNM":
            button = Button(text=letter, font_size=18)
            button.bind(on_press=self.on_key_press)
            self.keys[letter] = button
            self.add_widget(button)

    def on_key_press(self, instance):
        if self.parent and hasattr(self.parent, 'on_keyboard_input'):
            self.parent.on_keyboard_input(instance.text)

    def update_key_status(self, letter, status):
        if letter in self.keys:
            if status == "correct":
                self.keys[letter].background_color = (0.2, 0.8, 0.2, 1)  # green
            elif status == "present":
                self.keys[letter].background_color = (1, 1, 0.4, 1)  # yellow
            else:
                self.keys[letter].background_color = (0.6, 0.6, 0.6, 1)  # gray