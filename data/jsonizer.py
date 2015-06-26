#!/usr/bin/env python
# Convets the data.csv verb family database into an appropriate JSON
# representation for use in d3 program
# JSON has been validated by JSON validator online

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
def writeOut(roots):
    with open(OUTPUT, 'w') as filew:
        filew.write("[\n")
        rootsArray = roots.keys()
        for i in range(len(rootsArray)):
            root = rootsArray[i]
            filew.write("{\n")
            filew.write("\t\"root\":\"" + root + "\",\n")
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