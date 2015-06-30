#!/usr/bin/env python
# Convets the data.csv verb family database into an appropriate JSON
# representation for use in d3 program
# JSON has been validated by JSON validator online

from sys import exit
import csv

# Constants
INPUT = "verben.csv"
OUTPUT = "data.json"

def main():
    packing = readIn()
    writeOut(packing[0], packing[1])
    exit(0)

# Returns dictionary that has root as key and list of lists as value
# {gehen : [untergehen, y, descend], [aufgehen, n, whatevs, whatevs]}
# Returns this dict as first argument of list, second argument of
# list is translation of roots {gehen:go...}
def readIn():
    toReturn = {}
    rootDict = {}
    with open(INPUT, "Ur") as filer:
        fileReader = csv.reader(filer)
        for row in fileReader:
            if row[0].startswith("#"):  # skip header
                continue
            if row[0] == '':  # Found a root + trans
                rootDict[row[1]] = row[3]
                continue
            row = [x for x in row if x != '']  # get rid of blanks
            root = row[1]
            if root in toReturn.keys():
                toReturn[root].append([row[0]] + row[2:])
            else:
                toReturn[root] = [[row[0]] + row[2:]]

    return [toReturn, rootDict]


# Writes out the roots in JSON format
# adds in the translation of the roots
def writeOut(roots, rootTranses):
    with open(OUTPUT, 'w') as filew:
        filew.write("[\n")
        rootsArray = roots.keys()
        for i in range(len(rootsArray)):
            root = rootsArray[i]
            filew.write("{\n")
            filew.write("\t\"root\": \"" + root + "\",\n")
            filew.write("\t\"trans\": \"" + rootTranses[root] +"\",\n")
            filew.write("\t\"childWords\": [\n")
            for j in range(len(roots[root])):
                verb = roots[root][j]
                filew.write("\t\t{\n")
                filew.write("\t\t\t\"verb\": \"" + verb[0] + "\",\n")
                filew.write("\t\t\t\"separ\": " +  getJsonIsSep(verb[1])
                            + ",\n")
                filew.write("\t\t\t\"trans\": ")
                filew.write("\"" + verb[2] + "\"")
                filew.write("\n")
                if j < (len(roots[root]) - 1):  # not last entry, add comma
                    filew.write("\t\t},\n")
                else:  # last entry, don't add comma
                    filew.write("\t\t}\n")
            filew.write("\t]\n")
            if i < (len(rootsArray) - 1):  # not last entry, add comma
                filew.write("},\n")
            else:  # last entry, no comma
                filew.write("}\n")  

        filew.write("]")  # Close whole array


# Returns the string "true" (without quotes, mind you) if
# the argument passed in is anycase y. Returns "false" if
# anycase n, otherwise, prints an error message and fails
def getJsonIsSep(letter):
    letter = letter.lower()
    if letter == 'y':
        return "true"
    elif letter == 'n':
        return "false"
    else:
        print "ERROR:", letter, "is not a valid sep marker"
        exit(1)



if __name__ == '__main__':
    main()
