#!/usr/bin/env python

from sys import exit
from bs4 import BeautifulSoup

# CONSTANTS
INPUT = "filteredPhilsWayDE.xmlkeep"
OUTPUT = "verben.csv"

def main():
    soup = BeautifulSoup(open(INPUT), "xml")
    allPages = soup.findAll('page')

    print len(allPages)



if __name__ == '__main__':
    main()
