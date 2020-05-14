
__all__ = ["save_console_to_file", "print", "sys_print", "Panel"]

try:
    import rich
    _have_rich = True
except ImportError:
    _have_rich = False

if _have_rich:
    from rich.console import Console as _Console
    from rich.traceback import install as _install_rich
    from rich.panel import Panel

    # allow all code to use 'print' to print using rich,
    # and to fall back to 'sys_print' if they want normal
    # python printing behaviour
    _console = _Console(record=True)
    sys_print = print
    print = _console.print

    # install rich traceback printing support
    _install_rich()

else:
    sys_print = print
    print = print
    _console = None

    def Panel(args):
        return args


def save_console_to_file(FILE):
    """Save everything that has been printed using 'print' so far
       to the passed filehandle
    """
    if _console is not None:
        FILE.write(_console.export_text(clear=True, styles=False))
