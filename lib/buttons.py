from z3 import *
from dataclasses import dataclass, field
import lib

@dataclass
class Buttons:
    G: list = field(default_factory=lambda: [])
    F: list = field(default_factory=lambda: [])
    cost: list = field(default_factory=lambda: [])
    stride_cost: list = field(default_factory=lambda: [])
    cum_stride_cost: list = field(default_factory=lambda: [])
    cumulative_cost: list = field(default_factory=lambda: [])
    bi_count: list = field(default_factory=lambda: [])

# ***************************************
# Problem Definition and hard constraints
#  -Hard constraints cannot be violated
# ***************************************
def problem_def(s, n):
    # Let the bit-vector represent a button combo with this correspondance:
    # Index(LMR) Middle(LMR) Ring(LMR) Pinky(LMR)
    #       000         000       000        000
    G = [ BitVec('g%s' % i, 12) for i in range(len(n.grams))]

    # For any finger the combination (LR) or (LMR) is illegal,
    #   because it is too hard to do in practice.
    s.add([ Not(And(Extract(11, 11, G[i]) == 1, Extract(9, 9, G[i]) == 1))  for i in range(len(n.grams)) ]) # index_con
    s.add([ Not(And(Extract(8 , 8 , G[i]) == 1, Extract(6, 6, G[i]) == 1))  for i in range(len(n.grams)) ]) # middle_con
    s.add([ Not(And(Extract(5 , 5 , G[i]) == 1, Extract(3, 3, G[i]) == 1))  for i in range(len(n.grams)) ]) # ring_con
    s.add([ Not(And(Extract(2 , 2 , G[i]) == 1, Extract(0, 0, G[i]) == 1))  for i in range(len(n.grams)) ]) # pinky_con

    # No two n_grams can have the same combo
    #   Exception for 0 which is the null assignment
    for i in range(len(n.grams) - 1):
        s.add( [ Or(G[i] == 0, G[i] != G[j]) for j in range(i + 1, len(n.grams)) ] )

    # No single characters can have a null assignment.
    s.add( [ G[i] != 0 for i in range(n.alphabet_size) ] )

    # Let the bit-vector represent finger use with this correspondance:
    # Index(---) Middle(---) Ring(---) Pinky(---)
    #       000         000       000        000
    F = [ BitVec('f%s' % i, 12) for i in range(len(n.grams))]

    # If a finger is used then the entire triplet of bits is 1, else entire triplet is 0.
    s.add([ Extract(11, 11, F[i]) == Extract(10, 10, F[i])  for i in range(len(n.grams)) ]) # index_con
    s.add([ Extract(11, 11, F[i]) == Extract(9, 9, F[i])    for i in range(len(n.grams)) ]) # index_con

    s.add([ Extract(8,  8,  F[i]) == Extract(7,  7,  F[i])  for i in range(len(n.grams)) ]) # middle_con
    s.add([ Extract(8,  8,  F[i]) == Extract(6,  6,  F[i])  for i in range(len(n.grams)) ]) # middle_con
    
    s.add([ Extract(5,  5,  F[i]) == Extract(4,  4,  F[i])  for i in range(len(n.grams)) ]) # ring_con
    s.add([ Extract(5,  5,  F[i]) == Extract(3,  3,  F[i])  for i in range(len(n.grams)) ]) # ring_con
    
    s.add([ Extract(2,  2,  F[i]) == Extract(1,  1,  F[i])  for i in range(len(n.grams)) ]) # pinky_con
    s.add([ Extract(2,  2,  F[i]) == Extract(0,  0,  F[i])  for i in range(len(n.grams)) ]) # pinky_con

    # If a single button from that finger is used then the finger is used.
    s.add([ Or(
                And(    Extract(9, 9, F[i]) == 1,       Or(Extract(11, 11, G[i]) == 1, Extract(10, 10, G[i]) == 1, Extract(9, 9, G[i]) == 1)),
                And(Not(Extract(9, 9, F[i]) == 1),  Not(Or(Extract(11, 11, G[i]) == 1, Extract(10, 10, G[i]) == 1, Extract(9, 9, G[i]) == 1))),
            )  for i in range(len(n.grams)) ]) # index_con
    s.add([ Or(
                And(    Extract(6, 6, F[i]) == 1,       Or(Extract(8,  8,  G[i]) == 1, Extract(7,  7,  G[i]) == 1, Extract(6, 6, G[i]) == 1)),
                And(Not(Extract(6, 6, F[i]) == 1),  Not(Or(Extract(8,  8,  G[i]) == 1, Extract(7,  7,  G[i]) == 1, Extract(6, 6, G[i]) == 1))),
            )  for i in range(len(n.grams)) ]) # middle_con
    s.add([ Or(
                And(    Extract(3, 3, F[i]) == 1,       Or(Extract(5,  5,  G[i]) == 1, Extract(4,  4,  G[i]) == 1, Extract(3, 3, G[i]) == 1)),
                And(Not(Extract(3, 3, F[i]) == 1),  Not(Or(Extract(5,  5,  G[i]) == 1, Extract(4,  4,  G[i]) == 1, Extract(3, 3, G[i]) == 1))),
            )  for i in range(len(n.grams)) ]) # ring_con
    s.add([ Or(
                And(    Extract(0, 0, F[i]) == 1,       Or(Extract(2,  2,  G[i]) == 1, Extract(1,  1,  G[i]) == 1, Extract(0, 0, G[i]) == 1)),
                And(Not(Extract(0, 0, F[i]) == 1),  Not(Or(Extract(2,  2,  G[i]) == 1, Extract(1,  1,  G[i]) == 1, Extract(0, 0, G[i]) == 1))),
            )  for i in range(len(n.grams)) ]) # pinky_con

    cost = [ Real('rc%s' % i) for i in range(len(n.grams)) ]

