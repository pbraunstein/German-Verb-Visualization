#!/usr/bin/env python

# Right now, throws out all records without translation

from sys import exit
from bs4 import BeautifulSoup
import re

# CONSTANTS
INPUT = "filteredPhilsWayDE.xml"
OUTPUT = "verben.csv"
NA = u'N/A'
CODE = "utf-8-sig"

class xmlRecord:
    def __init__(self, record):
        self.name = unicode(record.title.contents[0])
        self.trans = unicode(self.getEnTrans(record.text))
        self.isRoot = None
        self.isSep = None
        self.prefix = None
        self.root = None
        self.children = []
        self.derivedWords = self.getDerivedTerms(record.text)

    def __str__(self):
        return self.name.encode(CODE) + "\n" + self.trans.encode(CODE)

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

    # Parses the text of the xml to record to get the derived words
    # (auf Deutsch: Wortbildungen)
    def getDerivedTerms(self, text):
        regEx1 = re.compile(ur'\{\{Wortbildungen\}\}(.*)\n\n===', re.DOTALL |
            re.UNICODE)

        match = regEx1.search(text)

        # This code is messy, it splits on commas and colons to make
        # a flat list. It uses a regex to strip certain punctuation
        if match:
            terms = match.group(1).strip()
            termsList1 = terms.split(u':')
            termsList2 = []
            for word in termsList1:
                wordList = word.split(u',')
                for littleWord in wordList:
                    termsList2.append(littleWord)
            regEx2 = re.compile(ur'([0-9\[\]\"\']*)')

            # Remove punctuation and numbers 
            termsList2 = [regEx2.sub('', x).strip() for x in termsList2]

            # Filter out empty strings
            termsList2 = [x for x in termsList2 if x != u'']
            return termsList2
        else:
            return []  # No derived words, could still be okay


def main():
    soup = BeautifulSoup(open(INPUT), "xml")
    allPages = soup.findAll('page')

    records = getRecords(allPages)
    
    for record in records:
        print "---------------------------"
        print record.name.encode(CODE)
        for x in record.derivedWords:
            print x.encode(CODE) + ",",
        print "\n---------------------------"
        print
    print len(records)

def getRecords(allPages):
    toReturn = []

    for page in allPages:
        newRec = xmlRecord(page)
        if newRec.trans != NA:
            toReturn.append(newRec)

    return toReturn












if __name__ == '__main__':
    main()
