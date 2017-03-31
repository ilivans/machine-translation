#!/usr/bin/python
import os, sys
from math import log
from random import random
from coins_example import generate_n_samples_size_m
from coins_example import read_user_input

def infer_posterior_probs_coin_r(samples, estimate_prob_coin_r,
                                 estimate_prob_head_r, estimate_prob_head_b):
    "Given the current model estimates, infer the probability of red for each sample."
    posterior_probs_coin_r = []
    expected_log_likelihood = 0.0
    for sample in samples:
        prob_sample_and_coin_r = (
            estimate_prob_coin_r * estimate_prob_head_r ** sample.count("H") *
            (1 - estimate_prob_head_r) ** sample.count("T"))
        prob_sample_and_coin_b = (
            (1 - estimate_prob_coin_r) * estimate_prob_head_b ** sample.count("H") *
            (1 - estimate_prob_head_b) ** sample.count("T"))
        posterior_prob_coin_r = prob_sample_and_coin_r / (prob_sample_and_coin_r + prob_sample_and_coin_b)

        expected_log_likelihood += posterior_prob_coin_r * log(prob_sample_and_coin_r)
        expected_log_likelihood += (1 - posterior_prob_coin_r) * log(prob_sample_and_coin_b)        

        posterior_probs_coin_r.append(posterior_prob_coin_r)

    return posterior_probs_coin_r, expected_log_likelihood

def get_expected_statistics(posterior_probs_coin_r, samples):
    "Given the posterior probability of red for each sample, collect fractional counts."
    expected_count_coin_r, expected_count_coin_b = 0.0, 0.0
    expected_count_head_r, expected_count_head_b = 0.0, 0.0
    for i, sample in enumerate(samples):
        expected_count_coin_r += posterior_probs_coin_r[i] * len(sample)
        expected_count_coin_b += (1 - posterior_probs_coin_r[i]) * len(sample)
        expected_count_head_r += posterior_probs_coin_r[i] * sample.count("H")
        expected_count_head_b += (1 - posterior_probs_coin_r[i]) * sample.count("H")

    return expected_count_coin_r, expected_count_coin_b, expected_count_head_r, expected_count_head_b

def get_maximum_likelihood_estimates(count_coin_r, count_coin_b,
                                     count_coin_r_and_head, count_coin_b_and_head):
    estimate_prob_coin_r = count_coin_r / float(count_coin_r + count_coin_b)
    estimate_prob_head_r = count_coin_r_and_head / float(count_coin_r)
    estimate_prob_head_b = count_coin_b_and_head / float(count_coin_b)
    return estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b

def em(samples, estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b):
    "Perform one iteration of em: inter posterior, compute expected statistics, update estimates."
    posterior_probs_coin_r, expected_log_likelihood = infer_posterior_probs_coin_r(
        samples, estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b)
    expected_count_coin_r, expected_count_coin_b, expected_count_head_r, expected_count_head_b = (
        get_expected_statistics(posterior_probs_coin_r, samples))
    estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b = (
        get_maximum_likelihood_estimates(expected_count_coin_r, expected_count_coin_b,
                                         expected_count_head_r, expected_count_head_b))
    for i, sample in enumerate(samples):
        print "Pr(A) = %1.5f %s" % (posterior_probs_coin_r[i], sample)
    return estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b, expected_log_likelihood

if __name__ == "__main__":
    prob_coin_r, prob_head_r, prob_head_b, n, m = read_user_input(sys.argv[1:])
    samples, _ = generate_n_samples_size_m(
        n, m, prob_coin_r, prob_head_r, prob_head_b)
    estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b = 0.5, 0.51, 0.49
    previous_expected_log_likelihood = 0.0
    for i in range(1000):
        estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b, expected_log_likelihood = (
            em(samples, estimate_prob_coin_r, estimate_prob_head_r, estimate_prob_head_b))
        print "expected_log_likelihood = %1.4f" % (expected_log_likelihood / len(samples))
        print "estimate_prob_coin_r = %1.4f (actual = %1.4f)" % (estimate_prob_coin_r, prob_coin_r)
        print "estimate_prob_head_r = %1.4f (actual = %1.4f)" % (estimate_prob_head_r, prob_head_r)
        print "estimate_prob_head_b = %1.4f (actual = %1.4f)" % (estimate_prob_head_b, prob_head_b)
        if i > 0:
            if expected_log_likelihood - previous_expected_log_likelihood < 0.0001:
                break
        previous_expected_log_likelihood = expected_log_likelihood
    print "number of iterations = %d" % i
    print "number of coins = %d" % n
    print "number of times each coin was flipped = %d" % m
    print "total coin flips = %d" % (m * n)
    print "Note: To rerun use ./hidden_coins_example_solution.py %1.4f %1.4f %1.4f %d %d" % (
        prob_coin_r, prob_head_r, prob_head_b, n, m)
