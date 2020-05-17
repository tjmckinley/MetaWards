
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

    def should_highlight(self):
        return False

    def highlighter(self):
        return None

    def should_markup(self):
        return False

    def text(self, style):
        if style == "warning":
            return "red"
        else:
            return "white"

    def error(self):
        return "red"

    def warning(self):
        return "magenta"

    def info(self):
        return "cyan"

    def error_text(self):
        return f"bold {self.error()}"

    def warning_text(self):
        return f"bold {self.warning()}"

    def info_text(self):
        return f"bold {self.info()}"

    def spinner_success(self, spinner):
        spinner.green.ok("✔")

    def spinner_failure(self, spinner):
        spinner.red.fail("✘")

    def rule(self, style):
        if style is None:
            return "green"
        elif style == "finish":
            return "magenta"
        elif style == "error":
            return self.error()
        elif style == "warning":
            return self.warning()
        elif style == "info":
            return self.info()
        elif style == "iteration":
            return "cyan"
        else:
            return "cyan"

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
