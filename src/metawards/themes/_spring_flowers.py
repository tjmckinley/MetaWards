
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List
from typing import Dict as _Dict

__all__ = ["SpringFlowers"]


@_dataclass
class SpringFlowers:
    """This is the colourful 'SpringFlowers' theme"""

    frames: _Dict[int, _List[str]] = _field(default_factory=dict)

    panel_colors: _List[str] = _field(default_factory=list)

    panel_color_count = 0

    def error_style(self):
        return "red"

    def warning_style(self):
        return "magenta"

    def info_style(self):
        return "blue"

    def error_text(self):
        return "bold red"

    def warning_text(self):
        return "bold magenta"

    def info_text(self):
        return "bold blue"

    def spinner_success(self, spinner):
        spinner.green.ok("✔")

    def spinner_failure(self, spinner):
        spinner.red.fail("✘")

    def panel(self, style):
        if style is None:
            return "on black"

        elif style == "alternate":
            if len(self.panel_colors) == 0:
                self.panel_colors = ["blue", "cyan"]
                self.panel_color_count = 0

            color = self.panel_colors[self.panel_color_count]
            self.panel_color_count += 1
            if self.panel_color_count >= len(self.panel_colors):
                self.panel_color_count = 0

            return f"on {color}"

    def get_frames(self, width: int = 80):
        """Return the frames used to animate a spinner in a console
           of specified width

           This returns the list of frames plus the timeout between
           the list
        """
        if width in self.frames:
            return self.frames[width]

        frames = []

        for i in range(0, width):
            frame = (i * '-') + '>' + ((width - i - 1) * ' ')
            frames.append(frame)

        self.frames[width] = (frames, 50)

        return self.frames[width]
