#!/usr/bin/env python

# Used to cut parse out the verbs in the Freedict

from sys import exit
from bs4 import BeautifulSoup

INPUT = "deu-eng.tei"
OUTPUT = "parsedFreeDictOutput.txt"
CODE = "utf-8"

def main():
    soup = BeautifulSoup(open(INPUT), 'xml')
    pages = soup.findAll('entry')
    filew = open(OUTPUT, 'w')
    for page in pages:
        gramGroup = page.find('gramGrp')
        if gramGroup:
            pos = gramGroup.find('pos')
            if pos:
                if unicode(pos.contents[0]) != u'v':
                    continue
        word = unicode(page.find('orth').contents[0]).encode(CODE)
        trans = unicode(page.find('cit').find('quote').contents[0]).encode(CODE)
        filew.write(word + ":" + trans + "\n")
    filew.close()

if __name__ == '__main__':
    main()
