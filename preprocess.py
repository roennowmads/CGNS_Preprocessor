import math
import os, os.path
import struct

def processFilePositions(dir, filename, valuePerLine, columnOffset):
    fIn = open(dir + "/" + filename)
    filenameNoExt = os.path.splitext(filename)[0]
    
    fOut = open("Output/" + filenameNoExt + ".pos.bytes", "wb+")

    numberOfFinalPoints = 0
    
    #skip first line
    fIn.readline()	
    for i, line in enumerate(fIn):
        #if valuePerLine[i] <> 0:
        strippedLined = line.strip()
        lines = strippedLined.split(',')
        
        x = float(lines[columnOffset])
        y = float(lines[columnOffset + 1])
        z = float(lines[columnOffset + 2])

        dataX = struct.pack('f',x)
        dataY = struct.pack('f',y)
        dataZ = struct.pack('f',z)

        fOut.write(dataX)
        fOut.write(dataY)
        fOut.write(dataZ)
        numberOfFinalPoints += 1
            

        if (i % 100000) == 0:
            print "Positions processed:", i
    
    fIn.close()
    fOut.close()
    print numberOfFinalPoints


def findInterestingFileValues(dir, filename, valuePerLine, fileData, scalarProperty):
    fIn = open(dir + "/" + filename)

    #skip first line
    fIn.readline()	
    for i, line in enumerate(fIn):
        strippedLined = line.strip()
        lines = strippedLined.split(',')
        magnitude = float(lines[0])
        if not scalarProperty:
            x = magnitude
            y = float(lines[1])
            z = float(lines[2])
            magnitude = math.sqrt(x*x + y*y + z*z)
        
        value = int(((magnitude - minMagnitude) / (maxMagnitude - minMagnitude)) * 255.0) #x -> 0-255
        
        fileData.append(value)
        
        #valuePerLine[i] += value        
    fIn.close()
	

def processFileValues(dir, filename, valuePerLine, fileData):
    filenameNoExt = os.path.splitext(filename)[0]
    fOut = open("Output/" + filenameNoExt + ".bytes", "wb+")
    for i, value in enumerate(fileData):
        #if valuePerLine[i] <> 0:
        #print value
        data = struct.pack('B', value) #pack values as binary byte 
        fOut.write(data)
    fOut.close()
    
    
def runPreprocess(directory, minMag, maxMag, numberOfPoints, scalarProperty):
    dir = directory + '\output'
    filenames = [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    numFiles = len(filenames)
    valuePerLine = [0] * numberOfPoints
    
    global maxMagnitude
    maxMagnitude = maxMag
    
    global minMagnitude
    minMagnitude = minMag
    
    print "Min max:", minMag, maxMag
    
    columnOffset = 3
    if scalarProperty:
        columnOffset = 1

    print ""
    print "Finding permanent zeroes in values data..."
    filesData = []
    for filename in filenames:
        fileData = []
        findInterestingFileValues(dir, filename, valuePerLine, fileData, scalarProperty)
        print filename + " processed"
        filesData.append(fileData)
        
    print ""
    print "Creating binary files..."
    for i, filename in enumerate(filenames):
        fileData = filesData[i]
        processFileValues(dir, filename, valuePerLine, fileData)
        print filename + " processed"
        
    print ""
    print "Processing positions..."
    processFilePositions(dir, filenames[0], valuePerLine, columnOffset)
        
    print minMagnitude, maxMagnitude
