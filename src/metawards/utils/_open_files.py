
from .._outputfiles import OutputFiles

__all__ = ["open_files"]


def open_files(output_dir: OutputFiles):
    """Opens all of the output files written to during the simulation,
       opening them all in the directory 'output_dir'

       This returns the file handles of all open files
    """
    files = []

    files.append(output_dir.open("WorkInfections.dat"))
    files.append(output_dir.open("NumberWardsInfected.dat"))
    files.append(output_dir.open("MeanXY.dat"))
    files.append(output_dir.open("PlayInfections.dat"))
    files.append(output_dir.open("TotalInfections.dat"))
    files.append(output_dir.open("VarXY.dat"))
    files.append(output_dir.open("Dispersal.dat"))

    return files
