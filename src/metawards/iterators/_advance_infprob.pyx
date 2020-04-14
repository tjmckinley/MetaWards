

__all__ = ["advance_infprob"]

def advance_infprob():
    cdef double length_day = params.length_day
    cdef double rate, inf_prob, denom

    # i is set to 0 now as we are only dealing now with new infections
    i = 0
    infections_i = get_int_array_ptr(infections[i])
    play_infections_i = get_int_array_ptr(play_infections[i])

    p = p.start("infprob")
    with nogil, parallel(num_threads=num_threads):
        for j in prange(1, nnodes_plus_one, schedule="static"):
            # pre-calculate the day and night infection probability
            # for each ward
            denom = wards_denominator_d[j] + wards_denominator_pd[j]

            if denom != 0.0:
                rate = (length_day * wards_day_foi[j]) / denom
                wards_day_inf_prob[j] = rate_to_prob(rate)
            else:
                wards_day_inf_prob[j] = 0.0

            denom = wards_denominator_n[j] + wards_denominator_p[j]

            if denom != 0.0:
                rate = (1.0 - length_day) * (wards_night_foi[j]) / denom
                wards_night_inf_prob[j] = rate_to_prob(rate)
        # end of loop over wards
    # end of parallel
    p = p.stop()
