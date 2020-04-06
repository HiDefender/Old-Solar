from z3 import *
from datetime import datetime, timedelta
import sys

setupTime = datetime.now()
s = Solver()

# ***************************************
# Guide the Search
# ***************************************
# This problem is too big for the solver to find a solution to by itself in a
#   reasonable amount of time. So we play with these variables to find a good solution.

# We want a model with a high Characters Per Second (CPS). The solver will search this
#   range for the highest CPS it can find. It will quit once the difference between the
#   highest satisfiable (sat) solution and the lowest unsatisfiable/timeout (unsat/unknown)
#   is less than the resolution.
cps_hi = 3.0
cps_lo = 1.0
assert(cps_hi > cps_lo)
cps_res = 0.05
# -Easy SAT and clearly UNSAT problems are solved quickly.
# -The solver learns more from solving SAT problems.
#   Therefore search begins at cps_lo and increases each time by initial_step_up.
#   Once the first UNSAT or UNKNOWN is encountered, binary search is used instead.
#   Set initial_lo_to_hi_ratio_step_up to zero to enter binary search immediately.
initial_lo_to_hi_ratio_step_up = 1/10
initial_step_up = (cps_hi - cps_lo) * initial_lo_to_hi_ratio_step_up
# The number of miliseconds the solver should spend on any single iteration.
#   Higher is better and slower.
timeout = timedelta(minutes=2)
# Ignores all n_grams (except single alphabet characters) with a frequency below the cutoff.
#   Lower is better and slower.
cutoff = 8000000
# Affects how aggressively the frequency of k_grams is reduced when they are sub-strings of
#   (k + 1)_grams. Set to 0 to turn off.
freq_prune = 2/3

print(f'Hi: {cps_hi}, Lo: {cps_lo}, Resolution: {cps_res}')
print(f'Timeout: {timeout}, Cutoff: {cutoff}, Freq_prune: {freq_prune:.2f}')
print("---------------------------------------")

# ***************************************
# Load and modify ngram data
# ***************************************

# Taken from: http://practicalcryptography.com/media/cryptanalysis/files/ngram_score_1.py
# Load frequency files:
def load(ngramfile, cutoff , sep=' '):
    key_list = list()
    count_list = list()
    with open(ngramfile) as f:
        for line in f:
            key,count = line.split(sep)
            count = int(count)
            if count < cutoff:
                continue
            key_list.append(key)
            count_list.append(count)
    return key_list, count_list

n_gram, count = load("english_monograms.txt", 0)
t1, t2 = load("english_bigrams.txt", cutoff)
n_gram.extend(t1)
count.extend(t2)
t1, t2 = load("english_trigrams.txt", cutoff)
n_gram.extend(t1)
count.extend(t2)
t1, t2 = load("english_quadgrams.txt", cutoff)
n_gram.extend(t1)
count.extend(t2)
t1, t2 = load("english_quintgrams.txt", cutoff)
n_gram.extend(t1)
count.extend(t2)

# We create a dictionary to quickly lookup the index of all n_grams
index_of = {}
total_count_assertion_check = 0
for i in range(len(n_gram)):
    index_of[n_gram[i]] = i
    total_count_assertion_check += count[i]

# Setup for some assertion checking below.
total_removal = 0
total_count = 0
for i in range(26):
    total_count += count[i]

# Remove excess counting.
# Frequency of "H" is 216768975, but the frequency of "TH" is 116997844.
# Notice that "H" is counted multiple times, we want to remove the counts of all k-grams
#   that are used in (k + 1)-grams so that the solver is incentivized to make a layout with
#   more combos. However, note that "H" appears in the 2-grams "TH" and "HE":
#   "H" 216768975 - "TH" 116997844 - "HE" 100689263 = -918132 which is clearly incorrect.
# Finally, even when accounting for this we can still subtract too much, so we add a
#   freq_prune ratio.
# Therefore the adjustment is as follows:
#   i-gram_frequency -= (i + 1)-gram_frequency * (k / (k + 1)) * freq_prune
for i in range(26, len(n_gram)):
    total_count += count[i]
    l = len(n_gram[i])
    a = n_gram[i][1:] # Get all but the first letter.
    if a in index_of:
        a_i = index_of[a]
        assert(a_i < i)
        sub = count[i] * ((l - 1) / l) * freq_prune
        count[a_i] -= sub
        total_removal += sub
        # if a == "TH":
        #     print(f"count: {count[a_i]}, index: {a_i}, sub: {sub}, word: {n_gram[i]}, ratio: {(l - 1) / l}")
    b = n_gram[i][:-1] # Get all but the last letter.
    if b in index_of:
        b_i = index_of[b]
        assert(b_i < i)
        sub = count[i] * ((l - 1) / l) * freq_prune
        count[b_i] -= sub
        total_removal += sub
        # if b == "TH":
        #     print(f"count: {count[b_i]}, index: {b_i}, sub: {sub}, word: {n_gram[i]}, ratio: {(l - 1) / l}")
    # print(f"a: {a}, b: {b}")

