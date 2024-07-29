import Levenshtein as lev
import re

file = open("outputtest.txt", "r")
lines = file.readlines()

electrodes = {}
for l in lines:
    #Electrode("FP1", "P", "YP"),
    name, color, sequence = re.search(r'Electrode\("(.*)", "(.*)", "(.*)"\)', l).groups()
    electrodes[name] = {"color": color, "sequence": sequence}

#print('"' + '", "'.join(electrodes.keys()) + '"')

def circularLevenshtein(a, b):
    minDistance = float("inf")
    concatenated = a + a

    for i in range(len(a)):
        rotated = concatenated[i:i + len(a)]
        distance = lev.distance(rotated, b)
        if distance < minDistance:
            minDistance = distance

    return minDistance

def checkTestColorSequence(eName, electrodes):
    e = electrodes[eName]

    distances = []
    for eName2 in electrodes:
        e2 = electrodes[eName2]
        if e["color"] != e2["color"] or eName2 == eName:
            continue

        dist = circularLevenshtein(e["sequence"], e2["sequence"])
        distances.append({"name": eName2, "distance": dist, "sequence": e2["sequence"]})

    distances.sort(key=lambda x: x["distance"])
    return distances


matches = {}

for eName in electrodes:
    bestEDef = checkTestColorSequence(eName, electrodes)
    for m in bestEDef:
        if m["distance"] <= 1:
            if eName not in matches:
                matches[eName] = []
            matches[eName].append(m)

testRes = open("testRes.txt", "w")

for e in matches:
    print(e + " " + str(electrodes[e]["sequence"]))
    testRes.write(e + " " + str(electrodes[e]["sequence"]) + "\n")
    for m in matches[e]:
        print("\t" + m["name"] + " " + str(m["distance"]) + " " + m["sequence"])
        testRes.write("\t" + m["name"] + " " + str(m["distance"]) + " " + m["sequence"] + "\n")
    print()
    testRes.write("\n")

testRes.close()