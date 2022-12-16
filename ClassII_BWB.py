"""

Class II Weight Estimation Method for the Blended Wing Body concept
Based off the articles:

"Semi-Analytical Weight Estimation Method for Fuselages with Oval Cross-Section"
by Roelof Vos and Maurice Hoogreef

"A Sizing Methodology for the Conceptual Design of Blended-Wing-Body Transports"
by Kevin R. Bradley

"The Flight Optimization System Weights Estimation Method"
by Douglas P. Wells and Bryce L. Horvath

@author: Thomas Stephan Vermeulen

"""

import numpy as np
from TankDesign import HydrogenTankWeightEstimation
from ambiance import Atmosphere

def classIIPropulsionScaling(Params):
    """
    Function to scale the engine dimensions such that they can be used within the FLOPS Weight Estimation Method.
    Taken from FLOPS Eq. 81, 82, 83, 84, 85

    Inputs:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Outputs:
    -----
    none, all scaling parameters are immediately updated into the Params class.
    """

    # Scale total number of engines, thrust per engine, and nacelle diameter
    if Params.PropulsionSizingParameters.num_engines <= 4:
        Params.ClassIIWEParameters.FNENG = Params.PropulsionSizingParameters.num_engines
        Params.ClassIIWEParameters.FTHRUST = Params.totalThrustRequired / Params.PropulsionSizingParameters.num_engines
        Params.ClassIIWEParameters.FNAC = Params.PropulsionSizingParameters.Dn
    else:
        Params.ClassIIWEParameters.FNENG = 4 + 2 * np.arctan((Params.PropulsionSizingParameters.num_engines - 4.0) / 3.0)
        Params.ClassIIWEParameters.FTHRUST = Params.totalThrustRequired / Params.ClassIIWEParameters.FNENG
        Params.ClassIIWEParameters.FNAC = Params.PropulsionSizingParameters.Dn * np.sqrt(Params.PropulsionSizingParameters.num_engines) / 2.0

    # Scale number of engines on the wing
    if Params.ClassIIWEParameters.NEW <= 4:
        Params.ClassIIWEParameters.NEW = Params.ClassIIWEParameters.NEW
    else:
        Params.ClassIIWEParameters.NEW = 4 + 2 * np.arctan((Params.ClassIIWEParameters.NEW - 4.0) / 3.0)

    # Scale number of engines on the fuselage
    if Params.ClassIIWEParameters.FNEF <= 4:
        Params.ClassIIWEParameters.FNEF = Params.ClassIIWEParameters.FNEF
    else:
        Params.ClassIIWEParameters.FNEF = 4 + 2 * np.arctan((Params.ClassIIWEParameters.FNEF - 4.0) / 3.0)
        
    return

def classIIFuselage(Params, ConvAndConst):
    """ 
    Function to calculate the weight of the fuselage. 
    Taken from FLOPS Eq. 58

    Input:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Output: 
    -----
    fuselageWeight, weight of the fuselage [N]
    """

    # Conversions of inputs for weight estimation equation from SI into Imperial
    DG = Params.ClassIWEParameters.WTO / ConvAndConst.lbs2kg / ConvAndConst.g
    ACABIN = ConvAndConst.FuselagePlanformConstants.cabinArea / (ConvAndConst.ft2m ** 2)

    # Calculate weight of fuselage in lb
    WFUSE = 1.8 * DG ** 0.167 * ACABIN ** 1.06

    # Weight of fuselage in N
    fuselageWeight = WFUSE * ConvAndConst.lbs2kg * ConvAndConst.g

    return fuselageWeight 

