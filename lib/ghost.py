from z3 import *
import lib

# Twiddler BitVector Index                                                      # Twiddler BitVector Index                                                      # Twiddler BitVector Index                                                      # Twiddler BitVector Index
#   L   M   R                                                                   #   L   M   R                                                                   #   L   M   R                                                                   #   L   M   R             
#   11  10  9 - Index                                                           #   11  10  9 - Index                                                           #   11  10  9 - Index                                                           #   11  10  9 - Index     
#   8   7   6 - Middle                                                          #   8   7   6 - Middle                                                          #   8   7   6 - Middle                                                          #   8   7   6 - Middle    
#   5   4   3 - Ring                                                            #   5   4   3 - Ring                                                            #   5   4   3 - Ring                                                            #   5   4   3 - Ring      
#   2   1   0 - Pinky                                                           #   2   1   0 - Pinky                                                           #   2   1   0 - Pinky                                                           #   2   1   0 - Pinky     

# These combos ghost on Twiddler 3, because the hardware wasn't designed to
#   use mupltiple buttons per row.
def ghost_combos(s, n, b):
    # Probably unnecessary constraint.
    # s.add([ Not(And(Extract(10, 10, b.G[i]) == 1, Extract(6, 6, b.G[i]) == 1, Extract(1, 1, b.G[i]) == 1), Extract(0, 0, b.G[i]) == 1)  for i in range(len(n.grams)) ]) # MR0(RM)

    for i in range(len(n.grams)):
        s.add(Or(Or(Extract(11, 11, b.G[i]) == 0, Extract(10, 10, b.G[i]) == 0), And(Extract(11, 11, b.G[i]) == 1, Extract(10, 10, b.G[i]) == 1, Extract( 8,  8, b.G[i]) == 0, Extract( 7,  7, b.G[i]) == 0,    Extract(5, 5, b.G[i]) == 0, Extract(4, 4, b.G[i]) == 0,    Extract(2, 2, b.G[i]) == 0, Extract(1, 1, b.G[i]) == 0)))
        s.add(Or(Or(Extract(10, 10, b.G[i]) == 0, Extract( 9,  9, b.G[i]) == 0), And(Extract(10, 10, b.G[i]) == 1, Extract( 9,  9, b.G[i]) == 1, Extract( 7,  7, b.G[i]) == 0, Extract( 6,  6, b.G[i]) == 0,    Extract(4, 4, b.G[i]) == 0, Extract(3, 3, b.G[i]) == 0,    Extract(1, 1, b.G[i]) == 0, Extract(0, 0, b.G[i]) == 0)))
        s.add(Or(Or(Extract( 8,  8, b.G[i]) == 0, Extract( 7,  7, b.G[i]) == 0), And(Extract( 8,  8, b.G[i]) == 1, Extract( 7,  7, b.G[i]) == 1, Extract(11, 11, b.G[i]) == 0, Extract(10, 10, b.G[i]) == 0,    Extract(5, 5, b.G[i]) == 0, Extract(4, 4, b.G[i]) == 0,    Extract(2, 2, b.G[i]) == 0, Extract(1, 1, b.G[i]) == 0)))
        s.add(Or(Or(Extract( 7,  7, b.G[i]) == 0, Extract( 6,  6, b.G[i]) == 0), And(Extract( 7,  7, b.G[i]) == 1, Extract( 6,  6, b.G[i]) == 1, Extract(10, 10, b.G[i]) == 0, Extract( 9,  9, b.G[i]) == 0,    Extract(4, 4, b.G[i]) == 0, Extract(3, 3, b.G[i]) == 0,    Extract(1, 1, b.G[i]) == 0, Extract(0, 0, b.G[i]) == 0)))
        s.add(Or(Or(Extract( 5,  5, b.G[i]) == 0, Extract( 4,  4, b.G[i]) == 0), And(Extract( 5,  5, b.G[i]) == 1, Extract( 4,  4, b.G[i]) == 1, Extract(11, 11, b.G[i]) == 0, Extract(10, 10, b.G[i]) == 0,    Extract(8, 8, b.G[i]) == 0, Extract(7, 7, b.G[i]) == 0,    Extract(2, 2, b.G[i]) == 0, Extract(1, 1, b.G[i]) == 0)))
        s.add(Or(Or(Extract( 4,  4, b.G[i]) == 0, Extract( 3,  3, b.G[i]) == 0), And(Extract( 4,  4, b.G[i]) == 1, Extract( 3,  3, b.G[i]) == 1, Extract(10, 10, b.G[i]) == 0, Extract( 9,  9, b.G[i]) == 0,    Extract(7, 7, b.G[i]) == 0, Extract(6, 6, b.G[i]) == 0,    Extract(1, 1, b.G[i]) == 0, Extract(0, 0, b.G[i]) == 0)))
        s.add(Or(Or(Extract( 2,  2, b.G[i]) == 0, Extract( 1,  1, b.G[i]) == 0), And(Extract( 2,  2, b.G[i]) == 1, Extract( 1,  1, b.G[i]) == 1, Extract(11, 11, b.G[i]) == 0, Extract(10, 10, b.G[i]) == 0,    Extract(8, 8, b.G[i]) == 0, Extract(7, 7, b.G[i]) == 0,    Extract(5, 5, b.G[i]) == 0, Extract(4, 4, b.G[i]) == 0)))
        s.add(Or(Or(Extract( 1,  1, b.G[i]) == 0, Extract( 0,  0, b.G[i]) == 0), And(Extract( 1,  1, b.G[i]) == 1, Extract( 0,  0, b.G[i]) == 1, Extract(10, 10, b.G[i]) == 0, Extract( 9,  9, b.G[i]) == 0,    Extract(7, 7, b.G[i]) == 0, Extract(6, 6, b.G[i]) == 0,    Extract(4, 4, b.G[i]) == 0, Extract(3, 3, b.G[i]) == 0)))

        # s.add(If(And(Extract(11, 11, b.G[i] == 1), Extract(10, 10, b.G[i] == 1)), And(Extract( 8,  8, b.G[i] == 0), Extract( 7,  7, b.G[i] == 0),    Extract(5, 5, b.G[i] == 0), Extract(4, 4, b.G[i] == 0),    Extract(2, 2, b.G[i] == 0), Extract(1, 1, b.G[i] == 0)), True))
        # s.add(If(And(Extract(10, 10, b.G[i] == 1), Extract( 9,  9, b.G[i] == 1)), And(Extract( 7,  7, b.G[i] == 0), Extract( 6,  6, b.G[i] == 0),    Extract(4, 4, b.G[i] == 0), Extract(3, 3, b.G[i] == 0),    Extract(1, 1, b.G[i] == 0), Extract(0, 0, b.G[i] == 0)), True))
        # s.add(If(And(Extract( 8,  8, b.G[i] == 1), Extract( 7,  7, b.G[i] == 1)), And(Extract(11, 11, b.G[i] == 0), Extract(10, 10, b.G[i] == 0),    Extract(5, 5, b.G[i] == 0), Extract(4, 4, b.G[i] == 0),    Extract(2, 2, b.G[i] == 0), Extract(1, 1, b.G[i] == 0)), True))
        # s.add(If(And(Extract( 7,  7, b.G[i] == 1), Extract( 6,  6, b.G[i] == 1)), And(Extract(10, 10, b.G[i] == 0), Extract( 9,  9, b.G[i] == 0),    Extract(4, 4, b.G[i] == 0), Extract(3, 3, b.G[i] == 0),    Extract(1, 1, b.G[i] == 0), Extract(0, 0, b.G[i] == 0)), True))
        # s.add(If(And(Extract( 5,  5, b.G[i] == 1), Extract( 4,  4, b.G[i] == 1)), And(Extract(11, 11, b.G[i] == 0), Extract(10, 10, b.G[i] == 0),    Extract(8, 8, b.G[i] == 0), Extract(7, 7, b.G[i] == 0),    Extract(2, 2, b.G[i] == 0), Extract(1, 1, b.G[i] == 0)), True))
        # s.add(If(And(Extract( 4,  4, b.G[i] == 1), Extract( 3,  3, b.G[i] == 1)), And(Extract(10, 10, b.G[i] == 0), Extract( 9,  9, b.G[i] == 0),    Extract(7, 7, b.G[i] == 0), Extract(6, 6, b.G[i] == 0),    Extract(1, 1, b.G[i] == 0), Extract(0, 0, b.G[i] == 0)), True))
        # s.add(If(And(Extract( 2,  2, b.G[i] == 1), Extract( 1,  1, b.G[i] == 1)), And(Extract(11, 11, b.G[i] == 0), Extract(10, 10, b.G[i] == 0),    Extract(8, 8, b.G[i] == 0), Extract(7, 7, b.G[i] == 0),    Extract(5, 5, b.G[i] == 0), Extract(4, 4, b.G[i] == 0)), True))
        # s.add(If(And(Extract( 1,  1, b.G[i] == 1), Extract( 0,  0, b.G[i] == 1)), And(Extract(10, 10, b.G[i] == 0), Extract( 9,  9, b.G[i] == 0),    Extract(7, 7, b.G[i] == 0), Extract(6, 6, b.G[i] == 0),    Extract(4, 4, b.G[i] == 0), Extract(3, 3, b.G[i] == 0)), True))

# Possible Multiple Button per Row Combinations.
# (ML)ROO
# (ML)ORO
# (ML)OOR
# (RM)LOO
# (RM)OLO
# (RM)OOL
# R(ML)OO
# O(ML)RO
# O(ML)OR
# L(RM)OO
# O(RM)LO
# O(RM)OL
# RO(ML)O
# OR(ML)O
# OO(ML)R
# LO(RM)O
# OL(RM)O
# OO(RM)L
# ROO(ML)
# ORO(ML)
# OOR(ML)
# LOO(RM)
# OLO(RM)
# OOL(RM)