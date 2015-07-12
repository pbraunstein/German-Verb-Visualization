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
CODE = "utf-8"
DICT = "buDict.txt"

class xmlRecord:
    def __init__(self, record, dictionary):
        self.name = unicode(record.title.contents[0])
        self.trans = self.getEnTrans(dictionary)
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

    # Shouldn't need to make any API calls, so it just makes note
    # if the dicionary look up fails
    # Also makes sure that it has the to prepended to the verb
    def getEnTrans(self, dictionary):
        try:
            trans = dictionary[self.name]
            if not trans.startswith(u'to ') and trans != NA:
                trans = u'to ' + trans
            return trans
        except KeyError:
            print self.name.encode(CODE)
            return NA
            try:
                link = "https://glosbe.com/gapi/translate?from=deu&dest=eng" +\
                            "&format=json&phrase=" +\
                            quote_plus(self.name.encode(CODE)) +\
                            "&callback=my_custom_function_name"

                content = urllib2.urlopen(link).read()
                regEx = re.compile("my_custom_function_name\(\{\"result\":\"ok\",\"tuc\":\[\{\"phrase\":\{\"text\":\"([\w\s]+)\",", re.UNICODE)
                match = regEx.search(content)
                if match:
                    trans = match.group(1).decode(CODE)
                    return trans
                else:
                    return NA
            except urllib2.HTTPError:
                writeOutDict(dictionary)
                print "ABORTED"
                exit(1)


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
    # TODO TODO FIX THIS AWEFUL FUNCTION
    def getDerivedTerms(self, text):
        regEx1 = re.compile(ur'\{\{Wortbildungen\}\}(.*)=', re.UNICODE |
                re.DOTALL)
        regEx2 = re.compile(ur'\{\{Unterbegriffe\}\}(.*?)\{\{Beispiele', re.UNICODE |
                re.DOTALL)

        regExP = re.compile(ur'([0-9:\[\]\"\']*)', re.UNICODE)

        regExP2 = re.compile(ur'\n', re.UNICODE)
        
        
        match2 = regEx2.search(text)
        listL1 = []
        if match2:
            termsListP = regExP.sub('', match2.group(1))
            termsListP = regExP2.sub(',', termsListP)  # Replace newLines
            listL1 = termsListP.split(",")
            listL1 = [x for x in listL1 if x != '']
            listL1 = [x.strip() for x in listL1]

        match = regEx1.search(text)

        # This code is messy, it splits on commas and colons to make
        # a flat list. It uses a regex to strip certain punctuation
        listL2 = []
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
            regEx3 = re.compile(ur'([0-9\[\]\"\']*)', re.UNICODE)

            # Remove punctuation and numbers 
            termsList2 = [regEx3.sub('', x).strip() for x in termsList2]

            # Filter out empty strings
            listL2 = [x for x in termsList2 if x != u'']

        # Collect results
        return listL1 + listL2


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
    print "Reading In Dictionary...."
    wordTrans = readInDict()
    print "Complete."

    print "Loading XML Doc...."
    soup = BeautifulSoup(open(INPUT), "xml")
    allPages = soup.findAll('page')
    print "Complete."

    print "Generating Records...."
    packing = getRecords(allPages, wordTrans)
    records = packing[0]
    wordTrans = packing[1]
    print "Complete."

    print "Annotating Reltations...."
    records = annotateRelations(records)
    print "Complete."

    print "Pruning Unwanted Data...."
    records = filterOrphans(records)
    print "Complete."

    print "Writing Out Results...."
    writeOut(records)
    print "Complete."


# Reads in the dict file to query first
def readInDict():
    toReturn = {}

    with open(DICT, 'r') as filer:
        for line in filer:
            line = line.decode(CODE)
            line = line.strip()
            listL = line.split(u':')
            toReturn[listL[0]] = listL[1]

    return toReturn


# updates the dictionary with API call results
def getRecords(allPages, wordTrans):
    toReturn = []

    for page in allPages:
        newRec = xmlRecord(page, wordTrans)
        wordTrans[newRec.name] = newRec.trans  # Update dictionary
        if newRec.trans != NA:
            if newRec.isSep is not None:
                toReturn.append(newRec)

    return [toReturn, wordTrans]


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


# Save cache of dict
def writeOutDict(dictionary):
    print "Rescuing Cache....."
    with open(DICT, 'w') as filew:
        for key in dictionary.keys():
            filew.write(key.encode(CODE) + ":" + dictionary[key].encode(CODE) +
                            "\n")

if __name__ == '__main__':
    main()
