from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from abaqus import *
from abaqusConstants import *

import os
import sys
sys.path.insert(0,'/home/fe/Documents/abaqus_work/AbaqusScripts/General')
from GeneralFunctions import *

def newJob(model, jobName, nCpus):
    mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF, 
        description='', echoPrint=OFF, explicitPrecision=SINGLE, 
        getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=
        PERCENTAGE, model=model.name, modelPrint=OFF, multiprocessingMode=DEFAULT, 
        name=jobName, nodalOutputPrecision=SINGLE, numCpus=nCpus, numDomains=nCpus, 
        parallelizationMethodExplicit=DOMAIN, queue=None, resultsFormat=ODB, 
        scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)

def deleteModel(model):
    del mdb.models[model.name]
    
def deleteJob(jobName):
    del mdb.jobs[jobName]

def newSketch(model, **kwargs):
    sketchName = kwargs['name']
    sketchPoints = kwargs['points']
    sketch = model.ConstrainedSketch(name=sketchName, sheetSize=200.0)
    for i in range(len(sketchPoints)):
        point1 = sketchPoints[i]
        if i != len(sketchPoints)-1:
            point2 = sketchPoints[i+1]
        else:
            point2 = sketchPoints[0]
        sketch.Line(point1=point1, point2=point2)


    sketch = model.ConstrainedSketch(name=sketchName, objectToCopy=sketch)

    return sketch

def addXYPlane(part, offset):
    return part.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=offset)

def addXZPlane(part, offset):
    return part.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offset)

def addYZPlane(part, offset):
    return part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offset)

def addEmpty3DPart(model, partName):
    part = model.Part(dimensionality=THREE_D, name=partName, type=DEFORMABLE_BODY)
    return part

def addAxis(part, axis):
    if axis == 1:
        Axis = part.DatumAxisByPrincipalAxis(principalAxis=XAXIS)
    elif axis == 2:
        Axis = part.DatumAxisByPrincipalAxis(principalAxis=YAXIS)
    elif axis == 3:
        Axis = part.DatumAxisByPrincipalAxis(principalAxis=ZAXIS)
    return Axis

def addSkectchAsWire(model, part, **kwargs):
    sketch = kwargs['sketch']
    plane = kwargs['plane']
    axis = kwargs['axis']
    angle = kwargs['rotate']
    vector = kwargs['transform']

    tempSkecth = model.ConstrainedSketch(name='__profile__', sheetSize=1000.0, transform= part.MakeSketchTransform(sketchPlane=plane, sketchPlaneSide=SIDE1, sketchUpEdge=axis, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
    part.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=tempSkecth)
    tempSkecth.retrieveSketch(sketch=sketch)
    if angle != False:
        tempSkecth.rotate(angle=angle, centerPoint=(0.0,0.0), objectList=[value for key, value in tempSkecth.geometry.items()])
    if vector != False:
        tempSkecth.move(objectList=[value for key, value in tempSkecth.geometry.items()],vector=vector)

    part.Wire(sketch=tempSkecth, sketchOrientation=RIGHT, sketchPlane=plane, sketchPlaneSide=SIDE1, sketchUpEdge=axis)
    del model.sketches[tempSkecth.name]

def getNewaddItem(curDict, preItemList):
    for key,item in curDict.items():
        if item not in preItemList:
            break
    preItemList.append(item)
    return item, preItemList

def getNewaddItemList(curDict, preItemList):
    out = []
    for item in curDict:
        if item not in preItemList:
           out.append(item)
    preItemList.extend(out)
    return out, preItemList

model = newModelStd('test')
newJob(model, 'test', 4)
tempPoints = [(-1.0, -1.0),
                (1.0, -1.0),
                (1.0,1.0),
                (-1.0,1.0),
                ]
kwargs = {
        'name':'test',
        'points':tempPoints        
        }
sketch = newSketch(model, **kwargs)

part = addEmpty3DPart(model, 'test')
partDatumList = []
partEdgeList = []
partSectionEdgeList = []

yAxisF = addAxis(part, 2)
yAxis, partDatumList = getNewaddItem(part.datums, partDatumList)

for i in range(5):
    xyPlaneF = addXYPlane(part, i*5.0)
    xyPlane, partDatumList = getNewaddItem(part.datums, partDatumList)
    sketchKwargs = {
        'sketch':sketch,
        'plane':xyPlane,
        'axis':yAxis,
        'rotate':i*5,
        'transform':(i,i*2),
        }
    addSkectchAsWire(model, part, **sketchKwargs)
    out, partEdgeList = getNewaddItemList(part.edges, partEdgeList)
    partSectionEdgeList.append(out)
    print(partSectionEdgeList[0][0])
    

#part.ShellLoft(endCondition=NONE, loftsections=[partSectionEdgeList[0], partSectionEdgeList[3]], startCondition=NONE)
