
from ._network import Network
from ._parameters import Parameters
from typing import List
from array import array
import math

import os

__all__ = ["run_model"]


def iterate(network: Network, infections, play_infections,
            params: Parameters, rng, timestep: int,
            is_dangerous=None,
            SELFISOLATE: bool = False,
            IMPORTS: bool = False):
    """Iterate the model forward one timestep (day) using the supplied
       network and parameters, advancing the supplied infections,
       and using the supplied random number generator (rng)
       to generate random numbers. This iterates for a normal
       (working) day (with predictable movements, mixed
       with random movements)

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    temp = 0.0
    uv = params.UV

    #starting day = 41
    uvscale = (1.0-uv/2.0 + math.cos(2.0*math.pi*timestep/365.0)/2.0)

    c_prob = 0.0
    prob_scaled = 0.0
    cutoff = params.dyn_dist_cutoff

    thresh = 0.01

    links = network.to_links
    wards = network.nodes
    plinks = network.play

    for i in range(1, network.nnodes+1):
        wards.day_foi[i] = 0.0
        wards.night_foi[i] = 0.0

    if IMPORTS:
        imported = import_infection(network=network, infections=infections,
                                    play_infections=play_infections,
                                    params=params, rng=rng)

        print(f"Day: {timestep} Imports: expected {params.daily_imports} "
              f"actual {imported}")

    N_INF_CLASSES = len(infections)

    for i in range(0, N_INF_CLASSES):
        scl_foi_uv = params.disease_params.contrib_foi[i] * \
                     params.disease_params.beta[i] * uvscale

        if params.disease_params.contrib_foi[i] > 0:
            for j in range(1, network.nlinks+1):
                # deterministic movements (e.g. to work)
                inf_ij = infections[i][j]
                if inf_ij > 0:
                    weight = links.weight[j]
                    ifrom = links.ifrom[j]
                    ito = links.ito[j]

                    if inf_ij > int(weight)
                        print(f"inf[{i}][{j}] {inf_ij} > links[j].weight "
                              f"{weight}")

                    if links.distance[j] < cutoff:
                        if SELFISOLATE:
                            frac = float(is_dangerous[ito]) / float(
                                     wards.denominator_d[ito] +
                                     wards.denominator_p[ito])

                            if frac > thresh:
                                staying = infections[i][j]
                            else:
                                # number staying - this is G_ij
                                staying = ran_binomial(rng,
                                                       params.disease_params.too_ill_to_move[i],
                                                       inf_ij)
                        else:
                            # number staying - this is G_ij
                            staying = ran_binomial(rng,
                                                    params.disease_params.too_ill_to_move[i],
                                                    inf_ij)

                        if staying < 0:
                            print(f"staying < 0")

                        # number moving, this is I_ij - G_ij
                        moving = inf_ij - staying

                        wards.day_foi[ifrom] += staying * scl_foi_uv

                        # Daytime Force of
                        # Infection is proportional to
                        # number of people staying
                        # in the ward (too ill to work)
                        # this is the sum for all G_ij (including g_ii

                        wards.day_foi[ito] += moving * scl_foi_uv

                        # Daytime FOI for destination is incremented (including self links, I_ii)
                    else:
                        # outside cutoff
                        wards.day_foi[ifrom] += inf_ij * scl_foi_uv

                    wards.night_foi[ifrom] += inf_ij * scl_foi_uv

                    # Nighttime Force of Infection is
                    # prop. to the number of Infected individuals
                    # in the ward
                    # This I_ii in Lambda^N

                # end of if inf_ij (are there any new infections)
            # end of infectious class loop

            for j in range(1, network.nnodes+1):
                # playmatrix loop FOI loop (random/unpredictable movements)
                inf_ij = play_infections[i][j]
                if inf_ij > 0:
                    nodes.night_foi[j] += inf_ij * scl_foi_uv

                    # number of people staying gets bigger as
                    # PlayAtHome increases
                    staying = ran_binomial(rng=rng,
                                           params.dyn_play_at_home * \
                                               params.disease_params.too_ill_to_move[i],
                                           inf_ij)

                    if staying < 0:
                        print(f"staying < 0")

                    moving = inf_ij - staying

                    cumulative_prob = 0.0
                    k = wards.begin_p[j]

                    end_p = wards.end_p[j]

                    while (moving > 0) and (k < end_p):
                        # distributing people across play wards
                        if plinks.distance[k] < cutoff:
                            weight = float(plinks.weight[k])
                            ifrom = plinks.ifrom[k]
                            ito = plinks.ito[k]

                            prob_scaled = weight / (1.0 - cumulative_prob)
                            cumulative_prob += weight

                            playmove = ran_binomial(rng, prob_scaled, moving)

                            if SELFISOLATE:
                                frac = is_dangerous[ito] / float(
                                                wards.denominator_d[ito] +
                                                wards.denominator_p[ito])

                                if frac > thresh:
                                    staying += playmove
                                else:
                                    wards.day_foi[ito] += playmove * scl_foi_uv
                            else:
                                wards.day_foi[ito] += playmove * scl_foi_uv

                            moving -= playmove
                        # end of if within cutoff

                        k += 1
                    # end of while loop

                    wards.day_foi[j] += (moving + staying) * scl_foi_uv
                # end of if inf_ij (there are new infections)

            # end of loop over all nodes
        # end of params.disease_params.contrib_foi[i] > 0:
    # end of loop over all disease classes


	for(i=N_INF_CLASSES-2;i>=0;i--){ // recovery, move through classes backwards.

		for(j=1;j<=net->nlinks;j++){

			if(inf[i][j]>0){

				l=gsl_ran_binomial(r,par->Progress[i],inf[i][j]);

				if(l>0){
					inf[i+1][j]+=l;

					inf[i][j]-=l;

				}

			}
			else if(inf[i][j]!=0){
				printf("PROBLEMs\n");

			}

		}

		for(j=1;j<=net->nnodes;j++){
			if(playinf[i][j]>0){
				l=gsl_ran_binomial(r,par->Progress[i],playinf[i][j]);

				if(l>0){

					playinf[i+1][j]+=l;
					playinf[i][j]-=l;

				}
			}
			else if(playinf[i][j]!=0){
				printf("PROBLEMS!!!");
			}
		}

	}



	i=0;

	InfProb=0.0;
	temp=0;

	for(j=1;j<=net->nlinks;j++){ // actual new infections for fixed movements

		InfProb=0.0;

		if(links[j].distance < cutoff){ // if distance is below cutoff (reasonable distance) infect in work ward

			if(wards[links[j].ito].DayFOI > 0){   // daytime infection of link j

#ifdef SELFISOLATE
				if((double)(IsDangerous[links[j].ito]/(wards[links[j].ito].Denominator_D + wards[links[j].ito].Denominator_P))>thresh){
					InfProb=0;
				}
				else {
#endif
					Rate= (par->LengthDay)*(wards[links[j].ito].DayFOI)/
						(wards[links[j].ito].Denominator_D + wards[links[j].ito].Denominator_PD);

					InfProb=Rate2Prob(Rate);

#ifdef SELFISOLATE
				}
#endif

			}
		}

		else if(wards[links[j].ifrom].DayFOI>0){ // if distance is too large infect in home ward with day FOI

			Rate=(par->LengthDay)*(wards[links[j].ifrom].DayFOI)/
				(wards[links[j].ifrom].Denominator_D + wards[links[j].ifrom].Denominator_PD);
			InfProb=Rate2Prob( Rate );

		}

		if(InfProb>0.0){ // Daytime Infection of workers

			l=gsl_ran_binomial(r,InfProb,(int)links[j].suscept); // actual infection

			if(l>0){
	//			printf("InfProb %lf, susc %lf, l %d\n",InfProb,links[j].suscept,l);
				inf[i][j] += l;
				links[j].suscept -= l;

			}

			InfProb=0.0;

		}


		InfProb=0.0;

		if(wards[links[j].ifrom].NightFOI>0){ //nighttime infection of workers j
			Rate = (1.0-par->LengthDay)*(wards[links[j].ifrom].NightFOI)/
				(wards[links[j].ifrom].Denominator_N + wards[links[j].ifrom].Denominator_P);
			InfProb = Rate2Prob( Rate );



			l = gsl_ran_binomial(r,InfProb,(int)(links[j].suscept));
			if(l > links[j].suscept){
				printf("l > links[j].suscept nighttime\n");
			}
			if(l>0){
	//			printf("NIGHT InfProb %lf, susc %lf, l %d\n",InfProb,links[j].suscept,l);
				inf[i][j]+=l;
				links[j].suscept -= l;


			}

		}

	}

	for(j=1;j<=net->nnodes;j++){ // playmatrix loop.
		InfProb=0.0;

		if(wards[j].play_suscept<0.0){

			printf("play_suscept is less than 0, problem %d\n",wards[j].label);

		}

		staying = gsl_ran_binomial(r,par->DynPlayAtHome,(int)wards[j].play_suscept);

		moving = (int)wards[j].play_suscept - staying;

		cum_prob=0;
		// daytime infection of play matrix moves

		for(k=wards[j].begin_p;k<wards[j].end_p;k++){

			if(plinks[k].distance < cutoff){

				if(wards[plinks[k].ito].DayFOI>0.0){

					ProbScaled=plinks[k].weight/(1-cum_prob);

					cum_prob += plinks[k].weight;

#ifdef SELFISOLATE
					if((double)(IsDangerous[plinks[j].ito]/(wards[plinks[k].ito].Denominator_P+wards[plinks[k].ito].Denominator_D))>thresh){
						InfProb=0;
						playmove=0;
					}
					else {
#endif
					playmove = gsl_ran_binomial(r,ProbScaled,moving);

					InfProb = Rate2Prob( (par->LengthDay)*(wards[plinks[k].ito].DayFOI)/
						(wards[plinks[k].ito].Denominator_PD+wards[plinks[k].ito].Denominator_D) );

#ifdef SELFISOLATE
					}
#endif
					l=gsl_ran_binomial(r,InfProb,playmove);

					moving -= playmove;

					if(l>0){
//						printf("PLAY: InfProb %lf, susc %d, l %d\n",InfProb,playmove,l);
						playinf[i][j] += l;
						wards[j].play_suscept -= l;

					}

				}// end of DayFOI if statement

			}// end of Dynamics Distance if statement.

		} // end of loop over links of wards[j]

		if((staying+moving)>0){ // infect people staying at home damnit!!!!!!!!

			InfProb = Rate2Prob( (par->LengthDay)*(wards[j].DayFOI)/
				(wards[j].Denominator_PD+wards[j].Denominator_D) );

			l=gsl_ran_binomial(r,InfProb,(staying+moving));

			if(l>0){
				playinf[i][j] += l;
				wards[j].play_suscept-=l;

			}

		}

		//nighttime infections of play movements

		if(wards[j].NightFOI>0.0){

			InfProb = Rate2Prob( (1.0-par->LengthDay)*(wards[j].NightFOI)/
				(wards[j].Denominator_N + wards[j].Denominator_P) );

			l = gsl_ran_binomial(r,InfProb,(int)(wards[j].play_suscept));

			if(l>0){

				playinf[i][j]+=l;
				wards[j].play_suscept -= l;

			}

		}

	}

	return;


def iterate_weekend(network: Network, infections, play_infections,
                    params: Parameters, rng, timestep: int,
                    is_dangerous = None, SELFISOLATE: bool = False):
    """Iterate the model forward one timestep (day) using the supplied
       network and parameters, advancing the supplied infections,
       and using the supplied random number generator (rng)
       to generate random numbers. This iterates for a non-working
       (weekend) day (with only random movements)

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    pass


