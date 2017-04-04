"""
Models for word alignment
"""
from collections import defaultdict

import numpy as np
from scipy import stats as sps


class TranslationModel:
    """
    Models conditional distribution over trg words given a src word.
    """

    def __init__(self, src_corpus, trg_corpus):
        self._src_trg_counts = defaultdict(lambda : {}) # Statistics
        self._trg_given_src_probs = {} # Parameters

    def get_conditional_prob(self, src_token, trg_token):
        """Return the conditional probability of trg_token given src_token."""
        if self._trg_given_src_probs == {}:
            return 1.0
        return self._trg_given_src_probs[src_token][trg_token]

    def collect_statistics(self, src_tokens, trg_tokens, posterior_matrix):
        """Accumulate fractional alignment counts from posterior_matrix."""
        assert len(posterior_matrix) == len(trg_tokens)
        for posterior in posterior_matrix:
            assert len(posterior) == len(src_tokens)

        for trg_token, posterior_probs in zip(trg_tokens, posterior_matrix):
            for src_token, posterior_prob in zip(src_tokens, posterior_probs):
                self._src_trg_counts[src_token][trg_token] = self._src_trg_counts[src_token].get(trg_token, 0.0) + posterior_prob

    def recompute_parameters(self):
        """Reestimate parameters from counts then reset counters"""
        for src_token, trg_counts in self._src_trg_counts.iteritems():
            trgs_count_total = sum(trg_counts.itervalues())
            self._trg_given_src_probs[src_token] = {}
            for trg_token, trg_count in trg_counts.iteritems():
                self._trg_given_src_probs[src_token][trg_token] = trg_count / trgs_count_total
        self._src_trg_counts = defaultdict(lambda: {})


class PriorModel:
    """
    Models the prior probability of an alignment given only the sentence lengths and token indices.
    """

    def __init__(self, src_corpus, trg_corpus):
        """Add counters and parameters here for more sophisticated models."""
        self._distance_counts = {}
        self._distance_probs = {}
        self._beta_coef = 5.
        self._rv = sps.beta(1., self._beta_coef)
        self._pdf = [self._rv.pdf(r) / self._beta_coef for r in np.linspace(0, 1, 50)]

    def get_prior_prob(self, src_index, trg_index, src_length, trg_length):
        distance = abs(trg_index - src_index)
        return self._pdf[int(float(distance) / max(src_length, trg_length) * 50)]

    def collect_statistics(self, src_length, trg_length, posterior_matrix):
        """Extract the necessary statistics from this matrix if needed."""
        pass

    def recompute_parameters(self):
        """Reestimate the parameters and reset counters."""
        pass
