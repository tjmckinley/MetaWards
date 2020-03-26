
from dataclasses import dataclass
import os

__all__ = ["InputFiles"]

_inputfiles = {}

# All input data files needed by this module will be in the
# metawards/data directory
_2011Data = os.path.join(os.path.dirname(__file__),
                         "data", "2011Data")


@dataclass
class InputFiles:
    work: str = None                # WORK MATRIX
    play: str = None                # PLAY MATRIX
    identifier: str = None          # WARD NAMES
    identifier2: str = None         # WARD IDs (Communities, Counties,
                                    #           Districts, UA's etc)
    weekend: str = None             # WEEKEND MATRIX
    play_size: str = None           # SIZE OF POPULATION IN THE PLAY PILE
    position: str = None            # CENTRE of BOUNDING BOXES
    seed: str = None                # LIST OF SEED NODES
    nodes_to_track: str = None      # LIST OF NODES TO TRACK
    additional_seeding: str = None  # LIST OF EXTRA SEED WARDS...
    uv: str = None                  # UV file

    def __str__(self):
        return f"work = {self.work}\n" \
               f"play = {self.play}\n" \
               f"identifier = {self.identifier}\n" \
               f"identifier2 = {self.identifier2}\n" \
               f"weekend = {self.weekend}\n" \
               f"play_size = {self.play_size}\n" \
               f"position = {self.position}\n" \
               f"seed = {self.seed}\n" \
               f"nodes_to_track = {self.nodes_to_track}\n" \
               f"additional_seeding = {self.additional_seeding}\n"

    @staticmethod
    def set_files(name: str, files):
        """Set the input files associated with a particular key"""
        if not isinstance(files, InputFiles):
            raise TypeError("The input files should be type 'InputFiles'")

        global _inputfiles
        _inputfiles[str(name).lower().strip()] = files

    @staticmethod
    def get_files(name: str):
        """Return the datafiles for the specified key"""
        global _inputfiles
        try:
            return _inputfiles[str(name).lower().strip()]
        except KeyError:
            raise KeyError(f"There are no input files for key '{name}' "
                           f"Known input files are {list(_inputfiles.keys())}")


# Initialise the _inputfiles dictionary for key '4'. Ideally
# this would come from a json data file (or equivalent) to stop
# researchers having to edit this code. They can use the
# "set_files" function above to change this though
_key4 = InputFiles()

_key4.work = os.path.join(_2011Data, "EW1.dat")
_key4.play = os.path.join(_2011Data, "PlayMatrix.dat")
_key4.play_size = os.path.join(_2011Data, "PlaySize.dat")
_key4.position = os.path.join(_2011Data, "CBB2011.dat")
_key4.seed = os.path.join(_2011Data, "seeds.dat")
_key4.nodes_to_track = os.path.join(_2011Data, "seeds.dat")
_key4.additional_seeding = os.path.join(_2011Data, "ExtraSeedsBrighton.dat")
_key4.uv = os.path.join(_2011Data, "UVScaling.csv")
_key4.weekend = None     # this is not set in the original code?
_key4.identifier = None  # this is not set in the original code?
_key4.identifier2 = None # this is not set in the original code?

InputFiles.set_files(4, _key4)