def classIIWingSimplified(Params, ConvAndConst):
    # (S, AR, fuselageWidth, cabinArea, wallLength, fuselageLength, TCA, FAERT, ULF, FCOMP, DG, NEW, FNEF, RSPCHD, PCTL, c4WingSweep, TR, SFLAP, Sfuselage, blendWidth)
    """
    FLOPS simplified wing weight estimation method
    note that all units are imperial
    note specific to BWB
    Input:
    -----
    S, wing area [m2]
    AR, assumed aspect ratio [-]
    fuselageWidth, width of the fuselage [m]
    TCA, weighted average of t/c of both fuselage and wing [-]
    FAERT, aeroelastic tailoring factor [-]
    ULF, ultimate load factor, standard value of 3.75 from source is used [-]
    FCOMP, composite utilization factor for wing structure, 0.0<FCOMP<1.0 [-]
    DG, MTOW [lb]
    NEW, number of engines on the wing [-]
    FNEF, number of engines on the back part of the fuselage [-]
    RSPCHD, root spar location as fraction of chord length [-]
    
    Output:
    -----
    WWING, wing weight [lb]
    SPAN, wingspan [ft]
    """

    #Conversions from SI into imperial
    S = Params.Sref / (ConvAndConst.ft2m ** 2)
    cabinArea = ConvAndConst.FuselagePlanformConstants.cabinArea / (ConvAndConst.ft2m ** 2)
    fuselageWidth = ConvAndConst.FuselagePlanformConstants.fuselageWidth / ConvAndConst.ft2m
    wallLength = ConvAndConst.FuselagePlanformConstants.XLW / ConvAndConst.ft2m
    fuselageLength = ConvAndConst.FuselagePlanformConstants.XLP / ConvAndConst.ft2m
    DG = Params.ClassIWEParameters.WTO / ConvAndConst.lbs2kg / ConvAndConst.g
    Sfuselage = ConvAndConst.FuselagePlanformConstants.fuselageArea / (ConvAndConst.ft2m ** 2)
    SFLAP = Params.ControlSurfaceParameters.aileronArea / (ConvAndConst.ft2m ** 2)

    #Wing Weight Equation Constants
    A1 = 8.8
    A2 = 6.25
    A3 = 0.68
    A4 = 0.34
    A5 = 0.60
    A6 = 0.035
    A7 = 1.5

    SPAN = ConvAndConst.WingPlanformConstants.b / ConvAndConst.ft2m #[ft]
    OSSPAN = (SPAN - fuselageWidth) / 2 #[ft]

    # Calculate Percentage of Load Carried by wing
    PCTL = Params.WingPlanformParameters.wingAreaExp / Params.Sref

    #Equivalent bending factor
    TLAM = np.tan(np.radians(Params.WingPlanformParameters.sweepC4)) - (2.0 * (1.0 - Params.WingPlanformParameters.wingTaper)) / (Params.PlanformParameters.geometricAR * (1.0 + Params.WingPlanformParameters.wingTaper))
    SLAM = TLAM / np.sqrt(1.0 + TLAM ** 2)
    C4 = 1.0 - 0.5 * Params.ClassIIWEParameters.FAERT
    C6 = 0.5 * Params.ClassIIWEParameters.FAERT 
    if Params.PlanformParameters.geometricAR <= 5:
        CAYA = 0
    else:
        CAYA = Params.PlanformParameters.geometricAR - 5
    CAYL = (1.0 - SLAM ** 2) * (1.0 + C6 * SLAM ** 2 + 0.03 * CAYA * C4 * SLAM)
    BT = 0.215 * (0.37 + 0.7 * Params.WingPlanformParameters.wingTaper) * (Params.PlanformParameters.geometricAR) / (CAYL * Params.ClassIIWEParameters.TCA)

    #Total Wing Bending Material Weight
    W1NIR = A1 * BT * (1.0 + np.sqrt( A2 / OSSPAN)) * Params.ClassIIWEParameters.ULF * OSSPAN * (1 - 0.4 * Params.ClassIIWEParameters.FCOMP) * (1.0 - 0.1 * Params.ClassIIWEParameters.FAERT) * PCTL / 1000000

    #Total Wing Shear Material and Control Surface Weight
    W2 = A3 * (1.0 - 0.17 * Params.ClassIIWEParameters.FCOMP) * SFLAP ** A4 * DG ** A5

    #Total Wing Miscellaneous Items Weight
    W3 = A6 * (1.0 - 0.3 * Params.ClassIIWEParameters.FCOMP) * S ** A7

    #Wing Bending Material Weight Inertia Relief Adjustment:
    CAYE = 1.0 - 0.03 * Params.ClassIIWEParameters.NEW
    W1 = (DG * CAYE * W1NIR + W2 + W3) / (1.0 + W1NIR) - W2 - W3

    #Total Aft Body Weight for Hybrid Wing Body Aircraft:
    TRAFTB = ((1.0 - ConvAndConst.FuselagePlanformConstants.rearSparXC) * wallLength / ConvAndConst.FuselagePlanformConstants.rearSparXC) / ((1 - ConvAndConst.FuselagePlanformConstants.rearSparXC) * fuselageLength)
    TRAFTB = wallLength * (1 - ConvAndConst.FuselagePlanformConstants.rearSparXC) / (fuselageLength * (1 - ConvAndConst.FuselagePlanformConstants.rearSparXC))
    FPAREA = fuselageWidth * (fuselageLength + wallLength) / (2 * ConvAndConst.FuselagePlanformConstants.rearSparXC)
    SAFTB = FPAREA - cabinArea
    SAFTB = Sfuselage - cabinArea

    W4 = (1.0 + 0.05 * Params.ClassIIWEParameters.FNEF) * 0.53 * SAFTB * DG ** 0.2 * (0.5 + TRAFTB) * (1 - 0.17 * Params.ClassIIWEParameters.FCOMP)

    WWING = W1 + W2 + W3 + W4
    WWING = WWING * ConvAndConst.lbs2kg * ConvAndConst.g
    # print("W1", W1, "W2", W2, "W3", W3, "W4", W4)
    Params.ClassIIWEParameters.W4 = W4 * ConvAndConst.lbs2kg * ConvAndConst.g
    
    return WWING

