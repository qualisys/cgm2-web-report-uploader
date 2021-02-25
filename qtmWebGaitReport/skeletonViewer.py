# -*- coding: utf-8 -*-

import btk
from qtmWebGaitReport import qtools
import numpy as np
import segmentCS
from qtmWebGaitReport import c3dValidation
import os
import json
from scipy.spatial import distance
from qtmWebGaitReport from qtmWebGaitReport import metadata
import scipy as sci

workingDirectory = "E:\\Qualisys_repository\\Gait-Web-Importer\\Data\\Oxford\\"

class SkeletonViewer:
    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory
        
        c3dValObj = c3dValidation.c3dValidation(workingDirectory) #create list of signals. Make sure that missing signal in one of trial will not break it
        self.fileNames = c3dValObj.getValidC3dList(False)
        
        self.markerList = ['LTOE','LANK','LTIB','LKNE','LTHI','LASI','RASI','LPSI','RPSI','SACR','RTOE','RANK','RTIB','RKNE','RTHI','LFHD','RFHD','LBHD','RBHD','C7','T10','CALV','STRN','RBAK','LSHO','LUPA','LELB','LFRM','LWRA','LWRB','LFIN','RSHO','RUPA','RELB','RFRM','RWRA','RWRB','RFIN']
        self.segmentList = ['PELO','RFEP','RFEO','RTIO','LFEP','LFEO','LTIO','TRXO','RHUO','RRAO','RHNO','LHUO','LRAO','LHNO','HEDO']
        self.segmentRotList = ['PEL','RFE','RTI','RFO','LFE','LTI','LFO','TRX','RHU','RRA','RHN','LHU','LRA','LHN','HED']

    def createJson(self):
        sig = {}
        for filename in self.fileNames:
            measurementName = os.path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            if '1' in measurementName: #temporaty
                acq = qtools.fileOpen(filename)
                noFrames = acq.GetLastFrame() - acq.GetFirstFrame()
                
                frames = []
                sig[measurementName] = {}
                for frame in range(noFrames):
                    fr = frame + 1
                    frames.append({
                                    "frame": fr,
                                    "markers": self.getMarkersPerFrame(acq,self.markerList,frame),
                                    "segmentPos": self.getMarkersPerFrame(acq,self.segmentList,frame),
                                    "segmentRot": self.combineCardanSeqPerFrame(acq,self.segmentRotList,frame),
                                    "force": self.getForceData(acq,frame,noFrames)
                                    })
                    sig[measurementName] =self.combineCardanSeqPerFrame(acq,self.segmentRotList,frame)
    
                root = {
                        "startTime": acq.GetFirstFrame() / acq.GetPointFrequency(),
                        "endTime": (acq.GetLastFrame() -  acq.GetFirstFrame()) / acq.GetPointFrequency(),
                        "frameRate": acq.GetPointFrequency(),
                        "uncroppedLength": acq.GetLastFrame() / acq.GetPointFrequency(),
                        "labels": [self.labels(acq,self.markerList)],
                        "bones": self.bones(acq),
                        "segments": self.segments(acq),
                        "frames": frames,
                        "force": {
                                "lengthUnit": "mm",
                                "forceUnit": "F",
                                "plates": self.calculateForcePlateInfo(acq)
                                }
                        }
        
