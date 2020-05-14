
try:
    import rich
    have_rich = True
except ImportError:
    have_rich = False

if have_rich:
    from rich.console import Console as _Console
    from rich.traceback import install as _install_rich

    # allow all code to use 'print' to print using rich,
    # and to fall back to 'sys_print' if they want normal
    # python printing behaviour
    console = _Console()
    sys_print = print
    print = console.print

    # install rich traceback printing support
    _install_rich()

else:
    sys_print = print
    print = print
