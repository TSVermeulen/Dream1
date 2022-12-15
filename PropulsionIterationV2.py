"""

Propulsion Subsystem Design Functions. 
Original work done by Thomas, Stefan & Sebastiaan from group 1 of the fall DSE 2021/2022
Reworked to use classes and ensure consistency amongst different subsystems/files.

@author: Thomas Stephan Vermeulen

"""

import numpy as np
from ambiance import Atmosphere
from scipy.integrate import quad

def engineAero(h, M, ConvAndConst):
    """
    Function to find aerodynamic properties
    of turboelectric engine cycle.
    Function output is verified to match original.

    Inputs:
    -----
    h, altitude [m]
    M, freestream Mach number [-]
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    Ve, exit velocity [m/s]
    Te, exit temperature [K]
    pe, exit pressure [Pa]
    T0a, total temperature before the engine [K]
    p0a, total pressure before the engine [Pa]
    p01, total pressure at the inlet [Pa]
    T02, total temperature after the fan [K]
    rho_e, airdensity at the nozzle [kg/m3]
    choked, boolean if nozzle throat is choked [-]
    """

    # Atmospheric properties
    atmos = Atmosphere(h)
    T = atmos.temperature
    p = atmos.pressure

    # Total freestream properties
    p0a = p * (1 + ((ConvAndConst.ka - 1) / 2) * M ** 2) ** (ConvAndConst.ka / (ConvAndConst.ka - 1))
    T0a = T * (1 + ((ConvAndConst.ka - 1) / 2) * M ** 2)

    # Temperature and pressure at the inlet
    T01 = T0a * (1 + (1 / (ConvAndConst.EngineConstants.inletEfficiency)) * ((ConvAndConst.EngineConstants.pressureLosses ** ((ConvAndConst.ka - 1) / ConvAndConst.ka)) - 1))
    p01 = p * (1 + ConvAndConst.EngineConstants.inletEfficiency * (T01 / T - 1)) ** (ConvAndConst.ka / (ConvAndConst.ka - 1)) * ConvAndConst.EngineConstants.pressureLosses

    # Temperature and pressure after the fan
    T02 = T01 * (1 + (1 / ((ConvAndConst.EngineConstants.fanEfficiency - ConvAndConst.EngineConstants.fanDistortion) * ConvAndConst.EngineConstants.fanIsentropicEfficiency)) * ((ConvAndConst.EngineConstants.FPR ** ((ConvAndConst.ka - 1) / ConvAndConst.ka)) - 1))
    p02 = ConvAndConst.EngineConstants.FPR * p01

    # Nozzle exit
    pecrit = p02 * (1 - (1 / ConvAndConst.EngineConstants.nozzleEfficiency) * ((ConvAndConst.ka - 1)/(ConvAndConst.ka + 1))) ** (ConvAndConst.ka / (ConvAndConst.ka - 1))
    if pecrit < p: # Unchoked Nozzle
        pe = p
        Te = T02 * (1 - ConvAndConst.EngineConstants.nozzleEfficiency * (1 - (p / p02) ** ((ConvAndConst.ka - 1) / ConvAndConst.ka)))
        Ve = np.sqrt(2 * ConvAndConst.Cp_air * (T02 - Te))
        rho_e = pe / (ConvAndConst.R * Te)
        choked = False

    else: # Choked Nozzle
        pe = pecrit
        Te = T02 * (2 / (ConvAndConst.ka + 1))
        Ve = np.sqrt(ConvAndConst.ka * ConvAndConst.R * Te) 
        rho_e = pe / (ConvAndConst.R * Te)
        choked = True

    return Ve, Te, pe, T0a, p0a, p01, T02, rho_e, choked
    

