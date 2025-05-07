from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle

class Tile(Label):
    def __init__(self, **kwargs):
        super().__init__(font_size=32, halign="center", valign="middle", **kwargs)
        self.status = "default"  # Status can be 'default', 'correct', 'present', or 'absent'
        self.bind(size=self._update_background, pos=self._update_background)

    def _update_background(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.status == "correct":
                Color(0.2, 0.8, 0.2, 1)  # green
            elif self.status == "present":
                Color(1, 1, 0.4, 1)      # yellow
            elif self.status == "absent":
                Color(0.6, 0.6, 0.6, 1)  # gray
            else:
                Color(0.9, 0.9, 0.9, 1)  # default (white/transparent)
            Rectangle(pos=self.pos, size=self.size)

    def set_status(self, status):
        """Set the status of the tile and update its background."""
        self.status = status
        self._update_background()

    def animate_flip(self):
        """Animate the tile to flip when revealing feedback."""
        anim = Animation(scale_y=0, duration=0.2) + Animation(scale_y=1, duration=0.2)
        anim.start(self)