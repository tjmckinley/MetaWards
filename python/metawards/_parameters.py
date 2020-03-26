
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
