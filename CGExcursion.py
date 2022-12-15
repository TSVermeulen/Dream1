"""

Program to perform a CG Excursion on the blended wing body concept. 
Based on:

Loosely based on an initial implementation by Rasa.

@author: Thomas Stephan Vermeulen

"""

import numpy as np

def emptyWeightCGCalculator(Params, ConvAndConst, xLEMAC=None):
    """
    Function to calculate the C.G. location of the aircraft OEW.
    
    Inputs:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants
    xLEMAC, longitudinal position of the leading edge of the mean aerodynamic chord [m]

    Outputs:
    -----
    OEWcg, C.G. location of the OEW of the aircraft, expressed as fraction of the fuselage length [-]
    """

    # Calculate C.G. location of vertical tail.
    verticalTailCGMAC = (np.tan(np.radians(Params.WingPlanformParameters.sweepLE)) * (ConvAndConst.WingPlanformConstants.b / 2 - Params.WingPlanformParameters.yMAC) + 0.42 * Params.EmpennageParameters.verticalTailMAC + Params.EmpennageParameters.verticalTailSpanwiseLocMAC * np.tan(np.radians(Params.EmpennageParameters.sweepLE))) / Params.WingPlanformParameters.wingMAC
    # Calculate C.G. location of engine on the wing. 
    enginesCGMAC = (0.7 * Params.WingPlanformParameters.kinkChord - np.tan(np.radians(Params.WingPlanformParameters.sweepLE)) * (Params.WingPlanformParameters.yMAC - Params.WingPlanformParameters.kinkLocation)) / Params.WingPlanformParameters.wingMAC
    # Calculate C.G. location of engine along nacelle length. 
    engineCGNacelle = (0.4 * Params.PropulsionSizingParameters.ln * Params.ClassIIWEParameters.nacelleWeight + 0.6 * Params.PropulsionSizingParameters.ln * Params.ClassIIWEParameters.motorWeight) / ((Params.ClassIIWEParameters.motorWeight + Params.ClassIIWEParameters.nacelleWeight) * Params.PropulsionSizingParameters.ln)
    engineCGFus = (0.7 * ConvAndConst.FuselagePlanformConstants.XLP + engineCGNacelle * Params.PropulsionSizingParameters.ln) / ConvAndConst.FuselagePlanformConstants.XLP

    fuselageCG = ((0.4 * Params.FuselagePlanformParameters.fuselageMAC) + (ConvAndConst.FuselagePlanformConstants.XLP - Params.FuselagePlanformParameters.fuselageMAC)) / ConvAndConst.FuselagePlanformConstants.XLP
	
    # Wing Group C.G. with respect to the mean aerodynamic chord
    WingGroupWeights = np.array([Params.ClassIIWEParameters.WWING - Params.ClassIIWEParameters.W4, Params.ClassIIWEParameters.WVT, Params.ClassIIWEParameters.engineWeight * Params.ClassIIWEParameters.NEW], dtype=object).flatten()
    WingGroupLocations = np.array([ConvAndConst.CGExcursionConstants.xi_wing, verticalTailCGMAC, enginesCGMAC], dtype=object).flatten() * Params.WingPlanformParameters.wingMAC 
    CGWingGroupMAC = np.sum(np.multiply(WingGroupWeights, WingGroupLocations)) / (np.sum(WingGroupWeights) * Params.WingPlanformParameters.wingMAC)

    # Fuselage Group C.G. with respect to fuselage length
    FuselageGroupWeights = np.array([Params.ClassIIWEParameters.WFUS + Params.ClassIIWEParameters.W4, Params.ClassIIWEParameters.engineWeight * Params.ClassIIWEParameters.FNEF, Params.ClassIIWEParameters.hydrogenTankWeight, Params.ClassIIWEParameters.fuelCellWeight, Params.ClassIIWEParameters.WSYSEQUIPMENT, Params.ClassIIWEParameters.WOPERATINGITEMS], dtype=object).flatten()
    FuselageGroupLocations = np.array([fuselageCG, engineCGFus, ConvAndConst.CGExcursionConstants.x_cg_Fuel, ConvAndConst.CGExcursionConstants.xi_fuel_cells, ConvAndConst.CGExcursionConstants.xi_sys_eq, ConvAndConst.CGExcursionConstants.xi_operating_items], dtype=object).flatten() * ConvAndConst.FuselagePlanformConstants.XLP
    CGFuselageGroupFus = np.sum(np.multiply(FuselageGroupWeights, FuselageGroupLocations)) / np.sum(FuselageGroupWeights)

    if xLEMAC is None:
        LEMACLocation = CGFuselageGroupFus + Params.WingPlanformParameters.wingMAC * (CGWingGroupMAC * (np.sum(WingGroupWeights) / np.sum(FuselageGroupWeights)) - ConvAndConst.CGExcursionConstants.xoew_aircraft_wrt_mac * (1 + (np.sum(WingGroupWeights) / np.sum(FuselageGroupWeights))))
        CGOEW = LEMACLocation + Params.WingPlanformParameters.wingMAC * ConvAndConst.CGExcursionConstants.xoew_aircraft_wrt_mac

    else:
        x_cg_wing_wrt_fuselage = xLEMAC + CGWingGroupMAC * Params.WingPlanformParameters.wingMAC
        CGOEW = ((x_cg_wing_wrt_fuselage * np.sum(WingGroupWeights)) + (CGFuselageGroupFus * np.sum(FuselageGroupWeights))) / (np.sum(FuselageGroupWeights) + np.sum(WingGroupWeights))

    # Calculate OEW C.G. along fuselage length.
    OEWcg = CGOEW / ConvAndConst.FuselagePlanformConstants.XLP

    return OEWcg

