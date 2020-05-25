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
    cps_res: float = 0.001
    # -Easy SAT and clearly UNSAT problems are solved quickly.
    # -The solver learns more from solving SAT problems.
    #   Therefore search begins at cps_lo and increases each time by initial_step_up.
    #   Once the first UNSAT or UNKNOWN is encountered, binary search is used instead.
    #   Set initial_lo_to_hi_ratio_step_up to zero to enter binary search immediately.
    initial_lo_to_hi_ratio_step_up: float = 1/10
    # The number of miliseconds the solver should spend on any single iteration.
    #   Higher is better and slower.
    timeout: timedelta = timedelta(minutes=5)
    # Ignores all n_grams (except single alphabet characters) with a frequency below the cutoff.
    #   Lower is better and slower.
    cutoff: int = 8000000
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
    stride: float = 0.5
    stutter: float = 0.75


    def setup():
        p = Parameters()
        assert p.cps_hi > p.cps_lo
        assert p.cps_hi - p.cps_lo > p.cps_res
        print(f'Hi: {p.cps_hi}, Lo: {p.cps_lo}, Resolution: {p.cps_res}')
        print(f'Timeout: {p.timeout}, Cutoff: {p.cutoff}, Freq_prune: {p.freq_prune:.2f}')
        print("---------------------------------------")
        return p

    def initial_step_up(self) -> float:
        return (self.cps_hi - self.cps_lo) * self.initial_lo_to_hi_ratio_step_up

