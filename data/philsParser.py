#!/usr/bin/env python

# Writing my own parser because everything is stupid

from sys import exit

INPUT = "dewiktionary-latest-pages-articles.xml" 
OUTPUT = "filteredPhilsWayDE.xml"

def main():
    inBody = False

    filew = open(OUTPUT, 'w')
    filer = open(INPUT, 'r')

    acc = ''

    for line in filer:
        # Get rid of preamble stuff
        if "<page>" in line and not inBody:
            inBody = True
            acc += line
        elif not inBody:  # In preamble, don't need it
            continue  
        elif "</page>" in line:  # end of reccord
            acc += line
            # found a German verb DE wiktionary
            if "{{Sprache|Deutsch}}" in acc and\
                    "{{Wortart|Verb|Deutsch}}" in acc:
                filew.write(acc)
            acc = ''  # end of reccord, reset ac
        else:  # in pages record, but not at end of record 
            acc += line


    filew.close()
    filer.close()
    

if __name__ == '__main__':
    main()
