"""

This file performs all the functions related to the aerodynamic performance of the blended wing body.

@author: Thomas Stephan Vermeulen

"""

import numpy as np

def calculateLiftCoefficients(Params):
    """
    Function to calculate the cruise and loiter lift coefficients.

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    cruiseCL, cruise lift coefficient [-]
    loiterCL, loiter lift coefficient [-]
    """

    # Cruise Lift Coefficient
    Params.WingLoadings.startOfCruiseWingLoading = (Params.ClassIWEParameters.WOE + Params.payloadWeight + Params.ClassIWEParameters.h2TO) / Params.Sref
    Params.WingLoadings.endOfCruiseWingLoading = (Params.ClassIWEParameters.WOE + Params.payloadWeight + Params.ClassIWEParameters.h2endCruise) / Params.Sref
    cruiseCL = 1 / (0.5 * Params.cruiseDensity * Params.cruiseSpeed ** 2) * (0.5 * (Params.WingLoadings.startOfCruiseWingLoading + Params.WingLoadings.endOfCruiseWingLoading))

    # Loiter Lift Coefficient
    Params.WingLoadings.startOfLoiterWingLoading = (Params.ClassIWEParameters.WOE + Params.payloadWeight + Params.ClassIWEParameters.h2endApp) / Params.Sref
    Params.WingLoadings.endOfLoiterWingLoading = (Params.ClassIWEParameters.WOE + Params.payloadWeight) / Params.Sref
    loiterCL = 1 / (0.5 * Params.loiterDensity * Params.loiterSpeed ** 2) * (0.5 * (Params.WingLoadings.startOfLoiterWingLoading + Params.WingLoadings.endOfLoiterWingLoading))

    return cruiseCL, loiterCL

def wettedAreas(Params, ConvAndConst):
    """
    Function to compute the component wetted areas. 

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    fuselageWettedArea, wetted area of the fuselage [m2]
    wingWettedArea, wetted area of the wing [m2]
    totalNacelleWettedArea, wetted area of all the nacelles combined [m2]
    totalPylonWettedArea, wetted area of all the engine pylons [m2]
    verticalTailWettedArea, wetted area of the vertical tails [m2]
    """

    # Nacelle relations are taken from Torenbeek 1988
    nacelleWettedArea = Params.PropulsionSizingParameters.ln * Params.PropulsionSizingParameters.Dn * ( 2 + 0.35 * ConvAndConst.EngineConstants.beta + 0.8 * ( Params.PropulsionSizingParameters.ln * ConvAndConst.EngineConstants.beta * Params.PropulsionSizingParameters.Di ) / ( Params.PropulsionSizingParameters.ln * Params.PropulsionSizingParameters.Dn ) + 1.15 * ( 1 - ConvAndConst.EngineConstants.beta ) * Params.PropulsionSizingParameters.De / Params.PropulsionSizingParameters.Dn ) #[m2]
    totalNacelleWettedArea = nacelleWettedArea * Params.PropulsionSizingParameters.num_engines * 0.85
    totalPylonWettedArea = 0.1 * totalNacelleWettedArea # Pylon area is typically 20% of nacelle wetted area, but with aerodynamic placement its assumed to be 10%

    # Empennage wetted area from Torenbeek 1988
    verticalTailWettedArea = 2 * Params.EmpennageParameters.areaTail * (1 + 0.25 * ConvAndConst.EmpennageConstants.tcVerticalTail)

    # Wing and Fuselage wetted area from Torenbeek 1988
    wingWettedArea = 2 * Params.WingPlanformParameters.wingAreaExp * (1 + 0.25 * ConvAndConst.AirfoilParams.tcWing)
    fuselageWettedArea = 2 * ConvAndConst.FuselagePlanformConstants.fuselageArea * (1 + 0.25 * ConvAndConst.AirfoilParams.tcFuselage) 

    return fuselageWettedArea, wingWettedArea, totalNacelleWettedArea, totalPylonWettedArea, verticalTailWettedArea