def how_many_vaccinated(vac):
    raise AssertionError("how_many_vaccinated has not yet been written")


def vaccinate_same_id(network: Network, risk_ra, sort_ra,
                      infections, play_infections,
                      vac, params):
    raise AssertionError("vaccinate_same_id has not yet been written")


def infect_additional_seeds(network: Network, params: Parameters,
                            infections, play_infections,
                            additional_seeds, timestep: int):
    """Cause more infection from additional infection seeds"""
    wards = network.nodes

    for seed in additional_seeds:
        if seed[0] == timestep:
            if wards.play_suscept[seed[1]] < seed[2]:
                print(f"Not enough susceptibles in ward for seeding")
            else:
                wards.play_suscept[seed[1]] -= seed[2]
                play_infections[0][seed[1]] += seed[2]


def load_additional_seeds(filename: str):
    """Load additional seeds from the passed filename. This returns
       the added seeds
    """
    with open(filename, "r") as FILE:
        line = FILE.readline()
        seeds = []

        while line:
            words = line.split()
            seeds.append( (int(words[0]), int(words[1]), int(words[2])) )
            line = FILE.readline()

    return seeds


def extract_data_for_graphics(network: Network, infections,
                              play_infections, FILE):
    """Extract data that will be used for graphical analysis"""
    links = network.to_links

    N_INF_CLASSES = len(infections)
    MAXSIZE = network.nnodes

    int_t = "i"

    inf_tot = array(int_t, N_INF_CLASSES, 0)
    total_inf_ward = []
    for i in range(0, N_INF_CLASSES):
        total_inf_ward.append( array(int_t, MAXSIZE, 0) )

    total = 0

    total_infections = array(int_t, MAXSIZE, 0)

    for i in range(0, N_INF_CLASSES):
        for j in range(1, network.nlinks+1):
            inf_ij = infections[i][j]
            if inf_ij != 0:
                inf_tot[i] += inf_ij
                ifrom = links.ifrom[j]
                total_inf_ward[i][ifrom] += inf_ij
                if i < N_INF_CLASSES-1:
                    total_infections[ifrom] += inf_ij
                    total += inf_ij

        for j in range(1, network.nnodes+1):
            pinf_ij = play_infections[i][j]
            total_inf_ward[i][j] += pinf_ij
            if (pinf_ij != 0) and (i < N_INF_CLASSES-1):
                total_infections[j] += pinf_ij
                total += pinf_ij

            if i == 2:
                FILE.write("%d ", total_infections[j])   # incidence

                #if i == N_INF_CLASSES - 1:
                #    FILE.write("%d ", total_infections[j])  # prevalence

                #if i == N_INF_CLASSES - 1:
                #    prevalence[j] = total_infections[j]

    FILE.write("\n")

    return total


