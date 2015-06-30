#!/usr/bin/env python

# Right now, throws out all records without translation

from sys import exit
from bs4 import BeautifulSoup
from urllib import quote_plus
import urllib2
import re

# CONSTANTS
INPUT = "filteredPhilsWayDE.xml"
OUTPUT = "verben.csv"
NA = u'N/A'
CODE = "utf-8-sig"
API = "SPOOF"

class xmlRecord:
    def __init__(self, record):
        self.name = unicode(record.title.contents[0])
        self.trans = self.getEnTrans()
        self.isRoot = None
        self.isChild = None
        self.isSep = self.getIsSep(record.text)
        self.root = None
        self.derivedWords = self.filterDerivedTerms(
                                self.getDerivedTerms(record.text))

    def __str__(self):
        if self.root is not None:
            r = self.root
        else:
            r = NA
        if self.isSep:
            separ = "Separable"
        else:
            separ = "Unseparable"
        return self.name.encode(CODE) + "\n" + self.trans.encode(CODE) +\
                "\n" + separ + "\nRoot:" + r.encode(CODE) + "\n"

    # Uses Yandex API key to make translation
    def getEnTrans(self):
        link = "https://translate.yandex.net/api/v1.5/tr/translate?key=" +\
                API + "&lang=de-en&text=" + quote_plus(self.name.encode(CODE))

        content = urllib2.urlopen(link).read()

        soup = BeautifulSoup(content, 'xml')

        trans = soup.find('Translation').text

        # Yandex returns input if no trans found
        if trans != self.name:
            return trans
        else:
            return NA


    # Parses the text of the XML record to get the En translation
    def __getEnTrans(self, text):

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
            conjArr = conj.split()
            conjArr = [x.strip() for x in conjArr]  # to be safe
            conjArrLen = len(conjArr)

            # reflexive, don't count the refl. pronoun
            if 'mich' in conjArr or 'mir' in conjArr:
                conjArrLen -= 1
            if conjArrLen > 1:
                return True
            else:
                return False

        return None

    # Parses the text of the xml to record to get the derived words
    # Returns a list of derived terms
    # (auf Deutsch: Wortbildungen)
    def getDerivedTerms(self, text):
        regEx1 = re.compile(ur'\{\{Wortbildungen\}\}(.*)=', re.UNICODE |
                re.DOTALL)

        match = regEx1.search(text)

        # This code is messy, it splits on commas and colons to make
        # a flat list. It uses a regex to strip certain punctuation
        if match:
            # Geedy match in Regex gobbles too much, split on ===
            # which I know to be the start of the next sectiont
            terms = match.group(1).split("===")[0]
            terms = terms.strip()
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


    #  Remove derived terms that do not contain the root as a complete
    #  suffix
    def filterDerivedTerms(self, derivedTerms):
        toReturn = []
        regEx = re.compile(u'(.+)' + self.name + u'$', re.UNICODE)
        for term in derivedTerms:
            m = regEx.search(term)
            if m:
                toReturn.append(term)
        return toReturn


def main():
    soup = BeautifulSoup(open(INPUT), "xml")
    allPages = soup.findAll('page')

    records = getRecords(allPages)

    records = annotateRelations(records)

    records = filterOrphans(records)

    writeOut(records)


#    for record in records:
#        print record


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


# Figures out from the derived terms, which terms are roots and which are
# children.
def annotateRelations(records):
    for recordOuter in records:
        derived = recordOuter.derivedWords
        for dw in derived:
            for recordInner in records:
                if dw == recordInner.name:  # found one!
                    recordOuter.isRoot = True  # Outer is a root
                    recordInner.isChild = True  # inner is a child
                    recordInner.root = recordOuter.name  # Note name of root

    return records


# Filters out the records that are neither children nor roots
def filterOrphans(records):
    toReturn = []

    for record in records:
        if record.isRoot is None and record.isChild is None: 
            continue  # Don't want records without relations
        toReturn.append(record)

    return toReturn

# Writes out information in the records into file
# A word can be both a root and a child
def writeOut(records):
    with open(OUTPUT, 'w') as filew:
        filew.write("#Verb,Root,Sep,Trans\n")
        for record in records:
            if record.isSep:
                separ = "y"
            else:
                separ = "n"

            # Write out record if it is a root
            # root by definition cannot be separable
            if record.isRoot:  
                filew.write("," + record.name.encode(CODE) + ",n" +\
                            "," + record.trans.encode(CODE) + "\n")

            # If it is a child, write it out
            if record.isChild:
                filew.write(record.name.encode(CODE) + "," +\
                            record.root.encode(CODE) + "," + separ + "," +\
                            record.trans.encode(CODE) + "\n")



if __name__ == '__main__':
    main()
