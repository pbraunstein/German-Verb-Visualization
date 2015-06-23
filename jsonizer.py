#!/usr/bin/env python
# Convets the data.csv verb family database into an appropriate JSON
# representation for use in d3 program

from sys import exit
import csv

# Constants
INPUT = "data.csv"
OUTPUT = "data.json"

def main():
    roots = readIn() 
    writeOut(roots)
    exit(0)

# Returns dictionary that has root as key and list of lists as value
# {gehen : [untergehen, y, descend], [aufgehen, n, whatevs, whatevs]}
def readIn():
    toReturn = {}
    with open(INPUT, "Ur") as filer:
        fileReader = csv.reader(filer)
        for row in fileReader:
            if row[0].startswith("#"):  # skip header
                continue
            row = [x for x in row if x != '']  # get rid of blanks
            root = row[1]
            if root in toReturn.keys():
                toReturn[root].append([row[0]] + row[2:])
            else:
                toReturn[root] = [[row[0]] + row[2:]]

    return toReturn


# Writes out the roots in JSON format
# TODO: Write this so it doesn't have trailing ocmmas in arrays
def writeOut(roots):
    with open(OUTPUT, 'w') as filew:
        filew.write("{\"verbRoots\": [\n")
        for root in roots.keys():
            filew.write("{\n")
            filew.write("\"root\":\"" + root + "\",\n")
            filew.write("\"childWords\":[\n")
            for verb in roots[root]:
                filew.write("\t{\n")
                filew.write("\t\"verb\":\"" + verb[0] + "\",\n")
                filew.write("\t\"separ\":\"" + verb[1].lower() + "\",\n")
                filew.write("\t\"transes\":[")
                for trans in verb[2:]:
                    filew.write("\"" + trans + "\",")
                filew.write("]\n")
                filew.write("\t},\n")
            filew.write("]\n")
            filew.write("},\n")
        filew.write("}")
                



if __name__ == '__main__':
    main()