def classIILandingGear(Params, ConvAndConst):
    """ 
    Function to calculate the weight of the landing gear.
    Taken from FLOPS Eq. 63-67

    Input:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Output: 
    -----
    WLG, Total landing gear weight [N]
    """

    # Conversion of inputs from SI into imperial
    XMLG = ConvAndConst.UndercarriageConstants.mainWheelStrutLength / ConvAndConst.inch2m
    XNLG = ConvAndConst.UndercarriageConstants.noseWheelStrutLength / ConvAndConst.inch2m
    WMLD = Params.ClassIWEParameters.WmaxLand / ConvAndConst.lbs2kg / ConvAndConst.g

    # Calculate landing gear weights
    WLGM = (0.0117) * WMLD ** 0.95 * XMLG ** 0.43 # MLG
    WLGN = (0.048) * WMLD ** 0.67 * XNLG ** 0.43 # NLG
    WLG = WLGM + WLGN

    # Convert weight back into SI units
    WLG = WLG * ConvAndConst.lbs2kg * ConvAndConst.g

    return WLG

def classIIPaint(Params, ConvAndConst):
    """ 
    Function to calculate the weight of the paint on the aircraft. 
    Taken from FLOPS Eq. 68

    Input:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants
    
    Output: 
    -----
    paintWeight, total weight of the paint [N]
    """

    # Conversion from SI into imperial
    SWTWG = Params.AerodynamicPerformanceParameters.wingWettedArea / (ConvAndConst.ft2m ** 2)
    SWTFU = Params.AerodynamicPerformanceParameters.fuselageWettedArea / (ConvAndConst.ft2m ** 2)
    SWTNA = Params.AerodynamicPerformanceParameters.totalNacelleWettedArea / (ConvAndConst.ft2m ** 2)
    SWTPY = Params.AerodynamicPerformanceParameters.totalPylonWettedArea / (ConvAndConst.ft2m ** 2)
    SWTVT = Params.AerodynamicPerformanceParameters.verticalTailWettedArea / (ConvAndConst.ft2m ** 2)
    
    # Calculate total weight of paint and convert into SI units
    WTPNT = Params.ClassIIWEParameters.paintDensity * (SWTWG + SWTFU + SWTNA + SWTPY + SWTVT)
    paintWeight = WTPNT * ConvAndConst.lbs2kg * ConvAndConst.g
    
    return paintWeight