# In the above loop count[i] should never be subtracted from before it
#   is added to total_count. This assestion checks this.
assert(total_count == total_count_assertion_check)

for i in range(len(n_gram)):
    # print(f'{n_gram[i]} {count[i]}')
    if count[i] <= 0:
        print("freq_prune is set too high!")
        sys.exit()
print(f"Removed {total_removal * 100 / total_count:.2f}% of frequency count as excess.")

# ***************************************
# Problem Definition and hard constraints
#  -Hard constraints cannot be violated
# ***************************************

# Let the bit-vector represent a button combo with this correspondance:
# Index(LMR) Middle(LMR) Ring(LMR) Pinky(LMR)
#       000         000       000        000
G = [ BitVec('g%s' % i, 12) for i in range(len(n_gram))]

# For any finger the combination (LR) or (LMR) is illegal,
#   because it is too hard to do in practice.
s.add([ Not(And(Extract(11, 11, G[i]) == 1, Extract(9, 9, G[i]) == 1))  for i in range(len(n_gram)) ]) # index_con
s.add([ Not(And(Extract(8 , 8 , G[i]) == 1, Extract(6, 6, G[i]) == 1))  for i in range(len(n_gram)) ]) # middle_con
s.add([ Not(And(Extract(5 , 5 , G[i]) == 1, Extract(3, 3, G[i]) == 1))  for i in range(len(n_gram)) ]) # ring_con
s.add([ Not(And(Extract(2 , 2 , G[i]) == 1, Extract(0, 0, G[i]) == 1))  for i in range(len(n_gram)) ]) # pinky_con

# No two n_grams can have the same combo
#   Exception for 0 which is the null assignment
for i in range(len(n_gram) - 1):
    s.add( [ Or(G[i] == 0, G[i] != G[j]) for j in range(i + 1, len(n_gram)) ] )

# No single characters can have a null assignment.
s.add( [ G[i] != 0 for i in range(26) ] )

# ***************************************
# Design principles as hard constraints
# ***************************************

# Multi-character chords shold be made up of combination of single character chords
# -This is taken from TabSpace philosophy: https://rhodesmill.org/brandon/projects/tabspace-guide.pdf
for i in range(26, len(n_gram)):
    assert len(n_gram[i]) > 1
    # Either
    #   n_gram must be union of letters that make up the n_gram
    # Or
    #   n_gram must have null assignment.
    if len(n_gram[i]) == 2:
        s.add(Or(G[index_of[n_gram[i][0]]] | G[index_of[n_gram[i][1]]] == G[i], G[i] == 0))
    elif len(n_gram[i]) == 3:
        s.add(Or(G[index_of[n_gram[i][0]]] | G[index_of[n_gram[i][1]]] | G[index_of[n_gram[i][2]]] == G[i], G[i] == 0))
    elif len(n_gram[i]) == 4:
        s.add(Or(G[index_of[n_gram[i][0]]] | G[index_of[n_gram[i][1]]] | G[index_of[n_gram[i][2]]] | G[index_of[n_gram[i][3]]] == G[i], G[i] == 0))
    elif len(n_gram[i]) == 5:
        s.add(Or(G[index_of[n_gram[i][0]]] | G[index_of[n_gram[i][1]]] | G[index_of[n_gram[i][2]]] | G[index_of[n_gram[i][3]]] | G[index_of[n_gram[i][4]]] == G[i], G[i] == 0))

# **********************************************
# Cost constraints
#  - Estimate and minimize cost of configuration 
# **********************************************

# Finding the cost of every possible chord is too much work
#   Num_chords > 5^4!
# Instead we approximate the cost of the chord as the most expensive
#   one/two finger press of that cord. Ex: Suppose the chord
#   (LM)0MR, we then pick the most expensive of all two finger
#   presses {(LM)0M0, (LM)00R, 00MR}
# Requires 5*5*6+5*4 = 170 known costs for chords.
# Single finger chords have a one-to-one correspondance with
#   single finger preferences.
# A chord involving more than two fingers cannot be approximated by
#   the cost of a single finger press.

