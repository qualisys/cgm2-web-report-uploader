# Overview
This Python script uploads CGM2 gait data recorded and processed with the PAF Gait Module to the Qualisys Report Center (http://report.qualisys.com) to generate a Web Report. CGM2 is updated version of "Conventional Gait Model" (also known as "Vicon Plug-in Gait").

# Requirements
- Qualisys Track Manager with PAF Gait Module installed
- Active Qualisys license.
- Active Report Center token. Please contact support@qualisys.com for details.
- Python 2.7 (32 bits)
- Mokka 0.6.2 (https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/b-tk/Mokka-0.6.2_win64.zip)
- pyCGM2 (https://github.com/pyCGM2/pyCGM2.git) > development branch

# Data processing and upload
- Use your qualisys.com credentials to log in to Report Center (https://report.qualisys.com)
- Claim the report