from paraview import simple, vtk
import os, os.path, sys
import preprocess
import glob
import math

if __name__ == '__main__':
    directory = 'Data'
    files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))]
    
    outDir = directory + '/output'
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    else:
        filesOut = glob.glob(outDir + '/*')
        for f in filesOut:
            os.remove(f)
	
    rangeMin = float("inf")
    rangeMax = float("-inf")
    numberOfPoints = 0
    
    attribute = sys.argv[1]#"CH4methaneIG.MassFraction"
    scalarProperty = True
    
    for i, file in enumerate(files):
        print "Processing: " + file
        reader = simple.OpenDataFile(directory + "/" + file)
        reader.PointArrayStatus = [attribute]
        reader.UpdatePipeline()
        info = reader.GetDataInformation().DataInformation
        arrayInfo = info.GetArrayInformation(attribute, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS)
        numberOfPoints = arrayInfo.GetNumberOfTuples()
        
        #if property is a 3D vector instead of a scalar we need to get the other component values as well:
        rangeX = arrayInfo.GetComponentRange(0)  #all the cgns files need to be loaded in in order to get the real range.
        
        if scalarProperty:
            if rangeMin > rangeX[0]:
                rangeMin = rangeX[0]
        
            if rangeMax < rangeX[1]:
                rangeMax = rangeX[1]
        else:        
            rangeY = arrayInfo.GetComponentRange(1)
            rangeZ = arrayInfo.GetComponentRange(2)
            
            #localRangeMin = math.sqrt(rangeX[0]*rangeX[0] + rangeY[0]*rangeY[0] + rangeZ[0]*rangeZ[0])
            localRangeMax = math.sqrt(rangeX[1]*rangeX[1] + rangeY[1]*rangeY[1] + rangeZ[1]*rangeZ[1])
            
            rangeMin = 0 #The range output from paraview stores the minimum for each value, I calculate an absolute value, so my minimum will always be >=0.
            #if rangeMin > localRangeMin:
            #    rangeMin = localRangeMin
        
            if rangeMax < localRangeMax:
                rangeMax = localRangeMax        
        
        writer = simple.CreateWriter(directory + "/output/" + "frame" + str(i) + ".csv", reader)
        writer.WriteAllTimeSteps = 1
        writer.FieldAssociation = "Points"
        writer.UpdatePipeline()
        simple.Delete() #Avoids memory leak
        print "File processed: " + file
        
    print rangeMin, rangeMax, numberOfPoints

    #Run preprocess directly after:
    preprocess.runPreprocess(directory, rangeMin, rangeMax, numberOfPoints, scalarProperty)
