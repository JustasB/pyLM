from LMIO.wrapper import *


swcFiles = ['swcFiles/HB060602_3ptSoma.swc']

##*********************************************************************************************************************
## Usage Example getMeasureDistribution
##*********************************************************************************************************************
#LMOutput = getMeasureDistribution(['Diameter'], swcFiles, nBins=50)
#plt.figure()


#print LMOutput[0]['measure1BinCentres']
#print LMOutput[0]['measure1BinCounts']
#plt.bar(LMOutput[0]['measure1BinCentres'], LMOutput[0]['measure1BinCounts'])
#plt.draw()
#plt.show(block=False)

##*********************************************************************************************************************

##*********************************************************************************************************************
## # Usage Example getMeasure
##*********************************************************************************************************************
LMOutput = getMeasure(['Surface'], swcFiles)
print 'Neuron Surface Area is ' + str(LMOutput[0, 0, 0])

##*********************************************************************************************************************

#*********************************************************************************************************************
# Usage Example getMeasureDependence
#*********************************************************************************************************************
#LMOutput = getMeasureDependence(['Branch_Order'], ['EucDistance'], swcFiles , nBins=50)
#plt.figure()
#plt.plot(LMOutput[0]['measure1BinCentres'], LMOutput[0]['measure2BinAverages'], 'ro', mfc = 'r', ms=5)
#plt.draw()
#plt.show(block=False)

#*********************************************************************************************************************