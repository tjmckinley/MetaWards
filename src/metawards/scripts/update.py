
def parse_args():
    """Parse all of the command line arguments"""
    import configargparse
    import sys

    configargparse.init_argument_parser(
        name="main",
        description="MetaWards update program. Used to update the software. "
        "https://metawards.org for more information.",
        prog="metawards-update")

    parser = configargparse.get_argument_parser("main")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about "
                             "metawards-install")

    parser.add_argument('--update', action="store_true",
                        default=None,
                        help="Update MetaWards to the latest version")

    parser.add_argument('--check-for-updates', action="store_true",
                        default=None,
                        help="Print whether or not there are any updates "
                             "available. If there aren't, then nothing "
                             "is printed to the screen")

    parser.add_argument("--dry-run", action="store_true",
                        default=None,
                        help="Just print out what will be done - don't "
                             "actually do anything")

    parser.add_argument("--user", action="store_true",
                        default=None,
                        help="Install updates using '--user' rather than "
                             "globally.")

    args = parser.parse_args()

    if args.version:
        from metawards import get_version_string
        print(get_version_string())
        sys.exit(0)

    return (args, parser)


def run_command(cmd, dry=False, capture_output=False, silent=False):
    """Run the passed shell command"""
    if dry:
        print(f"[DRY-RUN] {cmd}")
        return 0

    #print(f"[EXECUTE] {cmd}")

    lines = []

    try:
        import shlex
        import subprocess
        import sys

        args = shlex.split(cmd)
        with subprocess.Popen(args, stdin=sys.stdin,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE, bufsize=1,
                              universal_newlines=True) as PROC:
            while True:
                line = PROC.stdout.readline()
                if not line:
                    break

                if capture_output:
                    lines.append(line)

                if not silent:
                    sys.stdout.write(line)
                    sys.stdout.flush()

            return_val = PROC.poll()

            if capture_output:
                return lines
            else:
                return return_val

    except Exception as e:
        print(f"[ERROR] {e}")
        return -1


def cli():
    args, parser = parse_args()

    import sys

    try:
        import pip
        have_pip = True
    except ImportError:
        have_pip = False
    except Exception:
        have_pip = True

    if not have_pip:
        print("Unable to import pip. This means that we cannot upgrade "
              "metawards. Please make sure that pip is installed.")
        sys.exit(-1)

    if args.user:
        user = "--user"
    else:
        user = ""

    if args.dry_run:
        dry = True
    else:
        dry = False

    if args.update:
        cmd = f"{sys.executable} -m pip install {user} metawards --upgrade"
        try:
            run_command(cmd, dry=dry)
        except Exception:
            print("ERROR UPDATING. Do you have permission to update this "
                  "software?")
            sys.exit(-1)
    elif args.check_for_updates:
        cmd = f"{sys.executable} -m pip search metawards"
        output = run_command(cmd, dry=dry, silent=True, capture_output=True)

        if dry:
            sys.exit(0)

        installed = None
        latest = None

        for line in output:
            if line.find("INSTALLED") != -1:
                installed = line.strip().split()[-1]
            elif line.find("LATEST") != -1:
                latest = line.strip().split()[-1]

        if latest is None:
            sys.exit(0)

        installed = installed.split("+")[0]

        if installed != latest:
            print("Update available: metawards=={latest}")
    else:
        parser.print_help()