# Raw cost is the cost of entering a n_gram a single time regardless of frequency.
# "Generate Cost Function.xlsx" will generate this.
# Note: Doesn't this giant if-then-else block look ugly? Keep in mind that we are required
#   to express this problem in 1st-order logic for the SMT solver to accept it. The ITE block
#   will be converted to a SAT expression.
# 2nd Note: Unintuitively the masking is faster in this instance then using extract as in
#   the constraint blocking same finger (LR) presses above.
cost = [ Real('rc%s' % i) for i in range(len(n_gram)) ]
null_n_gram_cost = [ Real('nc%s' % i) for i in range(len(n_gram)) ]
s.add( [ cost[i] == \
    If(And(Extract(11, 11, G[i]) == 1, Extract(10, 10, G[i]) == 1),  0.5 / len(n_gram[i]), #  110 000 000 000
    If(And(Extract(10, 10, G[i]) == 1, Extract(9 , 9 , G[i]) == 1),  0.5 / len(n_gram[i]), #  011 000 000 000
    If(And(Extract(8 , 8 , G[i]) == 1, Extract(7 , 7 , G[i]) == 1),  0.5 / len(n_gram[i]), #  000 110 000 000
    If(And(Extract(7 , 7 , G[i]) == 1, Extract(6 , 6 , G[i]) == 1),  0.5 / len(n_gram[i]), #  000 011 000 000
    If(And(Extract(5 , 5 , G[i]) == 1, Extract(4 , 4 , G[i]) == 1),  0.5 / len(n_gram[i]), #  000 000 110 000
    If(And(Extract(4 , 4 , G[i]) == 1, Extract(3 , 3 , G[i]) == 1),  0.5 / len(n_gram[i]), #  000 000 011 000
    If(And(Extract(2 , 2 , G[i]) == 1, Extract(1 , 1 , G[i]) == 1),  0.5 / len(n_gram[i]), #  000 000 000 110
    If(And(Extract(1 , 1 , G[i]) == 1, Extract(0 , 0 , G[i]) == 1),  0.5 / len(n_gram[i]), #  000 000 000 011
    If(Extract(0 , 0 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 000 000 001
    If(Extract(1 , 1 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 000 000 010
    If(Extract(2 , 2 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 000 000 100
    If(Extract(3 , 3 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 000 001 000
    If(Extract(4 , 4 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 000 010 000
    If(Extract(5 , 5 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 000 100 000
    If(Extract(6 , 6 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 001 000 000
    If(Extract(7 , 7 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 010 000 000
    If(Extract(8 , 8 , G[i]) == 1,  0.5 / len(n_gram[i]), #  000 100 000 000
    If(Extract(9 , 9 , G[i]) == 1,  0.5 / len(n_gram[i]), #  001 000 000 000
    If(Extract(10, 10, G[i]) == 1,  0.5 / len(n_gram[i]), #  010 000 000 000
    If(Extract(11, 11, G[i]) == 1,  0.5 / len(n_gram[i]), #  100 000 000 000
    #  This can only be reached if the n-gram has a null assignment (is assigned no chord)
    #   We set it equal to null_n_gram_cost[i], null_n_gram_cost is just a placeholder to 
    #   prevent verbose code.
    null_n_gram_cost[i])))))))))))))))))))) \
        for i in range(len(n_gram)) \
        ] )

# null_n_gram_cost is the cost of entering a n_gram using smaller n_grams
#   For simplicity the cost of a null_n_gram is the cost of all the characters.
#   Feel free to expand this feature
# ********************************
# The no single character can have a null chord so we skip the first 26.
for i in range(26, len(n_gram)):
    assert len(n_gram[i]) > 1
    if len(n_gram[i]) == 2:
        s.add(null_n_gram_cost[i] == cost[index_of[n_gram[i][0]]] + cost[index_of[n_gram[i][1]]])
    elif len(n_gram[i]) == 3:
        s.add(null_n_gram_cost[i] == cost[index_of[n_gram[i][0]]] + cost[index_of[n_gram[i][1]]] + cost[index_of[n_gram[i][2]]])
    elif len(n_gram[i]) == 4:
        s.add(null_n_gram_cost[i] == cost[index_of[n_gram[i][0]]] + cost[index_of[n_gram[i][1]]] + cost[index_of[n_gram[i][2]]] + cost[index_of[n_gram[i][3]]])
    elif len(n_gram[i]) == 5:
        s.add(null_n_gram_cost[i] == cost[index_of[n_gram[i][0]]] + cost[index_of[n_gram[i][1]]] + cost[index_of[n_gram[i][2]]] + cost[index_of[n_gram[i][3]]] + cost[index_of[n_gram[i][4]]])


# cumulative_cost is cost times frequency.
cumulative_cost = [ Real('cc%s' % i) for i in range(len(n_gram)) ]

# This is a round about way of summing up the total cost of the
#   whole problem. Keep in mind that we are limited to 1st-order logic
s.add(cumulative_cost[0] == cost[0] * count[0])
s.add( [ cumulative_cost[i] == cumulative_cost[i-1] + cost[i] * count[i] \
            for i in range(1, len(n_gram)) ] )

# If cost of chords is given in seconds then cumulative_cost[len(n_gram)-1] is
#   the seconds to enter all n-grams k times per n-gram where k is the frequency
#   count of each n-gram.
# We can use this to calculate average characters per second:
# 1 / (cumulative_cost[len(n_gram)-1] / total_count) this simplifies to:
# total_count / cumulative_cost[len(n_gram)-1]
total_count = 0
for x in count:
    total_count += x
count = RealVal(total_count)
chars_per_second = Real("cps")
s.add(chars_per_second == total_count / cumulative_cost[len(n_gram)-1])

# **************************************************
# Sit back relax and let the SMT solver do the work.
# **************************************************

# Timeout is given in milliseconds
s.set("timeout", (timeout.days * 24 * 60 * 60 + timeout.seconds) * 1000)
total_time = datetime.now() - setupTime
print(f"N-Grams: {str(len(n_gram))}, Setup Time: {total_time}")
print("---------------------------------------")

hi_sat = 0
lo_unsat = float("inf")
lo_unknown = float("inf")
m = None
# See comments above in "Guide the Search" for understanding how this works.
while min(lo_unsat, lo_unknown, cps_hi) - max(hi_sat, cps_lo) > cps_res:
    solveTime = datetime.now()

    # We start from cps_lo initially and increment up by initial_step_up
    #   until we encounter an UNSAT or UNKNOWN problem then we begin
    #   binary search.
    if initial_step_up != 0:
        guess_cps = max(hi_sat, cps_lo - initial_step_up) + initial_step_up
    else:
        guess_cps = (min(lo_unsat, lo_unknown, cps_hi) + max(hi_sat, cps_lo)) / 2

    # For some reason the solver cannot handle this constraint:
    #   s.add(chars_per_second >= cps)
    #   So we calclate max cumulative cost and set the limit that way.
    guess_max_cumulative_cost = total_count / guess_cps
    s.push() # Create new state
    s.add(cumulative_cost[len(n_gram)-1] <= guess_max_cumulative_cost)
    
    result = s.check()
    guess_time = datetime.now() - solveTime
    total_time += guess_time
    print(f"CPS: {guess_cps:.4f} - {str(result):7} - {datetime.now() - solveTime}")

    if result == sat:
        hi_sat = guess_cps
        m = s.model()
    elif result == unsat:
        lo_unsat = guess_cps
        initial_step_up = 0
        s.pop() # Restore state (i.e. Remove guess constraint)
                # Only remove guess constraint when it can't be attained, not when sat.
    elif result == unknown:
        lo_unknown = guess_cps
        initial_step_up = 0
        s.pop() # Restore state (i.e. Remove guess constraint)
                # Only remove guess constraint when it can't be attained, not when sat.

    # s.pop() # Restore state (i.e. Remove guess constraint)

print("---------------------------------------")
print(f"Sat: {hi_sat}, Unknown: {lo_unknown}, Unsat: {lo_unsat}")
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
    print(f'|--------------------------------|')

# We generate a dictionary where the chords are the keys and n_grams the values.
num_2 = 0
num_3 = 0
num_4 = 0
num_5 = 0
press_lookup = {}
for i in range(len(n_gram)):
    if m[G[i]] in press_lookup:
        assert m[G[i]] == 0
    else:
        press_lookup[int(str(m[G[i]]))] = n_gram[i]
        if len(n_gram[i]) == 2:
            # print("i: " + str(i) + ", m[G[i]]: " + str(m[G[i]]) + ", n_gram: " + n_gram[i])
            num_2 += 1
        elif len(n_gram[i]) == 3:
            num_3 += 1
        elif len(n_gram[i]) == 4:
            num_4 += 1
        elif len(n_gram[i]) == 5:
            num_5 += 1
        elif len(n_gram[i]) == 1:
            print("i: " + str(i) + ", m[G[i]]: " + str(m[G[i]]) + ", n_gram: " + n_gram[i])
print(f'Chorded-2_grams: {num_2}, 3_grams: {num_3}, 4_grams: {num_4}, 5_grams: {num_5}')

print_config(press_lookup)

# ******************************************************
# TODO: Convert SMT solver output to configuration file.
# ******************************************************