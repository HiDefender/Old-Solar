from z3 import Or

# ***************************************
# Design principles as hard constraints
# ***************************************

# Multi-character chords shold be made up of combination of single character chords
# -This is taken from TabSpace philosophy: https://rhodesmill.org/brandon/projects/tabspace-guide.pdf
def mcc_from_scc(s, n, b):
    for i in range(n.alphabet_size, len(n.grams)):
        assert len(n.grams[i]) > 1
        # Either
        #   n_gram must be union of letters that make up the n_gram
        # Or
        #   n_gram must have null assignment.
        if len(n.grams[i]) == 2:
            s.add(Or(b.G[n.index[n.grams[i][0]]] | b.G[n.index[n.grams[i][1]]] == b.G[i], b.G[i] == 0))
        elif len(n.grams[i]) == 3:
            s.add(Or(b.G[n.index[n.grams[i][0]]] | b.G[n.index[n.grams[i][1]]] |
                b.G[n.index[n.grams[i][2]]] == b.G[i], b.G[i] == 0))
        elif len(n.grams[i]) == 4:
            s.add(Or(b.G[n.index[n.grams[i][0]]] | b.G[n.index[n.grams[i][1]]] |
                b.G[n.index[n.grams[i][2]]] | b.G[n.index[n.grams[i][3]]] == b.G[i], b.G[i] == 0))
        elif len(n.grams[i]) == 5:
            s.add(Or(b.G[n.index[n.grams[i][0]]] | b.G[n.index[n.grams[i][1]]] |
                b.G[n.index[n.grams[i][2]]] | b.G[n.index[n.grams[i][3]]] |
                b.G[n.index[n.grams[i][4]]] == b.G[i], b.G[i] == 0))


# Force all, but most frequent contradicting n-grams to null assignment.
# Suppose two n-grams share the same letters.
#   Ex: "HE" and "EH", with freqs 100689263 and 7559141 respectively.
#   Both cannot be assigned, so force the less frequent one to NULL.
#   Note we don't remove the less frequent one, because it's frequency will effect single-character-chord placement.
def handle_conflicting_n_grams(s, n, b):
    print("Stub, this should only speed up the solver not alter it's output. Do if too slow.")