from collections import OrderedDict
from itertools import takewhile, chain
import pickle
import argparse
import re
import numpy as np

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', help="input file")
    parser.add_argument('-c', '--countFile',
                        help="bin(pickle) word count file")
    parser.add_argument('-t', '--threshold', type=float, default=1e-5,
                        help="the threshold value, default = 1e-5")
    parser.add_argument('-m', '--minFreq', type=float, default=5.0,
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
    counterInfo['counter'] = counter
    return counterInfo

def filterfalse(predicate, iterable):
    # filterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
    if predicate is None:
        predicate = bool
    for x in iterable:
        if not predicate(x):
            yield x

def isSampled(token, counterInfo):
    isPunctuation = not token.isalnum()
    isFrequent = token in counterInfo['frequent']
    isMiddle = (token not in counterInfo['rare'] and
                token not in counterInfo['frequent'])
    isStayed = False
    proba = -1
    if isFrequent:
        proba = np.sqrt((counterInfo['thresholdCount'] /
                         counterInfo['frequent'][token]))
        isStayed = proba > np.random.random()
    return isPunctuation or isMiddle or (isFrequent and isStayed)

def main():
    options, args = parse_argument()
    counterInfo = readCountFile(options)
    print "Total count: {}".format(counterInfo['totalCount'])
    print "Threshold count: {}".format(counterInfo['thresholdCount'])
    print "Minimal count: {}".format(options.minFreq)
    pattern = re.compile('([\W_]+)')

    fout = open(options.outputFile, 'w')
    with open(options.inputFile, 'r') as f:
        print "Reading input from {}".format(options.inputFile)
        listIter = chain.from_iterable(
            pattern.split(line.lower().strip())
            for line in f)
        print "Writing output to {}".format(options.outputFile)
        fout.writelines(item for item in
                        filterfalse(lambda x: not isSampled(x, counterInfo),
                                    listIter))
    fout.close()

if __name__ == "__main__":
    main()
