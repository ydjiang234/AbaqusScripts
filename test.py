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
newSketch(model, **kwargs)
