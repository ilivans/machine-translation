from collections import defaultdict
# Models for word alignment

class TranslationModel:
    "Models conditional distribution over trg words given a src word."

    def __init__(self, src_corpus, trg_corpus):
        self._src_trg_counts = {} # Statistics
        self._trg_given_src_probs = {} # Parameters
        # for src_sentence, trg_sentence in zip(src_corpus, trg_corpus):
        #     for src_token in src_sentence:
        #         if src_token not in self._src_trg_counts:
        #             self._src_trg_counts = {}
        #         for trg_token in trg_sentence:
        #             self._src_trg_counts[src_token][trg_token] = self._src_trg_counts[src_token].get(trg_token, 0) + 1
        # for src_token, trg_counts in self._src_trg_counts.iteritems():
        #     trgs_count_total = float(sum(trg_counts.itervalues()))
        #     self._trg_given_src_probs[src_token] = {}
        #     for trg_token, trg_count in trg_counts:
        #         self._trg_given_src_probs[src_token][trg_token] = trg_count / trgs_count_total

    def get_conditional_prob(self, src_token, trg_token):
        "Return the conditional probability of trg_token given src_token."
        if src_token not in self._trg_given_src_probs:
            return 0.0
        if trg_token not in self._trg_given_src_probs[src_token]:
            return 0.0
        return self._trg_given_src_probs[src_token][trg_token]

    def collect_statistics(self, src_tokens, trg_tokens, posterior_matrix):
        "Accumulate fractional alignment counts from posterior_matrix."
        assert len(posterior_matrix) == len(trg_tokens)
        for posterior in posterior_matrix:
            assert len(posterior) == len(src_tokens)
        assert False, "Collect statistics here in self._src_trg_counts"

    def recompute_parameters(self):
        "Reestimate parameters from counts then reset counters"
        assert False, "Recompute parameters in self._trg_given_src_probs here."


class PriorModel:
    "Models the prior probability of an alignment given only the sentence lengths and token indices."

    def __init__(self, src_corpus, trg_corpus):
        "Add counters and parameters here for more sophisticated models."
        self._distance_counts = {}
        self._distance_probs = {}

    def get_prior_prob(self, src_index, trg_index, src_length, trg_length):
        "Returns a uniform prior probability."
        return 1.0 / src_length

    def collect_statistics(self, src_length, trg_length, posterior_matrix):
        "Extract the necessary statistics from this matrix if needed."
        pass

    def recompute_parameters(self):
        "Reestimate the parameters and reset counters."
        pass