#************ Cumulative Cost not used in stride version****************
    # # cumulative_cost is cost times frequency.
    # cumulative_cost = [ Real('cc%s' % i) for i in range(len(n.grams)) ]
    # print(f"cum_cost_len: {len(cumulative_cost)} n_gram_len: {len(n.grams)}")
    # # This is a round about way of summing up the total cost of the
    # #   whole problem. Keep in mind that we are limited to 1st-order logic
    # s.add(cumulative_cost[0] == cost[0] * n.count[0])
    # s.add( [ cumulative_cost[i] == cumulative_cost[i-1] + cost[i] * n.count[i] \
    #             for i in range(1, len(n.grams)) ] )

    return Buttons(G=G, F=F, cost=cost, cumulative_cost=cumulative_cost)

def cost_scc(p, s, n, b):

    bi_grams, bi_count = lib.load_files(p.bigrams_file, 0)
    stride_cost = [ Real('sc%s' % i) for i in range(len(bi_grams)) ]
    n.bi_gram_size = len(bi_grams)

    for i in range(len(bi_grams)):
        assert len(bi_grams[i]) == 2
        # print(f"bigram: {bi_grams[i]}, {bi_grams[i][0:1]}:{bi_grams[i][1:]}")
        first_char = n.index[bi_grams[i][0:1]]
        sec_char = n.index[bi_grams[i][1:]]
        assert first_char < n.alphabet_size and sec_char < n.alphabet_size
        s.add( stride_cost[i] == \
                If(b.F[first_char] & b.F[sec_char] == 0, p.stride, # Stride discount
                If(b.F[first_char] & b.G[sec_char] == b.G[first_char] & b.F[sec_char], p.stutter, # Stutter discount
                1.0)) * # No stride or stutter discount
                (b.cost[first_char] + b.cost[sec_char]) * bi_count[i]
            )
    
    cum_stride_cost = [ Real('csc%s' % i) for i in range(len(bi_grams)) ]
    # This is a round about way of summing up the total cost of the
    #   whole problem. Keep in mind that we are limited to 1st-order logic
    s.add(cum_stride_cost[0] == stride_cost[0])
    s.add( [ cum_stride_cost[i] == cum_stride_cost[i-1] + stride_cost[i] \
                for i in range(1, len(bi_grams)) ] )

    b.stride_cost = stride_cost
    b.cum_stride_cost = cum_stride_cost
    b.bi_count = bi_count