#            with open(self.workingDirectory + measurementName + '-3d-data.json', 'w') as f:
#                json.dump(root, f, indent=4,sort_keys=True)
                with open('E:\\Qualisys_repository\\q3dv\\examples\\data\\plugingait.js', 'w') as f:#temporaty
                    f.write('var plugingait = ')#temporaty
                with open('E:\\Qualisys_repository\\q3dv\\examples\\data\\plugingait.js', 'a') as f:#temporaty
                    json.dump(root, f, indent=4,sort_keys=True)#temporaty
        return root

    def getSegAngles(self):
        for filename in self.fileNames:
            measurementName = os.path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            if '1' in measurementName: #temporaty
                acq = qtools.fileOpen(filename)
                noFrames = acq.GetLastFrame() - acq.GetFirstFrame()
                sig = {}
                
                for sigName in self.segmentRotList:
                    if qtools.isPointExist(acq,sigName + 'O'):
                        sig[sigName] = np.array([0,0,0])
                        for frame in range(noFrames):
                            sig[sigName] = np.vstack((sig[sigName],self.combineCardanSeqPerFrame(acq,sigName.split(),frame)))
        return sig

    def labels(self,acq,markerList):
        out = []
        for marker in markerList:
            if qtools.isPointExist(acq,marker):
                out.append({"name": marker})
        return out
    
    def bones(self,acq):
        if qtools.isPointExist(acq,'SACR'):
            bonesLB =[["LTOE","LANK"],["LANK","LTIB"],["LTIB","LKNE"],["LKNE","LTHI"],["LTHI","LASI"],["LASI","SACR"],["RASI","SACR"],["RASI","RTHI"],["RTHI","RKNE"],["RKNE","RTIB"],["RTIB","RANK"],["RANK","RTOE"]]
        if qtools.isPointExist(acq,'LPSI'):
            bonesLB =[["LTOE","LANK"],["LANK","LTIB"],["LTIB","LKNE"],["LKNE","LTHI"],["LTHI","LASI"],["LASI","LPSI"],["LPSI","RPSI"],["RASI","RPSI"],["RASI","RTHI"],["RTHI","RKNE"],["RKNE","RTIB"],["RTIB","RANK"],["RANK","RTOE"]]

        bonesUB = [['LFHD','LBHD'],['LBHD','RBHD'],['RBHD','RFHD'],['LSHO','RSHO'],['LSHO','LELB'],['LELB','LWRB'],['RSHO','RELB'],['RELB','RWRB'],['C7','T10'],['C7','CLAV'],['CLAV','STRN']]
        
        if qtools.isPointExist(acq,'LSHO'):
            bones = bonesLB + bonesUB
        else:
            bones = bonesLB
        return bones

    def segments(self, acq):
        segments = [
                        {"name": "Pelvis",
                         "length": self.getSegmentLength(acq,'RASI','LASI')},
                        {"name": "RThigh",
                         "length": self.getSegmentLength(acq,'RFEP','RFEO')},
                        {"name": "RLeg",
                         "length": self.getSegmentLength(acq,'RFEO','RTIO')},
                        {"name": "RFoot",
                         "length": self.getSegmentLength(acq,'RTIO','RTOE')},
                        {"name": "LThigh",
                         "length": self.getSegmentLength(acq,'LFEP','LFEO')},
                        {"name": "LLeg",
                         "length": self.getSegmentLength(acq,'LFEO','LTIO')},
                        {"name": "LFoot",
                         "length": self.getSegmentLength(acq,'LTIO','LTOE')}
                    ]
        
        if qtools.isPointExist(acq,'LSHO') and qtools.isPointExist(acq,'RSHO'):
            segments.append ({"name": "Thorax",
                     "length": self.getSegmentLength(acq,'LSHO','RSHO')})
        if qtools.isPointExist(acq,'RSHO') and qtools.isPointExist(acq,'RELB'):
            segments.append ({"name": "RArm",
                     "length": self.getSegmentLength(acq,'RSHO','RELB')})
        if qtools.isPointExist(acq,'RELB') and qtools.isPointExist(acq,'RWRB'):
            segments.append ({"name": "RForearm",
                     "length": self.getSegmentLength(acq,'RELB','RWRB')})
        if qtools.isPointExist(acq,'RWRB') and qtools.isPointExist(acq,'RFIN'):
            segments.append ({"name": "RHand",
                     "length": self.getSegmentLength(acq,'RWRB','RFIN')})
        if qtools.isPointExist(acq,'LSHO') and qtools.isPointExist(acq,'LELB'):
            segments.append ({"name": "LArm",
                     "length": self.getSegmentLength(acq,'LSHO','LELB')})
        if qtools.isPointExist(acq,'LELB') and qtools.isPointExist(acq,'LWRB'):
            segments.append ({"name": "LForearm",
                     "length": self.getSegmentLength(acq,'LELB','LWRB')})
        if qtools.isPointExist(acq,'LWRB') and qtools.isPointExist(acq,'LFIN'):
            segments.append ({"name": "LHand",
                     "length": self.getSegmentLength(acq,'LWRB','LFIN')})
        if qtools.isPointExist(acq,'LFHD') and qtools.isPointExist(acq,'RFHD'):
           segments.append ({"name": "Head",
                     "length": self.getSegmentLength(acq,'RFHD','LFHD') * 2})
        
        return segments
 
    def getSegmentCardanSeqPerFrame(self, acq, markerOr, markerAnt, markerProx, frame):
        segObj = segmentCS.LCS()
        
        markerO = np.array(acq.GetPoint(markerOr).GetValues())
        markerA = np.array(acq.GetPoint(markerAnt).GetValues())
        markerP = np.array(acq.GetPoint(markerProx).GetValues())
        
        mo = markerO[frame,:].reshape(3,1)
        ma = markerA[frame,:].reshape(3,1)
        mp = markerP[frame,:].reshape(3,1)
        
        l = np.append(mo,ma,axis=1)
        l = np.append(l,mp,axis=1)
        M = np.array(l)

        if markerOr == 'PELO':
            a = 1
            b = 'x'
            c = [0,0,90] 
        elif markerOr == 'RFEO':
            a = 1
            b = 'x'
            c = [0,0,90] 
        elif markerOr == 'LFEO':
            a = 1
            b = 'x'
            c = [0,0,90] 
        elif markerOr == 'RTIO':
            a = 1
            b = 'x'
            c = [0,0,90] 
        elif markerOr == 'LTIO':
            a = 1
            b = 'x'
            c = [0,0,90] 
        elif markerOr == 'RFOO':
            a = 1
            b = 'x'
            c = [0,0,90] 
        elif markerOr == 'LFOO':
            a = 1
            b = 'x'
            c = [0,0,90] 
        else:
            a = 1
            b = 'x'
            c = [0,0,90] 

        R = segObj.LCS(M,a,b,c)
        q = segObj.ROTtoCAR(R,0,1,2) * 180 / np.pi
        q = np.reshape(q,(1,3)) #swap components
        q = q[:, [1,0,2]]
        q = np.reshape(q,(3,1))
        q = np.ravel(q)
        return q.tolist()

    def combineCardanSeqPerFrame(self, acq, segmentRotList, frame):
        out = []
        for segRot in segmentRotList:
            segRotO = segRot + 'O'
            segRotA = segRot + 'A'
            segRotP = segRot + 'P'
            
            if qtools.isPointExist(acq,segRotO):
                out.append(self.getSegmentCardanSeqPerFrame(acq, segRotO, segRotA, segRotP, frame))
        return out
            
    def getSegmentPosition(self, acq, jointOr):
       jointPos = np.array(acq.GetPoint(jointOr).GetValues())
       return jointPos
   
    def getSegmentLength(self, acq, jointOr1, jointOr2):
        jointPos1 = np.mean(self.getSegmentPosition(acq,jointOr1),axis=0).reshape(1,-1)
        jointPos2 = np.mean(self.getSegmentPosition(acq,jointOr2),axis=0).reshape(1,-1)
        segmentLength = float(distance.cdist(jointPos1, jointPos2,'euclidean'))
        return segmentLength
 
    def getMarkerCoordinates(self, acq, markerName, frame):
        markerPos = np.array(acq.GetPoint(markerName).GetValues())
        mPos = markerPos[frame,:]
        return mPos
    
    def getMarkersPerFrame(self, acq, markerList, frame):
        a = []
        for marker in markerList:
            if qtools.isPointExist(acq,marker):
                b = self.getMarkerCoordinates(acq,marker,frame)
                b = b.tolist()
                a.append(b)
        return a
     
    def calculateForcePlateInfo(self, acq):
        noForcePlates = self.getMetaValue(acq,'FORCE_PLATFORM','USED')
        c = self.getMetaValue(acq,'FORCE_PLATFORM','CORNERS')
        s = len(c)
        co = np.asarray(c).reshape(s/3,3)
        
        plates = []
        corners = {}
        dimensionX = {}
        dimensionY = {}
        dimensionZ = {}
        sizeX = {}
        sizeY = {}
        sizeZ = {}
        origin = {}
        
        i = 0
        j = 4
        for fp in range(int(noForcePlates[0])):
            corners[fp] = co[i:j,:]
            dimensionX[fp] = (np.min(corners[fp][:,0]),np.max(corners[fp][:,0]))
            dimensionY[fp] = (np.min(corners[fp][:,1]),np.max(corners[fp][:,1]))
            dimensionZ[fp] = (np.min(corners[fp][:,2]),np.max(corners[fp][:,2]))
            sizeX[fp] = np.abs(dimensionX[fp][0] - dimensionX[fp][1])
            sizeY[fp] = np.abs(dimensionY[fp][0] - dimensionY[fp][1])
            sizeZ[fp] = np.abs(dimensionZ[fp][0] - dimensionZ[fp][1])
            origin[fp] = ((dimensionX[fp][0] + dimensionX[fp][1]) / 2, (dimensionY[fp][0] + dimensionY[fp][1]) / 2, (dimensionZ[fp][0] + dimensionZ[fp][1]) / 2)
            i = i + 4
            j = j + 4

            plates.append({
                    "id": fp + 1,
                    "name": "",
                    "length": sizeX[fp],
                    "width": sizeY[fp],
                    "origin": origin[fp]}
                )
        return plates
    
    def getMetaValue(self,acq,groupLabelName,scalarName):
        md = acq.GetMetaData()
        fieldFormat = md.FindChild(groupLabelName).value().FindChild(scalarName).value().GetInfo().GetFormatAsString()
        scalarValue = list()
    
        if fieldFormat == "Char":
            sValue = md.FindChild(groupLabelName).value().FindChild(scalarName).value().GetInfo().ToString()
            sValue = list(sValue)
            scalarValue = [i.rstrip() for i in sValue]
        else:
            scalarValue = md.FindChild(groupLabelName).value().FindChild(scalarName).value().GetInfo().ToDouble()
        return scalarValue

    def getForceData(self,acq,frame, noFrames):
        pfe = btk.btkForcePlatformsExtractor()
        grwf = btk.btkGroundReactionWrenchFilter()
        pfe.SetInput(acq)
        pfc = pfe.GetOutput()
        grwf.SetInput(pfc)
        grwc = grwf.GetOutput()
        grwc.Update()
        
        for filename in self.fileNames:
            forceData = []
            acq = qtools.fileOpen(filename)
            
            for forceNumber in range(grwc.GetItemNumber()):
                forceData.append({
                            "id": forceNumber + 1,
                            "forceCount": 1,
                            "forcenumber": 2951,
                            "data": {
                                    "force": list(self.resampleForceData(grwc,forceNumber,0,noFrames)[frame,:]),
                                    "moment": list(self.resampleForceData(grwc,forceNumber,1,noFrames)[frame,:]),
                                    "position": list(self.resampleForceData(grwc,forceNumber,2,noFrames)[frame,:])
                                    }
                            })
        return forceData
    
    def resampleForceData(self, grwc, forceNumber, dataType, noFrames):
        data = np.array(self.extractForceData(grwc, forceNumber)[dataType])
        dataResampled = sci.signal.resample(data, noFrames)
        return dataResampled
    
    def extractForceData(self, grwc, forceNumber):
        force = grwc.GetItem(forceNumber).GetForce().GetValues()
        position = grwc.GetItem(forceNumber).GetPosition().GetValues()
        moment = grwc.GetItem(forceNumber).GetMoment().GetValues()

        return (force, moment, position)

viewerObj = SkeletonViewer(workingDirectory)
a = viewerObj.createJson()

#import matplotlib.pyplot as plt
#plt.plot(a["PEL"][:,:])
#plt.ylabel('degs')
#plt.show()
