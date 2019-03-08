import os
import subprocess
import platform
import numpy as np
import distutils.dir_util, os

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




def removeFileIfExists(fName):
    if os.path.isfile(fName):
        os.remove(fName)

def chunks(l, n):
    ''' Split a list into smaller n-sized lists'''
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))



class LMInput:

    def __init__(self, swcFileNames, measure1names, average=False, nBins=10, measure2names=None, PCA=False, specificity=None):

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
        self.PCA = PCA
        self.specificity = specificity


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

        self.parse_specificity()


    def parse_specificity(self):
        if self.specificity is not None:
            from pyparsing import Word, alphanums, nums, ParseException

            # Match patterns like: 'Type > 1 and EucDistance > 100.0'
            pattern = (Word("andxornt") + Word(alphanums + "_") + Word("<=>") + Word(nums + ".")) * (1, None)

            try:
                parsed = pattern.parseString("and " + self.specificity) # L-measure requires the first logical to be "AND"

            except ParseException:
                raise Exception("Could not parse specificity expression: '" + self.specificity +
                                "'. Examples of allowed expressions: 'Type > 1' or 'Type > 1 and EucDistance > 100.0'")

            # Each condition has exactly 4 elements
            conditions = chunks(parsed, 4)

            conditions_parsed = []

            # Validated each conditional
            for cond in conditions:

                # Parse the condition elements
                logical = cond[0]
                func = cond[1]
                comparison = cond[2]

                try:
                    value = float(cond[3])
                except:
                    raise Exception("Specificity: Found: '" + value + "', but expected a number")

                # Validate the condition terms
                if logical not in ('and', 'or'):
                    raise Exception("Specificity: Found: '"+logical+"', but expected either 'and' or 'or'")

                if func not in self.functionRef:
                    raise Exception("Specificity: Found: '"+func+"', but expected one of " + str(self.functionRef.keys()))
                elif func == "XYZ":
                    raise Exception("Specificity: Function 'XYZ' is not allowed")

                if comparison not in ("<", "==", ">"):
                    raise Exception("Specificity: Found: '" + comparison + "', but expected either '<', '>', or '=='")

                # Save the parsed condition
                conditions_parsed.append({"logical":logical, "func":func, "comparison":comparison, "value":value})

            # Replace the original with the parsed
            self.specificity = conditions_parsed

    def get_specificity_string(self):
        if self.specificity is None:
            return None

        '''
        L-Measure specificity strings look like this:

            -l1,1,8,1714.0 -l2,1,0,2714.0 -l1,1,1,3714.0  

        Where, each "-l...." is a separate condition
        The integers represent logical operator, comparison operator, and function in that order

        Logical Operator        or:2, and:1, first always 1/and           
        Comparison operator:    1: <, 2: =, 3: >                           
        Function:  		int                                        
        Value: 			float
        '''

        # L-measure specificity condition constants
        logical_map = { "or": "2", "and": "1" }
        comparison_map = { "<": "1", "==": "2", ">": "3" }

        result = ""
        for cond in self.specificity:
            result += ("-l" +
                       logical_map[cond["logical"]] + "," +
                       comparison_map[cond["comparison"]] + "," +
                       str(self.functionRef[cond["func"]]) + "," +
                       str(cond["value"]) + " ")

        return result

    def validate_measure_name(self, name):
        if name is not None:
            if  name not in self.functionRef:
                from pprint import pformat as pf
                raise Exception("Unknown measure: '"+str(name)+"'. Must be one of the following: \n" + pf(self.functionRef.keys(), indent=4))

        return True

    def getFunctionString(self):

        functionString = ''

        for measureInd, measure1Name in enumerate(self.measure1names):

            if self.measure2names is None:
                self.validate_measure_name(measure1Name)
                functionString += '-f' + str(self.functionRef[measure1Name]) + ',0,0,' + str(self.nBins) + ' '

            else:
                self.validate_measure_name(measure1Name)
                self.validate_measure_name(self.measure2names[measureInd])

                measure2 = self.functionRef[self.measure2names[measureInd]]

                functionString += '-f' + str(self.functionRef[measure1Name]) + ',f' + str(measure2) + ',' \
                                      + str(int(self.average)) + ',0,' + str(self.nBins) + ' '

        return functionString

    

    def writeLMIn(self, inputFName,  outputFileName):
        """
        Write the input file for L-measure.

        :param inputFName: Name of the input file for L-Measure
        :param outputFileName: Name of the output file of L-Measure
        :param PCA: Whether to rotate the points along the principal component axes (used for height, width, depth)
        :rtype: None
        """

        outputLine = '-s' + outputFileName + (" -C" if self.PCA else "")

        # Create parent folders if they don't exist
        distutils.dir_util.mkpath(os.path.dirname(inputFName))

        with open(inputFName, 'w') as LMInputFile:
            if self.specificity is not None:
                LMInputFile.write(self.get_specificity_string() + '\n')

            LMInputFile.write(self.getFunctionString() + '\n')
            LMInputFile.write(outputLine + '\n')

            for swcFileName in self.swcFileNames:
                LMInputFile.write(swcFileName + '\n')

            LMInputFile.flush()

    




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
            raise(NotImplementedError('Currently, this wrapper only supports Linux, Mac, and Windows. \
            Sorry for the inconvenience.'))

        self.packagePrefix = os.path.split(__file__)[0]

    

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
                                     WholeCellMeasures=None,
                                     WholeCellMeasuresDict=None)

        self.WholeCellMeasuresDictTemplate = {
            "TotalSum":None,
            "CompartmentsConsidered":None,
            "CompartmentsDiscarded":None,
            "Minimum":None,
            "Average":None,
            "Maximum":None,
            "StdDev":None
        }

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




