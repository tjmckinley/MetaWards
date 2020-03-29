
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
    uv_filename: str = None
    disease_params: Disease = None

    length_day: float = 0.7
    plength_day: float = 0.5
    initial_inf: int = 5

    static_play_at_home: float = 0.0
    dyn_play_at_home: float = 0.0

    data_dist_cutoff: float = 10000000.0
    dyn_dist_cutoff: float = 10000000.0

    play_to_work: float = 0.0
    work_to_play: float = 0.0

    local_vaccination_thresh: int = 4
    global_detection_thresh: int = 4
    daily_ward_vaccination_capacity: int = 5
    neighbour_weight_threshold: float = 0.0

    daily_imports: float = 0.0 # proportion of daily imports
    UV: float = 0.0

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
        par.length_day = 0.7
        par.plength_day = 0.5

        par.disease_params = deepcopy(disease)

        par.dyn_dist_cutoff = 10000000.0
        par.data_dist_cutoff = 10000000.0
        par.work_to_play = 0.0
        par.play_to_work = 0.0
        par.static_play_at_home = 0.0
        par.dyn_play_at_home = 0.0

        par.local_vaccination_thresh = 4
        par.global_detection_thresh = 4
        par.neighbour_weight_threshold = 0.0
        par.daily_ward_vaccination_capacity = 5
        par.UV = 0.0

        return par

    def set_input_files(self, input_files: InputFiles):
        """Set the input files that are used to initialise the
           simulation
        """
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
