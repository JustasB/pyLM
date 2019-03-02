import os
import subprocess
import platform
import numpy as np

#***********************************************************************************************************************


def str2floatTrap(someStr):
    """
    Checks if there is either a starting '('  or an ending ')' around the input string and returns a string without them.
    :param someStr: input string
    :return:
    """

    tempStr = someStr

    if tempStr.startswith('('):
        tempStr = tempStr[1:]

    if tempStr.endswith(')'):
        tempStr = tempStr[:len(tempStr) - 1]

    return float(tempStr)

#***********************************************************************************************************************


def removeFileIfExists(fName):

    if os.path.isfile(fName):
        os.remove(fName)

#***********************************************************************************************************************


class LMInput:

    def __init__(self, swcFileNames, measure1names, average=False, nBins=10, measure2names=None):

        for measure in measure1names:
            assert not measure == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasure()'

        if measure2names is not None:

            for measure in measure2names:
                assert not measure == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasure()'

        for name in swcFileNames:
            if not os.path.exists(name):
                raise IOError("File cannot be found:" + os.path.join(os.getcwd(),name))

        self.swcFileNames = swcFileNames
        self.measure1names = measure1names
        self.measure2names = measure2names
        self.numberOfMeasures = len(self.measure1names)
        self.numberOfSWCFiles = len(self.swcFileNames)
        self.nBins = nBins
        self.average = average

        self.functionRef = {'Soma_Surface'           :0,
                            'N_stems'                :1,
                            'N_bifs'                 :2,
                            'N_branch'               :3,
                            'N_tips'                 :4,
                            'Width'                  :5,
                            'Height'                 :6,
                            'Depth'                  :7,
                            'Type'                   :8,
                            'Diameter'               :9,
                            'Diameter_pow'           :10,
                            'Length'                 :11,
                            'Surface'                :12,
                            'SectionArea'            :13,
                            'Volume'                 :14,
                            'EucDistance'            :15,
                            'PathDistance'           :16,
                            'XYZ'                    :17,
                            'Branch_Order'           :18,
                            'Terminal_degree'        :19,
                            'TerminalSegment'        :20,
                            'Taper_1'                :21,
                            'Taper_2'                :22,
                            'Branch_pathlength'      :23,
                            'Contraction'            :24,
                            'Fragmentation'          :25,
                            'Daughter_Ratio'         :26,
                            'Parent_Daughter_Ratio'  :27,
                            'Partition_asymmetry'    :28,
                            'Rall_Power'             :29,
                            'Pk'                     :30,
                            'Pk_classic'             :31,
                            'Pk_2'                   :32,
                            'Bif_ampl_local'         :33,
                            'Bif_ampl_remote'        :34,
                            'Bif_tilt_local'         :35,
                            'Bif_tilt_remote'        :36,
                            'Bif_torque_local'       :37,
                            'Bif_torque_remote'      :38,
                            'Last_parent_diam'       :39,
                            'Diam_threshold'         :40,
                            'HillmanThreshold'       :41,
                            'Helix'                  :43,
                            'Fractal_Dim'            :44}

    #*******************************************************************************************************************

    def getFunctionString(self):

        functionString = ''

        for measureInd, measure1Name in enumerate(self.measure1names):

            if self.measure2names is None:
                functionString += '-f' + str(self.functionRef[measure1Name]) + ',0,0,' + str(self.nBins) + ' '
            else:
                measure2 = self.functionRef[self.measure2names[measureInd]]

                functionString += '-f' + str(self.functionRef[measure1Name]) + ',f' + str(measure2) + ',' \
                                      + str(int(self.average)) + ',0,' + str(self.nBins) + ' '

        return functionString

    #*******************************************************************************************************************

    def writeLMIn(self, inputFName,  outputFileName):
        """
        Write the input file for L-measure.

        :param inputFName: Name of the input file for L-Measure
        :param outputFileName: Name of the output file of L-Measure
        :rtype: None
        """

        outputLine = '-s' + outputFileName

        with open(inputFName, 'w') as LMInputFile:
            LMInputFile.write(self.getFunctionString() + '\n')
            LMInputFile.write(outputLine + '\n')

            for swcFileName in self.swcFileNames:
                LMInputFile.write(swcFileName + '\n')

            LMInputFile.flush()

    #*******************************************************************************************************************

