
import sys
import os
import subprocess
import shlex


def run_command(cmd, dry=False):
    """Run the passed shell command"""
    if dry:
        print(f"[DRY-RUN] {cmd}")
        return

    print(f"[EXECUTE] {cmd}")

    try:
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(-1)


os.chdir("gh-pages")

run_command("git config --local user.email 'action@github.com'")
run_command("git config --local user.name 'GitHub Action'")
run_command("git add .")
run_command("git commit -a -m 'Update website.'")
