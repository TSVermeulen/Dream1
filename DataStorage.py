"""

Data Storage file to store the outputs of the converged design.

@author: Thomas Stephan Vermeulen

"""

import pandas as pd

def dataOut(Params, ConvAndConst):
    """
    Function to store the data from the Params class to an excel sheet. 
    """
    # Class I WE Parameters
    classIWEParameters_frame = pd.DataFrame({'Parameter':["WTO", "WML", "WOE", "WF", "WPL"], 
                                             'Unit':["N", "N", "N", "N", "N"], 
                                             'Value':[Params.ClassIWEParameters.WTO, Params.ClassIWEParameters.WmaxLand, Params.ClassIWEParameters.WOE, Params.ClassIWEParameters.WF, Params.payloadWeight]})

    # Propulsion System Parameters
    