#***********************************************************************************************************************


class LMRun():

    def __init__(self):

        osName = platform.system()
        if osName == 'Linux':
            (bit, linkage) = platform.architecture()
            self.LMPath = 'LMLinux' + bit[:2] + '/'
            self.LMExec = 'lmeasure'

        elif osName == 'Darwin':
            self.LMPath = 'LMMac'
            self.LMExec = 'lmeasure'

        elif osName == 'Windows':
            self.LMPath = 'LMwin'
            self.LMExec = 'Lm.exe'

        else:
            raise(NotImplementedError('Currently, this wrapper is supported only on Linux. \
            Sorry for the inconvenience.'))

        self.packagePrefix = os.path.split(__file__)[0]

    #*******************************************************************************************************************

    def runLM(self, LMInputFName, LMOutputFName, LMLogFName):
        """
        Runs the appropriate L-measure executable with the required arguments.

        """

        removeFileIfExists(LMOutputFName)
        removeFileIfExists(LMLogFName)

        with open(LMLogFName, 'w') as LMLogFle:
            subprocess.call([os.path.join(self.packagePrefix, self.LMPath, self.LMExec), LMInputFName],
                            stdout=LMLogFle, stderr=LMLogFle)

            try:
                self.LMOutputFile = open(LMOutputFName, 'r')
                self.LMOutputFile.close()
            except:
                raise(Exception('No Output file created by Lmeasure. Check ' + LMLogFName))

    #*******************************************************************************************************************

#***********************************************************************************************************************


class BasicLMOutput:

    def __init__(self, lmInput):

        # WholeCellMeasures is a (# of swc files given)x7 numpy array. The seven entries along the
        # second dimension correspond respectively to
        # TotalSum, CompartmentsConsidered, Compartments Discarded, Minimum, Average, Maximum, StdDev

        self.LMOutput = []
        self.lmInput = lmInput
        self.LMOutputTemplate = dict(measure1BinCentres=None,
                                     measure1BinCounts=None,
                                     measure2BinAverages=None,
                                     measure2BinStdDevs=None,
                                     measure2BinSums=None,
                                     WholeCellMeasures=None)

    def saveOneLine(self, measureInd, swcFileInd):

        pass

    def readOutput(self, outputFile):

        self.outputFile = outputFile

        for swcFileInd in range(self.lmInput.numberOfSWCFiles):
            for measureInd in range(self.lmInput.numberOfMeasures):
                self.saveOneLine(measureInd, swcFileInd)

    def readOneLine(self, start=0, end=None):

        tempStr = self.outputFile.readline()
        tempWords = tempStr.split('\t')
        if end is None:
            return np.asarray([str2floatTrap(x) for x in tempWords[start:]])
        else:
            return np.asarray([str2floatTrap(x) for x in tempWords[start:end]])

#***********************************************************************************************************************


class getMeasureLMOutput(BasicLMOutput):

    def __init__(self, lmInput):

        BasicLMOutput.__init__(self, lmInput)

        for x in self.lmInput.measure1names:
            tempCopy = self.LMOutputTemplate.copy()
            tempCopy['WholeCellMeasures'] = np.zeros([self.lmInput.numberOfSWCFiles, 7])
            self.LMOutput.append(tempCopy)

    def saveOneLine(self, measureInd, swcFileInd):

        self.LMOutput[measureInd]['WholeCellMeasures'][swcFileInd, :] = self.readOneLine(2)

#***********************************************************************************************************************


class getMeasureDistLMOutput(BasicLMOutput):

    def __init__(self, lmInput):

        BasicLMOutput.__init__(self, lmInput)

        for x in self.lmInput.measure1names:
            tempCopy = self.LMOutputTemplate.copy()
            tempCopy['measure1BinCentres'] = np.zeros([self.lmInput.numberOfSWCFiles, self.lmInput.nBins])
            tempCopy['measure1BinCounts'] = np.zeros([self.lmInput.numberOfSWCFiles, self.lmInput.nBins])
            self.LMOutput.append(tempCopy)

    def saveOneLine(self, measureInd, swcFileInd):

        self.LMOutput[measureInd]['measure1BinCentres'][swcFileInd, :] = self.readOneLine(2, self.lmInput.nBins + 2)
        self.LMOutput[measureInd]['measure1BinCounts'][swcFileInd, :] = self.readOneLine(2, self.lmInput.nBins + 2)

