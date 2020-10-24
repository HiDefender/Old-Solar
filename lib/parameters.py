from dataclasses import dataclass, field
from datetime import datetime, timedelta

# ***************************************
# Guide the Search
# ***************************************
# This problem is too big for the solver to find a solution to by itself in a
#   reasonable amount of time. So we play with these variables to find a good solution.
@dataclass
class Parameters:
     # We want a model with a high Characters Per Second (CPS). The solver will search this
    #   range for the highest CPS it can find. It will quit once the difference between the
    #   highest satisfiable (sat) solution and the lowest unsatisfiable/timeout (unsat/unknown)
    #   is less than the resolution.
    cps_hi: float = 5.0
    cps_lo: float = 0.0
    cps_res: float = 1.0 #0.00000000001
    # -Easy SAT and clearly UNSAT problems are solved quickly.
    # -The solver learns more from solving SAT problems.
    #   Therefore search begins at cps_lo and increases each time by initial_lo_to_hi_ratio_step_up.
    #   Once the first UNSAT or UNKNOWN is encountered, after_failure_step_up_ratio is used instead.
    #   Set initial_lo_to_hi_ratio_step_up to zero to enter after_failure_step_up_ratio immediately.
    initial_lo_to_hi_ratio_step_up: float = 1/20 #1/10000
    #   After first failure increase guess more conservatively.
    after_failure_step_up_ratio: float = 1/10 #1/1000
    # The number of miliseconds the solver should spend on any single iteration.
    #   Higher is better and slower.
    timeout: timedelta = timedelta(seconds=60)
    # After a solver query is SAT, UNSAT, or UNKNOWN only print update to screen
    #   if at least update_time has passed since last printed update.
    #   First solver query always prints.
    update_time: timedelta = timedelta(seconds=30)
    # After a solver query is SAT only print update to file if at least sat_time
    #   has passed since last sat printed to file.
    sat_time: timedelta = timedelta(seconds=30)
    # Ignores all n_grams (except single alphabet characters) with a frequency below the cutoff.
    #   Lower is better and slower.
    cutoff: int = 50000000
    # Affects how aggressively the frequency of k_grams is reduced when they are sub-strings of
    #   (k + 1)_grams. Set to 0 to turn off.
    freq_prune: float = 2/3
    # Frequency files to load:
    alphabet_file: str = "english_monograms.txt"
    bigrams_file: str = "english_bigrams.txt"
    other_freq_files: list = field(default_factory=lambda:
                        ["english_trigrams.txt",
                        "english_quadgrams.txt",
                        "english_quintgrams.txt"])
    #Striding is assumed to be faster than normal, this is the discount given to strides.
    #   https://github.com/lancegatlin/typemax/blob/master/basic_layout_design.md#stride
    stride: float = 0.5
    #Stuttering is assumed to be faster than normal, this is the discount given to stutters.
    #   https://github.com/lancegatlin/typemax/blob/master/basic_layout_design.md#stutter
    stutter: float = 0.75
    stride_wt: float = 0.9


    def setup():
        p = Parameters()
        assert p.cps_hi > p.cps_lo
        assert p.cps_hi - p.cps_lo > p.cps_res
        print(f'Hi: {p.cps_hi}, Lo: {p.cps_lo}, Resolution: {p.cps_res}')
        print(f'Timeout: {p.timeout}, Cutoff: {p.cutoff}, Freq_prune: {p.freq_prune:.2f}')
        print(f"Stride discount: {p.stride}, Stutter discount: {p.stutter}")
        # min_print_time replaced with update_time and sat_time. No need to print those out.
        # print(f"If not last SAT solution print to STDOUT and file only if timer exceeds: {p.min_print_time}")
        print("---------------------------------------")
        return p

    def initial_step_up(self) -> float:
        return (self.cps_hi - self.cps_lo) * self.initial_lo_to_hi_ratio_step_up

    def after_failure_step_up(self, hi, low) -> float:
        return low + (hi - low) * self.after_failure_step_up_ratio

