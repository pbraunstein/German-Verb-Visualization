#!/usr/bin/env python

# So far, this script filters csv so that it only makes German pages

from sys import exit
from bs4 import BeautifulSoup

# CONSTANTS
INPUT_FILE = "dewiktionary-latest-pages-articles.xml"
OUTPUT_FILE = "filteredDeutsch.xml"

def main():
    soup = BeautifulSoup(open(INPUT_FILE), "xml")

    filew = open(OUTPUT_FILE, 'w')

    # Get all the pages
    allPages = soup.findAll('page')
    print "got all pages, starting searching through them"

    for page in allPages:
        # Only want German verbs
        if "{{Sprache|Deutsch}}" in page.text and\
                "{{Wortart|Verb|Deutsch}}" in page.text:
            filew.write(str(page))

    print "Complete"
    exit(0)

if __name__ == '__main__':
    main()
