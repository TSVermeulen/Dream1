""" 

This file contains the undercarriage related function used to size the landing gear for the 
Lightning2 aircraft.

@author: Thomas

"""

import numpy as np

def UnderCarriageSizing(Params, ConvAndConst):
    """
    Function to size the undercarriage of the Lightning2 aircraft. 
    Based on the methods outlined by the OER Aircraft Design from the 
    Hamburg University of Applied Sciences.

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    noseWheelDiameter, diameter of the nose landing gear wheels [m]
    noseWheelWidth, width of the nose landing gear wheels [m]
    numberMainWheels, number of wheels on the main landing gear [-]
    mainWheelDiameter, diameter of the main landing gear wheels [m]
    mainWheelWidth,, width of the main landing gear wheels [m]

    """

    # Number of Wheels for the Main Landing Gear
    numberMainWheels = 4 * np.ceil(Params.ClassIWEParameters.WmaxLand / Params.ClassIWEParameters.WTO * Params.ClassIWEParameters.WTO / 210000 / 4) # [-] - Number of main landing gear wheels, rounded to the nearest multiple of 4

    # Static Loads
    Pnw = 0.08 * Params.ClassIWEParameters.WTO / ConvAndConst.UndercarriageConstants.noseWheels / ConvAndConst.g / 1000 # [tonnes] - Load per nose gear wheel
    Pmw = 0.92 * Params.ClassIWEParameters.WTO / numberMainWheels / ConvAndConst.g / 1000 # [tonnes] - Load per main gear wheel

    # Wheel Dimensions
    # Nose wheel dimensions
    noseWheelDiameter = (Pnw / ConvAndConst.UndercarriageConstants.wheelLoading / ConvAndConst.UndercarriageConstants.ratioWidthDiameter) ** 0.5 # [m] - Diameter of nose wheel
    noseWheelWidth = noseWheelDiameter * ConvAndConst.UndercarriageConstants.ratioWidthDiameter # [m] - Width of nose wheel
    
    # Main wheel dimensions
    mainWheelDiameter = (Pmw / ConvAndConst.UndercarriageConstants.wheelLoading / ConvAndConst.UndercarriageConstants.ratioWidthDiameter) ** 0.5 # [m] - Diameter of main wheel
    mainWheelWidth = mainWheelDiameter * ConvAndConst.UndercarriageConstants.ratioWidthDiameter # [m] - Width of main wheel
    
    return noseWheelDiameter, noseWheelWidth, numberMainWheels, mainWheelDiameter, mainWheelWidth