

def advance_fixed():

    cdef int suscept = 0
    cdef double dyn_play_at_home = params.dyn_play_at_home

    p = p.start("play")
    with nogil, parallel(num_threads=num_threads):
        thread_id = cython.parallel.threadid()
        pr = _get_binomial_ptr(rngs_view[thread_id])

        for j in prange(1, nnodes_plus_one, schedule="static"):
            # playmatrix loop
            inf_prob = 0.0

            suscept = <int>wards_play_suscept[j]

            #if suscept < 0:
            #    print(f"play_suscept is less than 0 ({suscept}) "
            #        f"problem {j}, {wards_label[j]}")

            staying = _ran_binomial(pr, dyn_play_at_home, suscept)

            moving = suscept - staying

            cumulative_prob = 0.0

            # daytime infection of play matrix moves
            for k in range(wards_begin_p[j], wards_end_p[j]):
                if plinks_distance[k] < cutoff:
                    ito = plinks_ito[k]

                    if wards_day_foi[ito] > 0.0:
                        weight = plinks_weight[k]
                        prob_scaled = weight / (1.0-cumulative_prob)
                        cumulative_prob = cumulative_prob + weight

                        if cSELFISOLATE:
                            frac = is_dangerous_array[ito] / (
                                                    wards_denominator_p[ito] +
                                                    wards_denominator_d[ito])

                            if frac > thresh:
                                inf_prob = 0.0
                                play_move = 0
                            else:
                                play_move = _ran_binomial(pr, prob_scaled, moving)
                                inf_prob = wards_day_inf_prob[ito]
                        else:
                            play_move = _ran_binomial(pr, prob_scaled, moving)
                            inf_prob = wards_day_inf_prob[ito]

                        l = _ran_binomial(pr, inf_prob, play_move)

                        moving = moving - play_move

                        if l > 0:
                            # infection
                            #print(f"PLAY: InfProb {inf_prob}, susc {play_move}, "
                            #      f"l {l}")
                            #print(f"daytime play_infections[{i}][{j}] += {l}")
                            play_infections_i[j] += l
                            wards_play_suscept[j] -= l

                    # end of DayFOI if statement
                # end of Dynamics Distance if statement
            # end of loop over links of wards[j]

            if (staying + moving) > 0:
                # infect people staying at home
                inf_prob = wards_day_inf_prob[j]
                l = _ran_binomial(pr, inf_prob, staying+moving)

                if l > 0:
                    # another infections, this time from home
                    #print(f"staying home play_infections[{i}][{j}] += {l}")
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l

            # nighttime infections of play movements
            inf_prob = wards_night_inf_prob[j]
            if inf_prob > 0.0:
                l = _ran_binomial(pr, inf_prob, <int>(wards_play_suscept[j]))

                if l > 0:
                    # another infection
                    #print(f"nighttime play_infections[{i}][{j}] += {l}")
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l
        # end of loop over wards (nodes)
    # end of parallel
    p = p.stop()
