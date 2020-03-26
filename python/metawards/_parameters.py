
from dataclasses import dataclass
from typing import List

__all__ = ["Parameters"]


@dataclass
class Parameters:
    def __init__(self):
        """Allow creation of a null Parameters object"""
        pass

    WorkName: str = None             # WORK MATRIX
    PlayName: str = None             # PLAY MATRIX
    WeekendName: str = None          # WEEKENDMATRIX
    IdentifierName: str = None       # WARD NAMES
    IdentifierName2: str = None      # WARD ID's (Communities, Counties,
                                     #            Districts, UA's etc);

    PositionName: str = None        # CENTRE of BOUNDING BOXES
    PlaySizeName: str = None        # SIZE OF POPULATION IN THE PLAY PILE

    SeedName: str = None            # LIST OF SEED NODES
    NodesToTrack: str = None        # LIST OF NODES TO TRACK

    AdditionalSeeding: str = None   #LIST OF EXTRA SEED WARDS...

    UVFilename: str = None

    beta: List[float] = None        # (Python float == C double)
    TooIllToMove: List[float] = None
    Progress: List[float] = None
    ContribFOI: List[float] = None

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

        from ._disease import Disease
        disease = Disease.get_disease(disease)

        # Now build the parameters object that will hold parameters
        # for this disease, plus space to hold the running simulation
        from ._parameters import Parameters

        par = Parameters()

        par.initial_inf = 5
        par.LengthDay = 0.7
        par.PLengthDay = 0.5

        par.beta = list(disease.beta)
        par.Progress = list(disease.progress)
        par.TooIllToMove = list(disease.TooIllToMove)
        par.ContribFOI = list(disease.ContribFOI)

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

                self.beta[2] = vals[0]
                self.beta[3] = vals[1]
                self.Progress[1] = vals[2]
                self.Progress[2] = vals[3]
                self.Progress[3] = vals[4]

                return
            else:
                i += 1

        # get here if we can't find this line in the file
        raise ValueError(f"Cannot read parameters from line {line_number} "
                         f"as the file contains just {i} lines")
