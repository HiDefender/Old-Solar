# This constraint is inspired by typemax:
# https://github.com/lancegatlin/typemax
from z3 import *

def stride_constraint(s):
    print("Just a stub for now!")

    # Stride cost is:
    #     -cost = 
    #     -Cost of most expensive button *
    #     -(sum_of_bigram_freq_not_in_stride_or_stutter + 0.5 *  sum_of_bigram_freq_in_stride + 0.75 * sum_of_bigram_freq_in_stutter) / sum_of_all_bigram_freq