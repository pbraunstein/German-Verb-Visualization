#!/usr/bin/env python

from sys import argv
from sys import exit
from sets import Set

def main():
    if len(argv) != 3:
        print "USAAGE:", argv[0], "first_csv second_csv"
        exit(1)

    firstSet = readIn(argv[1])
    secondSet = readIn(argv[2])

    diffSet = firstSet.symmetric_difference(secondSet)

    print diffSet

    exit(0)

def readIn(f):
    toReturn = Set()
    with open(f, 'r') as filer:
        for line in filer:
            listL = line.strip().split(",")
            toReturn.add(listL[0])

    return toReturn




if __name__ == '__main__':
    main()