def classIISystemsandEquipment(Params, ConvAndConst):
    """ 
    Function to calculate the systems and equipment weight.
    Taken from FLOPS Eq. 97-115
 
    Input:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Output: 
    -----
    systemsAndEquipmentWeight, weight of the systems and equipment [N]
    """

    # Scaling of Propulsion Subsystem
    classIIPropulsionScaling(Params)

    # Conversion from SI into imperial
    S = Params.Sref / (ConvAndConst.ft2m ** 2) 
    SFLAP = Params.ControlSurfaceParameters.aileronArea / (ConvAndConst.ft2m ** 2) 
    DG = Params.ClassIWEParameters.WTO / ConvAndConst.lbs2kg / ConvAndConst.g
    fuselageWidth = ConvAndConst.FuselagePlanformConstants.fuselageWidth / ConvAndConst.ft2m 
    DESRNG = Params.designRange / 1000 * ConvAndConst.km2nmi
    ACABIN = ConvAndConst.FuselagePlanformConstants.cabinArea / (ConvAndConst.ft2m ** 2) 
    FPAREA = ConvAndConst.FuselagePlanformConstants.fuselageArea / (ConvAndConst.ft2m ** 2) 
    FNAC = Params.ClassIIWEParameters.FNAC / ConvAndConst.ft2m
    B = ConvAndConst.WingPlanformConstants.b / ConvAndConst.ft2m
    DF = ConvAndConst.FuselagePlanformConstants.fuselageHeight / ConvAndConst.ft2m
    FTHRST = Params.ClassIIWEParameters.FTHRUST / ConvAndConst.g / ConvAndConst.lbs2kg
    XL = ConvAndConst.FuselagePlanformConstants.XLP / ConvAndConst.ft2m

    # Calculate weight of the engine controls
    WEC = 0.26 * Params.ClassIIWEParameters.FNENG * (FTHRST) ** 0.5 
    # Calculate surface controls weight
    WSC = 1.1 * Params.ClassIIWEParameters.VMAX ** 0.52 * SFLAP ** 0.6 * DG ** 0.32   
    # Calculate instruments weight
    WIN = 0.48 * FPAREA ** 0.57 * Params.ClassIIWEParameters.VMAX ** 0.5 * (10 + 2.5 * Params.ClassIIWEParameters.NFLCR + Params.ClassIIWEParameters.NEW + 1.5 * Params.ClassIIWEParameters.FNEF)   
    # Calculate hydraulics weight
    WHYD = 0.57 * (FPAREA + 0.27 * S) * (1 + 0.03 * Params.ClassIIWEParameters.NEW + 0.05 * Params.ClassIIWEParameters.FNEF) * (3000 / Params.ClassIIWEParameters.HYDPR) ** 0.35 * Params.ClassIIWEParameters.VMAX ** 0.33
    # Calculate electrical systems weight
    WELEC = 92 * XL ** 0.4 * fuselageWidth ** 0.14 * Params.ClassIIWEParameters.FNENG ** 0.69 * (1 + 0.044 * Params.ClassIIWEParameters.NFLCR + 0.0015 * Params.numberPax)
    # Calculate avionics weight
    WAVONC = 15.8 * DESRNG ** 0.1 * Params.ClassIIWEParameters.NFLCR ** 0.7 * FPAREA ** 0.43
    # Calculate furniture weight
    WFURN = 127 * Params.ClassIIWEParameters.NFLCR + 44 * Params.numberPax + 2.6 * ((ACABIN * (fuselageWidth + DF))/fuselageWidth + fuselageWidth * DF * (1 + 1/np.cos(np.radians(Params.FuselagePlanformParameters.sweepLE))))
    # Calculate airconditioning weight
    WAC = (3.2 * (FPAREA * DF) ** 0.6 + 9 * Params.numberPax ** 0.83) * Params.ClassIIWEParameters.VMAX + 0.075 * WAVONC 
    # Calculate anti-ice weight
    WAI = B / (np.cos(np.radians(Params.PlanformParameters.averagedSweepC4))) + 3.8 * FNAC * Params.ClassIIWEParameters.FNENG + 1.5 * fuselageWidth
    
    # Sum subsystem weights to obtain overall systems and equipment weight and convert back to SI units
    WSYSEQUIPMENT = WEC + WSC + WIN + WHYD + WELEC + WAVONC + WFURN + WAC + WAI
    systemsAndEquipmentWeight = WSYSEQUIPMENT * ConvAndConst.lbs2kg * ConvAndConst.g
    
    return systemsAndEquipmentWeight

def classIIOperatingItems(Params, ConvAndConst):
    """ 
    Function to calculate the weight of the operating items.
    Taken from FLOPS Eq. 116-124
    
    Input:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Output: 
    -----
    operatingItemsWeight, the weight of the operating items [N]
    """

    # Conversion from SI into imperial units
    DESRNG = Params.designRange * ConvAndConst.km2nmi / 1000

    # Calculate weight of flight attendants and flight crew
    WSTUAB = Params.numberFlightAttendants * 155 
    WFLCRB = Params.ClassIIWEParameters.NFLCR * 225

    # Calculate in-flight service weight
    WSRV = (2.529 * Params.numberPax) * (DESRNG / Params.ClassIIWEParameters.VMAX) ** 0.225 

    # Calculate total weight of operating items and convert back to SI units
    WOPERATING = WSTUAB + WFLCRB + WSRV
    operatingItemsWeight = WOPERATING * ConvAndConst.lbs2kg * ConvAndConst.g
    
    return operatingItemsWeight