def classIICGExcursion(Params, ConvAndConst):
    """
    Function to calculate the most forward and aft C.G. locations.

    Inputs:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Outputs:
    -----
    aftCG, the most aft cg location, measured from the nose of the aircraft [m]
    """

    # CG location of fuel multiplied by fuel weight
    WxCGFuel = Params.ClassIWEParameters.WF * ConvAndConst.CGExcursionConstants.x_cg_Fuel * ConvAndConst.FuselagePlanformConstants.XLP
    # CG location of OEW multiplied by OEW weight
    WxCGOEW = Params.ClassIWEParameters.WOE * Params.CGExcursionParameters.cgOEW * ConvAndConst.FuselagePlanformConstants.XLP
    # CG location of payload multiplied by payload weight
    WxCGPL = Params.payloadWeight * ConvAndConst.CGExcursionConstants.x_cg_payload * ConvAndConst.FuselagePlanformConstants.XLP

    # Calculate CG locations of different configurations
    cgOEWFuel = (WxCGFuel + WxCGOEW) / (Params.ClassIWEParameters.WF + Params.ClassIWEParameters.WOE)
    cgOEWPayload = (WxCGOEW + WxCGPL) / (Params.payloadWeight + Params.ClassIWEParameters.WOE)
    cgAll = (WxCGPL + WxCGFuel + WxCGOEW) / (Params.payloadWeight + Params.ClassIWEParameters.WOE + Params.ClassIWEParameters.WF)
    
    # Calculate most forward and most aft CG locations
    fwdCG = min(cgOEWFuel, cgOEWPayload, cgAll)
    aftCG = max(cgOEWFuel, cgOEWPayload, cgAll)

    return aftCG

def CGExcursion(Params, ConvAndConst):
    """
    Function to perform the C.G. excursion.

    Inputs:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants
    """

    # Calculate OEW C.G. location as fraction of fuselage length
    Params.CGExcursionParameters.cgOEW = emptyWeightCGCalculator(Params, ConvAndConst, xLEMAC=19.)
    # Calculate the most aft C.G. location from different configurations
    aftCG = classIICGExcursion(Params, ConvAndConst)
    
    # Calculate vertical tail CG location
    cgVT = ConvAndConst.CGExcursionConstants.xLEMAC + (ConvAndConst.WingPlanformConstants.b - 2 * Params.WingPlanformParameters.yMAC - ConvAndConst.FuselagePlanformConstants.fuselageWidth) / 2 * np.tan(np.radians(Params.WingPlanformParameters.sweepLE)) + np.tan(np.radians(Params.EmpennageParameters.sweepLE)) * Params.EmpennageParameters.verticalTailSpanwiseLocMAC + Params.EmpennageParameters.verticalTailMAC * 0.42
    Params.EmpennageParameters.Lvt = cgVT - aftCG

    return