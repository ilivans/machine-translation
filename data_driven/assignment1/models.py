from collections import defaultdict, Counter

import numpy as np
from scipy import stats as sps
from nltk.stem import SnowballStemmer
stemmer_eng = SnowballStemmer("english")

# Models for word alignment

class TranslationModel:
    "Models conditional distribution over trg words given a src word."

    def __init__(self, src_corpus, trg_corpus):
        self._src_trg_counts = defaultdict(lambda : {}) # Statistics
        self._trg_given_src_probs = {} # Parameters
        # self._src_mapping = TranslationModel.build_mapping(src_corpus)

    @staticmethod
    def build_mapping(corpus):
        counts_dict = Counter()
        for tokens in corpus:
            counts_dict.update(tokens)
        tokens, counts = zip(*sorted(counts_dict.items()))

        mapping = {}
        count_treshold = 1
        min_token_len = 4
        cur_index = 0
        num_tokens = len(tokens)
        while cur_index < num_tokens:
            cur_token = tokens[cur_index]
            cur_count = counts[cur_index]
            if cur_count >= count_treshold:
                mapping[cur_token] = cur_token
                cur_index += 1
                continue

            left_index = cur_index
            right_index = cur_index + 1
            prefix = cur_token
            prefix_count = cur_count
            for prefix_len in range(len(cur_token), min_token_len - 1, -1):
                prefix = cur_token[:prefix_len]
                for neigh_index in xrange(left_index, -1, -1):
                    neigh_token = tokens[neigh_index]
                    if neigh_token.startswith(prefix):
                        prefix_count += counts[neigh_index]
                        if neigh_index == 0:
                            left_index = neigh_index
                    else:
                        left_index = neigh_index + 1
                        break
                for neigh_index in xrange(right_index, num_tokens):
                    neigh_token = tokens[neigh_index]
                    if neigh_token.startswith(prefix):
                        prefix_count += counts[neigh_index]
                        if neigh_index == num_tokens - 1:
                            right_index = num_tokens
                    else:
                        right_index = neigh_index
                        break
                if prefix_count < count_treshold:
                    continue

            for neigh_token in tokens[left_index:right_index]:
                mapping[neigh_token] = prefix
            cur_index = right_index

        return mapping

    def get_conditional_prob(self, src_token, trg_token):
        "Return the conditional probability of trg_token given src_token."
        # src_token = self._src_mapping[src_token]
        if self._trg_given_src_probs == {}:
            return 1.0
        return self._trg_given_src_probs[src_token][trg_token]

    def collect_statistics(self, src_tokens, trg_tokens, posterior_matrix):
        "Accumulate fractional alignment counts from posterior_matrix."
        assert len(posterior_matrix) == len(trg_tokens)
        for posterior in posterior_matrix:
            assert len(posterior) == len(src_tokens)

        # src_tokens = [self._src_mapping[token] for token in src_tokens]

        for trg_token, posterior_probs in zip(trg_tokens, posterior_matrix):
            for src_token, posterior_prob in zip(src_tokens, posterior_probs):
                self._src_trg_counts[src_token][trg_token] = self._src_trg_counts[src_token].get(trg_token, 0.0) + posterior_prob

    def recompute_parameters(self):
        "Reestimate parameters from counts then reset counters"
        for src_token, trg_counts in self._src_trg_counts.iteritems():
            trgs_count_total = sum(trg_counts.itervalues())
            self._trg_given_src_probs[src_token] = {}
            for trg_token, trg_count in trg_counts.iteritems():
                self._trg_given_src_probs[src_token][trg_token] = trg_count / trgs_count_total
        self._src_trg_counts = defaultdict(lambda: {})


class PriorModel:
    "Models the prior probability of an alignment given only the sentence lengths and token indices."

    def __init__(self, src_corpus, trg_corpus):
        "Add counters and parameters here for more sophisticated models."
        self._distance_counts = {}
        self._distance_probs = {}
        self._beta_coef = 5.
        self._rv = sps.beta(1., self._beta_coef)
        self._pdf = [self._rv.pdf(r) / self._beta_coef for r in np.linspace(0, 1, 50)]

    def get_prior_prob(self, src_index, trg_index, src_length, trg_length):
        distance = abs(trg_index - src_index)
        return self._pdf[int(float(distance) / max(src_length, trg_length) * 50)]

    def collect_statistics(self, src_length, trg_length, posterior_matrix):
        "Extract the necessary statistics from this matrix if needed."
        pass

    def recompute_parameters(self):
        "Reestimate the parameters and reset counters."
        pass