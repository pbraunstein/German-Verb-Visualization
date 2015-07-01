#!/usr/bin/env python

# Filters out the other words in the dictCC file, just looks at verbs

from sys import exit

# CONSTANTS
INPUT = "cbomndsnbf-1306421878-e95oi5.txt"
OUTPUT = "dictCCVerbList.txt"

def main():
    filew = open(OUTPUT, 'w')
    with open(INPUT, 'r') as filer:
        for line in filer:
            if line.startswith("#"):
                continue
            try:
                if line.strip().split("\t")[2].lower() == 'verb':
                    filew.write(line)
            except IndexError:  # No 2nd column? Weird. Don't want it.
                pass

    filew.close()


if __name__ == '__main__':
    main()
