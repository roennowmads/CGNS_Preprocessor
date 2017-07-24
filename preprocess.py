import math
import os, os.path
import struct

def processFilePositions(indices, oldToNewIndex, dir, filename, valuePerLine, columnOffset):
    fIn = open(dir + "/" + filename)
    filenameNoExt = os.path.splitext(filename)[0]
    
    fOut = open("Output/" + filenameNoExt + ".pos.bytes", "wb+")

    numberOfFinalPoints = 0
    
    #skip first line
    fIn.readline()
    index = 0
    for i, line in enumerate(fIn):
        if i in indices:
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
            
            oldToNewIndex[i] = index
            
            index += 1

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
    
    
'''def runPreprocess(directory, minMag, maxMag, numberOfPoints, scalarProperty):
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
        
    print minMagnitude, maxMagnitude'''

    
def readBinaryPosFile(filename):
    filenameNoExt = os.path.splitext(filename)[0]

    with open('Output/' + filenameNoExt + ".pos.bytes", "rb") as f:
        xyzBin = f.read(4*3)
        while xyzBin:
            # Do stuff with byte.
            #x = struct.unpack("f", float)[0]
            #float = f.read(4)
            
            #y = struct.unpack("f", float)[0]
            #float = f.read(4)
            
            #z = struct.unpack("f", float)[0]
            #print xyz
            
            xyz = struct.unpack('f'*3, xyzBin)
            #print xyz
            
            print str(xyz[0]) + " " + str(xyz[1]) + " " + str(xyz[2])
            
            #print x,y,z
            #float = f.read(4)
            
            xyzBin = f.read(4*3)
    
    
    
def findMinMax(dir, filenames):
    min = float("inf")
    max = float("-inf")

    for filename in filenames:
        print filename
        with open(dir + "/" + filename) as f:
            f.readline()
            for line in f:
                strippedLined = line.strip()
                lines = strippedLined.split(',')
                magnitude = float(lines[0])
                if magnitude < min:
                    min = magnitude
                    print min, max
                elif magnitude > max:
                    max = magnitude
                    print min, max
                    
    print min, max
    return min, max
    
    
def findUsedIndices(indices, dir, filename, minDesired, maxDesired):
    fIn = open(dir + "/" + filename)
    
    #skip first line
    fIn.readline()	
    for i, line in enumerate(fIn):
        strippedLined = line.strip()
        lines = strippedLined.split(',')
        magnitude = float(lines[0])
        
        if magnitude >= minDesired and magnitude <= maxDesired:
            if i not in indices:
                indices[i] = True
                
                #if len(indices) % 10000 == 0:
                #    print magnitude, len(indices)
           
    fIn.close()
    print len(indices)
    
def createValuesFileAndIndexFile(indices, oldToNewIndex, dir, filename, minMag, maxMag, minDesired, maxDesired):
    fIn = open(dir + "/" + filename)
    filenameNoExt = os.path.splitext(filename)[0]
    fOut = open("Output/" + filenameNoExt + ".bytes", "wb+")
    
    #skip first line
    fIn.readline()	
    for i, line in enumerate(fIn):
        if i in indices:
            strippedLined = line.strip()
            lines = strippedLined.split(',')
            magnitude = float(lines[0])
            
            if magnitude >= minDesired and magnitude <= maxDesired:
                bytes = struct.unpack('4B', struct.pack('<I', oldToNewIndex[i]))
                
                value = int(((magnitude - minMag) / (maxMag - minMag)) * 255.0) #x -> 0-255
                #data = struct.pack('B', value) #pack values as binary byte 
                
                #We pack the 8bit color value along with the 24bit position index:
                val = struct.unpack('I', bytearray([value]) + bytearray(bytes[0:3]))[0]
                
                packedValue = struct.pack('I', val)
                fOut.write(packedValue)          
           
    fIn.close()
    fOut.close()
    

def runPreprocess(minDesired, maxDesired):
    dir = 'Data' + '/output'
    filenames = [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    numFiles = len(filenames)

    print numFiles
    
    minMag = 0.0
    maxMag = 0.735
    
    
    
    indices = {}
    for filename in filenames:
        findUsedIndices(indices, dir, filename, minDesired, maxDesired)
    
    
    oldToNewIndex = {}
    processFilePositions(indices, oldToNewIndex, dir, filenames[0], [], 1)
    
    for filename in filenames:
        createValuesFileAndIndexFile(indices, oldToNewIndex, dir, filename, minMag, maxMag, minDesired, maxDesired)   
    
    #findMinMax(dir, filenames)
    #Oil Rig: min: 0.0, max: 0.735
    
    #readBinaryPosFile(filenames[0])
    
runPreprocess(0.01, 1.0)


















