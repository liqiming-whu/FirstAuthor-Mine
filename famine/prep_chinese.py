#!/usr/bin/env python3
"""
Prepare Chinese Family name and First name sets
"""
import sys
import gzip
from xpinyin import Pinyin

p = Pinyin()

famset = set()
compoundfam = set()
for line in open("data/Chinese_Family_Name.csv"):
    b = line.rstrip().split(",")
    if b[0] == "NameB":
        continue
    cname = b[0]
    if len(cname) > 1:
        compoundfam.add(cname)
    famset.add(cname)


print(len(famset))
print(len(compoundfam))
with open("ChineseFamily.csv", "w") as f:
    names = set(p.get_pinyin(name, '') for name in famset)
    for name in sorted(names):
        f.write(name+"\n")


firstset = set()
with gzip.open("data/Chinese_Names_Corpus120W.txt.gz", 'r') as f:
    for line in f:
        full = line.rstrip().decode()

        is_compound = False
        for compound in compoundfam:
            if full.startswith(compound):
                is_compound = True
                break
        if is_compound:
            continue

        firstset.add(full[1:])

print(len(firstset))
with open("ChineseFirst.csv", "w") as f:
    names = set(p.get_pinyin(name, '') for name in firstset)
    for name in sorted(names):
        f.write(name+"\n")
