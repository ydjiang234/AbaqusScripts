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


def newModelStd(modelName):
    return mdb.Model(modelType=STANDARD_EXPLICIT, name=modelName)