#***********************************************************************************************************************


class getMeasureDepLMOutput(BasicLMOutput):

    def __init__(self, lmInput):

        BasicLMOutput.__init__(self, lmInput)

        for x in self.lmInput.measure1names:

            tempCopy = self.LMOutputTemplate.copy()
            tempCopy['measure1BinCentres'] = np.zeros([self.lmInput.numberOfSWCFiles, self.lmInput.nBins])

            if self.lmInput.average:

                tempCopy['measure2BinAverages'] = np.zeros([self.lmInput.numberOfSWCFiles, self.lmInput.nBins])
                tempCopy['measure2BinStdDevs'] = np.zeros([self.lmInput.numberOfSWCFiles, self.lmInput.nBins])

            else:

                tempCopy['measure2BinSums'] = np.zeros([self.lmInput.numberOfSWCFiles, self.lmInput.nBins])

            self.LMOutput.append(tempCopy)

    def saveOneLine(self, measureInd, swcFileInd):

        self.LMOutput[measureInd]['measure1BinCentres'][swcFileInd, :] = self.readOneLine(2, self.lmInput.nBins + 2)

        if self.lmInput.average:

            self.LMOutput[measureInd]['measure2BinAverages'][swcFileInd, :] = \
                self.readOneLine(2, self.lmInput.nBins + 2)
            self.LMOutput[measureInd]['measure2BinStdDevs'][swcFileInd, :] = self.readOneLine(1, self.lmInput.nBins + 1)

        else:

            self.LMOutput[measureInd]['measure2BinSums'][swcFileInd, :] = self.readOneLine(2, self.lmInput.nBins + 2)

#***********************************************************************************************************************


def LMIOFunction(mode, swcFileNames, measure1Names, measure2Names=None, average=False, nBins=10, Filter=False):

    tempDir = 'tmp'

    if not os.path.isdir(tempDir):
        os.mkdir(tempDir)

    LMInputFName = os.path.join(tempDir, 'LMInput.txt')
    LMOutputFName = os.path.join(tempDir, 'LMOutput.txt')
    LMLogFName = os.path.join(tempDir, 'LMLog.txt')

    lmInput = LMInput(swcFileNames, measure1Names, average, nBins, measure2Names)
    lmInput.writeLMIn(LMInputFName, LMOutputFName)

    if mode == 'getMeasure':
        lmOutput = getMeasureLMOutput(lmInput)
    elif mode == 'getDist':
        lmOutput = getMeasureDistLMOutput(lmInput)
    elif mode == 'getDep':
        lmOutput = getMeasureDepLMOutput(lmInput)
    else:
        raise(ValueError('Unknown value for parameter \'mode\''))

    lmRun = LMRun()
    lmRun.runLM(LMInputFName, LMOutputFName, LMLogFName)



    with open(LMOutputFName, 'r') as outputFile:
        lmOutput.readOutput(outputFile)

    return lmOutput.LMOutput

#***********************************************************************************************************************


def getMeasure(measureNames, swcFileNames, Filter=False):

    return LMIOFunction('getMeasure', swcFileNames, measureNames, Filter=Filter)

#***********************************************************************************************************************


def getMeasureDistribution(measureNames, swcFileNames, nBins=10, Filter=False):

    return LMIOFunction('getDist', swcFileNames, measureNames, measureNames, nBins=nBins, Filter=Filter)

#***********************************************************************************************************************


def getMeasureDependence(measure1Names, measure2Names, swcFileNames, nBins=10, average=True, Filter=False):

    return LMIOFunction('getDep', swcFileNames, measure1Names, measure2Names, average, nBins, Filter=Filter)

#***********************************************************************************************************************