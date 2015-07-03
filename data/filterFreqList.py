#!/usr/bin/env python

# Filters the frequency list of English words downloaded from
# http://www.kilgarriff.co.uk/bnc-readme.html only includes verbs
# as well as the numerical rank (frequency not included cause it's
# not so important)
# Ensures the words are all lower case and appends "to " for compatability
# with dictCC derived file

from sys import exit

INPUT = "lemma.num"
OUTPUT = "englFreq.csv"

def main():
    filew = open(OUTPUT, 'w')

    with open(INPUT, 'r') as filer:
        for line in filer:
            listL = line.lower().strip().split()

            if listL[3] == 'v':  # Is a verb
                filew.write("to " + listL[2] + "," + listL[0] + "\n")

    filew.close()


if __name__ == '__main__':
    main()


