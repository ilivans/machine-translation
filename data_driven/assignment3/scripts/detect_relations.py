import sys
import numpy as np
from embeddings import Vocab, WordEmbedding, Model


def load_example_sets(path):
    # Loads list of pairs per line.
    return [[tuple(pair.split()) for pair in line.strip().split('\t')] for line in open(path)]


def load_labels(path):
    # Loads a label for each line (-1 indicates the pairs do not form a relation).
    return [int(label) for label in open(path)]


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print "Usage ./detect_relations.py vocab_file embedding_file train_data train_labels test_data"
        sys.exit(0)

    # Load vocab and embedding (these are not used yet!)
    vocab = Vocab(sys.argv[1])
    embedding = WordEmbedding(vocab, sys.argv[2])
    model = Model(vocab, embedding)

    # Loads training data and labels.
    training_examples = load_example_sets(sys.argv[3])
    training_labels = load_labels(sys.argv[4])
    assert len(training_examples) == len(training_labels), "Expected one label for each line in training data."

    # Training the model
    train_diffs_means = []  # model params
    train_diffs_stds = []  # other model params
    for training_example, training_label in zip(training_examples, training_labels):
        diffs =[]
        for w1, w2 in training_example:
            w1, w2 = w1.decode("utf-8"), w2.decode("utf-8")  # essential for Russian
            diffs.append(embedding.Projection(w1) - embedding.Projection(w2))
        diffs = np.array(diffs)
        train_diffs_means.append(diffs.mean(axis=0))
        train_diffs_stds.append(diffs.std(axis=0))
    train_diffs_means = np.array(train_diffs_means)
    train_diffs_stds = np.array(train_diffs_stds)

    # Loading test data
    test_examples = load_example_sets(sys.argv[5])

    # Prediction
    test_labels = []
    for test_example in test_examples:
        diffs = []
        for w1, w2 in test_example:
            w1, w2 = w1.decode("utf-8"), w2.decode("utf-8")
            diffs.append(embedding.Projection(w1) - embedding.Projection(w2))
        diffs = np.array(diffs)
        test_diffs_mean = diffs.mean(axis=0)
        test_diffs_std = diffs.std(axis=0)

        # If std of differences (between words in pairs) is big (and close to those from training data)
        # than it's probably random pairs (-1 class)
        idx = np.linalg.norm(train_diffs_stds - test_diffs_std.reshape((1, -1)), 1, axis=1).argmin()
        if training_labels[idx] == -1:
            test_labels.append(-1)
            continue

        # Otherwise look at mean difference and find the closest one from training data
        idx = np.linalg.norm(train_diffs_means - test_diffs_mean.reshape((1, -1)), 1, axis=1).argmin()
        test_labels.append(training_labels[idx])

    # Writing the results
    with open("predicted_labels.txt", "w") as f:
        for l in test_labels:
            f.write("{}\n".format(l))
