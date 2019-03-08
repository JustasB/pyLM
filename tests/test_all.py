from pylmeasure import *
from pylmeasure.util.morphometricMeasurements import getMorphMeasures
import pytest

swcFiles = ['tests/testFiles/HB130408-1NS_VB.swc']

def test_documentation():
    import os
    os.system("jupyter nbconvert --to python --output usage.py 'PyLMeasure Usage.ipynb'")
    os.system("sed -i '1iimport matplotlib; matplotlib.use(\"Agg\");' usage.py") # Disable interactive plots
    import usage # Fail on any notebook errors

## Usage Example getMeasureDistribution
def test_getMeasureDistribution():
    LMOutput = getMeasureDistribution(['Pk_classic'], swcFiles, nBins=50)

    assert LMOutput[0]['measure1BinCentres'][0][0] == 0.057149
    assert LMOutput[0]['measure1BinCounts'][0][0] == 3

## # Usage Example getMeasure
def test_getMeasure():
    LMOutput = getMeasure(['Surface'], swcFiles)
    assert LMOutput[0]['WholeCellMeasures'][0][4] == 4.24798

def test_getOneMeasure():
    LMOutput = getOneMeasure('Surface', swcFiles[0])
    assert LMOutput["TotalSum"] == 49599.4

def test_getOneMeasurePCA():
    LMOutputReg = getOneMeasure('Height', swcFiles[0])
    LMOutputPCA = getOneMeasure('Height', swcFiles[0],PCA=True)

    assert LMOutputReg["Maximum"] != LMOutputPCA["Maximum"]

def test_getOneMeasureWithSpecificityGT():
    LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Type > 1")
    assert LMOutput["TotalSum"] == 49582.2

def test_getOneMeasureWithSpecificityLT():
    LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Type < 1")
    assert LMOutput["TotalSum"] == 0

def test_getOneMeasureWithSpecificityEQ():
    LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Type == 1")
    assert LMOutput["TotalSum"] == 17.2021

def test_getOneMeasureWithSpecificityOR():
    LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Type == 1 or Type == 2")
    assert LMOutput["TotalSum"] == 17.2021

def test_getOneMeasureWithSpecificityAND():
    LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Type < 2 and Type < 3")
    assert LMOutput["TotalSum"] == 17.2021

def test_getOneMeasureWithSpecificityInvalidSWCPath():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', "XYZ")

def test_getOneMeasureWithSpecificityInvalidForm():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="XYZ")

def test_getOneMeasureWithSpecificityInvalidEQ():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Type = 1")

def test_getOneMeasureWithSpecificityInvalidGEQ():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Type >= 1")

def test_getOneMeasureWithSpecificityInvalidXYZ():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="XYZ == 1")

def test_getOneMeasureWithSpecificityInvalidFunc():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Surface3 == 1")

def test_getOneMeasureWithSpecificityInvalidLogical():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', swcFiles[0], specificity="Type < 2 xor Type < 3")

def test_getOneMeasureWithSpecificityInvalidValue():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface', swcFiles[0],specificity="Diameter == 1.0.1111")

def test_getOneMeasureInvalidFunc():
    with pytest.raises(Exception):
        LMOutput = getOneMeasure('Surface321', swcFiles[0])

# Usage Example getMeasureDependence without averaging
def test_getMeasureDependence_without_averaging():
    LMOutput = getMeasureDependence(['N_branch'], ['EucDistance'], swcFiles, nBins=100, average=False)
    assert LMOutput[0]['measure1BinCentres'][0][0] == 0.950399
    assert LMOutput[0]['measure2BinSums'][0][0] == 0

# Usage Example getMeasureDependence with averaging
def test_getMeasureDependence_with_averaging():
    LMOutput = getMeasureDependence(['Diameter'], ['EucDistance'], swcFiles, nBins=100, average=True)

    assert LMOutput[0]['measure1BinCentres'][0][0] == 0.950399
    assert LMOutput[0]['measure2BinAverages'][0][0] == 2.221
    assert LMOutput[0]['measure2BinStdDevs'][0][0] == 0.168291


def test_getMorphMeasures():
    result = getMorphMeasures(swcFiles[0])

    assert result["scalarMeasurements"]["Width"].magnitude == 174.758

if __name__ == "__main__":
    test_getMeasureDistribution()
    test_getMeasure()
    test_getMeasureDependence_without_averaging()
    test_getMeasureDependence_with_averaging()