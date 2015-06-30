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
        self.isSep = self.getIsSep(record.text)
        self.prefix = None
        self.root = None
        self.derivedWords = self.getDerivedTerms(record.text)

    def __str__(self):
        if self.isSep:
            separ = "Separable"
        else:
            separ = "Unseparable"
        return self.name.encode(CODE) + "\n" + self.trans.encode(CODE) +\
                "\n" + separ + "\n"

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

    # Determines if the verb is separable by counting the number of words
    # used to conjugate the present first person (Gegenwart_ich)
    def getIsSep(self, text):
        regEx = re.compile(ur'Gegenwart_ich *= *(.*)', re.UNICODE)
        match = regEx.search(text)
        if match:
            conj = match.group(1).strip()
            if len(conj.split()) > 1:
                return True
            else:
                return False

        return None

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
        print record
    print len(records)

# Creates the xml records, and filters out the records that have no
# english translation filters out as well those without conjugations
# (can't tell if it is separable). As of first draft, only one word
# in dewiki has no separability information (babysitten).
def getRecords(allPages):
    toReturn = []

    for page in allPages:
        newRec = xmlRecord(page)
        if newRec.trans != NA:
            if newRec.isSep is not None:
                toReturn.append(newRec)

    return toReturn


if __name__ == '__main__':
    main()
