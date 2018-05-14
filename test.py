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
    isClose = kwargs['isClose']

    tempSkecth = model.ConstrainedSketch(name='__profile__', sheetSize=1000.0, transform= part.MakeSketchTransform(sketchPlane=plane, sketchPlaneSide=SIDE1, sketchUpEdge=axis, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
    part.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=tempSkecth)
    tempSkecth.retrieveSketch(sketch=sketch)
    if angle != False:
        tempSkecth.rotate(angle=angle, centerPoint=(0.0,0.0), objectList=[value for key, value in tempSkecth.geometry.items()])
    if vector != False:
        tempSkecth.move(objectList=[value for key, value in tempSkecth.geometry.items()],vector=vector)
    
    if isClose:
        part.Shell(sketch=tempSkecth, sketchOrientation=RIGHT, sketchPlane=plane, sketchPlaneSide=SIDE1, sketchUpEdge=axis)
    else:
        part.Wire(sketch=tempSkecth, sketchOrientation=RIGHT, sketchPlane=plane, sketchPlaneSide=SIDE1, sketchUpEdge=axis)
    del model.sketches[tempSkecth.name]

def getNewaddItem(curDict, preItemList, Type='dict'):
    if Type == 'dict': 
        for key,item in curDict.items():
            if item not in preItemList:
                break
        preItemList.append(item)
    elif Type == 'list':
        for item in curDict:
            if item not in preItemList:
                break
        preItemList.append(item)
    return item, preItemList

def getNewaddItemList(curDict, preItemList, Type='dict'):
    out = []
    if Type == 'dict':
        for key,item in curDict.items():
            if item not in preItemList:
               out.append(item)
    elif Type == 'list':
        for item in curDict:
            if item not in preItemList:
               out.append(item)
        preItemList.extend(out)
    return out, preItemList

def getEdgesByPointOn(pointOnList, edges):
    out = []
    for edge in edges:
        if edge.pointOn in pointOnList:
            out.append(edge)
    return out

def addLayers(mLayer, **kwargs):
    for i in range(kwargs['layerNum']):
        mLayer.CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material=kwargs['material'][i].name, numIntPoints=kwargs['intPointNum'][i], orientationType=SPECIFY_ORIENT, orientationValue=kwargs['angle'][i], plyName=kwargs['name'][i], region=kwargs['set'][i], suppressed=False, thickness=kwargs['thickness'][i], thicknessType=SPECIFY_THICKNESS)

def addEmptyMLayer(part, **kwargs):
    mLayer = part.CompositeLayup(description='', elementType=SHELL, name=kwargs['name'], offsetType=kwargs['offsetType'], symmetric=False, thicknessAssignment=FROM_SECTION)
    mLayer.Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)
    mLayer.ReferenceOrientation(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, flipNormalDirection=False, flipPrimaryDirection=False, localCsys=None, normalAxisDefinition=SURFACE, normalAxisDirection=AXIS_3, normalAxisRegion=kwargs['normalSurface'], orientationType=DISCRETE, primaryAxisDefinition=VECTOR, primaryAxisDirection=AXIS_1, primaryAxisVector=kwargs['dirVector'], stackDirection=STACK_3)
    return mLayer

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
partEdgePointOnList = []
partSectionEdgePointOnList = []

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
        'isClose':False,
        }
    if i==4:
        sketchKwargs['isClose'] = True
    addSkectchAsWire(model, part, **sketchKwargs)
    out, partEdgeList = getNewaddItemList([item.pointOn for item in part.edges], partEdgePointOnList, Type='list')
    partSectionEdgePointOnList.append(out)
    
loftsections = [getEdgesByPointOn(item, part.edges) for item in partSectionEdgePointOnList]

part.ShellLoft(endCondition=NONE, loftsections=loftsections, startCondition=NONE)


material = model.Material(name='Material-1')
material.Elastic(table=((200000.0, 0.3), ))


set1 = part.Set(name = 'mLayerRegion',faces=part.faces.findAt([(0.0,1.0,0.0)]))
set2 = part.Set(name='mLayerDirection', edges=part.edges.findAt([(1.0,1.0, 0.0)]))
surface1 = part.Surface(name = 'mLayerRegionNormal',side1Faces=part.faces.findAt([(0.0,1.0,0.0)]))


compositeKwargs = {
                    'name': 'composite1',
                    'offsetType': TOP_SURFACE,
                    'normalSurface': surface1,
                    'dirVector': (0.0,0.0,1.0),
                    }
mLayer = addEmptyMLayer(part, **compositeKwargs)

#mLayer.CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='Material-1', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=set1, suppressed=False, thickness=0.1, thicknessType=SPECIFY_THICKNESS)
mLayerKwargs = {'layerNum':9}
mLayerKwargs['name'] = ['layer-{0:.0f}'.format(i+1) for i in range(mLayerKwargs['layerNum'])]
mLayerKwargs['set'] = [set1 for i in range(mLayerKwargs['layerNum'])]
mLayerKwargs['intPointNum'] = [(i+1)*2+1 for i in range(mLayerKwargs['layerNum'])]
mLayerKwargs['material'] = [material for i in range(mLayerKwargs['layerNum'])]
mLayerKwargs['thickness'] = [(i+1)*0.01 for i in range(mLayerKwargs['layerNum'])]
mLayerKwargs['angle'] = []
for i in range(mLayerKwargs['layerNum']):
    if i%3==0:
        mLayerKwargs['angle'].append(0.0)
    elif i%3==1:
        mLayerKwargs['angle'].append(45.0)
    elif i%3==2:
        mLayerKwargs['angle'].append(-45.0)

addLayers(mLayer, **mLayerKwargs)
