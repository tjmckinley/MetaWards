
from typing import Union as _Union
from typing import IO as _IO

from contextlib import contextmanager as _contextmanager

__all__ = ["Console"]


# Global rich.Console()
_console = None


@_contextmanager
def redirect_output(outdir):
    """Nice way to redirect stdout and stderr - thanks to
       Emil Stenström in
       https://stackoverflow.com/questions/6735917/redirecting-stdout-to-nothing-in-python
    """


class Console:
    """This is a singleton class that provides access to printing
       and logging functions to the console. This uses 'rich'
       for rich console printing
    """
    @staticmethod
    def _get_console():
        global _console

        if _console is None:
            from rich.console import Console as _Console
            _console = _Console(record=True)

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
    def print(text: str, markdown: bool = False, *args, **kwargs):
        """Print to the console"""
        if markdown:
            from rich.markdown import Markdown as _Markdown
            try:
                text = _Markdown(text)
            except Exception:
                text = _Markdown(str(text))

        Console._get_console().print(text, *args, **kwargs)

    @staticmethod
    def rule(title: str = None, **kwargs):
        """Write a rule across the screen with optional title"""
        from rich.rule import Rule as _Rule
        Console.print("")
        Console.print(_Rule(title, **kwargs))

    @staticmethod
    def panel(text: str, markdown: bool = False, width=None,
              padding: bool = True,
              expand=True, *args, **kwargs):
        """Print within a panel to the console"""
        from rich.panel import Panel as _Panel
        from rich import box as _box

        if markdown:
            from rich.markdown import Markdown as _Markdown
            text = _Markdown(text)

        if padding:
            from rich.padding import Padding as _Padding
            text = _Padding(text, (1, 2), style="on black")

        Console.print(_Panel(text, box=_box.SQUARE, width=width,
                             expand=expand), *args, **kwargs)

    @staticmethod
    def error(text: str, *args, **kwargs):
        """Print an error to the console"""
        Console.rule("ERROR", style="red")
        kwargs["style"] = "bold red"
        Console.print(text, *args, **kwargs)
        Console.rule(style="red")

    @staticmethod
    def warning(text: str, *args, **kwargs):
        """Print a warning to the console"""
        Console.rule("WARNING", style="magenta")
        kwargs["style"] = "bold magenta"
        Console.print(text, *args, **kwargs)
        Console.rule(style="magenta")

    @staticmethod
    def info(text: str, *args, **kwargs):
        """Print an info section to the console"""
        Console.rule("INFO", style="blue")
        kwargs["style"] = "bold blue"
        Console.print(text, *args, **kwargs)
        Console.rule(style="blue")

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
