class ThemeManager:
    def __init__(self):
        self.dark_mode = False
        self.colorblind_mode = False

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

    def toggle_colorblind_mode(self):
        self.colorblind_mode = not self.colorblind_mode

    def get_tile_colors(self, status):
        if self.colorblind_mode:
            if status == "correct":
                return (0.96, 0.47, 0.23, 1)  # orange
            elif status == "present":
                return (0.52, 0.75, 0.97, 1)  # blue
        else:
            if status == "correct":
                return (0.2, 0.8, 0.2, 1)  # green
            elif status == "present":
                return (1, 1, 0.4, 1)  # yellow
        return (0.6, 0.6, 0.6, 1)  # gray