def engineSizing(h, M, Neng, thrustSetting, Params, ConvAndConst, TC=False):
    """
    Function to determine the dimensions of the engines
    Function output is verified to match original.

    Inputs:
    -----
    h, altitude [m]
    M, freestream Mach number [-]
    Neng, number of engines [-]
    thrustSetting, thrust setting used as fraction of maximum thrust
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    Pfan, fan power required per engine [W]
    Ptot, total fan power required [W]
    massFlow, air mass flow through the engine [kg/s]
    Dfan, fan diameter [m]
    Se, nozzle exit area [m2]
    Di, inlet diameter [m]
    De, exit diameter [m]
    Dn, maximum nacelle diameter [m]
    Dh, hub diameter [m]
    ln, nacelle length [m]
    """

    # Atmospheric properties
    atmos = Atmosphere(h)
    a = atmos.speed_of_sound
    rho = atmos.density
    pa = atmos.pressure

    # Dummy list to start out the sizing process
    Se_lst = [10,2]

    # Obtain aerodynamic properties of cycle
    Ve, Te, pe, T0a, p0a, p01, T02, rho_e, choked = engineAero(h, M, ConvAndConst)

    while abs((Se_lst[-1]-Se_lst[-2]) / Se_lst[-2]) > 0.01:
        # Start iteration to obtain correct engine size
        
        # Required thrust per Engine
        thrustPerEngine = (Params.totalThrustRequired) / Neng * thrustSetting * (rho / ConvAndConst.rho0) ** (3/4) # [N]

        if TC == True:
            #Thrust required at top of climb, with correct weight of aircraft. 
            thrustTC = (Params.thrustLoading * (Params.ClassIWEParameters.WOE + Params.payloadWeight + Params.ClassIWEParameters.h2TO) + np.sin(ConvAndConst.EngineConstants.vpa) * (Params.ClassIWEParameters.WOE + Params.payloadWeight + Params.ClassIWEParameters.h2TO)) / np.cos(ConvAndConst.EngineConstants.vpa)
            thrustPerEngine = (thrustTC / Neng) * thrustSetting * (rho / ConvAndConst.rho0) ** (3/4)

        # Required mass flow to satisfy the take-off requirement
        massFlow = (thrustPerEngine - Se_lst[-1] * (pe - pa)) / (Ve - M * a) # [kg/s]

        # Nozzle exit area and diameter
        Se = massFlow / (Ve * rho_e) # [m2]
        De = 2 * np.sqrt(Se / np.pi)  # [m] - Assume circular section

        # Fan surface area and radius. Radius takes into account tip-hub ratio
        Sfan = massFlow / (p0a * ConvAndConst.EngineConstants.Mfan * np.sqrt(ConvAndConst.ka / (ConvAndConst.R * T0a)) * (1 + (ConvAndConst.ka - 1) / 2 * ConvAndConst.EngineConstants.Mfan ** 2) ** ((1 + ConvAndConst.ka) / (2 * (1 - ConvAndConst.ka))))
        rfan = np.sqrt(Sfan / (np.pi * (1 - ConvAndConst.EngineConstants.sigma ** 2)))

        if choked == False:
            Se_lst.append(Se)
            Se_lst.append(Se)
        elif choked == True:
            Se_lst.append(Se)

    # Change in Enthalpy & required fan power
    dH = ConvAndConst.Cp_air * (T02 - T0a)
    Pfan = dH * massFlow

    # Engine sizing
    Dfan = 2 * rfan # [m]
    Di = Dfan # [m] - We assume fan and inlet diameter are equal
    motorLength = rfan * ConvAndConst.EngineConstants.motorLengthRatio
    volumeInverter = ConvAndConst.EngineConstants.motorPower / ConvAndConst.EngineConstants.specificVolumeInverter
    lInverter = volumeInverter / ((np.pi * (rfan * ConvAndConst.EngineConstants.sigma)) ** 2)
    lHub = lInverter + motorLength
    ln = lHub / (1 - ConvAndConst.EngineConstants.beta)
    Dn = Di + 0.06 * ConvAndConst.EngineConstants.phi * ln + 0.03
    Dh = Di * ConvAndConst.EngineConstants.sigma # [m] - hub diameter

    # Total power required
    Ptot = Pfan * Neng

    # Fan blade tip speed
    n = (np.sqrt(T0a) / (np.pi * 2 * rfan)) * (2227.9 * ConvAndConst.EngineConstants.FPR - 1941.2)
    Params.PropulsionSizingParameters.Vtip = (2 * rfan) * np.pi * n / 60

    return Pfan, Ptot, massFlow, Dfan, Se, Di, De, Dn, Dh, ln

