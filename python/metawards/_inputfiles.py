
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
    WorkName: str = None            # WORK MATRIX
    PlayName: str = None            # PLAY MATRIX
    IdentifierName: str = None      # WARD NAMES
    IdentifierName2: str = None     # WARD IDs (Communities, Counties,
                                    #           Districts, UA's etc)
    WeekendName: str = None         # WEEKEND MATRIX
    PlaySizeName: str = None        # SIZE OF POPULATION IN THE PLAY PILE
    PositionName: str = None        # CENTRE of BOUNDING BOXES
    SeedName: str = None            # LIST OF SEED NODES
    NodesToTrack: str = None        # LIST OF NODES TO TRACK
    AdditionalSeeding: str = None   #LIST OF EXTRA SEED WARDS...

    def __str__(self):
        return f"WorkName = {self.WorkName}\n" \
               f"PlayName = {self.PlayName}\n" \
               f"IdentifierName = {self.IdentifierName}\n" \
               f"IdentifierName2 = {self.IdentifierName2}\n" \
               f"WeekendName = {self.WeekendName}\n" \
               f"PlaySizeName = {self.PlaySizeName}\n" \
               f"PositionName = {self.PositionName}\n" \
               f"SeedName = {self.SeedName}\n" \
               f"NodesToTrack = {self.NodesToTrack}\n" \
               f"AdditionalSeeding = {self.AdditionalSeeding}\n"

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

_key4.WorkName = os.path.join(_2011Data, "EW1.dat")
_key4.PlayName = os.path.join(_2011Data, "PlayMatrix.dat")
_key4.PlaySizeName = os.path.join(_2011Data, "PlaySize.dat")
_key4.PositionName = os.path.join(_2011Data, "CBB2011.dat")
_key4.SeedName = os.path.join(_2011Data, "seeds.dat")
_key4.NodesToTrack = os.path.join(_2011Data, "seeds.dat")
_key4.AdditionalSeeding = os.path.join(_2011Data, "ExtraSeedsBrighton.dat")
_key4.UVFilename = os.path.join(_2011Data, "UVScaling.csv")
_key4.WeekendName = None   # this is not set in the original code?

InputFiles.set_files(4, _key4)
