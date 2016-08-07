from collections import Counter
import re
import pickle
import argparse
import itertools

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', help="input file")
    parser.add_argument('-o', '--outputFile', help='output file')
    return parser.parse_known_args()

def countWords():
    options, args = parse_argument()
    print "Counting words... This can take several minutes..."
    pattern = re.compile('[\W_]+')
    fout = open(options.outputFile, 'wb')
    with open(options.inputFile, 'r') as f:
        lineCount = (pattern.sub(' ', line.lower().strip()).split()
                     for line in f)
        counter = Counter(itertools.chain.from_iterable(lineCount))
    pickle.dump(counter, fout)
    print "Write out to {}".format(options.outputFile)
    print "The most frequent word: {}".format(counter.most_common(10))
    fout.close()

    return counter

if __name__ == "__main__":
    countWords()
