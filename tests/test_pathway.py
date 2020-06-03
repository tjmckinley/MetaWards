
import os

from metawards import Parameters, Network, Population, \
    OutputFiles, Demographics, Disease

from metawards.mixers import mix_evenly

script_dir = os.path.dirname(__file__)

demographics_json = os.path.join(script_dir, "data",
                                 "spreader_demographics.json")

home_json = os.path.join(script_dir, "data", "lurgy_home.json")
super_json = os.path.join(script_dir, "data", "lurgy_super.json")


def test_pathway():
    demographics = Demographics.load(demographics_json)
    assert len(demographics) == 2

    disease_home = Disease.load(filename=home_json)
    disease_super = Disease.load(filename=super_json)

    assert demographics[1].disease is None
    assert demographics[0].disease == disease_super

    params = Parameters.load()
    params.set_disease(disease_home)
    params.set_input_files("single")
    params.add_seeds("ExtraSeedsOne.dat")

    network = Network.build(params)

    print(network.params.disease_params)
    print(disease_home)

    assert network.params.disease_params == disease_home

    network = network.specialise(demographics)

    print(network.params.disease_params)
    print(disease_home)

    assert network.params.disease_params == disease_home

    print(network.subnets[1].params.disease_params)
    print(disease_home)

    assert network.subnets[1].params.disease_params == disease_home

    print(network.subnets[0].params.disease_params)
    print(disease_super)

    assert network.subnets[0].params.disease_params == disease_super

    infections = network.initialise_infections()

    assert infections.N_INF_CLASSES == disease_home.N_INF_CLASSES()

    assert \
        infections.subinfs[1].N_INF_CLASSES == disease_home.N_INF_CLASSES()

    assert \
        infections.subinfs[0].N_INF_CLASSES == disease_super.N_INF_CLASSES()

    assert disease_super.N_INF_CLASSES() != disease_home.N_INF_CLASSES()

    outdir = os.path.join(script_dir, "test_pathway")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        results = network.run(population=Population(),
                              output_dir=output_dir,
                              mixer=mix_evenly,
                              nthreads=2,
                              seed=36538943)

    OutputFiles.remove(outdir, prompt=None)

    print(results[-1])
    print(results[-1].initial)

    expected = Population(susceptibles=902,
                          latent=0,
                          total=0,
                          recovereds=98,
                          n_inf_wards=0,
                          day=119)

    print(expected)

    assert results[-1].has_equal_SEIR(expected)
    assert results[-1].day == expected.day


if __name__ == "__main__":
    test_pathway()
