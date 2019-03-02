from pylmeasure import *
import os
from filecmp import cmp


def compare_outputs(inFile, outFile, testFile, LMIn, testMode):
    LMIn.writeLMIn(inFile, outFile)
    inFile = os.path.join(os.getcwd(),inFile)
    outFile = os.path.join(os.getcwd(), outFile)
    testFile = os.path.join(os.getcwd(), testFile)

    if os.system("diff -w " + inFile + " " + testFile) == 0:
        print('Testing ' + testMode + ' LMIn: Pass')
    else:
        print('Testing ' + testMode + ' LMIn: Fail. Result file is different from expected. Result: ' + inFile + ". Expected: " + testFile)


tmpDir = 'tmp'
swcFiles = [os.path.join('tests/testFiles', 'HB130605-1NS.swc')]
inFile = os.path.join(tmpDir, 'LMInput.txt')
testFile = os.path.join('tests/testFiles', 'getMeasure', 'LMInput.txt')
outFile = os.path.join(tmpDir, 'LMOutput.txt')

def test_getMeasureLMIn():
    getMeasureLMIn = LMInput(swcFiles, ['Surface'])
    compare_outputs(inFile, outFile, testFile, getMeasureLMIn, 'getMeasure')


def test_getDistLMIn():
    testFile = os.path.join('tests/testFiles', 'getDist', 'LMInput.txt')
    getDistLMIn = LMInput(swcFiles, ['Diameter'], nBins=50, measure2names=['Diameter'])
    compare_outputs(inFile, outFile, testFile, getDistLMIn, 'getDist')


def test_getDepAverageTrue():
    testFile = os.path.join('tests/testFiles', 'getDepAverageTrue', 'LMInput.txt')
    getDepAverageTrue = LMInput(swcFiles, ['Diameter'], nBins=100, average=True, measure2names=['EucDistance'])
    compare_outputs(inFile, outFile, testFile, getDepAverageTrue, 'getDepAverageTrue')


def test_getDepAverageFalse():
    testFile = os.path.join('tests/testFiles', 'getDepAverageFalse', 'LMInput.txt')
    getDepAverageFalse = LMInput(swcFiles, ['N_branch'], nBins=100, average=False, measure2names=['EucDistance'])
    compare_outputs(inFile, outFile, testFile, getDepAverageFalse, 'getDepAverageFalse')

