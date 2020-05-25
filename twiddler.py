from z3 import *
from datetime import datetime, timedelta
import lib
import sys


# def run():
setupTime = datetime.now()
s = Solver() 
p = lib.Parameters.setup()
n = lib.NGrams.load_n_grams(p)
print(len(n.grams))
b = lib.problem_def(s, n)
print(len(n.grams))
lib.mcc_from_scc(s, n, b)
print(len(n.grams))
lib.cost_mcc(s, n, b)
lib.cost_scc(s, n, b)
print(f"last: {len(n.grams)}")


# If cost of chords is given in seconds then cumulative_cost[len(n.grams)-1] is
#   the seconds to enter all n-grams k times per n-gram where k is the frequency
#   count of each n-gram.
# We can use this to calculate average characters per second:
# 1 / (cumulative_cost[len(n.grams)-1] / total_count) this simplifies to:
# total_count / cumulative_cost[len(n.grams)-1]
total_count = 0
for x in n.count:
    total_count += x
total_count = RealVal(total_count)
chars_per_second = Real("cps")
print(len(b.cumulative_cost))
s.add(chars_per_second == total_count / b.cumulative_cost[len(n.grams)-1])

# **************************************************
# Sit back relax and let the SMT solver do the work.
# **************************************************

# Timeout is given in milliseconds
s.set("timeout", (p.timeout.days * 24 * 60 * 60 + p.timeout.seconds) * 1000)
total_time = datetime.now() - setupTime
print(f"N-Grams: {str(len(n.grams))}, Setup Time: {total_time}")
print("---------------------------------------")

hi_sat = 0
lo_unsat = float("inf")
lo_unknown = float("inf")
search_has_failed = False
m = None
# See comments above in "Guide the Search" for understanding how this works.
while min(lo_unsat, lo_unknown, p.cps_hi) - max(hi_sat, p.cps_lo) > p.cps_res:
    # print(f"lo_unsat: {lo_unsat}, lo_unknown: {lo_unknown}, p.cps_hi: {p.cps_hi}, hi_sat: {hi_sat}, p.cps_lo: {p.cps_lo}, p.cps_res: {p.cps_res}")
    solveTime = datetime.now()

    # We start from p.cps_lo initially and increment up by initial_step_up
    #   until we encounter an UNSAT or UNKNOWN problem then we begin
    #   binary search.
    if not search_has_failed:
        guess_cps = max(hi_sat, p.cps_lo - p.initial_step_up()) + p.initial_step_up()
    else:
        guess_cps = (min(lo_unsat, lo_unknown, p.cps_hi) + max(hi_sat, p.cps_lo)) / 2

    # For some reason the solver cannot handle this constraint:
    #   s.add(chars_per_second >= cps)
    #   So we calclate max cumulative cost and set the limit that way.
    guess_max_cumulative_cost = total_count / guess_cps
    s.push() # Create new state
    s.add(b.cumulative_cost[len(n.grams)-1] <= guess_max_cumulative_cost)
    
    result = s.check()
    guess_time = datetime.now() - solveTime
    total_time += guess_time
    print(f"CPS: {guess_cps:.4f} - {str(result):7} - {datetime.now() - solveTime}")

    if result == sat:
        hi_sat = guess_cps
        m = s.model()
    elif result == unsat:
        lo_unsat = guess_cps
        search_has_failed = True
        s.pop() # Restore state (i.e. Remove guess constraint)
                # Only remove guess constraint when it can't be attained, not when sat.
    elif result == unknown:
        lo_unknown = guess_cps
        search_has_failed = True
        s.pop() # Restore state (i.e. Remove guess constraint)
                # Only remove guess constraint when it can't be attained, not when sat.

    # s.pop() # Restore state (i.e. Remove guess constraint)

print("---------------------------------------")
print(f"Sat: {hi_sat:.4f}, Unknown: {lo_unknown:.4f}, Unsat: {lo_unsat:.4f}")
print(f"Total Time: {total_time}")
print("---------------------------------------")


# ******************************************************
# Print out quick view of what configuration looks like.
# ******************************************************

def print_config(d):
    # The default buttons and double row buttons
    f = [
        2048, 3072, 1024, 1536, 512,
        2304, 3456, 1152, 1728, 576,
        256, 384, 128, 192, 64,
        288, 432, 144, 216, 72,
        32, 48, 16, 24, 8,
        36, 54, 18, 27, 9,
        4, 6, 2, 3, 1,
    ]

    # Mask f here when adding combo display feature.

    # If a chord doesn't have an n_gram fill it with the empty string.
    for x in f:
        if x not in d:
            d[x] = ""
    # print(f[0].sort())
    print(f'\n   Left       Middle       Right')
    print(f' ________________________________')
    print(f'|              Space      BckSpc | <-- Mouseclick buttons')
    print(f'|--------------------------------|')
    print(f'| [{d[f[0]]:4}] {d[f[1]]:4} [{d[f[2]]:4}] {d[f[3]]:4} [{d[f[4]]:4}] |')
    print(f'|                                |')
    print(f'|  {d[f[5]]:4}  {d[f[6]]:4}  {d[f[7]]:4}  {d[f[8]]:4}  {d[f[9]]:4}  |')
    print(f'|                                |')
    print(f'| [{d[f[10]]:4}] {d[f[11]]:4} [{d[f[12]]:4}] {d[f[13]]:4} [{d[f[14]]:4}] |')
    print(f'|                                |')
    print(f'|  {d[f[15]]:4}  {d[f[16]]:4}  {d[f[17]]:4}  {d[f[18]]:4}  {d[f[19]]:4}  |')
    print(f'|                                |')
    print(f'| [{d[f[20]]:4}] {d[f[21]]:4} [{d[f[22]]:4}] {d[f[23]]:4} [{d[f[24]]:4}] |')
    print(f'|                                |')
    print(f'|  {d[f[25]]:4}  {d[f[26]]:4}  {d[f[27]]:4}  {d[f[28]]:4}  {d[f[29]]:4}  |')
    print(f'|                                |')
    print(f'| [{d[f[30]]:4}] {d[f[31]]:4} [{d[f[32]]:4}] {d[f[33]]:4} [{d[f[34]]:4}] |')
    print(f'|________________________________|')

# We generate a dictionary where the chords are the keys and n_grams the values.
num_2 = 0
num_3 = 0
num_4 = 0
num_5 = 0
press_lookup = {}
for i in range(len(n.grams)):
    if m[b.G[i]] in press_lookup:
        assert m[b.G[i]] == 0
    else:
        press_lookup[int(str(m[b.G[i]]))] = n.grams[i]
        if len(n.grams[i]) == 2:
            # print("i: " + str(i) + ", m[G[i]]: " + str(m[G[i]]) + ", n.grams: " + n.grams[i])
            num_2 += 1
        elif len(n.grams[i]) == 3:
            num_3 += 1
        elif len(n.grams[i]) == 4:
            num_4 += 1
        elif len(n.grams[i]) == 5:
            num_5 += 1
        elif len(n.grams[i]) == 1:
            print("i: " + str(i) + ", m[G[i]]: " + str(m[b.G[i]]) + ", n_gram: " + n.grams[i])
print(f'Chorded-2_grams: {num_2}, 3_grams: {num_3}, 4_grams: {num_4}, 5_grams: {num_5}')

print_config(press_lookup)

# ******************************************************
# TODO: Convert SMT solver output to configuration file.
# ******************************************************