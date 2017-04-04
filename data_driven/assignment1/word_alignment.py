#!/usr/bin/python
import os, sys, codecs, utils
from math import log

import numpy as np

from models import PriorModel
from models import TranslationModel


def get_posterior_distribution_for_trg_token(trg_index, src_tokens, trg_tokens,
                                             prior_model, translation_model):
    """Compute the posterior distribution over alignments for trg_index: P(a_j = i|f_j, e)."""
    # marginal_prob = p(f_j|e)
    # posterior_probs[i] = p(a_j = i|f_j, e)
    trg_token = trg_tokens[trg_index]
    src_len, trg_len = len(src_tokens), len(trg_tokens)

    prior_mult_condition_probs = np.zeros(src_len)
    for src_index, src_token in enumerate(src_tokens):
        conditional_prob = translation_model.get_conditional_prob(src_token, trg_token)
        prior_prob = prior_model.get_prior_prob(src_index, trg_index, src_len, trg_len)
        prior_mult_condition_probs[src_index] = prior_prob * conditional_prob
    prior_mult_condition_probs = np.array(prior_mult_condition_probs)
    marginal_prob = prior_mult_condition_probs.sum()
    posterior_probs = prior_mult_condition_probs / marginal_prob

    return marginal_prob, list(posterior_probs)


def get_posterior_alignment_matrix(src_tokens, trg_tokens, prior_model, translation_model):
    """For each target token compute the posterior alignment probability: p(a_j=i | f_j, e)"""
    # 1. Prior model assumes that a_j is independent of all other alignments.
    # 2. Translation model assume each target word is generated independently given its alignment.
    sentence_marginal_log_likelihood = 0.0
    posterior_matrix = []
    for trg_index in xrange(len(trg_tokens)):
        marginal_prob, posterior_probs = get_posterior_distribution_for_trg_token(trg_index, src_tokens, trg_tokens,
                                                                                  prior_model, translation_model)
        sentence_marginal_log_likelihood += log(marginal_prob) # if marginal_prob != 0.0 else 0.0
        posterior_matrix.append(posterior_probs)

    return sentence_marginal_log_likelihood, posterior_matrix


def collect_expected_statistics(src_corpus, trg_corpus, prior_model, translation_model):
    """Infer posterior distribution over each sentence pair and collect statistics: E-step"""
    corpus_marginal_log_likelihood = 0.0
    for src_tokens, trg_tokens in zip(src_corpus, trg_corpus):
        src_len, trg_len = len(src_tokens), len(trg_tokens)
        # 1. Infer posterior
        sentence_marginal_log_likelihood, posterior_matrix = get_posterior_alignment_matrix(
            src_tokens, trg_tokens, prior_model, translation_model
        )
        # 2. Collect statistics in each model.
        prior_model.collect_statistics(src_len, trg_len, posterior_matrix)
        translation_model.collect_statistics(src_tokens, trg_tokens, posterior_matrix)
        # 3. Update log prob
        corpus_marginal_log_likelihood += sentence_marginal_log_likelihood

    return corpus_marginal_log_likelihood


def reestimate_models(prior_model, translation_model):
    """Recompute parameters of each model: M-step"""
    prior_model.recompute_parameters()
    translation_model.recompute_parameters()


def initialize_models(src_corpus, trg_corpus):
    prior_model = PriorModel(src_corpus, trg_corpus)
    translation_model = TranslationModel(src_corpus, trg_corpus)
    return prior_model, translation_model


def estimate_models(src_corpus, trg_corpus, prior_model, translation_model, num_iterations):
    """Estimate models iteratively."""
    for iteration in range(num_iterations):
        corpus_log_likelihood = collect_expected_statistics(
            src_corpus, trg_corpus, prior_model, translation_model)
        reestimate_models(prior_model, translation_model)
        if iteration > 0:
            print "corpus log likelihood: %1.3f" % corpus_log_likelihood
    return prior_model, translation_model


def align_sentence_pair(src_tokens, trg_tokens, prior_probs, translation_probs):
    """For each target token, find the src_token with the highest posterior probability."""
    # Compute the posterior distribution over alignments for all target tokens.
    _, posterior_matrix = get_posterior_alignment_matrix(
        src_tokens, trg_tokens, prior_probs, translation_probs)
    # For each target word find the src index with the highest posterior probability.
    alignments = []
    for trg_index, posteriors in enumerate(posterior_matrix):
        best_src_index = posteriors.index(max(posteriors))
        alignments.append((best_src_index, trg_index))
    return alignments


def align_corpus_given_models(src_corpus, trg_corpus, prior_model, translation_model):
    """Align each sentence pair in the corpus in turn."""
    alignments = []
    for i in range(len(src_corpus)):
        these_alignments = align_sentence_pair(
            src_corpus[i], trg_corpus[i], prior_model, translation_model)
        alignments.append(these_alignments)
    return alignments


def align_corpus(src_corpus, trg_corpus, num_iterations):
    """Learn models and then align the corpus using them."""
    prior_model, translation_model = initialize_models(src_corpus, trg_corpus)
    prior_model, translation_model = estimate_models(
        src_corpus, trg_corpus, prior_model, translation_model, num_iterations)
    return align_corpus_given_models(src_corpus, trg_corpus, prior_model, translation_model)


if __name__ == "__main__":
    if not len(sys.argv) == 5:
        print "Usage: python word_alignment.py src_corpus trg_corpus iterations output_prefix."
        sys.exit(0)
    src_corpus = utils.read_all_tokens(sys.argv[1])
    trg_corpus = utils.read_all_tokens(sys.argv[2])
    num_iterations = int(sys.argv[3])
    output_prefix = sys.argv[4]
    assert len(src_corpus) == len(trg_corpus), "Corpora should be same size!"

    alignments = align_corpus(src_corpus, trg_corpus, num_iterations)
    utils.output_alignments_per_test_set(alignments, output_prefix)
