import os

with os.scandir("voice") as File:
    for entry in File:
        if entry.name != "ELT.aac":
            os.remove(entry.name)