def classIIVerticalTail(Params, ConvAndConst):
    """
    Function to calculate the weights of the vertical tail.
    Taken from FLOPS Eq. 50

    Input:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Outputs:
    -----
    verticalTailWeight, total weight of the vertical tails [N]
    """

    # Conversion from SI into imperial units
    DG = Params.ClassIWEParameters.WTO / ConvAndConst.lbs2kg / ConvAndConst.g
    SVT = Params.EmpennageParameters.areaTail / (ConvAndConst.ft2m ** 2) / ConvAndConst.EmpennageConstants.NVERT

    # Calculate vertical tail weight and convert back to SI units
    WVT = 0.32 * DG ** 0.3 * (ConvAndConst.EmpennageConstants.taper + 0.5) * ConvAndConst.EmpennageConstants.NVERT ** 0.7 * SVT ** 0.85
    verticalTailWeight = WVT * ConvAndConst.lbs2kg * ConvAndConst.g

    return verticalTailWeight

def weightEstimationFan(Params, ConvAndConst):
    """ 
    Function to estimate the weight of the engines
    Based On: https://ntrs.nasa.gov/api/citations/19720005136/downloads/19720005136.pdf

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    Wtotal, the total weight of all the engines [N]
    Wnacelle, the weight of a nacelle [N]
    """

    # Mass of the fan
    fanMass = 85.38 * (Params.PropulsionSizingParameters.Dfan ** 2.7) * ((Params.PropulsionSizingParameters.Vtip / 350) ** 0.3)
    fanMass = fanMass * ConvAndConst.EngineConstants.compositeFan

    # Duct Lining Mass
    # Hub length is assumed to be 80% of nacelle
    linningMass = np.pi * ((Params.PropulsionSizingParameters.ln * Params.PropulsionSizingParameters.Di) + (Params.PropulsionSizingParameters.ln * 0.65 * Params.PropulsionSizingParameters.Dh)) * ConvAndConst.EngineConstants.WAw

    # Duct casing Mass
    ductMass = np.pi * ((Params.PropulsionSizingParameters.Di + Params.PropulsionSizingParameters.De + Params.PropulsionSizingParameters.Dn) / 3) * Params.PropulsionSizingParameters.ln * ConvAndConst.EngineConstants.rhoDuct * ConvAndConst.EngineConstants.tDuct

    # Grouping Masses
    totalPerFanMass = fanMass + linningMass + ductMass
    nacelleWeight = (ductMass + linningMass) * ConvAndConst.g
    totalWeight = totalPerFanMass * Params.PropulsionSizingParameters.num_engines * ConvAndConst.g

    return totalWeight, nacelleWeight

def Fuelcells(Pmax, ConvAndConst):
    """
    Function to estimate the fuell cell mass.
    Based on the use of the PowerCellution P Stack fuel cells:
    https://www.datocms-assets.com/36080/1636022110-p-stack-v-221.pdf

    Inputs:
    -----
    Pmax, maximum power required from the fuel cells to drive the fans [W]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    fuelCellWeight, the total mass of the fuel cells [N]
    """

    fuelCellWeight = Pmax / ConvAndConst.EngineConstants.fuelCellEnergyDensity * ConvAndConst.g

    return fuelCellWeight

