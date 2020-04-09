"""
.. currentmodule:: metawards

Functions
=========

.. autosummary::
    :toctree: generated/
"""

from dataclasses import dataclass
from typing import List
from copy import deepcopy
import pathlib
import os
import json

from ._inputfiles import InputFiles
from ._disease import Disease
from ._variableset import VariableSets, VariableSet


__all__ = ["Parameters", "get_repository_version"]

_default_parameters_path = os.path.join(pathlib.Path.home(),
                                        "GitHub", "MetaWardsData")

_default_folder_name = "parameters"


_repositories = {}


def generate_repository_version(repository):
    """Try to run the './version' script within the passed repository,
       to generate the required 'version.txt' file
    """
    import subprocess
    script = os.path.join(repository, "version")
    print(f"Regenerating version information using {script}")
    subprocess.run(script, cwd=repository)


def get_repository_version(repository):
    """Read and return the Git version of the passed repository"""
    global _repositories

    if repository in _repositories:
        return _repositories[repository]

    filename = os.path.join(repository, "version.txt")

    try:
        with open(filename) as FILE:
            version = json.load(FILE)
            _repositories[repository] = version
            return version
    except Exception:
        pass

    # could not get the version, so see if we have permission
    # to run the 'version' program
    try:
        generate_repository_version(repository)

        with open(filename) as FILE:
            version = json.load(FILE)
            _repositories[repository] = version
            return version
    except Exception:
        print(f"Could not find the repository version info in {filename}."
              f"Please make sure that you have run './version' in that "
              f"repository to generate the version info.")
        _repositories[repository] = {"repository": "unknown",
                                     "version": "unknown",
                                     "branch": "unknown"}
        return _repositories[repository]


