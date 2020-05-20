from dataclasses import dataclass, field
import lib

# Taken from: http://practicalcryptography.com/media/cryptanalysis/files/ngram_score_1.py
# Load frequency files:
def load_files(ngramfile, cutoff , sep=' '):
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

def create_dict(n_grams, count):
    # We create a dictionary to quickly lookup the index of all n_grams
    index = {}
    total_count_assertion_check = 0
    for i in range(len(n_grams)):
        index[n_grams[i]] = i
        total_count_assertion_check += count[i]
    return index, total_count_assertion_check

def prune_excess_counts(p, n_grams, count):
    index, total_count_assertion_check = create_dict(n_grams, count)

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
    #   i-gram_frequency -= (i + 1)-gram_frequency * (k / (k + 1)) * p.freq_prune
    for i in range(26, len(n_grams)):
        total_count += count[i]
        l = len(n_grams[i])
        a = n_grams[i][1:] # Get all but the first letter.
        if a in index:
            a_i = index[a]
            assert(a_i < i)
            sub = count[i] * ((l - 1) / l) * p.freq_prune
            count[a_i] -= sub
            total_removal += sub
            
        b = n_grams[i][:-1] # Get all but the last letter.
        if b in index:
            b_i = index[b]
            assert(b_i < i)
            sub = count[i] * ((l - 1) / l) * p.freq_prune
            count[b_i] -= sub
            total_removal += sub

    # In the above loop count[i] should never be subtracted from before it
    #   is added to total_count. This assestion checks this.
    assert(total_count == total_count_assertion_check)
    assert len(count) == len(n_grams)

    for i in range(len(n_grams)):
        if count[i] <= 0:
            print("freq_prune is set too high!")
            sys.exit()
    print(f"Removed {total_removal * 100 / total_count:.2f}% of frequency count as excess.")

    return index

@dataclass
class NGrams:
    grams: list = field(default_factory=lambda: [])
    count: list = field(default_factory=lambda: [])
    index: dict = field(default_factory=lambda : {})

    def load_n_grams(p):
        n_grams, count = load_files(p.alphabet_file, 0)
        t1, t2 = load_files(p.bigrams_file, p.cutoff)
        n_grams.extend(t1)
        count.extend(t2)
        for file in p.other_freq_files:
            t1, t2 = load_files(file, p.cutoff)
            n_grams.extend(t1)
            count.extend(t2)
        assert len(count) == len(n_grams)

        index = prune_excess_counts(p, n_grams, count)
        return NGrams(grams=n_grams, count=count, index=index)