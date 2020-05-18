
from typing import Union as _Union
from typing import IO as _IO

from contextlib import contextmanager as _contextmanager


__all__ = ["Console"]


# Global rich.Console()
_console = None

# Global console theme
_theme = None


class _NullSpinner:
    """Null spinner to use if yaspin isn't available"""

    def __init__(self):
        pass

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

    def ok(self):
        pass

    def fail(self):
        pass


class Console:
    """This is a singleton class that provides access to printing
       and logging functions to the console. This uses 'rich'
       for rich console printing
    """
    @staticmethod
    def set_theme(theme):
        """Set the theme used for the console - this should be
           one of the themes in metawards.themes
        """
        global _theme

        if isinstance(theme, str):
            if theme.lower().strip() == "simple":
                from metawards.themes import Simple
                _theme = Simple()
            elif theme.lower().strip() == "default":
                from metawards.themes import SpringFlowers
                _theme = SpringFlowers()
        else:
            _theme = theme

    @staticmethod
    def _get_theme():
        global _theme

        if _theme is None:
            from metawards.themes import SpringFlowers
            _theme = SpringFlowers()

        return _theme

    @staticmethod
    def _get_console():
        global _console

        if _console is None:
            from rich.console import Console as _Console
            theme = Console._get_theme()

            _console = _Console(record=True,
                                highlight=theme.should_highlight(),
                                highlighter=theme.highlighter(),
                                markup=theme.should_markup())

            # also install pretty traceback support
            from rich.traceback import install as _install_rich
            _install_rich()

        return _console

    @staticmethod
    @_contextmanager
    def redirect_output(outdir: str, auto_bzip: bool = True):
        """Redirect all output and error to the directory 'outdir'"""
        import os as os
        import sys as sys
        import bz2
        from rich.console import Console as Console

        outfile = os.path.join(outdir, "output.txt")
        errfile = os.path.join(outdir, "output.err")

        if auto_bzip:
            outfile += ".bz2"
            errfile += ".bz2"

            OUTFILE = bz2.open(outfile, "wt")
            ERRFILE = bz2.open(errfile, "wt")
        else:
            OUTFILE = open(outfile, "wt")
            ERRFILE = open(errfile, "wt")

        global _console
        new_out = Console(file=OUTFILE, record=False)
        old_out = _console
        _console = new_out

        new_err = ERRFILE
        old_err = sys.stderr
        sys.stderr = new_err

        try:
            yield new_out
        finally:
            _console = old_out
            sys.stderr = old_err
            OUTFILE.close()
            ERRFILE.close()

    @staticmethod
    def print(text: str, markdown: bool = False, style: str = None,
              *args, **kwargs):
        """Print to the console"""
        if markdown:
            from rich.markdown import Markdown as _Markdown
            try:
                text = _Markdown(text)
            except Exception:
                text = _Markdown(str(text))

        theme = Console._get_theme()
        style = theme.text(style)

        Console._get_console().print(text, style=style)

    @staticmethod
    def rule(title: str = None, style=None, **kwargs):
        """Write a rule across the screen with optional title"""
        from rich.rule import Rule as _Rule
        Console.print("")
        theme = Console._get_theme()
        style = theme.rule(style)
        Console.print(_Rule(title, style=style))

    @staticmethod
    def panel(text: str, markdown: bool = False, width=None,
              padding: bool = True, style: str = None,
              expand=True, *args, **kwargs):
        """Print within a panel to the console"""
        from rich.panel import Panel as _Panel

        if markdown:
            from rich.markdown import Markdown as _Markdown
            text = _Markdown(text)

        theme = Console._get_theme()
        padding_style = theme.padding_style(style)
        style = theme.panel(style)
        box = theme.panel_box(style)

        if padding:
            from rich.padding import Padding as _Padding
            text = _Padding(text, (1, 2), style=padding_style)

        Console.print(_Panel(text, box=box, width=width,
                             expand=expand,
                             style=style, *args, **kwargs))

    @staticmethod
    def error(text: str, *args, **kwargs):
        """Print an error to the console"""
        Console.rule("ERROR", style="error")
        Console.print(text, style="error", *args, **kwargs)
        Console.rule(style="error")

    @staticmethod
    def warning(text: str, *args, **kwargs):
        """Print a warning to the console"""
        Console.rule("WARNING", style="warning")
        Console.print(text, style="warning", *args, **kwargs)
        Console.rule(style="warning")

    @staticmethod
    def info(text: str, *args, **kwargs):
        """Print an info section to the console"""
        Console.rule("INFO", style="info")
        Console.print(text, style="info", *args, **kwargs)
        Console.rule(style="info")

    @staticmethod
    def center(text: str, *args, **kwargs):
        from rich.text import Text as _Text
        Console.print(_Text(str, justify="center"), *args, **kwargs)

    @staticmethod
    def command(text: str, *args, **kwargs):
        Console.print("    " + text, markdown=True)

    @staticmethod
    def print_population(population, demographics=None,
                         *args, **kwargs):
        Console.print(population.summary(demographics=demographics))

    @staticmethod
    def print_profiler(profiler, *args, **kwargs):
        Console.print(str(profiler))

    @staticmethod
    def spinner(text: str = None):
        try:
            from yaspin import yaspin, Spinner
            have_yaspin = True
        except ImportError:
            have_yaspin = False

        if not have_yaspin:
            return _NullSpinner()

        console = Console._get_console()
        theme = Console._get_theme()
        frames, delay = theme.get_frames(width=console.width - len(text) - 10)
        sp = Spinner(frames, delay)

        y = yaspin(sp, text=text, side="right")

        y.success = lambda: theme.spinner_success(y)
        y.failure = lambda: theme.spinner_failure(y)

        return y

    @staticmethod
    def save(file: _Union[str, _IO]):
        """Save the accumulated printing to the console to 'file'.
           This can be a file or a filehandle. The buffer is
           cleared after saving
        """
        if isinstance(file, str):
            with open(file, "w") as FILE:
                FILE.write(Console._get_console().export_text(clear=True,
                                                              styles=False))
        else:
            file.write(Console._get_console().export_text(clear=True,
                                                          styles=False))