class getMeasureLMOutput(BasicLMOutput):

    def __init__(self, lmInput):

        BasicLMOutput.__init__(self, lmInput)

        for x in self.lmInput.measure1names:
            tempCopy = self.LMOutputTemplate.copy()
            tempCopy['WholeCellMeasures'] = np.zeros([self.lmInput.numberOfSWCFiles, 7])

            # Pre-populate with blank copies of the output dictionary
            tempCopy['WholeCellMeasuresDict'] = [self.WholeCellMeasuresDictTemplate.copy() for i in range(self.lmInput.numberOfSWCFiles)]

            self.LMOutput.append(tempCopy)

    def saveOneLine(self, measureInd, swcFileInd):

        line = self.readOneLine(2)

        self.LMOutput[measureInd]['WholeCellMeasures'][swcFileInd, :] = line

        # Parse the values from the line into corresponding dict keys
        swcDict = self.LMOutput[measureInd]['WholeCellMeasuresDict'][swcFileInd]

        swcDict["TotalSum"] = line[0]
        swcDict["CompartmentsConsidered"] = line[1]
        swcDict["CompartmentsDiscarded"] = line[2]
        swcDict["Minimum"] = line[3]
        swcDict["Average"] = line[4]
        swcDict["Maximum"] = line[5]
        swcDict["StdDev"] = line[6]




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




def LMIOFunction(mode, swcFileNames, measure1Names, measure2Names=None, average=False, nBins=10, PCA=False, specificity=None):

    tempDir = 'tmp'

    if not os.path.isdir(tempDir):
        os.mkdir(tempDir)

    LMInputFName = os.path.join(tempDir, 'LMInput.txt')
    LMOutputFName = os.path.join(tempDir, 'LMOutput.txt')
    LMLogFName = os.path.join(tempDir, 'LMLog.txt')

    lmInput = LMInput(swcFileNames, measure1Names, average, nBins, measure2Names, PCA, specificity)
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



def getMeasure(measureNames, swcFileNames, PCA=False, specificity=None):
    '''
    Computes a list of measures of a list of SWC files.

    :param measureNames: A list of measures. See "Function list" in: http://cng.gmu.edu:8080/Lm/help/index.htm
    :param swcFileNames: A list of paths to SWC files
    :param PCA: If True, rotates the cell to "stand up right". See: http://cng.gmu.edu:8080/Lm/help/Width.htm
    :param specificity: An expression of filter conditions. E.g. 'Type > 1 and EucDistance > 100.0'. See:
    http://cng.gmu.edu:8080/Lm/help/speci.htm
    :return: A list in the form of:
                                                       V-- measure index           V-- file index
        print("Surface area of first file:",    result[0]["WholeCellMeasuresDict"][0]["TotalSum"])
        print("Mean diameter in first file:",   result[1]["WholeCellMeasuresDict"][0]["Average"])
        print("Surface area of 2nd file:",      result[0]["WholeCellMeasuresDict"][1]["TotalSum"])
        print("Mean diameter in 2nd file:",     result[1]["WholeCellMeasuresDict"][1]["Average"])

    '''
    return LMIOFunction('getMeasure', swcFileNames, measureNames, PCA=PCA, specificity=specificity)


def getOneMeasure(measure, swcFile, PCA=False, specificity=None):
    '''
    Computes one measure statistics of one SWC file

    :param measure: Name of the measure to use. See "Function list" in: http://cng.gmu.edu:8080/Lm/help/index.htm
    :param swcFile: Path to SWC file
    :param PCA: If True, rotates the cell to "stand up right". See: http://cng.gmu.edu:8080/Lm/help/Width.htm
    :param specificity: An expression of filter conditions. E.g. 'Type > 1 and EucDistance > 100.0'. See:
    :return: A dictionary with measure statistics
    '''
    result = getMeasure([measure], [swcFile], PCA=PCA, specificity=specificity)

    return result[0]["WholeCellMeasuresDict"][0]


def getMeasureDistribution(measureNames, swcFileNames, nBins=10, PCA=False, specificity=None):
    '''

    :param measureNames:
    :param swcFileNames:
    :param nBins:
    :param PCA: If True, rotates the cell to "stand up right". See: http://cng.gmu.edu:8080/Lm/help/Width.htm
    :param specificity: An expression of filter conditions. E.g. 'Type > 1 and EucDistance > 100.0'. See:
    :return:
    '''
    return LMIOFunction('getDist', swcFileNames, measureNames, measureNames, nBins=nBins, PCA=PCA, specificity=specificity)


def getMeasureDependence(measure1Names, measure2Names, swcFileNames, nBins=10, average=True, PCA=False, specificity=None):
    '''

    :param measure1Names:
    :param measure2Names:
    :param swcFileNames:
    :param nBins:
    :param average:
    :param PCA: If True, rotates the cell to "stand up right". See: http://cng.gmu.edu:8080/Lm/help/Width.htm
    :param specificity: An expression of filter conditions. E.g. 'Type > 1 and EucDistance > 100.0'. See:
    :return:
    '''
    return LMIOFunction('getDep', swcFileNames, measure1Names, measure2Names, average, nBins, PCA=PCA, specificity=specificity)

