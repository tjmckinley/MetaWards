
import os

__all__ = ["open_files"]


def open_files(output_dir: str):
    """Opens all of the output files written to during the simulation,
       opening them all in the directory 'output_dir'

       This returns the file handles of all open files
    """
    files = []

    files.append( open(os.path.join(output_dir, "WorkInfections.dat"), "w") )
    files.append( open(os.path.join(output_dir, "NumberWardsInfected.dat"),
                       "w") )
    files.append( open(os.path.join(output_dir, "MeanXY.dat"), "w") )
    files.append( open(os.path.join(output_dir, "PlayInfections.dat"), "w") )
    files.append( open(os.path.join(output_dir, "TotalInfections.dat"), "w") )
    files.append( open(os.path.join(output_dir, "VarXY.dat"), "w") )
    files.append( open(os.path.join(output_dir, "Dispersal.dat"), "w") )

    return files
