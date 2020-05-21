from z3 import BitVec, Not, And, Extract, Or
from dataclasses import dataclass, field

@dataclass
class Twiddler
    G: list = field(default_factory=lambda: [])

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

    return Twiddler(G=G)