def getCD0(speed, Mach, nu, Params, ConvAndConst):
    """ 
    Function to calculate the zero-lift drag coefficient of the aircraft, 
    based on the drag component build-up method.

    Inputs:
    -----
    speed, airspeed of condition considered [m/s]
    Mach, mach number of condition considered [-]
    nu, kinematic viscosity of air at condition considered [m2/s]
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    cleanCD0, the zero-lift drag coefficient of the aircraft in clean configuration [-]
    landingCD0, the zero-lift drag coefficient of the aircraft in landing configuration [-]
    """

    # Calculate Reynolds numbers for each component of the aircraft
    if Mach >= 0.8:
        # Transonic Regime
        reynoldsFuselage = min(speed * Params.FuselagePlanformParameters.fuselageMAC / nu, 44.62 * (Params.FuselagePlanformParameters.fuselageMAC / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor) ** 1.053 * Mach ** 1.16)
        reynoldsWing = min(speed * Params.WingPlanformParameters.wingMAC / nu, 44.62 * (Params.WingPlanformParameters.wingMAC / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor) ** 1.053 * Mach ** 1.16) 
        reynoldsVtail = min(speed * Params.EmpennageParameters.verticalTailMAC / nu, 44.62 * (Params.EmpennageParameters.verticalTailMAC / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor ) ** 1.503 * Mach ** 1.16) 
        reynoldsNacelle = min(speed * Params.PropulsionSizingParameters.ln / nu, 44.62 * (Params.PropulsionSizingParameters.ln / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor ) ** 1.503 * Mach ** 1.16)
    else:
        # Subsonic Regime
        reynoldsFuselage = min(speed * Params.FuselagePlanformParameters.fuselageMAC / nu, 38.21 * (Params.FuselagePlanformParameters.fuselageMAC / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor) ** 1.053)
        reynoldsWing = min(speed * Params.WingPlanformParameters.wingMAC / nu, 38.21 * (Params.WingPlanformParameters.wingMAC / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor) ** 1.053) 
        reynoldsVtail = min(speed * Params.EmpennageParameters.verticalTailMAC / nu, 38.21 * (Params.EmpennageParameters.verticalTailMAC / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor ) ** 1.503) 
        reynoldsNacelle = min(speed * Params.PropulsionSizingParameters.ln / nu, 38.21 * (Params.PropulsionSizingParameters.ln / ConvAndConst.AerodynamicPerformanceConstants.surfaceFactor ) ** 1.503)

    # Laminar skin friction coefficients
    CfFuselageLam = 1.328 / np.sqrt(reynoldsFuselage)   
    CfWingLam = 1.328 / np.sqrt(reynoldsWing)
    CfVtailLam = 1.328 / np.sqrt(reynoldsVtail)
    CfNacelleLam = 1.328 / np.sqrt(reynoldsNacelle)
    
    # Turbulent skin friction coefficients
    CfFuselageTur = 0.455 / (((np.log10(reynoldsFuselage)) ** 2.58) * (1 + 0.144 * Mach ** 2) ** 0.65)
    CfWingTur = 0.455 / (((np.log10(reynoldsWing)) **  2.58) * (1 + 0.144 * Mach ** 2) ** 0.65)
    CfVtailTur = 0.455 / (((np.log10(reynoldsVtail)) ** 2.58) * (1 + 0.144 * Mach ** 2) ** 0.65)
    CfNacelleTur = 0.455 / (((np.log10(reynoldsNacelle)) ** 2.58) * (1 + 0.144 * Mach ** 2) ** 0.65)
    
    # Calculate the averaged skin friction coefficients
    CfFuselage = (1 - ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction) * CfFuselageLam + ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction * CfFuselageTur
    CfWing = (1 - ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction) * CfWingLam + ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction * CfWingTur
    CfVtail = (1 - ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction) * CfVtailLam + ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction * CfVtailTur
    CfNacelle = (1 - ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction) * CfNacelleLam + ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction * CfNacelleTur
    CfPylon = (1 - ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction) * CfWingLam + ConvAndConst.AerodynamicPerformanceConstants.turbulenceFraction * CfWingTur #We assume the pylon to have the same properties as the wing

    # Calculate form factors
    formFacFuselage = (1 + 0.6 / ConvAndConst.AirfoilParams.xcMaxFuselage * ConvAndConst.AirfoilParams.tcFuselage + 100 * ConvAndConst.AirfoilParams.tcFuselage ** 4) * (1.34 * Mach ** 0.18 * (np.cos(np.radians(Params.FuselagePlanformParameters.sweepC2))) ** 0.28 )
    formFacWing = (1 + 0.6 / ConvAndConst.AirfoilParams.xcMaxWing * ConvAndConst.AirfoilParams.tcWing + 100 * ConvAndConst.AirfoilParams.tcWing ** 4) * (1.34 * Mach ** 0.18 * (np.cos(np.radians(Params.WingPlanformParameters.sweepC4))) ** 0.28 )
    formFacVtail =  (1 + 0.6 / ConvAndConst.EmpennageConstants.xcMaxVtail * ConvAndConst.EmpennageConstants.tcVerticalTail + 100 *ConvAndConst.EmpennageConstants.tcVerticalTail ** 4) * (1.34 * Mach ** 0.18 * (np.cos(np.radians(Params.EmpennageParameters.sweepC4))) ** 0.28)
    nacelleFactor = Params.PropulsionSizingParameters.ln / Params.PropulsionSizingParameters.Dn 
    formFacNacelle = 1 + 0.35 / nacelleFactor
    formFacPylon = (1 + 0.6 / 0.3 * 0.12 + 100 * 0.12 ** 4) * (1.34 * Mach ** 0.18 * (np.cos(np.radians(45))) ** 0.28) # assumed NACA0012 airfoil, pylon sweep of 30 deg
     
    # Product of interference and form factors. For Fuselage and Wing simply equal to formFac, as no interference occurs here
    facFuselage = formFacFuselage
    facWing = formFacWing
    facVtail = formFacVtail * ConvAndConst.AerodynamicPerformanceConstants.intFacVtail
    facNacelle = formFacNacelle * ConvAndConst.AerodynamicPerformanceConstants.intFacNacelle
    facPylon = formFacPylon * ConvAndConst.AerodynamicPerformanceConstants.intFacPylon

    # Streamwise thickness to chord ratios
    tcStreamwiseWing = ConvAndConst.AirfoilParams.tcWing * np.cos(np.radians(Params.WingPlanformParameters.sweepC4)) 
    tcStreamwiseFus = ConvAndConst.AirfoilParams.tcFuselage * np.cos(np.radians(Params.FuselagePlanformParameters.sweepC4))

    # Estimating drag divergence Mach number
    MddFuselage = ConvAndConst.AerodynamicPerformanceConstants.kaFuselage / np.cos(np.radians(Params.FuselagePlanformParameters.sweepLE)) - tcStreamwiseFus / (np.cos(np.radians(Params.FuselagePlanformParameters.sweepLE)) ** 2) - Params.AerodynamicPerformanceParameters.cruiseCL / (10 * (np.cos(np.radians(Params.FuselagePlanformParameters.sweepLE))) ** 3)
    MddWing = ConvAndConst.AerodynamicPerformanceConstants.kaWing / np.cos(np.radians(Params.WingPlanformParameters.sweepLE)) - tcStreamwiseWing / (np.cos(np.radians(Params.WingPlanformParameters.sweepLE)) ** 2) - Params.AerodynamicPerformanceParameters.cruiseCL / (10 * (np.cos(np.radians(Params.WingPlanformParameters.sweepLE))) ** 3)
    MddAverage = (MddFuselage * ConvAndConst.FuselagePlanformConstants.fuselageArea + MddWing * Params.WingPlanformParameters.wingAreaExp) / (Params.Sref)

    # Wave drag contributions
    McritAverage = (ConvAndConst.AerodynamicPerformanceConstants.McritFuselage * ConvAndConst.FuselagePlanformConstants.fuselageArea + ConvAndConst.AerodynamicPerformanceConstants.McritWing * Params.WingPlanformParameters.wingAreaExp) / (Params.Sref)
    if Mach < ConvAndConst.AerodynamicPerformanceConstants.McritFuselage and Mach < ConvAndConst.AerodynamicPerformanceConstants.McritWing:
        CD0WaveDrag = 0
    elif McritAverage < Mach < MddAverage:
        CD0WaveDrag = 0.002 * (1 + 2.5 * (MddAverage - Mach)/0.05) ** (-1)
    elif MddAverage < Mach:
        CD0WaveDrag = 0.002 * (1 + (Mach - MddAverage) / 0.05) ** (2.5)

    # Landing gear drag contributions
    # We assume closed wheel wells!
    Sa_nose = ConvAndConst.UndercarriageConstants.noseWheelStrutLength * (Params.UndercarriageParameters.noseWheelWidth * 0.25) + (Params.UndercarriageParameters.noseWheelWidth * Params.UndercarriageParameters.noseWheelDiameter) * 2 # [m2] - Reference area of nose gear
    dCD0_NLGS = 0.04955 * np.exp(5.615 * Sa_nose / (ConvAndConst.UndercarriageConstants.noseWheelStrutLength * Params.UndercarriageParameters.noseWheelWidth * 2.25))

    Sa_main = ConvAndConst.UndercarriageConstants.mainWheelStrutLength * (Params.UndercarriageParameters.mainWheelWidth * 0.25) + (Params.UndercarriageParameters.mainWheelWidth * Params.UndercarriageParameters.mainWheelDiameter) * 2 # [m2] - Reference area of main gear
    dCD0_MLGS = 0.04955 * np.exp(5.615 * Sa_main / (ConvAndConst.UndercarriageConstants.mainWheelStrutLength * Params.UndercarriageParameters.mainWheelWidth * 2.25))

    noseGearCD0 = dCD0_NLGS * Sa_nose / (Params.Sref)
    mainGearCD0 = dCD0_MLGS * Sa_main / (Params.Sref)

    # Wetted Areas
    Params.AerodynamicPerformanceParameters.fuselageWettedArea, Params.AerodynamicPerformanceParameters.wingWettedArea, Params.AerodynamicPerformanceParameters.totalNacelleWettedArea, Params.AerodynamicPerformanceParameters.totalPylonWettedArea, Params.AerodynamicPerformanceParameters.verticalTailWettedArea = wettedAreas(Params, ConvAndConst)

    # Calculate CD0 in clean and landing configuration
    cleanCD0Base = ((CfFuselage * facFuselage * Params.AerodynamicPerformanceParameters.fuselageWettedArea + CfWing * facWing * Params.AerodynamicPerformanceParameters.wingWettedArea + CfVtail * facVtail * Params.AerodynamicPerformanceParameters.verticalTailWettedArea + CfNacelle * facNacelle * Params.AerodynamicPerformanceParameters.totalNacelleWettedArea + CfPylon * facPylon * Params.AerodynamicPerformanceParameters.totalPylonWettedArea) / Params.Sref)
    cleanCD0 = cleanCD0Base + CD0WaveDrag + cleanCD0Base * ConvAndConst.AerodynamicPerformanceConstants.excDrag
    landingCD0 = cleanCD0Base + cleanCD0Base * ConvAndConst.AerodynamicPerformanceConstants.excDrag + noseGearCD0 + mainGearCD0
    
    return cleanCD0, landingCD0