def altitudeThrustChecker(h, M, Neng, thrustSetting, Params, ConvAndConst, TC=False):
    """
    Function to check if ducted fan optimised for take-off also satisfies cruise thrust requirement.
    Function output is verified to match original.

    Inputs:
    -----
    h, altitude [m]
    M, freestream mach number [-]
    Neng, number of engines [-]
    thrustSetting, thrust setting used as fraction of maximum thrust
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    Pfan, fan power per engine [W]
    Ptot, total power [W]
    thrustDeficit, difference in thrust between actual and required [N]
    """

    # Cycle analysis results at altitude of interest
    Ve, Te, pe, T0a, p0a, p01, T02, rhoe, choked = engineAero(h, M, ConvAndConst)

    # Atmospheric properties
    atmos = Atmosphere(h)
    a = atmos.speed_of_sound
    rho = atmos.density
    pa = atmos.pressure

    # Mach number at exit
    Me = Ve / a

    # Maximum massflow at the nozzle at cruise altitude
    maxMassFlow = pe * Me * Params.PropulsionSizingParameters.Se * np.sqrt(ConvAndConst.ka / (ConvAndConst.R * Te))
    
    # Thrust per engine at cruise altitude
    maxThrustPerEngine = maxMassFlow * (Ve - M * a)

    # Required thrust per engine based on Take-off thrust and thrust setting (corrected for altitude)
    thrustPerEngineRequired = ((Params.thrustLoading * Params.ClassIWEParameters.WTO) / Neng) * thrustSetting * (rho / ConvAndConst.rho0) ** (3/4)
    if TC == True:
        #Thrust required at top of climb, with correct weight of aircraft.        
        thrustTC = (Params.thrustLoading * (Params.ClassIWEParameters.WOE + Params.payloadWeight + Params.ClassIWEParameters.h2TO) + np.sin(ConvAndConst.EngineConstants.vpa) * (Params.ClassIWEParameters.WOE + Params.payloadWeight + Params.ClassIWEParameters.h2TO)) / np.cos(ConvAndConst.EngineConstants.vpa)
        thrustPerEngineRequired = (thrustTC / Neng) * thrustSetting * (rho / ConvAndConst.rho0) ** (3/4)
    # Mass flow required to obtain the needed thrust per engine
    if choked == False:
        massFlowRequired = thrustPerEngineRequired / (Ve - M * a)
    else:
        massFlowRequired = (thrustPerEngineRequired - Params.PropulsionSizingParameters.Se * (pe - pa)) / (Ve - M * a)
        
    # Change in Enthalpy & power required by the fan
    dH = ConvAndConst.Cp_air * (T02 - T0a)
    Pfan = dH * massFlowRequired

    # Total Fan Power Required
    Ptot = Pfan * Neng

    #Thrust Deficit
    thrustDeficit = maxThrustPerEngine - thrustPerEngineRequired

    return Pfan, Ptot, thrustDeficit

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

def weightComponents(Params, ConvAndConst):
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
    atmos = Atmosphere(Params.cruiseAltitude)
    T_cr = atmos.temperature
    p_cr = atmos.pressure
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
    CpcompCR = ConvAndConst.Cp_air * (T_cr / ConvAndConst.EngineConstants.compressorEfficiency) * ((ConvAndConst.EngineConstants.pExitCompressor / p_cr) ** ((ConvAndConst.ka - 1) / ConvAndConst.ka) - 1)
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

def averageDensity(hmax):
    """
    Function to calculate the altitude at which the area density is half of that of the density at hmax
    Function output is verified to match original.

    Inputs:
    -----
    hmax, maximum altitude in the interval [0,hmax] [m]

    Outputs:
    -----
    delta, the altitude at which the area density is half [m]
    """

    heights = np.linspace(0, hmax, num=11000)
    density = Atmosphere(heights).density
    weighted_density = density / 1.225

    degree = -((9.80665) / (-0.0065 * 287.15) + 1)
    x = np.polyfit(heights, weighted_density, degree)
    y = np.poly1d(x)
    delta = 0
    while quad(y, 0, delta) < quad(y, delta, hmax):
        delta += 1
    return delta

