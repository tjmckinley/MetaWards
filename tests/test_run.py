
import os
import io
from pathlib import Path
from metawards import run, Disease, Ward


def _rmdir(directory):
    """Function modified from one copied from 'mitch' on stackoverflow
       https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively
    """
    directory = Path(directory)

    # first, check for removing important directories such as $HOME or root
    if directory == Path.home():
        raise FileExistsError(f"We WILL NOT remove your "
                              f"home directory ${directory}")

    if directory == Path("/"):
        raise FileExistsError(f"We WILL NOT remove the root directory "
                              f"{directory}")

    # get the directory containing '$HOME'
    if directory == Path.home().parent:
        raise FileExistsError(f"We WILL NOT remove the users/home "
                              f"directory {directory}")

    if not directory.is_dir():
        directory.unlink()
        return

    for item in directory.iterdir():
        if item.is_dir():
            _rmdir(item)
        else:
            item.unlink()

    directory.rmdir()


def test_run():
    lurgy = Disease(name="lurgy")
    lurgy.add("E", beta=0.0, progress=0.5)
    lurgy.add("I", beta=0.8, progress=0.25)
    lurgy.add("R")

    home = Ward(name="home")
    home.set_num_players(10000)

    output_csv = run(model=home, 
                     disease=lurgy,
                     auto_load=False)

    print(f"output = {output_csv}")

    # If the output exists then we can assume
    # that the job ran ok
    assert output_csv is not None
    assert os.path.exists(output_csv)

    # Remove the output from the directory
    outdir = os.path.dirname(output_csv)
    _rmdir(outdir)


if __name__ == "__main__":
    test_run()
