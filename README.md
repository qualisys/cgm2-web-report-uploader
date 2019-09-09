# Overview

This document explains how to upload gait data recorded and processed with the "Conventional Gait Model" (CGM, also known as "Vicon Plug-in Gait") or CGM2 to the Qualisys Report Server (http://report.qualisys.com) to generate a Web Report. 

# Requirements
- Signal names in the c3d files must follow the naming conventions used by CGM and must include gait specific landmarks before they can be processed with the Web Report Importer.
- Other files containing patient/session/measurement related meta data must be copied into the same folder as c3d files. (see below for list of required files and formats).
- Videos in .avi format can be added to the same folder (see below for list of required files and formats).
- You must have a valid QTM licence. Contact sales@qualisys.com if you require a trial licence.
    - The QTM User Name must be added as "clientId" to Templates\config.json. 
    - You need to request an access token from Qualisys and place it as "token" into Templates\config.json.
    - You need to have a personal account for qualisys.com. Your account needs to be connected to the licence that you use as "clientID" and you need to be set as Lab Manager for your account to be able to see the uploaded reports.
- Python 2.7
- BTK 0.3 (https://pypi.org/project/btk/)

# File naming conventions
File naming must follow these conventions:
- c3d files: [Patient name] Walk[nn].c3d
- meta files: 
    - [Patient name] Walk[nn].Trial.enf,
    - [Patient name] Walk[nn].system,
    - [Patient name].Session.enf,
    - [Patient name].mp,
    - [Patient name].vsk
- videos: [Patient name] Walk[nn].[camera number].avi

# Install Python environment and BTK
## Python
The most convenient solution is to install a Python distribution, e.g. Anaconda (https://www.anaconda.com). 

## BTK
BTK python (Biomechanical Toolkit) is required to read content of c3d files. Download corresponding binary and install it. (https://code.google.com/archive/p/b-tk/downloads)
*Please note that BTK requires Python 2.7.*

# Data processing and upload
- Run QWRI.py.
- Dialog window will popup where the path to session folder with .c3d files must be specified. Hit Create report and report will be uploaded to Report Center.
- Use your qualisys.com credentials to log in to Report Center (https://report.qualisys.com)
- In Report Center, click the gear icon (top right) and activate "See all [QTM User Name] reports"
