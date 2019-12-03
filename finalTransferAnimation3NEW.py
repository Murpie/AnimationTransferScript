import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt
import os
import math

tGUIJoints = []
sGUIJoints = []
index = 0

sRotations = []
sOrientations = []
sJoints = []

tRotations = []
tOrientations = []
tJoints = []
tJointsFinalMatrix = []

def getParentMatrix(sJoint, tJoint):
    sparentMatrix = dt.Matrix()
    tparentMatrix = dt.Matrix()
    sIndex = 0
    for parents in sJoint.getParent( generations = None):
        sIndex = 0
        for Joints in sJoints:
            if parents == Joints:
                sparentMatrix *= (sOrientations[sIndex] * sRotations[sIndex])
            sIndex += 1
            
    tIndex = 0            
    for parents in tJoint.getParent( generations = None):
        tIndex = 0
        for Joints in tJoints:
            if parents == Joints:
                tparentMatrix *= (tOrientations[tIndex] * tRotations[tIndex])
            tIndex += 1
 
    return sparentMatrix, tparentMatrix
    

def applyAnimation(keyFrame, sUIJoints, tUIJoints):
    
    sourceUIIndex = []
    sourceIndex = []
    for x, joints in enumerate(sUIJoints):
        sourceUIIndex.append(x)
        for index in range(0,len(sJoints)):
            if(sJoints[index] == joints):
                sourceIndex.append(index)
    
    targetUIIndex = []
    targetIndex = []
    for x, joints in enumerate(tUIJoints):
        targetUIIndex.append(x)
        for index in range(0, len(tJoints)):
            if (tJoints[index] == joints):
                targetIndex.append(index)
    
    
    elements=len(sourceUIIndex)
    if elements > len(targetUIIndex):
        elements = len(targetUIIndex)
    for i in range(0,elements):
        translatedRotation = tJointsFinalMatrix[sourceIndex[i]]
       
        pm.setKeyframe(tJoints[targetIndex[i]], v=translatedRotation[0], at='rotateX', t=(keyFrame, keyFrame))
        pm.setKeyframe(tJoints[targetIndex[i]], v=translatedRotation[1], at='rotateY', t=(keyFrame, keyFrame))
        pm.setKeyframe(tJoints[targetIndex[i]], v=translatedRotation[2], at='rotateZ', t=(keyFrame, keyFrame))

        

def transferMatrices(tIndex, sUIJoints, tUIJoints, currentKF):
    
    tRIndex = 0
    for joints in tJoints:
        if joints == tUIJoints[tIndex]:
            break
        tRIndex += 1
        
    sRIndex = 0
    for joints in sJoints:
        if joints == sUIJoints[tIndex]:
            break
        sRIndex += 1
    

    sOrientation = sOrientations[sRIndex]
    sCurrentRotation = sJoints[sRIndex].getRotation().asMatrix()
    tOrientation = tOrientations[tRIndex]
    tCurrentRotation = tJoints[tRIndex].getRotation().asMatrix()
    
    SPM, TPM = getParentMatrix(sJoints[sRIndex], tJoints[tRIndex])
    
    isolatedRotation = sRotations[sRIndex].inverse() * sCurrentRotation
    worldSpaceRotation = sOrientation.inverse() * SPM.inverse() * isolatedRotation * SPM * sOrientation
    translatedRotation = tOrientation * TPM * worldSpaceRotation * TPM.inverse() * tOrientation.inverse()
    translatedRotation = tRotations[tRIndex] * translatedRotation
    finalRotation = dt.degrees(dt.EulerRotation(translatedRotation))
    tJointsFinalMatrix.append(finalRotation)
    
    
    pm.setKeyframe(tJoints[tRIndex], v=finalRotation[0], at='rotateX', t=(currentKF, currentKF))
    pm.setKeyframe(tJoints[tRIndex], v=finalRotation[1], at='rotateY', t=(currentKF, currentKF))
    pm.setKeyframe(tJoints[tRIndex], v=finalRotation[2], at='rotateZ', t=(currentKF, currentKF))
    
    
    tIndex += 1
    
    if tIndex < len(tUIJoints) and tIndex < len(sUIJoints):
        transferMatrices(tIndex, sUIJoints, tUIJoints, currentKF)




        
def fixList(source, list1, list2, list3):
    list1.append(source.getRotation().asMatrix())
    list2.append(source.getOrientation().asMatrix())
    list3.append(source)  
    
    for child in source.getChildren():
        if(pm.nodeType(child)=="joint"):
            if child.numChildren() > 0:
                fixList(child, list1, list2, list3)
                
def fixList2(list1, list2, list3, list4, list5, list6, UIList1, UIList2, i):
    list1.append(UIList1[i].getRotation().asMatrix())
    list2.append(UIList1[i].getOrientation().asMatrix())
    list3.append(UIList1[i])
    list4.append(UIList2[i].getRotation().asMatrix())
    list5.append(UIList2[i].getOrientation().asMatrix())
    list6.append(UIList2[i])
    
    i += 1
    if i < len(UIList1) and i < len(UIList2):
        fixList2(list1, list2, list3, list4, list5, list6, UIList1, UIList2, i)
    
def fixBeforeTransfer():
    pm.currentTime(0)
    del sJoints[:]
    del tJoints[:]
    del tOrientations[:]
    del tRotations[:]
    del sRotations[:]
    del sOrientations[:]
    rootSource = pm.ls(sl = True, type="joint")[0]
    rootTarget = pm.ls(sl = True, type="joint")[1]
    fixList(rootSource, sRotations, sOrientations, sJoints)
    fixList(rootTarget, tRotations, tOrientations, tJoints)
    return sJoints, tJoints       

        
def transferAnimation(startFrame, endFrame, UIsJoints, UItJoints):
    pm.currentTime(0)

    
    del sJoints[:]
    del tJoints[:]
    del tOrientations[:]
    del tRotations[:]
    del sRotations[:]
    del sOrientations[:]
    del tJointsFinalMatrix[:]

    
    rootSource = pm.ls(sl = True, type="joint")[0]
    rootTarget = pm.ls(sl = True, type="joint")[1]
    
    whileCondition = 0
    keyframeNumber = startFrame
    fixList(rootSource, sRotations, sOrientations, sJoints)
    fixList(rootTarget, tRotations, tOrientations, tJoints)
    
    for i in range(startFrame, endFrame):
        pm.currentTime(keyframeNumber)
        global index
        index = 0
        sParentMatrix = dt.Matrix()
        tParentMatrix = dt.Matrix()
        tIndex = 0
        
        sourceTranslation = rootSource.getTranslation()
        rootTarget.setTranslation(sourceTranslation)
        
        pm.setKeyframe(tJoints[0], v=sourceTranslation[0], at='translateX', t=(keyframeNumber, keyframeNumber))
        pm.setKeyframe(tJoints[0], v=sourceTranslation[1], at='translateY', t=(keyframeNumber, keyframeNumber))
        pm.setKeyframe(tJoints[0], v=sourceTranslation[2], at='translateZ', t=(keyframeNumber, keyframeNumber))
        
        transferMatrices(tIndex, UIsJoints, UItJoints, keyframeNumber)
        #applyAnimation(keyframeNumber, UIsJoints, UItJoints)
        
        del tJointsFinalMatrix[:]
        keyframeNumber += 1


#sJointList, tJointList = fixBeforeTransfer()
#transferAnimation(0, 20, sJointList, tJointList)     