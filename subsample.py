from collections import OrderedDict
from itertools import takewhile, chain
import string
import pickle
import argparse
import re
import numpy as np

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', help="input file")
    parser.add_argument('-c', '--countFile',
                        help="bin(pickle) word count file")
    parser.add_argument('-t', '--threshold', type=int, default=1e-5,
                        help="the threshold value, default = 1e-5")
    parser.add_argument('-m', '--minFreq', type=int, default=5,
                        help="minimal frequency count, default = 5")
    parser.add_argument('-o', '--outputFile', help='output file')
    return parser.parse_known_args()

def readCountFile(options):
    counterInfo = {}
    counter = pickle.load(open(options.countFile, 'rb'))
    counterInfo['totalCount'] = float(sum(counter.values()))
    counterInfo['thresholdCount'] = np.ceil(counterInfo['totalCount'] *
                                            options.threshold)
    counterInfo['rare'] = OrderedDict(takewhile(
        lambda x: x[1] < options.minFreq,
        counter.most_common()[-1:0:-1]))
    counterInfo['frequent'] = OrderedDict(takewhile(
        lambda x: x[1] > counterInfo['thresholdCount'],
        counter.most_common()))
    return counterInfo

def filterfalse(predicate, iterable):
    # filterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
    if predicate is None:
        predicate = bool
    for x in iterable:
        if not predicate(x):
            yield x

def isSampled(token, counterInfo):
    isRare = token in counterInfo['rare']
    isPunctuation = not token.isalnum()
    isFrequent = token in counterInfo['frequent']
    isStayed = False
    if isFrequent:
        isStayed = np.sqrt((1 / counterInfo['frequent'][token]) *
                           counterInfo['thresholdCount']) < np.random.random()
    return isPunctuation or isRare or (isFrequent and isStayed)

def main():
    options, args = parse_argument()
    counterInfo = readCountFile(options)
    print "Start streaming the file..."
    np.random.seed(87)
    pattern = re.compile('([\W_]+)')

    fout = open(options.outputFile, 'w')
    with open(options.inputFile, 'r') as f:
        listIter = chain.from_iterable(
            pattern.split(line.lower().strip())
            for line in f)
        fout.write(''.join(
            list(filterfalse(lambda x: not isSampled(x, counterInfo),
                             listIter))))
    print "Write out to {}".format(options.outputFile)
    fout.close()

    # return counter

if __name__ == "__main__":
    main()