def extract_data(network: Network, infections, play_infections,
                 timestep: int, files, is_dangerous=None,
                 SELFISOLATE: bool = False):
    """Extract data for timestep 'timestep' from the network and
       infections and write this to the output files in 'files'
       (these must have been opened by 'open_files')

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    links = network.to_links
    wards = network.nodes

    int_t = "i"
    N_INF_CLASSES = len(infections)
    MAXSIZE = network.nnodes

    assert len(infections) == len(play_infections)

    if SELFISOLATE and (is_dangerous is None):
        raise AssertionError("You must pass in the 'is_dangerous' array "
                             "if SELFISOLATE is True")

    inf_tot = array(int_t, N_INF_CLASSES, 0)
    pinf_tot = array(int_t, N_INF_CLASSES, 0)

    total_inf_ward = array(int_t, MAXSIZE, 0)
    total_new_inf_ward = array(int_t, MAXSIZE, 0)

    n_inf_wards = array(int_t, N_INF_CLASSES, 0)

    total = 0
    total_new = 0

    recovereds = 0
    susceptibles = 0
    latent = 0

    sum_x = 0.0
    sum_y = 0.0
    sum_x2 = 0.0
    sum_y2 = 0.0
    mean_x = 0.0
    mean_y = 0.0
    var_x = 0.0
    var_y = 0.0
    dispersal = 0.0

    files[0].write("%d " % timestep)
    files[1].write("%d " % timestep)
    files[3].write("%d " % timestep)

    for i in range(0, N_INF_CLASSES):
        # do we need to initialise total_new_inf_wards and
        # total_inf_wards to 0?

        for j in range(1, network.nlinks+1):
            if i == 0:
                susceptibles += int(links.suscept[j])
                total_new_inf_ward[links.ifrom[j]] += infections[i][j]

            if infections[i][j] != 0:
                if SELFISOLATE:
                    if (i > 4) and (i < 10):
                        is_dangerous[links.ito[j]] += infections[i][j]

                inf_tot[i] += infections[i][j]
                total_inf_ward[links.ifrom[j]] += infections[i][j]

        for j in range(1, network.nnodes+1):
            if i == 0:
                susceptibles += int(wards.play_suscept[j])
                if play_infections[i][j] > 0:
                    total_new_inf_ward[j] += play_infections[i][j]

                if total_new_inf_ward[j] != 0:
                    newinf = total_new_inf_ward[j]
                    x = wards.x[j]
                    y = wards.y[j]
                    sum_x += newinf * x
                    sum_y += newinf * y
                    sum_x2 += newinf * x * x
                    sum_y2 += newinf * y * y
                    total_new += newinf

            if play_infections[i][j] > 0:
                pinf = play_infections[i][j]
                pinf_tot[i] += pinf
                total_inf_ward[j] += pinf

                if SELFISOLATE:
                    if (i > 4) and (i < 10):
                        is_dangerous[i] += pinf

            if (i < N_INF_CLASSES-1) and total_inf_ward[j] > 0:
                n_inf_wards[i] += 1

        files[0].write("%d " % inf_tot[i])
        files[1].write("%d " % n_inf_wards[i])
        files[3].write("%d " % pinf_tot[i])

        if i == 1:
            latent += inf_tot[i] + pinf_tot[i]
        elif (i < N_INF_CLASSES-1) and (i > 1):
            total += inf_tot[i] + pinf_tot[i]
        else:
            recovereds += inf_tot[i] + pinf_tot[i]

    if total_new > 0:
        mean_x = float(sum_x) / float(total_new)
        mean_y = float(sum_y) / float(total_new)

        var_x = float(sum_x2 - sum_x*mean_x) / float(total_new - 1)
        var_y = float(sum_y2 - sum_y*mean_y) / float(total_new - 1)

        dispersal = math.sqrt(var_x + var_y)
        files[2].write("%d %f %f\n" % (timestep, mean_x, mean_y))
        files[5].write("%d %f %f\n" % (timestep, var_x, var_y))
        files[6].write("%d %f\n" % (timestep, dispersal))
    else:
        files[2].write("%d %f %f\n" % (timestep, 0.0, 0.0))
        files[5].write("%d %f %f\n" % (timestep, 0.0, 0.0))
        files[6].write("%d %f\n" % (timestep, 0.0))

    files[0].write("\n")
    files[1].write("\n")
    files[3].write("\n")
    files[4].write("%d \n" % total)
    files[4].fflush()

    print(f"S: {susceptibles}    ", end="")
    print(f"E: {latent}    ", end="")
    print(f"I: {total}    ", end="")
    print(f"R: {recovereds}    ", end="")
    print(f"IW: {n_inf_wards}   ", end="")
    print(f"TOTAL POPULATION {susceptibles+total+recovereds}")

    return (total+latent)


def seed_infection_at_node(network: Network, params: Parameters,
                           seed: int, infections, play_infections):
    """Seed the infection at a specific ward"""
    wards = network.nodes
    links = network.to_links

    j = 0

    while (links.ito[j] != seed) or (links.ifrom[j] != seed):
        j += 1

    print(f"j {j} link from {links.ifrom[j]} to {links.ito[j]}")

    if links.suscept[j] < params.initial_inf:
        wards.play_suscept[seed] -= params.initial_inf
        play_infections[0][seed] += params.initial_inf

    infections[0][j] = params.initial_inf
    links.suscept[j] -= params.initial_inf


def seed_all_wards(network: Network, play_infections,
                   expected: int, population: int = 57104043):
    """Seed the wards with an initial set of infections, assuming
       an 'expected' number of infected people out of a population
       of 'population'
    """
    wards = network.nodes

    frac = float(expected) / float(population)

    for i in range(0, network.nnodes+1):  # 1-index but also count at 0?
        temp = wards.denominator_n[i] + wards.denominator_p[i]
        to_seed = int(frac*temp + 0.5)
        wards.play_suscept[i] -= to_seed
        play_infections[0][i] += to_seed


def clear_all_infections(infections, play_infections):
    """Clears all infections (held in the list of array(int) in infections,
       and array(int) in play_infections) associated with the
       passed network
    """
    assert len(infections) == len(play_infections)

    for i in range(0, len(infections)):
        a = infections[i]
        for j in range(0, len(a)):
            a[j] = 0

        a = play_infections[i]
        for j in range(0, len(a)):
            a[j] = 0


def open_files(output_dir: str):
    """Opens all of the output files written to during the simulation,
       opening them all in the directory 'output_dir'

       This returns the file handles of all open files
    """
    files = []

    files.append( open(os.path.join(output_dir, "WorkInfections.dat", "w")) )
    files.append( open(os.path.join(output_dir, "NumberWardsInfected.dat",
                       "w")) )
    files.append( open(os.path.join(output_dir, "MeanXY.dat", "w")) )
    files.append( open(os.path.join(output_dir, "PlayInfections.dat", "w")) )
    files.append( open(os.path.join(output_dir, "TotalInfections.dat", "w")) )
    files.append( open(os.path.join(output_dir, "VarXY.dat", "w")) )
    files.append( open(os.path.join(output_dir, "Dispersal.dat", "w")) )

    return files


def run_model(network: Network, params: Parameters,
              infections, play_infections,
              rng, to_seed: List[float], s: int,
              output_dir: str=".",
              population: int=57104043,
              MAXSIZE: int=10050,
              VACCINATE: bool = False,
              IMPORTS: bool = False,
              EXTRASEEDS: bool = True,
              WEEKENDS: bool = False):
    """Actually run the model... Real work happens here"""

    int_t = "i"    # signed int64
    float_t = "d"  # double (float64)

    size = MAXSIZE   # suspect this will be the number of nodes

    EXPORT = open(os.path.join(output_dir, "ForMattData.dat", "w"))

    if VACCINATE:
        trigger = 0
        vac = array(int_t, size, 0)
        #wards_ra = array(int_t, size, 0)
        risk_ra = array(float_t, size, 0.0)
        sort_ra = array(int_t, size, 0)
        VACF = open(os.path.join(output_dir, "Vaccinated.dat", "w"))

    files = open_files(output_dir=output_dir)

    clear_all_infections(infections=infections,
                         play_infections=play_infections)

    print(f"node_seed {to_seed[s]}")

    if not IMPORTS:
        if s < 0:
            seed_all_wards(network=network,
                           play_infections=play_infections,
                           expected=params.daily_imports,
                           population=population)
        else:
            seed_infection_at_node(network=network, params=params,
                                   seed=to_seed[s],
                                   infections=infections,
                                   play_infections=play_infections)

    timestep = 0  # start timestep of the model (day since infection starts)

    infecteds = extract_data(network=network, infections=infections,
                             play_infections=play_infections,
                             timestep=timestep, files=files)

    if WEEKENDS:
        day = 1  # day number of the week, 1-5 = weekday, 6-7 = weekend

    if EXTRASEEDS:
        additional_seeds = load_additional_seeds(
                                params.input_files.additional_seeding)

    while (infecteds != 0) or (timestep < 5):
        if EXTRASEEDS:
            infect_additional_seeds(network=network, params=params,
                                    infections=infections,
                                    play_infections=play_infections,
                                    additional_seeds=additional_seeds,
                                    timestep=timestep)

        if WEEKENDS:
            print(f"day: {day}")
            if day > 5:
                iterate_weekend(network=network, infections=infections,
                                play_infections=play_infections,
                                params=params, rng=rng, timestep=timestep)
                print("weekend")
            else:
                iterate(network=network, infections=infections,
                        play_infections=play_infections,
                        params=params, rng=rng, timestep=timestep)
                print("normal day")

            if day == 7:
                day = 0

            day += 1
        else:
            iterate(network=network, infections=infections,
                    play_infections=play_infections,
                    params=params, rng=rng, timestep=timestep)

        print(f"\n {timestep} {infecteds}")

        infecteds = extract_data(network=network, infections=infections,
                                 play_infections=play_infections,
                                 timestep=timestep, files=files)

        extract_data_for_graphics(network=network, infections=infections,
                                  play_infections=play_infections,
                                  FILE=EXPORT)

        timestep += 1

        if VACCINATE:
            #vaccinate_wards(network=network, wards_ra=wards_ra,
            #                infections=infections,
            #                play_infections=play_infections,
            #                vac=vac, params=params)

            if infecteds > params.global_detection_thresh:
                trigger = 1

            if trigger == 1:
                #vaccinate_county(network=network, risk_ra=risk_ra,
                #                 sort_ra=sort_ra,
                #                 infections=infections,
                #                 play_infections=play_infections,
                #                 vac=vac, params=params)

                vaccinate_same_id(network=network, risk_ra=risk_ra,
                                  sort_ra=sort_ra,
                                  infections=infections,
                                  play_infections=play_infections,
                                  vac=vac, params=params)

                if params.disease_params.contrib_foi[0] == 1.0:
                    N_INF_CLASSES = len(infections)
                    for j in range(0, N_INF_CLASSES-1):
                        params.disease_params.contrib_foi[j] = 0.2

            VACF.write("%d %d\n" % (timestep, how_many_vaccinated(vac)))

        # end of "IF VACCINATE"
    # end of while loop

    EXPORT.close()

    if VACCINATE:
        VACF.close()

    for FILE in files:
        FILE.close()

    print(f"Infection died ... Ending at time {timestep}")