def cost_mcc(s, n, b):
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

    # null_n_gram_cost = [ Real('nc%s' % i) for i in range(len(n.grams)) ]
    for i in range(len(n.grams)):
        if len(n.grams[i]) == 1:
            null_assignment = 100000 # Single characters cannot have a null assignment.
        elif len(n.grams[i]) == 2:
            null_assignment = b.cost[n.index[n.grams[i][0]]] + b.cost[n.index[n.grams[i][1]]]
        elif len(n.grams[i]) == 3:
            null_assignment = b.cost[n.index[n.grams[i][0]]] + b.cost[n.index[n.grams[i][1]]] + \
                                b.cost[n.index[n.grams[i][2]]]
        elif len(n.grams[i]) == 4:
            null_assignment = b.cost[n.index[n.grams[i][0]]] + b.cost[n.index[n.grams[i][1]]] + \
                                b.cost[n.index[n.grams[i][2]]] + b.cost[n.index[n.grams[i][3]]]
        elif len(n.grams[i]) == 5:
            null_assignment = b.cost[n.index[n.grams[i][0]]] + b.cost[n.index[n.grams[i][1]]] + \
                                b.cost[n.index[n.grams[i][2]]] + b.cost[n.index[n.grams[i][3]]] + \
                                b.cost[n.index[n.grams[i][4]]]
        else:
            assert(2 + 2 == 5) # Model isn't programmed to handle 6_grams or larger.

        s.add( b.cost[i] == \
            If(And(Extract(4, 4, b.G[i]) == 1, Extract(3, 3, b.G[i]) == 1),  1.53846153846154 / len(n.grams[i]), #  000 000 011 000
            If(And(Extract(5, 5, b.G[i]) == 1, Extract(4, 4, b.G[i]) == 1),  1.53846153846154 / len(n.grams[i]), #  000 000 110 000
            If(And(Extract(1, 1, b.G[i]) == 1, Extract(0, 0, b.G[i]) == 1),  1.53846153846154 / len(n.grams[i]), #  000 000 000 011
            If(And(Extract(2, 2, b.G[i]) == 1, Extract(1, 1, b.G[i]) == 1),  1.53846153846154 / len(n.grams[i]), #  000 000 000 110
            If(And(Extract(11, 11, b.G[i]) == 1, Extract(10, 10, b.G[i]) == 1),  1.27659574468085 / len(n.grams[i]), #  110 000 000 000
            If(And(Extract(8, 8, b.G[i]) == 1, Extract(7, 7, b.G[i]) == 1),  1.2 / len(n.grams[i]), #  000 110 000 000
            If(And(Extract(7, 7, b.G[i]) == 1, Extract(6, 6, b.G[i]) == 1),  1.11111111111111 / len(n.grams[i]), #  000 011 000 000
            If(And(Extract(10, 10, b.G[i]) == 1, Extract(9, 9, b.G[i]) == 1),  1.09090909090909 / len(n.grams[i]), #  011 000 000 000
            If(Extract(2, 2, b.G[i]) == 1,  0.689655172413793 / len(n.grams[i]), #  000 000 000 100
            If(Extract(5, 5, b.G[i]) == 1,  0.674157303370786 / len(n.grams[i]), #  000 000 100 000
            If(Extract(0, 0, b.G[i]) == 1,  0.625 / len(n.grams[i]), #  000 000 000 001
            If(Extract(3, 3, b.G[i]) == 1,  0.594059405940594 / len(n.grams[i]), #  000 000 001 000
            If(Extract(9, 9, b.G[i]) == 1,  0.560747663551402 / len(n.grams[i]), #  001 000 000 000
            If(Extract(1, 1, b.G[i]) == 1,  0.538116591928251 / len(n.grams[i]), #  000 000 000 010
            If(Extract(11, 11, b.G[i]) == 1,  0.530973451327434 / len(n.grams[i]), #  100 000 000 000
            If(Extract(8, 8, b.G[i]) == 1,  0.530973451327434 / len(n.grams[i]), #  000 100 000 000
            If(Extract(6, 6, b.G[i]) == 1,  0.521739130434783 / len(n.grams[i]), #  000 001 000 000
            If(Extract(7, 7, b.G[i]) == 1,  0.470588235294118 / len(n.grams[i]), #  000 010 000 000
            If(Extract(4, 4, b.G[i]) == 1,  0.465116279069767 / len(n.grams[i]), #  000 000 010 000
            If(Extract(10, 10, b.G[i]) == 1,  0.452830188679245 / len(n.grams[i]), #  010 000 000 000

            #  This can only be reached if the n-gram has a null assignment (is assigned no chord)
            #   We set it equal to null_n_gram_cost[i], null_n_gram_cost is just a placeholder to 
            #   prevent verbose code.
            null_assignment)))))))))))))))))))))