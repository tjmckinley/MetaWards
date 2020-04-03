
from dataclasses import dataclass
from typing import List
import pathlib
import os

__all__ = ["Disease"]

_default_disease_path = os.path.join(pathlib.Path.home(),
                                     "GitHub", "MetaWardsData")

_default_folder_name = "diseases"


@dataclass
class Disease:
    """This class holds the parameters about a single disease"""
    beta: List[float] = None
    progress: List[float] = None
    too_ill_to_move: List[float] = None
    contrib_foi: List[float] = None
    _name: str = None
    _version: str = None
    _authors: str = None
    _contacts: str = None
    _references: str = None
    _filename: str = None
    _repository: str = None
    _repository_version: str = None

    def __str__(self):
        return f"Disease {self._name}\n" \
               f"loaded from {self._filename}\n" \
               f"version: {self._version}\n" \
               f"author(s): {self._authors}\n" \
               f"contact(s): {self._contacts}\n" \
               f"references(s): {self._references}\n" \
               f"repository: {self._repository}\n" \
               f"repository_version: {self._repository_version}\n\n" \
               f"beta = {self.beta}\n" \
               f"progress = {self.progress}\n" \
               f"too_ill_to_move = {self.too_ill_to_move}\n" \
               f"contrib_foi = {self.contrib_foi}\n\n"

    def __eq__(self, other):
        return self.beta == other.beta and \
               self.progress == other.progress and \
               self.too_ill_to_move == other.too_ill_to_move and \
               self.contrib_foi == other.contrib_foi

    def N_INF_CLASSES(self):
        return len(self.beta)

    def _validate(self):
        """Check that the loaded parameters make sense"""
        try:
            n = len(self.beta)

            assert len(self.progress) == n
            assert len(self.too_ill_to_move) == n
            assert len(self.contrib_foi) == n
        except Exception as e:
            raise AssertionError(f"Data read for disease {self._name} "
                                 f"is corrupted! {e.__class__}: {e}")

    @staticmethod
    def load(disease: str = "ncov",
             repository: str=None,
             folder: str=_default_folder_name,
             filename: str = None):
        """Load the disease parameters for the specified disease.
           This will look for a file called f"{disease}.json"
           in the directory f"{repository}/{disease}/{disease}.ncon"

           By default this will load the ncov (SARS-Cov-2)
           parameters from
           $HOME/GitHub/model_data/2011Data/diseases/ncov.json

           Alternatively you can provide the full path to the
           json file via the "filename" argument
        """
        repository_version = None

        if filename is None:
            if repository is None:
                repository = os.getenv("METAWARDSDATA")
                if repository is None:
                    repository = _default_disease_path

            from ._parameters import get_repository_version
            repository_version = get_repository_version(repository)
            filename = os.path.join(repository, folder,
                                    f"{disease}.json")

        json_file = filename

        try:
            with open(json_file, "r") as FILE:
                import json
                data = json.load(FILE)

        except Exception as e:
            print(f"Could not find the disease file {json_file}")
            print(f"Either it does not exist of was corrupted.")
            print(f"Error was {e.__class__} {e}")
            print(f"To download the disease data type the command:")
            print(f"  git clone https://github.com/metawards/MetaWardsData")
            print(f"and then re-run this function passing in the full")
            print(f"path to where you downloaded this directory")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        disease = Disease(beta=data["beta"],
                          progress=data["progress"],
                          too_ill_to_move=data["too_ill_to_move"],
                          contrib_foi=data["contrib_foi"],
                          _name=disease,
                          _authors=data["author(s)"],
                          _contacts=data["contact(s)"],
                          _references=data["reference(s)"],
                          _filename=json_file,
                          _repository=repository,
                          _repository_version=repository_version)

        disease._validate()

        return disease
