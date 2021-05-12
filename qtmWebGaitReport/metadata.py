# -*- coding: utf-8 -*-

import os
from os import path


def get_creation_date(file):
    stat = os.stat(file)
    try:
        return stat.st_birthtime
    except AttributeError:
        return stat.st_mtime


class Metadata:
    def __init__(self, workingDirectory, modelledC3dfilenames, subjectMetadata, creationDate):
        self.workingDirectory = workingDirectory
        self.subjectMetadata = subjectMetadata
        self.modelledC3dfilenames = modelledC3dfilenames
        self.creationDate = creationDate

        self.fileNames = []
        for filename in self.modelledC3dfilenames:
            self.fileNames.append(str(path.join(self.workingDirectory, filename)))

    def medatadaInfo(self):

        generatedByType = "UNSPECIFIED"
        name = "UNSPECIFIED"
        version = "UNSPECIFIED"

        generatedBy = [{"type": "".join(generatedByType), "name": "".join(name), "version": "".join(version)}]

        fields = [
            {"id": "Creation date", "value": str(self.creationDate.date()), "type": "text"},
            {"id": "Creation time", "value": str(self.creationDate.time()), "type": "text"},
        ]

        # add fields from subject metadata
        for key, val in self.subjectMetadata.items():
            fields.append({"id": key, "value": val, "type": "text"})

        info = {"isUsingStandardUnits": True, "generatedBy": generatedBy, "customFields": fields}

        return info

    def subjectInfo(self):
        subject = {
            "id": self.subjectMetadata["Patient ID"] + "_" + self.subjectMetadata["Date of birth"],
            "displayName": self.subjectMetadata["First name"] + " " + self.subjectMetadata["Last name"],
        }
        return subject

    def projectInfo(self):
        project = {"type": "Gait", "subtype": self.subjectMetadata["Sub Session Type"]}
        return project