def DragPolar(Params, ConvAndConst):
    """
    Function to calculate the required parameters for the drag polar.

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    cruiseLD, cruise lift-to-drag ratio [-]
    loiterLD, loiter lift-to-drag ratio [-]
    """
    
    # Calculate effective aspect ratio taking into account wing tips
    Params.PlanformParameters.effectiveAR = Params.PlanformParameters.geometricAR * (1 + 1.9 * Params.EmpennageParameters.verticalTailSpan / (2 * ConvAndConst.WingPlanformConstants.b))
    
    # Lift coefficients
    Params.AerodynamicPerformanceParameters.cruiseCL, Params.AerodynamicPerformanceParameters.loiterCL = calculateLiftCoefficients(Params)

    # Zero-lift drag coefficients
    Params.AerodynamicPerformanceParameters.cleanCruiseCD0, Params.AerodynamicPerformanceParameters.dirtyCruiseCD0 = getCD0(Params.cruiseSpeed, Params.cruiseMach, Params.cruiseNu, Params, ConvAndConst)
    Params.AerodynamicPerformanceParameters.cleanLoiterCD0, Params.AerodynamicPerformanceParameters.dirtyLoiterCD0 = getCD0(Params.loiterSpeed, Params.loiterMach, Params.loiterNu, Params, ConvAndConst)

    # Cruise drag coefficient
    cruiseCD = Params.AerodynamicPerformanceParameters.cleanCruiseCD0 + Params.AerodynamicPerformanceParameters.cruiseCL ** 2 / (np.pi * Params.PlanformParameters.effectiveAR * Params.PlanformParameters.oswaldFactor)

    # Loiter drag Coefficient
    loiterCD = Params.AerodynamicPerformanceParameters.cleanLoiterCD0 + Params.AerodynamicPerformanceParameters.loiterCL ** 2 / (np.pi * Params.PlanformParameters.effectiveAR * Params.PlanformParameters.oswaldFactor)

    # Lift-to-drag ratios
    cruiseLD = Params.AerodynamicPerformanceParameters.cruiseCL / cruiseCD
    loiterLD = Params.AerodynamicPerformanceParameters.loiterCL / loiterCD

    return cruiseLD, loiterLD