def classIIPropulsionSystem(Params, ConvAndConst):
    """
    Grouping functions to calculate the weights of the different components of the propulsion subsystem

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    totalWeight, total weight of the propulsion subsystem [N]
    fuelCellWeight, total weight of fuel cells [N]
    WperEngine, mass per engine [N]
    motorWeight, weight of one motor [N]
    nacelleWeight, mass of one nacelle [N]
    """
    
    # Atmospheric properties
    atmos = Atmosphere(ConvAndConst.EngineConstants.climbAppAlt)
    T_cl = atmos.temperature
    p_cl = atmos.pressure
    atmos = Atmosphere(Params.loiterAltitude)
    T_loi = atmos.temperature
    p_loi = atmos.pressure
    
    # Calculate Ducted Fan Weight
    totalFanWeight, nacelleWeight = weightEstimationFan(Params, ConvAndConst)

    # Calculate the weight of the motor 
    motorWeight = ConvAndConst.EngineConstants.motorPower / ConvAndConst.EngineConstants.specificEnergyMotor * ConvAndConst.g

    # Calculate the weight of the electrical inverter
    inverterWeight = ConvAndConst.EngineConstants.motorPower / ConvAndConst.EngineConstants.specificEnergyInverter * ConvAndConst.g

    # Calculate total power required in each phase accounting for efficiencies and additional power needed to power other systems
    Ptot_CL_we = (Params.ClassIWEParameters.climbPower / (ConvAndConst.EngineConstants.motorEfficiency * ConvAndConst.EngineConstants.inverterEfficiency) +  ConvAndConst.EngineConstants.additionalPower) / ConvAndConst.EngineConstants.cableEfficiency
    Ptot_TO_we = (Params.ClassIWEParameters.takeOffPower / (ConvAndConst.EngineConstants.motorEfficiency * ConvAndConst.EngineConstants.inverterEfficiency) +  ConvAndConst.EngineConstants.additionalPower) / ConvAndConst.EngineConstants.cableEfficiency
    Ptot_CR_we = (Params.ClassIWEParameters.cruisePower / (ConvAndConst.EngineConstants.motorEfficiency * ConvAndConst.EngineConstants.inverterEfficiency) +  ConvAndConst.EngineConstants.additionalPower) / ConvAndConst.EngineConstants.cableEfficiency
    Ptot_APP_we = (Params.ClassIWEParameters.approachPower / (ConvAndConst.EngineConstants.motorEfficiency * ConvAndConst.EngineConstants.inverterEfficiency) +  ConvAndConst.EngineConstants.additionalPower) / ConvAndConst.EngineConstants.cableEfficiency
    Ptot_LOI_we = (Params.ClassIWEParameters.loiterPower / (ConvAndConst.EngineConstants.motorEfficiency * ConvAndConst.EngineConstants.inverterEfficiency) +  ConvAndConst.EngineConstants.additionalPower) / ConvAndConst.EngineConstants.cableEfficiency
    Ptot_TC_we = (Params.ClassIWEParameters.topOfClimbPower / (ConvAndConst.EngineConstants.motorEfficiency * ConvAndConst.EngineConstants.inverterEfficiency) +  ConvAndConst.EngineConstants.additionalPower) / ConvAndConst.EngineConstants.cableEfficiency

    # Calculating Compressor Power during each phase of flight considered
    CpcompCR = ConvAndConst.Cp_air * (Params.cruiseTemperature / ConvAndConst.EngineConstants.compressorEfficiency) * ((ConvAndConst.EngineConstants.pExitCompressor / Params.cruisePressure) ** ((ConvAndConst.ka - 1) / ConvAndConst.ka) - 1)
    CpcompTO = ConvAndConst.Cp_air * (ConvAndConst.T0 / ConvAndConst.EngineConstants.compressorEfficiency) * ((ConvAndConst.EngineConstants.pExitCompressor / ConvAndConst.p0) ** ((ConvAndConst.ka - 1) / ConvAndConst.ka) - 1)
    CpcompCL = ConvAndConst.Cp_air * (T_cl / ConvAndConst.EngineConstants.compressorEfficiency) * ((ConvAndConst.EngineConstants.pExitCompressor / p_cl) ** ((ConvAndConst.ka - 1) / ConvAndConst.ka) - 1)
    CpcompLOI = ConvAndConst.Cp_air * (T_loi / ConvAndConst.EngineConstants.compressorEfficiency) * ((ConvAndConst.EngineConstants.pExitCompressor / p_loi) ** ((ConvAndConst.ka - 1) / ConvAndConst.ka) - 1)

    compressorPowerCL = CpcompCL * Ptot_CL_we / (ConvAndConst.EngineConstants.specificEnergyLH / 9 - CpcompCL) 
    compressorPowerTO = CpcompTO * Ptot_TO_we / (ConvAndConst.EngineConstants.specificEnergyLH / 9 - CpcompTO) 
    compressorPowerCR = CpcompCR * Ptot_CR_we / (ConvAndConst.EngineConstants.specificEnergyLH / 9 - CpcompCR)
    compressorPowerApp = CpcompCL * Ptot_APP_we / (ConvAndConst.EngineConstants.specificEnergyLH / 9 - CpcompCL)
    compressorPowerLOI = CpcompLOI * Ptot_LOI_we / (ConvAndConst.EngineConstants.specificEnergyLH / 9 - CpcompLOI)
    compressorPowerTC = CpcompCR * Ptot_TC_we / (ConvAndConst.EngineConstants.specificEnergyLH / 9 - CpcompCR)

    # Adding compressor power to obtain total power
    totalClimbPower = Ptot_CL_we + compressorPowerCL
    totalTakeOffPower = Ptot_TO_we + compressorPowerTO
    totalCruisePower = Ptot_CR_we + compressorPowerCR
    totalApproachPower = Ptot_APP_we + compressorPowerApp
    totalLoiterPower = Ptot_LOI_we + compressorPowerLOI
    totalTopOfClimbPower = Ptot_TC_we + compressorPowerTC
    
    # Calculate fuel cell mass
    fuelCellWeight = Fuelcells(max(totalClimbPower, totalTakeOffPower, totalCruisePower, totalApproachPower, totalLoiterPower, totalTopOfClimbPower), ConvAndConst)

    # Calculate liquid cooling mass
    LCWeight = fuelCellWeight * ConvAndConst.EngineConstants.ratioLC

    # Total mass
    WperEngine = totalFanWeight / Params.PropulsionSizingParameters.num_engines + motorWeight + inverterWeight
    totalWeight = totalFanWeight + Params.PropulsionSizingParameters.num_engines * (motorWeight + inverterWeight) + fuelCellWeight + LCWeight

    # Writing power during each phase of flight to design parameter class
    Params.ClassIWEParameters.takeOffPower = totalTakeOffPower
    Params.ClassIWEParameters.cruisePower = totalCruisePower
    Params.ClassIWEParameters.approachPower = totalApproachPower
    Params.ClassIWEParameters.loiterPower = totalLoiterPower
    Params.ClassIWEParameters.climbPower = totalClimbPower
    Params.ClassIWEParameters.topOfClimbPower = totalTopOfClimbPower

    return totalWeight, fuelCellWeight, WperEngine, motorWeight, nacelleWeight

