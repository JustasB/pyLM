#Author: Ajayrama Kumaraswamy(ajayramak@bio.lmu.de)
#Date: 2 May 2014
#Place: Dept. of Biology II, LMU, Munich


from .. import *
import os
from pint import UnitRegistry
ureg = UnitRegistry()

def getMorphMeasures(swcfName):
    """

    :param swcfName: relative/absolute path of the swc file.
    :return: a dictionary of scalar measurements as key value pairs. The name of the key is the name of the measurement. The values are pint quantities.
    """

    swcfName = os.path.abspath(swcfName)

    measureNames = ['Width', 'Height', 'Depth', 'Length', 'Volume', 'Surface', 'N_bifs']

    LMOutputSimple = getMeasure(measureNames, [swcfName])
    width = LMOutputSimple[0]['WholeCellMeasures'][0][0]
    height = LMOutputSimple[1]['WholeCellMeasures'][0][0]
    depth = LMOutputSimple[2]['WholeCellMeasures'][0][0]
    length = LMOutputSimple[3]['WholeCellMeasures'][0][0]
    volume = LMOutputSimple[4]['WholeCellMeasures'][0][0]
    surface = LMOutputSimple[5]['WholeCellMeasures'][0][0]
    nbifs = LMOutputSimple[6]['WholeCellMeasures'][0][0]


    scalarDict = dict(
                    Width=width * ureg.um,
                    Height=height * ureg.um,
                    Depth=depth * ureg.um,
                    Length=length * ureg.um,
                    Volume=volume * (ureg.um) ** 3,
                    Surface=surface * (ureg.um) ** 2,
                    NumberofBifurcations=ureg.Quantity(nbifs, None) ,
                    )

    retDict = dict(scalarMeasurements=scalarDict)


    return retDict
