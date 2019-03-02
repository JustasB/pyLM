Python Wrapper for L-measure.

It is advised that one be familiar with L-measure and it's functionalities before using this wrapper.

Mainly, three functions are implemented getMeasure(), getMeasureDistribution() and
getMeasureDependence().

Operating systems Supported:
1. Linux 32 and 64 bit

Installation:
Linux:
Caution: Do not place these files in a system path.
 1. Copy the folder 'python-Lmeasure' to a location(for example <home directory>/installations/)
 2. Add the path '<path to python-Lmeasure>/LMIO/' to the system PYTHONPATH  by adding the following line to .profile or .bashrc

    export PYTHONPATH="$PYTHONPATH:<path to python-Lmeasure>/LMIO/"

    Source the .profile or .bashrc file.


Output Format:

The object returned by any of the three functions is a list of a dictionaries, each dictionary with the following
structure. Each dictionary corresponds to one measure specified as input to the function being used(in measureNames or
measure1Names).

LMOutputTemplate = dict(rawData=None,
                    measure1BinCentres=None,
                    measure1BinCounts=None,
                    measure2BinAverages=None,
                    measure2BinStdDevs=None,
                    WholeCellMeasures=None,
                    )


WholeCellMeasures is a (# of swc files given)x7 numpy array. The seven entries along the second dimension correspond
respectively to

TotalSum, CompartmentsConsidered, Compartments Discarded, Minimum, Average, Maximum, StdDev

All meaure**** fields are (# of swc files given) x (nBins +1) numpy arrays.

getMeasure() has its results in WholeCellMeasures.

getMeasureDistribution has its results in measure1BinCentres and measure1BinCounts

getMeasureDependence has its results in measure1BinCentres, measure2BinAverages and measure2BinStdDevs


Misc:

See the file ExampleUsage.py for example usage.

Look at the documentation strings for more information
