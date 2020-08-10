
from metawards import Network, Ward, Parameters, Disease, WardID, Population, \
    OutputFiles
from metawards.movers import go_ward, MoveGenerator, MoveRecord

import os

script_dir = os.path.dirname(__file__)


def move_cycle(**kwargs):
    generator = MoveGenerator(from_stage="R", to_stage="S")
    go_cycle = lambda **kwargs: go_ward(generator=generator, **kwargs)

    return [go_cycle]


def go_travel(generator, **kwargs):
    record = MoveRecord()
    go_ward(generator=generator, record=record, **kwargs)
    print(record._record)


def move_bristol(**kwargs):
    gen = MoveGenerator(to_ward="bristol")
    go_bristol = lambda **kwargs: go_travel(generator=gen, **kwargs)
    return [go_bristol]


def move_travel(network, **kwargs):
    gen1 = MoveGenerator(from_ward=network.get_ward_ids("bristol"),
                         from_stage="E",
                         to_ward="london",
                         to_stage="E",
                         fraction=0.5)

    gen2 = MoveGenerator(from_ward=network.get_ward_ids("bristol"),
                         from_stage="E",
                         to_ward="oxford",
                         to_stage="E",
                         fraction=1.0)

    gen3 = MoveGenerator(from_ward=network.get_ward_ids("london") +
                         network.get_ward_ids("bristol"),
                         from_stage="R",
                         to_ward="oxford",
                         to_stage="R")

    go_travel1 = lambda **kwargs: go_travel(generator=gen1, **kwargs)
    go_travel2 = lambda **kwargs: go_travel(generator=gen2, **kwargs)
    go_travel3 = lambda **kwargs: go_travel(generator=gen3, **kwargs)

    return [go_travel1, go_travel2, go_travel3]


def test_go_ward():
    bristol = Ward("bristol")
    london = Ward("london")
    oxford = Ward("oxford")

    bristol.set_num_players(100)
    london.set_num_players(100)
    oxford.set_num_players(100)

    bristol.add_workers(0, destination=london)
    bristol.add_workers(0, destination=oxford)
    oxford.add_workers(0, destination=bristol)
    oxford.add_workers(0, destination=london)
    london.add_workers(0, destination=bristol)
    london.add_workers(0, destination=oxford)

    disease = Disease(name="lurgy")
    disease.add(name="E", beta=0.5, progress=0.5)
    disease.add(name="I", beta=0.8, progress=0.25)
    disease.add(name="R")
    disease.assert_sane()

    params = Parameters()
    params.set_disease(disease)
    params.add_seeds("1 20 bristol")

    outdir = os.path.join(script_dir, "test_go_ward_output")

    network = Network.from_wards(bristol + london + oxford, params=params)

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        nthreads=1)

    print(trajectory[-1])

    # there are no workers, so can only infect the 100 Bristolians
    assert trajectory[-1].recovereds <= 100

    # Repeat with a different number of threads to test parallel code
    outdir = os.path.join(script_dir, "test_go_ward_output")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        nthreads=4)

    print(trajectory[-1])

    # there are no workers, so can only infect the 100 Bristolians
    assert trajectory[-1].recovereds <= 100

    # now do a cyclic move, from "R" to "S"
    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        mover=move_cycle,
                                        nsteps=200)

    print(trajectory[-1])

    # we should have completed all 200 steps as this will never end
    assert trajectory[-1].day == 200
    assert trajectory[-1].recovereds <= 100

    # move everyone to Bristol
    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        mover=move_bristol)

    print(trajectory[-1])
    assert trajectory[-1].recovereds > 100

    # now move through all of bristol, london, oxford
    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        mover=move_travel)

    print(trajectory[-1])
    assert trajectory[-1].recovereds > 100

    OutputFiles.remove(outdir, prompt=None)


if __name__ == "__main__":
    test_go_ward()
