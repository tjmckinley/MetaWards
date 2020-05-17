
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List
from typing import Dict as _Dict

__all__ = ["Simple"]


@_dataclass
class Simple:
    """This is the monochrome 'Simple' theme"""

    frames: _Dict[int, _List[str]] = _field(default_factory=dict)

    def error_style(self):
        return "white"

    def warning_style(self):
        return "white"

    def info_style(self):
        return "white"

    def error_text(self):
        return "white"

    def warning_text(self):
        return "white"

    def info_text(self):
        return "white"

    def spinner_success(self, spinner):
        spinner.ok("Success")

    def spinner_failure(self, spinner):
        spinner.fail("Failed")

    def panel(self, style):
        return "white on black"

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
