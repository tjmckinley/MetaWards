
from dataclasses import dataclass
import os
import pathlib

__all__ = ["InputFiles"]

_inputfiles = {}

_default_model_path = os.path.join(pathlib.Path.home(),
                                   "GitHub", "MetaWardsData")

_default_folder_name = "model_data"


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

    _filename: str = None            # Full path of the description.json file
    _model_name: str = None          # Name of the model
    _model_path: str = None          # Directory containing the input files
    _model_version: str = None       # Version loaded from the data
    _authors: str = None             # Author(s) of this data
    _contacts: str = None            # Contact(s) for this data
    _references: str = None          # References for this data
    _repository: str = None          # GitHub repository for this data
    _repository_version: str = None  # Git version of the data

    def model_name(self):
        """Return the name of this model"""
        return self._model_name

    def model_path(self):
        """Return the path to the directory containing this model"""
        return self._model_path

    def model_version(self):
        """Return the version of the data in this model"""
        return self._model_version

    def __str__(self):
        return f"Model {self._model_name} version {self._model_version}\n" \
               f"loaded from {self._filename}\n" \
               f"root directory {self._model_path}\n" \
               f"author(s): {self._authors}\n" \
               f"contact(s): {self._contacts}\n" \
               f"references(s): {self._references}\n" \
               f"repository: {self._repository}\n" \
               f"repository_version: {self._repository_version}\n\n" \
               f"work = {self.work}\n" \
               f"play = {self.play}\n" \
               f"identifier = {self.identifier}\n" \
               f"identifier2 = {self.identifier2}\n" \
               f"weekend = {self.weekend}\n" \
               f"play_size = {self.play_size}\n" \
               f"position = {self.position}\n" \
               f"seed = {self.seed}\n" \
               f"nodes_to_track = {self.nodes_to_track}\n" \
               f"additional_seeding = {self.additional_seeding}\n\n"

    def _localise(self):
        """Localise the filenames in this input files set. This will
           prepend model_path/model to every filename and will also
           double-check that all files exist and are readable
        """
        members = [attr for attr in dir(self)
                    if not callable(getattr(self, attr))
                        and not attr.startswith("_")]

        for member in members:
            filename = getattr(self, member)
            if filename:
                filename = os.path.join(self._model_path, filename)

                if not (os.path.exists(filename) and os.path.isfile(filename)):
                    raise FileNotFoundError(
                            f"Cannot find input file {member} = {filename}")

                setattr(self, member, filename)

    @staticmethod
    def load(model: str = "2011Data",
             repository: str=_default_model_path,
             folder: str=_default_folder_name,
             description: str="description.json",
             filename: str = None):
        """Load the parameters associated with the passed model.
           This will look for the parameters specified in
           the json file called f"{repository}/{folder}/{model}/{description}"

           By default this will load the 2011Data parameters
           from $HOME/GitHub/model_data/2011Data/description.json

           Alternatively you can provide the full path to the
           description json file usng the 'filename' argument.
           All files within this description will be searched
           for using the directory that contains that file
           as a base
        """
        repository_version = None

        if filename is None:
            if repository is None:
                repository = os.getenv("METAWARDSDATA")
                if repository is None:
                    repository = _default_model_path

            from ._parameters import get_repository_version
            repository_version = get_repository_version(repository)
            filename = os.path.join(repository, folder,
                                    model, description)

        json_file = filename
        model_path = os.path.dirname(filename)

        try:
            with open(json_file, "r") as FILE:
                import json
                files = json.load(FILE)

        except Exception as e:
            print(f"Could not find the model file {json_file}")
            print(f"Either it does not exist of was corrupted.")
            print(f"Error was {e.__class__} {e}")
            print(f"To download the model data type the command:")
            print(f"  git clone https://github.com/metawards/MetaWardsData")
            print(f"and then re-run this function passing in the full")
            print(f"path to where you downloaded this directory")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        model = InputFiles(work=files["work"],
                           play=files["play"],
                           identifier=files["identifier"],
                           identifier2=files["identifier2"],
                           weekend=files["weekend"],
                           play_size=files["play_size"],
                           position=files["position"],
                           seed=files["seed"],
                           nodes_to_track=files["nodes_to_track"],
                           additional_seeding=files["additional_seeding"],
                           uv=files["uv"],
                           _filename=json_file,
                           _model_path=model_path,
                           _model_name=files["name"],
                           _model_version=files["version"],
                           _references=files["reference(s)"],
                           _authors=files["author(s)"],
                           _contacts=files["contact(s)"],
                           _repository=repository,
                           _repository_version=repository_version)

        model._localise()

        return model
