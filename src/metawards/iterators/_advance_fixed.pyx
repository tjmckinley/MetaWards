
__all__ = ["advance_fixed"]


def advance_fixed():
    p = p.start("fixed")
    with nogil, parallel(num_threads=num_threads):
        thread_id = cython.parallel.threadid()
        pr = _get_binomial_ptr(rngs_view[thread_id])

        for j in prange(1, nlinks_plus_one, schedule="static"):
            # actual new infections for fixed movements
            inf_prob = 0

            ifrom = links_ifrom[j]
            ito = links_ito[j]
            distance = links_distance[j]

            if distance < cutoff:
                # distance is below cutoff (reasonable distance)
                # infect in work ward
                if wards_day_foi[ito] > 0:
                    # daytime infection of link j
                    if cSELFISOLATE:
                        frac = is_dangerous_array[ito] / (
                                                wards_denominator_d[ito] +
                                                wards_denominator_p[ito])

                        if frac > thresh:
                            inf_prob = 0.0
                        else:
                            inf_prob = wards_day_inf_prob[ito]
                    else:
                        inf_prob = wards_day_inf_prob[ito]

                # end of if wards.day_foi[ito] > 0
            # end of if distance < cutoff
            elif wards_day_foi[ifrom] > 0:
                # if distance is too large then infect in home ward with day FOI
                inf_prob = wards_day_inf_prob[ifrom]

            if inf_prob > 0.0:
                # daytime infection of workers
                l = _ran_binomial(pr, inf_prob, <int>(links_suscept[j]))

                if l > 0:
                    # actual infection
                    #print(f"InfProb {inf_prob}, susc {links.suscept[j]}, l {l}")
                    infections_i[j] += l
                    links_suscept[j] -= l

            # nighttime infection of workers
            inf_prob = wards_night_inf_prob[ifrom]

            if inf_prob > 0.0:
                l = _ran_binomial(pr, inf_prob, <int>(links_suscept[j]))

                #if l > links_suscept[j]:
                #    print(f"l > links[{j}].suscept {links_suscept[j]} nighttime")

                if l > 0:
                    # actual infection
                    # print(f"NIGHT InfProb {inf_prob}, susc {links.suscept[j]}, {l}")
                    infections_i[j] += l
                    links_suscept[j] -= l
            # end of wards.night_foi[ifrom] > 0  (nighttime infections)
        # end of loop over all network links
    # end of parallel section
    p = p.stop()
