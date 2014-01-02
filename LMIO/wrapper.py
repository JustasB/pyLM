import os
import subprocess
import platform
import pkgutil
from string import join as strJoin
import numpy as np

#TODO add raw_data=True flag to functions



class LMIO:
    """
    Wrapper class for using L-meausure via python scripting.
    """

    LMPath = ''
    LMExec = ''


    functionRef = {'Soma_Surface'           :0,
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

    # WholeCellMeasures is a (# of swc files given)x7 numpy array. The seven entries along the
    # second dimension correspond respectively to
    # TotalSum, CompartmentsConsidered, Compartments Discarded, Minimum, Average, Maximum, StdDev

    LMOutputTemplate = dict(rawData=None,
                    measure1BinCentres=None,
                    measure1BinCounts=None,
                    measure2BinAverages=None,
                    measure2BinStdDevs=None,
                    WholeCellMeasures=None,
                    )


    LMInputFName = 'tmp/LMInput.txt'
    LMOutputFName = 'tmp/LMOutput.txt'
    LMLogFName = 'tmp/LMLog.txt'

    packagePrefix = pkgutil.get_loader("LMIO").filename

    #*******************************************************************************************************************

    def isMeasureNameCorrect(self, measureName):

        return measureName in self.functionRef

    #*******************************************************************************************************************

    def __init__(self):

        """
        Initializes the object.

        :param morphFile    : string containing the path to the target SWC file.
        :rtype              : None.
        """

        tmpPathFull = os.path.join('tmp')
        if not os.path.isdir(tmpPathFull):
            os.mkdir(tmpPathFull)

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


    #*******************************************************************************************************************

    def composeInputString(self, measure1Name, nBins, measure2Name):
        if measure2Name is None:
            return '-f' + str(self.functionRef[measure1Name]) + ',0,0,' + str(nBins)
        else:
            measure2 = self.functionRef[measure2Name]
            if measure1Name == measure2Name:
                aver = 0
            else:
                aver = 1

            return '-f' + str(self.functionRef[measure1Name]) + ',f' + str(measure2) + ',' + str(aver) + ',0,' \
                                                                                                    + str(nBins)


    #*******************************************************************************************************************

    def writeLMIn(self, measure1Names, measure2Names, swcFileNames, nBins, rawData=False):
        """
        Write the input file for L-measure.

        :param line1: The string containing the first line of the input file to L-measure
        :param line2: The string containing the second line of the input file to L-measure
        :param line3: The string containing the third line of the input file to L-measure
        :rtype: None
        """

        LMIn = open(self.LMInputFName, 'w')

        outputLine = '-s' + self.LMOutputFName

        #TODO: raw data feature is not yet implemented
        # if rawData:
        #     outputLine += '-R'

        inputLine = strJoin([self.composeInputString(measure1Name, nBins, measure2Name) \
                             for measure1Name,measure2Name in zip(measure1Names, measure2Names)], ' ')

        LMIn.write(inputLine + '\n')
        LMIn.write(outputLine + '\n')
        for swcFileName in swcFileNames:
            LMIn.write(swcFileName + '\n')
        LMIn.close()

    #*******************************************************************************************************************

    def runLM(self):
        """
        Runs the appropriate L-measure executable with the required arguments.

        """

        if os.path.isfile(self.LMOutputFName):
            os.remove(self.LMOutputFName)
        if os.path.isfile(self.LMLogFName):
            os.remove(self.LMLogFName)

        LMLogFle = open(self.LMLogFName, 'w')
        subprocess.call([os.path.join(self.packagePrefix, self.LMPath, self.LMExec), self.LMInputFName], \
                        stdout=LMLogFle, stderr=LMLogFle)

        try:
            self.LMOutputFile = open(self.LMOutputFName, 'r')
            self.LMOutputFile.close()
        except:
            raise(Exception('No Output file created by Lmeasure. Check \'~tmp/LMLog.txt\''))

        LMLogFle.close()

    #*******************************************************************************************************************

    def str2floatTrap(self, someStr):
        """
        Checks if there is either a starting '('  or an ending ')' around the input string and returns a string without them.
        :param str: input string
        :return:
        """

        tempStr = someStr

        if tempStr.startswith('('):
            tempStr = tempStr[1:]

        if tempStr.endswith(')'):
            tempStr = tempStr[:len(tempStr) - 1]

        return float(tempStr)

    #*******************************************************************************************************************

    def readOneLineOutput(self, LMOutputFile, outputFormat, rawData=False):

        #TODO: implement reading raw Data. Problem is that number of lines of raw data generated per swcFile is unknown
        #TODO:  beforehand
        # if rawData:
        #
        #     self.LMOutput['rawData'] = []
        #     prevLine = LMOutputFile.tell()
        #     tempStr = LMOutputFile.readline()
        #
        #     while not tempStr.count('\t'):
        #
        #         prevLine = LMOutputFile.tell()
        #         self.LMOutput['rawData'].append(self.str2floatTrap(tempStr))
        #         tempStr = LMOutputFile.readline()
        #
        #     LMOutputFile.seek(prevLine)

        if outputFormat == 'getMeasure':

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            return np.asarray([self.str2floatTrap(x) for x in tempWords[2:]])

        elif outputFormat == 'getDistribution':

            toReturn = []

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            toReturn.append(np.asarray([self.str2floatTrap(x) for x in tempWords]))

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            toReturn.append(np.asarray([self.str2floatTrap(x) for x in tempWords]))

            return toReturn

        elif outputFormat == 'getDependence':

            toReturn = []

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            toReturn.append(np.asarray([self.str2floatTrap(x) for x in tempWords]))

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            toReturn.append(np.asarray([self.str2floatTrap(x) for x in tempWords]))

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[1:len(tempWords) - 1]
            toReturn.append(np.asarray([self.str2floatTrap(x) for x in tempWords]))

            return toReturn

    #*******************************************************************************************************************

    def readOutput(self, numberOfMeasures, numberOfSWCFiles, outputFormat, nBins, rawData=False):
        """
        Reads output from the L-measure output file according to the format specified in 'outputFormat' and fills in the structure LMOutput
        :return:
        """

        LMOutput = []

        for measureInd in range(numberOfMeasures):
            LMOutputTempCopy = self.LMOutputTemplate.copy()
            if outputFormat == 'getMeasure':
                LMOutputTempCopy['WholeCellMeasures'] = np.zeros([numberOfSWCFiles, 7])
            if outputFormat == 'getDistribution':
                LMOutputTempCopy['measure1BinCentres'] = np.zeros([numberOfSWCFiles, nBins + 1])
                LMOutputTempCopy['measure1BinCounts'] = np.zeros([numberOfSWCFiles, nBins + 1])
            if outputFormat ==  'getDependence':
                LMOutputTempCopy['measure1BinCentres'] = np.zeros([numberOfSWCFiles, nBins + 1])
                LMOutputTempCopy['measure2BinAverages'] = np.zeros([numberOfSWCFiles, nBins + 1])
                LMOutputTempCopy['measure2BinStdDevs'] = np.zeros([numberOfSWCFiles, nBins + 1])

            LMOutput.append(LMOutputTempCopy)

        LMOutputFile = open(self.LMOutputFName, 'r')

        for swcFileInd in range(numberOfSWCFiles):
            for measureInd in range(numberOfMeasures):
                if outputFormat == 'getMeasure':
                    LMOutput[measureInd]['WholeCellMeasures'][swcFileInd, :] = self.readOneLineOutput(LMOutputFile,
                                                                                                      outputFormat)
                if outputFormat == 'getDistribution':
                    returned = self.readOneLineOutput(LMOutputFile, outputFormat)
                    LMOutput[measureInd]['measure1BinCentres'][swcFileInd, :] = returned[0]
                    LMOutput[measureInd]['measure1BinCounts'][swcFileInd, :] = returned[1]

                if outputFormat == 'getDependence':
                    returned = self.readOneLineOutput(LMOutputFile, outputFormat)
                    LMOutput[measureInd]['measure1BinCentres'][swcFileInd, :] = returned[0]
                    LMOutput[measureInd]['measure2BinAverages'][swcFileInd, :] = returned[1]
                    LMOutput[measureInd]['measure2BinStdDevs'][swcFileInd, :] = returned[2]

        LMOutputFile.close()
        return LMOutput

    #*******************************************************************************************************************

    def getMeasure(self, measureNames, swcFileNames, Filter=False):

        """
        Runs L-measure on the SWC file in the initialized path to calculate the statistics of the measure specified. The fields 'CompartmentsConsidered', 'CompartmentsDiscarded', 'Minimum', 'Maximum', 'Average' and 'StdDev' of the LMOutput dictionary are filled in. The values of the remaining fields of the dictionary are not valid.

        :param measureNames: A list of string containing the measures required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param swcFileNames: A list of swc file paths. All the measures in measureNames are applied on all files.
        :param Filter: Not implemented
        :return:
        """

        for measure in measureNames:
            assert not measure == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasure()'

        self.writeLMIn(measureNames, [None] * len(measureNames), swcFileNames, 10)

        self.runLM()

        return self.readOutput(len(measureNames), len(swcFileNames), 'getMeasure', 10)

    #*******************************************************************************************************************

    def getMeasureDistribution(self, measureNames, swcFileNames, nBins=10, Filter=False):
        """
        Runs L-measure on the SWC file in the initialized path to calculate the distribution of the measure specified. The fields 'measure1BinCentres' and 'measure1BinCounts' of the LMOutput dictionary are filled in. The values of the remaining fields of the dictionary are not valid.

        :param measureNames:A list of strings containing the measures required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param swcFileNames: A list of swc file paths. All the measures in measureNames are applied on all files.
        :param nBins: number of bins for the distribution
        :param Filter: Not implemented
        :return:
        """
        for measure in measureNames:
            assert not measure == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasureDistribution()'

        self.writeLMIn(measureNames, measureNames, swcFileNames, nBins)

        self.runLM()

        return self.readOutput(len(measureNames), len(swcFileNames), 'getDistribution', nBins)


    #*******************************************************************************************************************

    def getMeasureDependence(self, measure1Names, measure2Names, swcFileNames, nBins=10, Filter=False):
        """
        Runs L-measure on the SWC file in the initialized path to calculate the averages and standard deviations of measure2 for different bins along the values of measure1.
        The fields 'measure1BinCentres', 'measure2BinAverages' and 'measure2BinStdDevs' of the LMOutput dictionary are filled in. The values of the remaining fields of the dictionary are not valid.

        :param measure1Names: A list of strings containing the dependent measures required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param measure2Names: A list of strings containing the independent Measures required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param nBins: number of bins for the distribution of measure1
        :param Filter: Not Implemented
        :return:
        """

        for measure1 in measure1Names:
            assert not measure1 == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasureDependence()'
        for measure2 in measure2Names:
            assert not measure2 == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasureDependence()'


        self.writeLMIn(measure1Names, measure2Names, swcFileNames, nBins)

        self.runLM()

        return self.readOutput(len(measure1Names), len(swcFileNames), 'getDependence', nBins)

    #*******************************************************************************************************************
#***********************************************************************************************************************

lmio = LMIO()
getMeasure = lmio.getMeasure
getMeasureDistribution = lmio.getMeasureDistribution
getMeasureDependence = lmio.getMeasureDependence