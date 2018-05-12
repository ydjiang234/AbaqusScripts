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
    print(tempSkecth.geometry)
    if angle != False:
        tempSkecth.rotate(angle=angle, centerPoint=(0.0,0.0), objectList=[value for key, value in tempSkecth.geometry.items()])
    if vector != False:
        tempSkecth.move(objectList=[value for key, value in tempSkecth.geometry.items()],vector=vector)

    part.Wire(sketch=tempSkecth, sketchOrientation=RIGHT, sketchPlane=plane, sketchPlaneSide=SIDE1, sketchUpEdge=axis)
    del model.sketches[tempSkecth.name]


model = newModelStd('test')
newJob(model, 'test', 4)
tempPoints = [(0.0, 0.0),
                (1.0, 2.0),
                (4.0,1.0),
                ]
kwargs = {
        'name':'test',
        'points':tempPoints        
        }
sketch = newSketch(model, **kwargs)

part = addEmpty3DPart(model, 'test')

xAxisF = addAxis(part, 1)
yAxisF = addAxis(part, 2)
zAxisF = addAxis(part, 3)
yzPlaneF = addYZPlane(part, 0.0)
xzPlaneF = addXZPlane(part, 0.0)
xyPlaneF = addXYPlane(part, 0.0)

xAxis = part.datums[1]
yAxis = part.datums[2]
zAxis = part.datums[3]
yzPlane = part.datums[4]
xzPlane = part.datums[5]
xyPlane = part.datums[6]

sketchKwargs = {
        'sketch':sketch,
        'plane':xyPlane,
        'axis':yAxis,
        'rotate':45,
        'transform':(5.0,5.0),
        }

addSkectchAsWire(model, part, **sketchKwargs)
sketchKwargs = {
        'sketch':sketch,
        'plane':xyPlane,
        'axis':yAxis,
        'rotate':False,
        'transform':False,
        }

addSkectchAsWire(model, part, **sketchKwargs)

