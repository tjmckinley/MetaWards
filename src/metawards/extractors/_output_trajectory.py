
from .._population import Populations
from .._outputfiles import OutputFiles

__all__ = ["output_trajectory"]


def output_trajectory(output_dir: OutputFiles,
                      trajectory: Populations,
                      **kwargs) -> None:
    """Call in the "finalise" stage to output the
       population trajectory to the 'trajectory.csv' file
    """

    RESULTS = output_dir.open("trajectory.csv")

    print(f"\nWriting a summary of all results into the\n"
          f"csv file {output_dir.get_filename('results.csv')}.\n"
          f"You can use this to quickly look at statistics across\n"
          f"all runs using e.g. R or pandas")

    has_date = trajectory[0].date

    if has_date:
        datestring = "date,"
    else:
        datestring = ""

    RESULTS.write(f"day,{datestring}S,E,I,R,IW,UV\n")
    for i, pop in enumerate(trajectory):
        if pop.date:
            d = pop.date.isoformat() + ","
        else:
            d = ""

        RESULTS.write(f"{pop.day},{d}{pop.susceptibles},"
                      f"{pop.latent},{pop.total},"
                      f"{pop.recovereds},{pop.n_inf_wards},"
                      f"{pop.scale_uv}\n")
