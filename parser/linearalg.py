from animator import *
def scaleVector(array:list,*scalars:float) -> list:
    return [element * scalars[c] for c,element in enumerate(array)]
def scalePoint(array:list,scaleX:float,scaleY:float,ih:float=1,jh:float=1) -> list:
    return scaleVector(array,scaleX*ih,scaleY*jh)
ih = 1
jh = 1
point = [1*ih,1*jh]
nPoint = scalePoint(point,-1,2,ih,jh)
visualizeVectors(point,nPoint)