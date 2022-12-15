"""

Class I Weight Estimation for the Blended Wing Body Design Concept

@author: Thomas

"""

import numpy as np

def fuelWeightFractions(Params, ConvAndConst):
    """
    Function using the brequet range equations to find the mass fractions
    for cruise and loiter

    Inputs:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Outputs:
    -----
    usedTotalMf, the fuel fraction of total used fuel [-]
    cruiseMf, fuel fraction of fuel used during cruise [-]
    """

    # Statistical Fuel Fractions
    statisticalFractions = np.array([0.99, 0.99, 0.995, 0.98, 0.99, 1, 1, 1, 0.992])

    # Brequet Range Equations 
    cruiseMf = 1/(np.exp((Params.designRange)/((Params.cruiseSpeed/(ConvAndConst.g * Params.ClassIWEParameters.cruiseCj)) * Params.ClassIWEParameters.cruiseLD)))
    loiterMf = 1/(np.exp(Params.loiterTime/((1/(ConvAndConst.g * Params.ClassIWEParameters.loiterCj)) * Params.ClassIWEParameters.loiterLD)))    
    usedTotalMf = cruiseMf * loiterMf * np.product(statisticalFractions)
    
    return usedTotalMf, cruiseMf

def hydrogenWeightEstimation(Params, ConvAndConst):
    """ 
    Function to calculate the required amount of Hydrogen.
    Note that the outputs of this function do not account for required boil off in hydrogen tank!

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    WF, design fuel weight [N]
    WFCruiseAppLoiter, design fuel weight left after take-off and climb [N]
    WFAppLoiter, design fuel weight left after cruise [N]
    WFLoiter, design fuel weight left after descent [N]
    """
    
    # Calculate the energy needed for various portions of the flight
    totalEnergy = Params.ClassIWEParameters.takeOffPower * Params.climbTime + Params.ClassIWEParameters.cruisePower * Params.cruiseTime + Params.ClassIWEParameters.approachPower * Params.approachTime + Params.ClassIWEParameters.loiterPower * Params.loiterTime
    totalEnergyCruiseAppLoiter = totalEnergy - Params.ClassIWEParameters.takeOffPower * Params.climbTime
    totalEnergyAppLoiter = totalEnergyCruiseAppLoiter - Params.ClassIWEParameters.cruisePower * Params.cruiseTime
    totalEnergyLoiter = Params.ClassIWEParameters.loiterPower * Params.loiterTime

    # Hydrogen needed for the various portions of flight
    WF = totalEnergy / (ConvAndConst.EngineConstants.fuelCellEfficiency * ConvAndConst.EngineConstants.specificEnergyLH) * ConvAndConst.g
    WFCruiseAppLoiter = totalEnergyCruiseAppLoiter / (ConvAndConst.EngineConstants.fuelCellEfficiency * ConvAndConst.EngineConstants.specificEnergyLH) * ConvAndConst.g
    WFAppLoiter = totalEnergyAppLoiter / (ConvAndConst.EngineConstants.fuelCellEfficiency * ConvAndConst.EngineConstants.specificEnergyLH) * ConvAndConst.g
    WFLoiter = totalEnergyLoiter / (ConvAndConst.EngineConstants.fuelCellEfficiency * ConvAndConst.EngineConstants.specificEnergyLH) * ConvAndConst.g
    
    return WF, WFCruiseAppLoiter, WFAppLoiter, WFLoiter

def classIWeight(Params, ConvAndConst, nIter):
    """
    Function to perform the class I weight estimation

    Inputs:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants
    nIter, iteration number [-]

    Outputs:
    -----
    WTO, MTOW [N]
    WOE, Operating empty weight [N]
    WF, fuel weight [N]
    h2TO, hydrogen used during take-off [N]
    h2endCruise, hydrogen left at the end of cruise [N]
    h2endApp, hydrogen left at the end of approach [N]
    """

    # Statistical Class I Weight Estimation
    if nIter == 1:
        usedTotalMf, cruiseMf = fuelWeightFractions(Params, ConvAndConst)
        WTO = (- ConvAndConst.ClassIWEConstants.b - Params.payloadWeight) / (-1 + ConvAndConst.ClassIWEConstants.a + Params.ClassIWEParameters.Mres * (1 - usedTotalMf) + (1 - usedTotalMf)) 
        WF = ((1 - usedTotalMf) * WTO + Params.ClassIWEParameters.Mres * (1 - usedTotalMf) * Params.ClassIWEParameters.WTO) * (1 + ConvAndConst.HydrogenTankConstants.boilOff)
        h2TO = 0.958577004 * WF
        h2endCruise = (1 - cruiseMf) * h2TO
        h2endApp = 0.99 * h2endCruise
        WOE = WTO - WF - Params.payloadWeight

    # Class I Weight Estimation using calculations for Hydrogen weight
    else:               
        h2, h2TO, h2endCruise, h2endApp = hydrogenWeightEstimation(Params, ConvAndConst)
        WF = h2 * (1 + ConvAndConst.HydrogenTankConstants.boilOff)
        h2TO = h2TO * (1 + ConvAndConst.HydrogenTankConstants.boilOff)
        h2endCruise = h2endCruise * (1 + ConvAndConst.HydrogenTankConstants.boilOff)
        h2endApp = h2endApp * (1 + ConvAndConst.HydrogenTankConstants.boilOff)
        WTO = WF + Params.ClassIWEParameters.WOE + Params.payloadWeight
        WOE = Params.ClassIWEParameters.WOE

    # Calculate Maximum Landing Weight. Equation is taken from FLOPS but implemented here to improve runtime efficiency.
    Params.ClassIWEParameters.WmaxLand = WTO * ConvAndConst.ClassIWEConstants.maxLandingWeightRatio

    return WTO, WOE, WF, h2TO, h2endCruise, h2endApp
