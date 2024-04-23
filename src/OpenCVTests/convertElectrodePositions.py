import os

file = open("CA-106.nlr-clean.elc", "r")
lines = file.readlines()

electrodes = []

for line in lines:
    parts = line.split(":")

    coordinates = parts[1].strip().split("\t")
    x = float(coordinates[0]) / 1000
    y = float(coordinates[1]) / 1000
    z = float(coordinates[2]) / 1000

    electrode = {
        "name": parts[0].strip(),
        "x": x,
        "y": y,
        "z": z
    }

    electrodes.append(electrode)

print(electrodes)

result = "ElectrodeDefinition[] electrodePositions = {\n"

for electrode in electrodes:
    result += "new ElectrodeDefinition(\"" + electrode["name"] + "\", " + str(electrode["x"]) + ", " + str(electrode["y"]) + ", " + str(electrode["z"]) + "),\n"

result += " };"

print(result)