def classIIWeightEstimation(Params, ConvAndConst):
    """
    Class II Weight Estimation function to calculate the weight of the blended-wing-body design.

    Inputs:
    -----
    Params, class of design parameters
    ConvAndConst, class containing unit conversions and constants

    Outputs:
    -----
    none, all parameters are immediately updated into the Params class.
    """

    # Calculate Hydrogen Tank Weight
    Params.ClassIIWEParameters.hydrogenTankWeight = HydrogenTankWeightEstimation(Params, ConvAndConst)

    # Calculate Propulsion System Weight
    Params.ClassIIWEParameters.propulsionWeight, Params.ClassIIWEParameters.fuelCellWeight, Params.ClassIIWEParameters.engineWeight, Params.ClassIIWEParameters.motorWeight, Params.ClassIIWEParameters.nacelleWeight = classIIPropulsionSystem(Params, ConvAndConst)
    
    # Calculate Fuselage Weight
    Params.ClassIIWEParameters.WFUS = classIIFuselage(Params, ConvAndConst)

    # Calculate Wing Weight
    Params.ClassIIWEParameters.WWING = classIIWingSimplified(Params, ConvAndConst)  

    # Calculate Weight of Vertical Tail
    Params.ClassIIWEParameters.WVT = classIIVerticalTail(Params, ConvAndConst) 

    # Calculate Landing Gear Weight
    Params.ClassIIWEParameters.WLG = classIILandingGear(Params, ConvAndConst)

    # Calculate Paint Weight
    Params.ClassIIWEParameters.WTPNT = classIIPaint(Params, ConvAndConst)

    # Calculate Systems and Equipment Weight
    Params.ClassIIWEParameters.WSYSEQUIPMENT = classIISystemsandEquipment(Params, ConvAndConst)

    # Calculate Operating Items Weight
    Params.ClassIIWEParameters.WOPERATINGITEMS = classIIOperatingItems(Params, ConvAndConst)

    # Calculate Operating Empty Weight
    Params.ClassIWEParameters.WOE = (Params.ClassIIWEParameters.WFUS + Params.ClassIIWEParameters.WWING + Params.ClassIIWEParameters.WLG + Params.ClassIIWEParameters.WTPNT + Params.ClassIIWEParameters.WSYSEQUIPMENT + Params.ClassIIWEParameters.WOPERATINGITEMS + Params.ClassIIWEParameters.WVT + Params.ClassIIWEParameters.propulsionWeight + Params.ClassIIWEParameters.hydrogenTankWeight)

    return