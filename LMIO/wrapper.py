import os
import subprocess
import platform
import pkgutil
from sys import exit


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

    LMOutput = dict(rawData=[],
                    measure1BinCentres=[],
                    measure1BinCounts=[],
                    measure2BinAverages=[],
                    measure2BinStdDevs=[],
                    Minimum=None,
                    Maximum=None,
                    Average=None,
                    CompartmentsConsidered=None,
                    CompartmentsDiscarded=None,
                    TotalSum=None,
                    StdDev=None)
    outputFormat = None

    line1 = ""
    line2 = ""
    line3 = ""

    LMInputFName = 'tmp/LMInput.txt'
    LMOutputFName = 'tmp/LMOutput.txt'
    LMLogFName = 'tmp/LMLog.txt'

    rawDataOutputFlag = False

    packagePrefix = pkgutil.get_loader("LMIO").filename

    #*******************************************************************************************************************

    def resetOutputData(self):

        """
        Resets all the fields of the output dictionary LMOutput

        :argument   : None
        :returns    : None

        :rtype : None
        """
        self.LMOutput['rawData'] = []
        self.LMOutput['measure1BinCentres'] = []
        self.LMOutput['measure1BinCounts'] = []
        self.LMOutput['measure2BinAverages'] = []
        self.LMOutput['measure2BinStdDevs'] = []
        self.LMOutput['Minimum'] = None
        self.LMOutput['Maximum'] = None
        self.LMOutput['Average'] = None
        self.LMOutput['CompartmentsConsidered'] = None
        self.LMOutput['CompartmentsDiscarded'] = None
        self.LMOutput['TotalSum'] = None
        self.LMOutput['StdDev'] = None

        self.outputFormat = None

    #*******************************************************************************************************************

    def __init__(self, morphFile):

        """
        Initializes the object.

        :param morphFile    : string containing the path to the target SWC file.
        :rtype              : None.
        """
        self.rawDataOutputFlag = False

        self.resetOutputData()

        self.line1 = ""
        self.line2 = ""
        self.line3 = morphFile

        if not os.path.isdir('tmp'):
            os.mkdir('tmp')

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
            print 'Currently, this wrapper is supported only on Linux. Sorry for the inconvenience.'
            exit(1)

    #*******************************************************************************************************************

    def writeLMIn(self, line1, line2, line3):
        """
        Write the input file for L-measure.

        :param line1: The string containing the first line of the input file to L-measure
        :param line2: The string containing the second line of the input file to L-measure
        :param line3: The string containing the third line of the input file to L-measure
        :rtype: None
        """

        LMIn = open(self.LMInputFName, 'w')

        if self.rawDataOutputFlag:
            line2 += '-R'

        LMIn.write(line1 + '\n' + line2 + '\n' + line3)
        LMIn.close()

    #*******************************************************************************************************************

    def runLM(self):
        """
        Runs the appropriate L-measure executable with the required arguments.

        """

        self.resetOutputData()
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
            print('No Output file created by Lmeasure. Check \'tmp/LMLog.txt\'')
            exit(1)

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

    def readOutput(self):
        """
        Reads output from the L-measure output file according to the format specified in 'outputFormat' and fills in the structure LMOutput
        :return:
        """

        LMOutputFile = open(self.LMOutputFName, 'r')

        if self.rawDataOutputFlag:

            self.LMOutput['rawData'] = []
            prevLine = LMOutputFile.tell()
            tempStr = LMOutputFile.readline()

            while not tempStr.count('\t'):

                prevLine = LMOutputFile.tell()
                self.LMOutput['rawData'].append(self.str2floatTrap(tempStr))
                tempStr = LMOutputFile.readline()

            LMOutputFile.seek(prevLine)

        if self.outputFormat == 1:

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            self.LMOutput['TotalSum'] = self.str2floatTrap(tempWords[2])
            self.LMOutput['CompartmentsConsidered'] = self.str2floatTrap(tempWords[3])
            self.LMOutput['CompartmentsDiscarded'] = self.str2floatTrap(tempWords[4])
            self.LMOutput['Minimum'] = self.str2floatTrap(tempWords[5])
            self.LMOutput['Average'] = self.str2floatTrap(tempWords[6])
            self.LMOutput['Maximum'] = self.str2floatTrap(tempWords[7])
            self.LMOutput['StdDev'] = self.str2floatTrap(tempWords[8])

        elif self.outputFormat == 2:

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            self.LMOutput['measure1BinCentres'] = [self.str2floatTrap(x) for x in tempWords]

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            self.LMOutput['measure1BinCounts'] = [self.str2floatTrap(x) for x in tempWords]

        elif self.outputFormat == 3:

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            self.LMOutput['measure1BinCentres'] = [self.str2floatTrap(x) for x in tempWords]

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[2:len(tempWords) - 1]
            self.LMOutput['measure2BinAverages'] = [self.str2floatTrap(x) for x in tempWords]

            tempStr = LMOutputFile.readline()
            tempWords = tempStr.split('\t')
            tempWords = tempWords[1:len(tempWords) - 1]
            self.LMOutput['measure2BinStdDevs'] = [self.str2floatTrap(x) for x in tempWords]

        LMOutputFile.close()

    #*******************************************************************************************************************

    def getMeasure(self, measure, Filter=False):

        """
        Runs L-measure on the SWC file in the initialized path to calculate the statistics of the measure specified. The fields 'CompartmentsConsidered', 'CompartmentsDiscarded', 'Minimum', 'Maximum', 'Average' and 'StdDev' of the LMOutput dictionary are filled in. The values of the remaining fields of the dictionary are not valid.

        :param measure: A string containing the measure required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param Filter: Not implemented
        :return:
        """
        assert not measure == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasure()'

        self.line1 = '-f' + str(self.functionRef[measure]) + ',' + '0,0,10'

        self.line2 = '-s' + self.LMOutputFName

        self.writeLMIn(self.line1, self.line2, self.line3)

        self.runLM()

        self.outputFormat = 1
        self.readOutput()

        return self.LMOutput

    #*******************************************************************************************************************

    def getMeasureDistribution(self, measure, nBins=10, Filter=False):
        """
        Runs L-measure on the SWC file in the initialized path to calculate the distribution of the measure specified. The fields 'measure1BinCentres' and 'measure1BinCounts' of the LMOutput dictionary are filled in. The values of the remaining fields of the dictionary are not valid.

        :param measure:A string containing the measure required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param nBins: number of bins for the distribution
        :param Filter: Not implemented
        :return:
        """

        assert not measure == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasureDistribution()'

        self.line1 = '-f' + str(self.functionRef[measure]) + ',' \
                     + 'f' + str(self.functionRef[measure]) + ',' + '0,0,' + str(nBins)

        self.line2 = '-s' + self.LMOutputFName

        self.writeLMIn(self.line1, self.line2, self.line3)

        self.runLM()

        self.outputFormat = 2
        self.readOutput()

        return self.LMOutput

    #*******************************************************************************************************************

    #*******************************************************************************************************************

    def getMeasureDependence(self, measure1, measure2, nBins=10, Filter=False):
        """
        Runs L-measure on the SWC file in the initialized path to calculate the averages and standard deviations of measure2 for different bins along the values of measure1.
        The fields 'measure1BinCentres', 'measure2BinAverages' and 'measure2BinStdDevs' of the LMOutput dictionary are filled in. The values of the remaining fields of the dictionary are not valid.

        :param measure1: A string containing the measure1 required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param measure2: A string containing the measure2 required. Look at the different functions available in L-measure in 'help/index.html'. Examples: 'Diameter', 'N_tips'
        :param nBins: number of bins for the distribution of measure1
        :param Filter: Not Implemented
        :return:
        """

        assert not measure1 == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasureDependence()'
        assert not measure2 == 'XYZ', 'Measure \'XYZ\' cannot be used with getMeasureDependence()'

        self.line1 = '-f' + str(self.functionRef[measure1]) + ',' \
                     + 'f' + str(self.functionRef[measure2]) + ',' + '1,0,' + str(nBins)

        self.line2 = '-s' + self.LMOutputFName

        self.writeLMIn(self.line1, self.line2, self.line3)

        self.runLM()

        self.outputFormat = 3
        self.readOutput()

        return self.LMOutput

    #*******************************************************************************************************************
#***********************************************************************************************************************