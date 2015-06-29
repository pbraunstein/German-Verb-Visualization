#!/usr/bin/env python

from sys import exit
from bs4 import BeautifulSoup
import re

# CONSTANTS
INPUT = "filteredPhilsWayDE.xml"
OUTPUT = "verben.csv"
NA = "N/A"

class xmlRecord:
    def __init__(self, record):
        self.name = unicode(record.title.contents[0])
        self.trans = self.getEnTrans(record.text)
        self.isRoot = None
        self.isSep = None
        self.prefix = None
        self.root = None
        self.children = []

    def __str__(self):
        return self.name + "\n" + self.trans

    # Parses the text of the XML record to get the En translation
    def getEnTrans(self, text):

        # e.g. {{UE|en|know}} Trying to pull out know,
        # UE represents uppercase umlauted U
        # Only matches the first definition (if there are more than one)
        regEx = re.compile(ur'\{\{\u00dc\|en\|(\w*)\}\}', re.UNICODE)

        match = regEx.search(text)

        if match:
            if match.group(1).strip() == '':  # Sometimes records are empty
                return NA
            else:
                return match.group(1)
        else:
            return NA

def main():
    soup = BeautifulSoup(open(INPUT), "xml")
    allPages = soup.findAll('page')

    for page in allPages:
        if page.title.contents[0] == 'suchen':
            print xmlRecord(page)
            break











if __name__ == '__main__':
    main()
