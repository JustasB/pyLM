from LMIO.wrapper_v2 import *
import matplotlib.pyplot as plt

swcFiles = ['testFiles/HB130605-1NS.swc']

##*********************************************************************************************************************
## Usage Example getMeasureDistribution
##*********************************************************************************************************************
# LMOutput = getMeasureDistribution(['Diameter'], swcFiles, nBins=50)
# plt.figure()
#
#
# print LMOutput[0]['measure1BinCentres']
# print LMOutput[0]['measure1BinCounts']
# plt.bar(LMOutput[0]['measure1BinCentres'][0], LMOutput[0]['measure1BinCounts'][0])
# plt.draw()
# plt.show(block=False)

##*********************************************************************************************************************

##*********************************************************************************************************************
## # Usage Example getMeasure
##*********************************************************************************************************************
# LMOutput = getMeasure(['Surface'], swcFiles)
# print 'Neuron Surface Area is ' + str(LMOutput[0]['WholeCellMeasures'][0][4])

##*********************************************************************************************************************

#*********************************************************************************************************************
# Usage Example getMeasureDependence without averaging
#*********************************************************************************************************************
# LMOutput = getMeasureDependence(['N_branch'], ['EucDistance'], swcFiles, nBins=100, average=False)
# plt.figure()
# plt.plot(LMOutput[0]['measure1BinCentres'][0], LMOutput[0]['measure2BinSums'][0], 'ro', mfc='r', ms=5)
# plt.draw()
# plt.show(block=False)

#*********************************************************************************************************************

#*********************************************************************************************************************
# Usage Example getMeasureDependence with averaging
#*********************************************************************************************************************
LMOutput = getMeasureDependence(['Diameter'], ['EucDistance'], swcFiles, nBins=100, average=True)
plt.figure()
plt.errorbar(LMOutput[0]['measure1BinCentres'][0],
             LMOutput[0]['measure2BinAverages'][0],
             LMOutput[0]['measure2BinStdDevs'][0],
                color='r', ls='-', marker='o', ms=5, mfc='r')
plt.draw()
plt.show(block=False)

#*********************************************************************************************************************