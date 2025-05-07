from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class OnScreenKeyboard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 10
        self.spacing = 5
        self.size_hint_y = 0.3  # Use size_hint_y instead of size_hint to avoid conflicts
        self.keys = {}
        self.create_keys()

    def create_keys(self):
        # Top row
        for letter in "QWERTYUIOP":
            self.add_key(letter)

        # Middle row
        for letter in "ASDFGHJKL":
            self.add_key(letter)

        # Bottom row
        self.add_widget(Button(text="ENTER", font_size=18, on_press=self.on_enter))
        for letter in "ZXCVBNM":
            self.add_key(letter)
        self.add_widget(Button(text="←", font_size=18, on_press=self.on_backspace))

    def add_key(self, letter):
        button = Button(text=letter, font_size=18)
        button.bind(on_press=self.on_key_press)
        self.keys[letter] = button
        self.add_widget(button)

    def on_key_press(self, instance):
        if self.parent and hasattr(self.parent, 'on_keyboard_input'):
            self.parent.on_keyboard_input(instance.text)

    def on_enter(self, instance):
        if self.parent and hasattr(self.parent, 'submit_guess'):
            self.parent.submit_guess(instance)

    def on_backspace(self, instance):
        if self.parent and hasattr(self.parent, 'on_backspace'):
            self.parent.on_backspace()

    def update_key_status(self, letter, status):
        if letter in self.keys:
            button = self.keys[letter]
            if status == "correct":
                button.background_color = (0.2, 0.8, 0.2, 1)  # green
            elif status == "present":
                button.background_color = (1, 1, 0.4, 1)  # yellow
            elif status == "absent":
                button.background_color = (0.6, 0.6, 0.6, 1)  # gray
            else:
                button.background_color = (0.9, 0.9, 0.9, 1)  # default (light gray)