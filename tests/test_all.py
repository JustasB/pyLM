print("starting...")
import os; print("Working in: ", os.getcwd());

from pylmeasure import *
from pylmeasure.util.morphometricMeasurements import getMorphMeasures

swcFiles = ['tests/testFiles/HB130408-1NS_VB.swc']

# swcFiles = ["tests/testFiles/D00V00C00S00_3ptSoma.swc",
#              "tests/testFiles/D15V10C00S00_3ptSoma.swc",
#              "tests/testFiles/HB130313-4NS.swc",
#              "tests/testFiles/HB130408-1NS_VB.swc",
#              "tests/testFiles/HB130605-1NS.swc"]

##*********************************************************************************************************************
## Usage Example getMeasureDistribution
##*********************************************************************************************************************
def test_getMeasureDistribution():
    LMOutput = getMeasureDistribution(['Pk_classic'], swcFiles, nBins=50)

    assert LMOutput[0]['measure1BinCentres'][0][0] == 0.057149
    assert LMOutput[0]['measure1BinCounts'][0][0] == 3

##*********************************************************************************************************************

##*********************************************************************************************************************
## # Usage Example getMeasure
##*********************************************************************************************************************
def test_getMeasure():
    LMOutput = getMeasure(['Surface'], swcFiles)
    assert LMOutput[0]['WholeCellMeasures'][0][4] == 4.24798


def test_getOneMeasure():
    LMOutput = getOneMeasure('Surface', swcFiles[0])
    assert LMOutput["TotalSum"] == 49599.4

##*********************************************************************************************************************

#*********************************************************************************************************************
# Usage Example getMeasureDependence without averaging
#*********************************************************************************************************************
def test_getMeasureDependence_without_averaging():
    LMOutput = getMeasureDependence(['N_branch'], ['EucDistance'], swcFiles, nBins=100, average=False)
    assert LMOutput[0]['measure1BinCentres'][0][0] == 0.950399
    assert LMOutput[0]['measure2BinSums'][0][0] == 0

    # plt.figure()
    # plt.plot(LMOutput[0]['measure1BinCentres'][0], LMOutput[0]['measure2BinSums'][0], 'ro', mfc='r', ms=5)
    # plt.draw()
    # plt.show(block=False)

#*********************************************************************************************************************

#*********************************************************************************************************************
# Usage Example getMeasureDependence with averaging
#*********************************************************************************************************************
def test_getMeasureDependence_with_averaging():
    LMOutput = getMeasureDependence(['Diameter'], ['EucDistance'], swcFiles, nBins=100, average=True)

    assert LMOutput[0]['measure1BinCentres'][0][0] == 0.950399
    assert LMOutput[0]['measure2BinAverages'][0][0] == 2.221
    assert LMOutput[0]['measure2BinStdDevs'][0][0] == 0.168291

    # plt.figure()
    # plt.errorbar(LMOutput[0]['measure1BinCentres'][0],
    #              LMOutput[0]['measure2BinAverages'][0],
    #              LMOutput[0]['measure2BinStdDevs'][0],
    #                 color='r', ls='-', marker='o', ms=5, mfc='r')
    # plt.draw()
    # plt.show(block=False)

#*********************************************************************************************************************

def test_getMorphMeasures():
    result = getMorphMeasures(swcFiles[0])

    assert result["scalarMeasurements"]["Width"].magnitude == 174.758

if __name__ == "__main__":
    test_getMeasureDistribution()
    test_getMeasure()
    test_getMeasureDependence_without_averaging()
    test_getMeasureDependence_with_averaging()