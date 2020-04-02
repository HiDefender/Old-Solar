from z3 import *
from datetime import datetime, timedelta

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
print("12 buttons limited to 15 chars expanded form.")
cps_hi = 5.0
cps_lo = 1.0
cps_res = 0.01
# The number of miliseconds the solver should spend on any single iteration.
#   Higher is better and slower.
timeout = timedelta(minutes=15)
# Ignores all n_grams (except single alphabet characters) with a frequency below the cutoff.
#   Lower is better and slower.
cutoff = 8000000

print(f'Hi: {cps_hi}, Lo: {cps_lo}, Resolution: {cps_res}')
print(f'Timeout: {timeout}, Cutoff: {cutoff}')
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
for i in range(len(n_gram)):
    index_of[n_gram[i]] = i

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
# Time Saving Heuristics
#  - Help the solver by adding constaints.
#  - Note this may yield a worse configuration,
#     so be sure to only add sensible constraints
# **********************************************

# We force that one of the 15 most frequent alphabet characters are assigned to each of the 12 buttons.
# for button in range(12):
#     res = True
#     for i in range(15):
#         res = Or(res, G[i] == 2**button)
#     s.add(res)
#     print(res)

s.add(Or(G[0] == 1, G[1] == 1, G[2] == 1, G[3] == 1, G[4] == 1, G[5] == 1, G[6] == 1, G[7] == 1, G[8] == 1, G[9] == 1, G[10] == 1, G[11] == 1, G[12] == 1, G[13] == 1, G[14] == 1))
s.add(Or(G[0] == 2, G[1] == 2, G[2] == 2, G[3] == 2, G[4] == 2, G[5] == 2, G[6] == 2, G[7] == 2, G[8] == 2, G[9] == 2, G[10] == 2, G[11] == 2, G[12] == 2, G[13] == 2, G[14] == 2))
s.add(Or(G[0] == 4, G[1] == 4, G[2] == 4, G[3] == 4, G[4] == 4, G[5] == 4, G[6] == 4, G[7] == 4, G[8] == 4, G[9] == 4, G[10] == 4, G[11] == 4, G[12] == 4, G[13] == 4, G[14] == 4))
s.add(Or(G[0] == 8, G[1] == 8, G[2] == 8, G[3] == 8, G[4] == 8, G[5] == 8, G[6] == 8, G[7] == 8, G[8] == 8, G[9] == 8, G[10] == 8, G[11] == 8, G[12] == 8, G[13] == 8, G[14] == 8))
s.add(Or(G[0] == 16, G[1] == 16, G[2] == 16, G[3] == 16, G[4] == 16, G[5] == 16, G[6] == 16, G[7] == 16, G[8] == 16, G[9] == 16, G[10] == 16, G[11] == 16, G[12] == 16, G[13] == 16, G[14] == 16))
s.add(Or(G[0] == 32, G[1] == 32, G[2] == 32, G[3] == 32, G[4] == 32, G[5] == 32, G[6] == 32, G[7] == 32, G[8] == 32, G[9] == 32, G[10] == 32, G[11] == 32, G[12] == 32, G[13] == 32, G[14] == 32))
s.add(Or(G[0] == 64, G[1] == 64, G[2] == 64, G[3] == 64, G[4] == 64, G[5] == 64, G[6] == 64, G[7] == 64, G[8] == 64, G[9] == 64, G[10] == 64, G[11] == 64, G[12] == 64, G[13] == 64, G[14] == 64))
s.add(Or(G[0] == 128, G[1] == 128, G[2] == 128, G[3] == 128, G[4] == 128, G[5] == 128, G[6] == 128, G[7] == 128, G[8] == 128, G[9] == 128, G[10] == 128, G[11] == 128, G[12] == 128, G[13] == 128, G[14] == 128))
s.add(Or(G[0] == 256, G[1] == 256, G[2] == 256, G[3] == 256, G[4] == 256, G[5] == 256, G[6] == 256, G[7] == 256, G[8] == 256, G[9] == 256, G[10] == 256, G[11] == 256, G[12] == 256, G[13] == 256, G[14] == 256))
s.add(Or(G[0] == 512, G[1] == 512, G[2] == 512, G[3] == 512, G[4] == 512, G[5] == 512, G[6] == 512, G[7] == 512, G[8] == 512, G[9] == 512, G[10] == 512, G[11] == 512, G[12] == 512, G[13] == 512, G[14] == 512))
s.add(Or(G[0] == 1024, G[1] == 1024, G[2] == 1024, G[3] == 1024, G[4] == 1024, G[5] == 1024, G[6] == 1024, G[7] == 1024, G[8] == 1024, G[9] == 1024, G[10] == 1024, G[11] == 1024, G[12] == 1024, G[13] == 1024, G[14] == 1024))
s.add(Or(G[0] == 2048, G[1] == 2048, G[2] == 2048, G[3] == 2048, G[4] == 2048, G[5] == 2048, G[6] == 2048, G[7] == 2048, G[8] == 2048, G[9] == 2048, G[10] == 2048, G[11] == 2048, G[12] == 2048, G[13] == 2048, G[14] == 2048))

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
while min(lo_unsat, lo_unknown, cps_hi) - max(hi_sat, cps_lo) > cps_res:
    solveTime = datetime.now()
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
        s.pop() # Restore state (i.e. Remove guess constraint)
                # Only remove guess constraint when it can't be attained, not when sat.
    elif result == unknown:
        lo_unknown = guess_cps
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