
from dataclasses import dataclass
from typing import List
from copy import deepcopy

from ._inputfiles import InputFiles
from ._disease import Disease

__all__ = ["Parameters"]


@dataclass
class Parameters:
    def __init__(self):
        """Allow creation of a null Parameters object"""
        pass

    input_files: InputFiles = None

    UVFilename: str = None

    disease_params: Disease = None

    LengthDay: float = None
    PLengthDay: float = None
    initial_inf: int = None

    StaticPlayAtHome: float = None
    DynPlayAtHome: float = None

    DataDistCutoff: float = None
    DynDistCutoff: float = None

    PlayToWork: float = None
    WorkToPlay: float = None

    LocalVaccinationThresh: int = None
    GlobalDetectionThresh: int = None
    DailyWardVaccinationCapacity: int = None
    NeighbourWeightThreshold: float = None

    DailyImports: float = None # proportion of daily imports
    UV: float = None

    @staticmethod
    def create(disease: str):
        """ This will return a Parameters object containing all of the
            parameters and space to run a simulation for the specified
            disease
        """

        if not isinstance(disease, Disease):
            disease = Disease.get_disease(disease)

        par = Parameters()

        par.initial_inf = 5
        par.LengthDay = 0.7
        par.PLengthDay = 0.5

        par.disease_params = deepcopy(disease)

        par.DynDistCutoff = 10000000
        par.DataDistCutoff = 10000000
        par.WorkToPlay = 0.0
        par.PlayToWork = 0.0
        par.StaticPlayAtHome = 0
        par.DynPlayAtHome = 0

        par.LocalVaccinationThresh = 4
        par.GlobalDetectionThresh = 4
        par.NeighbourWeightThreshold = 0.0
        par.DailyWardVaccinationCapacity = 5
        par.UV = 0.0

        return par

    def set_input_files(self, input_files: str):
        """Set the input files that are used to initialise the
           simulation
        """
        if not isinstance(input_files, InputFiles):
            input_files = InputFiles.get_files(input_files)

        print("Using input files:")
        print(input_files)

        self.input_files = deepcopy(input_files)

    def read_file(self, filename: str, line_number: int):
        """Read in extra parameters from the specified line number
           of the specified file
        """
        print(f"Reading in parameters from line {line_number} of {filename}")

        i = 0
        with open(filename, "r") as FILE:
            line = FILE.readline()

            if i == line_number:
                words = line.split(",")

                if len(words) != 5:
                    raise ValueError(
                        f"Corrupted input file. Expecting 5 values. "
                        f"Received {line}")

                vals = []

                try:
                    for word in words:
                        vals.append(float(word))
                except Exception:
                    raise ValueError(
                            f"Corrupted input file. Expected 5 numbers. "
                            f"Received {line}")

                self.disease_params.beta[2] = vals[0]
                self.disease_params.beta[3] = vals[1]
                self.disease_params.progress[1] = vals[2]
                self.disease_params.progress[2] = vals[3]
                self.disease_params.progress[3] = vals[4]

                return
            else:
                i += 1

        # get here if we can't find this line in the file
        raise ValueError(f"Cannot read parameters from line {line_number} "
                         f"as the file contains just {i} lines")