@dataclass
class Parameters:
    input_files: InputFiles = None
    uv_filename: str = None
    disease_params: Disease = None

    additional_seeds: List[str] = None

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

    daily_imports: float = 0.0  # proportion of daily imports
    UV: float = 0.0

    _name: str = None
    _version: str = None
    _authors: str = None
    _contacts: str = None
    _references: str = None
    _filename: str = None
    _repository: str = None
    _repository_version: str = None
    _repository_branch: str = None
    _repository_dir: str = None

    def __str__(self):
        return f"Parameters {self._name}\n" \
               f"loaded from {self._filename}\n" \
               f"version: {self._version}\n" \
               f"author(s): {self._authors}\n" \
               f"contact(s): {self._contacts}\n" \
               f"references(s): {self._references}\n" \
               f"repository: {self._repository}\n" \
               f"repository_branch: {self._repository_branch}\n" \
               f"repository_version: {self._repository_version}\n\n" \
               f"length_day = {self.length_day}\n" \
               f"plength_day = {self.plength_day}\n" \
               f"initial_inf = {self.initial_inf}\n" \
               f"static_play_at_home = {self.static_play_at_home}\n" \
               f"dyn_play_at_home = {self.dyn_play_at_home}\n" \
               f"data_dist_cutoff = {self.data_dist_cutoff}\n" \
               f"dyn_dist_cutoff = {self.dyn_dist_cutoff}\n" \
               f"play_to_work = {self.play_to_work}\n" \
               f"work_to_play = {self.work_to_play}\n" \
               f"local_vaccination_thresh = " \
               f"{self.local_vaccination_thresh}\n" \
               f"global_detection_thresh = {self.global_detection_thresh}\n" \
               f"daily_ward_vaccination_capacity = " \
               f"{self.daily_ward_vaccination_capacity}\n" \
               f"neighbour_weight_threshold = " \
               f"{self.neighbour_weight_threshold}\n" \
               f"daily_imports = {self.daily_imports}\n" \
               f"UV = {self.UV}\n" \
               f"additional_seeds = {self.additional_seeds}\n\n"

    @staticmethod
    def load(parameters: str = "march29",
             repository: str = None,
             folder: str = _default_folder_name,
             filename: str = None):
        """ This will return a Parameters object containing all of the
            parameters loaded from the parameters found in file
            f"{repository}/{folder}/{parameters}.json"

            By default this will load the march29 parameters from
            $HOME/GitHub/model_data/2011Data/parameters/march29.json

            Alternatively, you can provide the exact path to the
            filename via the 'filename' argument
        """
        repository_version = None
        repository_branch = None
        repository_dir = None

        if filename is None:
            if repository is None:
                repository = os.getenv("METAWARDSDATA")
                if repository is None:
                    repository = _default_parameters_path

            filename = os.path.join(repository, folder, f"{parameters}.json")
            v = get_repository_version(repository)
            repository_dir = repository
            repository = v["repository"]
            repository_branch = v["branch"]
            repository_version = v["version"]

        json_file = filename

        try:
            with open(json_file, "r") as FILE:
                import json
                data = json.load(FILE)

        except Exception as e:
            print(f"Could not find the parameters file {json_file}")
            print(f"Either it does not exist of was corrupted.")
            print(f"Error was {e.__class__} {e}")
            print(f"To download the parameters type the command:")
            print(f"  git clone https://github.com/metawards/MetaWardsData")
            print(f"and then re-run this function passing in the full")
            print(f"path to where you downloaded this directory")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        par = Parameters(
                length_day=data["length_day"],
                plength_day=data["plength_day"],
                initial_inf=data["initial_inf"],
                static_play_at_home=data["static_play_at_home"],
                dyn_play_at_home=data["dyn_play_at_home"],
                data_dist_cutoff=data["data_dist_cutoff"],
                dyn_dist_cutoff=data["dyn_dist_cutoff"],
                play_to_work=data["play_to_work"],
                work_to_play=data["work_to_play"],
                local_vaccination_thresh=data["local_vaccination_threshold"],
                global_detection_thresh=data["global_detection_threshold"],
                daily_ward_vaccination_capacity=data[
                                "daily_ward_vaccination_capacity"],
                neighbour_weight_threshold=data["neighbour_weight_threshold"],
                daily_imports=data["daily_imports"],
                UV=data["UV"],
                _name=data["name"],
                _authors=data["author(s)"],
                _version=data["version"],
                _contacts=data["contact(s)"],
                _references=data["reference(s)"],
                _filename=json_file,
                _repository=repository,
                _repository_dir=repository_dir,
                _repository_branch=repository_branch,
                _repository_version=repository_version
                )

        print("Using parameters:")
        print(par)

        return par

    def add_seeds(self, filename: str):
        """Add an 'additional seeds' file that can be used to
           seed wards with new infections at different times and
           locations. Several additional_seed files can be added
        """
        # resolve the filename to the GitHub repo if possible...
        if self.additional_seeds is None:
            self.additional_seeds = []

        if not os.path.exists(filename):
            f = os.path.join(self._repository_dir, "extra_seeds", filename)

            if os.path.exists(f):
                filename = f
            else:
                raise FileExistsError(
                        f"Unable to find extra seeds file {filename} in "
                        f"the current directory or in {f}")

        self.additional_seeds.append(filename)

    def set_input_files(self, input_files: InputFiles):
        """Set the input files that are used to initialise the
           simulation
        """
        if isinstance(input_files, str):
            input_files = InputFiles.load(input_files,
                                          repository=self._repository_dir)

        print("Using input files:")
        print(input_files)

        self.input_files = deepcopy(input_files)

    def set_disease(self, disease: Disease):
        """"Set the disease that will be modelled"""
        if isinstance(disease, str):
            disease = Disease.load(disease,
                                   repository=self._repository_dir)

        print("Using disease")
        print(disease)

        self.disease_params = deepcopy(disease)

    def set_variables(self, variables: VariableSet):
        """This function sets the adjustable variable values to those
           specified in 'variables' in A COPY OF THIS PARAMETERS OBJECT.
           This returns the copy. It does not change this object
        """
        params = deepcopy(self)

        if isinstance(variables, dict):
            variables = VariableSet(variables)

        variables.adjust(params)

        return params

    @staticmethod
    def read_variables(filename: str, line_numbers: List[int]):
        """Read in extra variable parameters from the specified line number(s)
           of the specified file, returning the list
           of the dictionaries of variables that have been
           read. You can then apply those variable parameters
           using the 'set_variables' function
        """
        variables = VariableSets()

        if not isinstance(line_numbers, list):
            if line_numbers is not None:
                line_numbers = [line_numbers]

        i = -1
        with open(filename, "r") as FILE:
            line = FILE.readline()
            while line:
                i += 1

                if line_numbers is None or i in line_numbers:
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

                    variables.append({"beta2": vals[0],
                                      "beta3": vals[1],
                                      "progress1": vals[2],
                                      "progress2": vals[3],
                                      "progress3": vals[4]})

                    if line_numbers is not None:
                        if len(variables) == len(line_numbers):
                            return variables

                line = FILE.readline()

        # get here if we can't find this line in the file (or if we
        # are supposed to read all lines)
        if line_numbers is None:
            return variables
        else:
            raise ValueError(
                    f"Cannot read parameters from line {line_numbers} "
                    f"as the number of lines in the file is {i+1}")
