from LMIO.wrapper import *
import os
from filecmp import cmp



def testIn(inFile, outFile, testFile, LMIn, testMode):
    LMIn.writeLMIn(inFile, outFile)
    if cmp(inFile, testFile):
        print('Testing ' + testMode + ' LMIn: Pass')
    else:
        print('Testing ' + testMode + ' LMIn: Fail')


tmpDir = 'tmp'
swcFiles = [os.path.join('testFiles', 'HB130605-1NS.swc')]
inFile = os.path.join(tmpDir, 'LMInput.txt')
testFile = os.path.join('testFiles', 'getMeasure', 'LMInput.txt')
outFile = os.path.join(tmpDir, 'LMOutput.txt')

getMeasureLMIn = LMInput(swcFiles, ['Surface'])

testIn(inFile, outFile, testFile, getMeasureLMIn, 'getMeasure')

testFile = os.path.join('testFiles', 'getDist', 'LMInput.txt')




getDistLMIn = LMInput(swcFiles, ['Diameter'], nBins=50, measure2names=['Diameter'])

testIn(inFile, outFile, testFile, getDistLMIn, 'getDist')

testFile = os.path.join('testFiles', 'getDepAverageTrue', 'LMInput.txt')



getDepAverageTrue = LMInput(swcFiles, ['Diameter'], nBins=100, average=True, measure2names=['EucDistance'])

testIn(inFile, outFile, testFile, getDepAverageTrue, 'getDepAverageTrue')

testFile = os.path.join('testFiles', 'getDepAverageFalse', 'LMInput.txt')



getDepAverageFalse = LMInput(swcFiles, ['N_branch'], nBins=100, average=False, measure2names=['EucDistance'])

testIn(inFile, outFile, testFile, getDepAverageFalse, 'getDepAverageFalse')