def PropulsionIteration(Params, ConvAndConst):
    """ 
    Iterative function to size the propulsion subsystem
    Function output is verified to match original.

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    num, number of engines [-]
    Dfan, diameter of the fan [m]
    Di, diameter of the inlet [m]
    De, diameter of the exhaust [m]
    Se, exit area [m2]
    ln, length of the nacelle [m]
    Dn, maximum nacelle thickness [m]
    """ 

    # Number of engines on which will be iterated
    N_engines = np.arange(4, 50, 1)

    # Calculate thrust settings:
    Params.PropulsionSizingParameters.TsetCr = ((0.5 * (Params.WingLoadings.startOfCruiseWingLoading + Params.WingLoadings.endOfCruiseWingLoading) * Params.Sref) / Params.ClassIWEParameters.cruiseLD) / Params.totalThrustRequired
    Params.PropulsionSizingParameters.TsetLoiter = ((0.5 * (Params.WingLoadings.startOfLoiterWingLoading + Params.WingLoadings.endOfLoiterWingLoading) * Params.Sref) / Params.ClassIWEParameters.loiterLD) / Params.totalThrustRequired
            

    #Iterate
    for num in N_engines:
        # Initial sizing is based on top-of-climb
        Pfan_TC, Params.ClassIWEParameters.topOfClimbPower, mass_flow, Params.PropulsionSizingParameters.Dfan, Params.PropulsionSizingParameters.Se, Params.PropulsionSizingParameters.Di, Params.PropulsionSizingParameters.De, Params.PropulsionSizingParameters.Dn, Params.PropulsionSizingParameters.Dh, Params.PropulsionSizingParameters.ln = engineSizing(Params.cruiseAltitude, Params.cruiseMach, num, Params.PropulsionSizingParameters.TsetTC, Params, ConvAndConst, TC=True)      
        
        # Climb
        Pfan_cl, Params.ClassIWEParameters.climbPower, diff1 = altitudeThrustChecker(ConvAndConst.EngineConstants.climbAppAlt, ConvAndConst.EngineConstants.climbMach, num, Params.PropulsionSizingParameters.TsetCL, Params, ConvAndConst) 
        # Take-off
        Pfan_TO, Params.ClassIWEParameters.takeOffPower, diff2 = altitudeThrustChecker(0, 0.25, num, Params.PropulsionSizingParameters.TsetTO, Params, ConvAndConst)
        # Cruise
        Pfan_CR, Params.ClassIWEParameters.cruisePower, diff3 = altitudeThrustChecker(Params.cruiseAltitude, Params.cruiseMach, num, Params.PropulsionSizingParameters.TsetCr, Params, ConvAndConst)
        
        if max(Pfan_cl, Pfan_TO, Pfan_CR, Pfan_TC) <= ConvAndConst.EngineConstants.motorPower and diff1 >= 0 and diff2 >= 0 and diff3 >= 0:
            # Approach power for final config
            Params.ClassIWEParameters.approachPower = altitudeThrustChecker(ConvAndConst.EngineConstants.climbAppAlt, ConvAndConst.EngineConstants.approachMach, num, Params.PropulsionSizingParameters.TsetApp, Params, ConvAndConst)[1]
            # Loiter power for final config
            Params.ClassIWEParameters.loiterPower = altitudeThrustChecker(Params.loiterAltitude, Params.loiterMach, num, Params.PropulsionSizingParameters.TsetLoiter, Params, ConvAndConst)[1]
            
            Params.PlanformParameters.propulsionWidth = (Params.PropulsionSizingParameters.Dn + 0.05) * num
            # Locations of the Engines. FNEF is the number of engines on the aft fuselage, and NEW is the number of engines on the wing
            if ConvAndConst.FuselagePlanformConstants.fuselageWidth > Params.PlanformParameters.propulsionWidth: #If the engines take up less width than the fuselage area, all engines fit on the aft part of the fuselage
                Params.ClassIIWEParameters.FNEF = num
                Params.ClassIIWEParameters.NEW = 0
            else:
                Params.ClassIIWEParameters.FNEF = np.floor((ConvAndConst.FuselagePlanformConstants.fuselageWidth / Params.PlanformParameters.propulsionWidth) * num)
                Params.ClassIIWEParameters.NEW = num - Params.ClassIIWEParameters.FNEF      
            break
    
    return num
