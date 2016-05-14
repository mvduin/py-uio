import re
f = open('process.txt', 'r')
finalString = "dict("
for line in f.readlines():
    OffsetRe = re.compile('[a-fA-F0-9]*h')
    match = OffsetRe.search(line)
    #print(hex(int(match.group()[:-1],16)))
    junkRe = re.compile("Section")
    toDelete = junkRe.search(line)
    finalString = finalString + line[match.span()[1]:toDelete.span()[0]].strip() + "=(" + hex(int(match.group()[:-1],16)) + ',4),'
finalString = finalString + ")"
print(finalString)
f.close()
