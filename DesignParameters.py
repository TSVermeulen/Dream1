"""

This file contains the class definitions for the initial parameters of the design vector used in the iteration for the Lightning2 aircraft.

@author: Thomas

"""

from ambiance import Atmosphere
from PropulsionIterationV2 import averageDensity
import numpy as np

class DesignParameters:
    """
    Design parameters Class
    """

    # Iteration Parameters
    wingLoading = 1800                                      # [N/m2]
    thrustLoading = 0.26                                    # [-]
    Sref = 340.43 # [m2]
    totalThrustRequired = 0. # [N]

    # # Mission and general design parameters
    numberPax = 150                                         # [-]
    numberFlightAttendants = 1 + np.ceil(numberPax / 40)
    payloadWeight = 154454.7375                               # [N]
    designRange = 3700 * 10 ** 3 # [m] 
    cruiseMach = 0.8                                        # [-]    

    cruiseAltitude = 10972.8                                # [m]
    atmos = Atmosphere(cruiseAltitude)
    cruiseSpeed = atmos.speed_of_sound * cruiseMach         # [m/s]
    cruiseDensity = atmos.density      # [kg/m3]
    cruiseTemperature = atmos.temperature
    cruisePressure = atmos.pressure
    cruiseSpeedOfSound = atmos.speed_of_sound
    cruiseNu = atmos.kinematic_viscosity
    
    loiterAltitude = 5000                                   # [m]
    loiterSpeed = 118.3222212                               # [m/s]
    atmos = Atmosphere(loiterAltitude)
    loiterDensity = atmos.density      # [kg/m3]
    loiterNu = atmos.kinematic_viscosity
    loiterMach = loiterSpeed / atmos.speed_of_sound
    loiterTime = 3600.                                      # [s]

    approachSpeed = 82.12                                   # [m/s]
    # climbSpeed = 154.333332                                 # [m/s]
    flightTime = 15660.                                     # [s]

    averageROC = 12.7 # [m/s]
    averageDOC = 15.225 # [m/s]
    climbTime = cruiseAltitude / averageROC
    flightTime = designRange / (cruiseSpeed)
    approachTime = cruiseAltitude / averageDOC
    cruiseTime = flightTime - climbTime - approachTime

    class ClassIWEParameters:
        """ Parameters stored relating to the Class I Weight Estimation """
        takeOffPower = 0.                                       # [W] 
        cruisePower = 0.                                        # [W] 
        approachPower = 0.                                      # [W] 
        loiterPower = 0. 
        climbPower = 0.
        topOfClimbPower = 0.                                       # [W]
        
        ROC = 12.7                                             # [m/s]
        DOC = 15.225                                            # [m/s]
        cruiseLD = 22.                                           # [-]
        loiterLD = 26.                                           # [-]
        cruiseCj = 6.1183 * 10 ** (-6)                          # [kg/Ns]
        loiterCj = 0.8 * cruiseCj                               # [kg/Ns]   
        Mres = 0.05                                             # [-]

        WF = 60783.01576352                                     # [N]
        WmaxLand = 0                                            # [N] 
        WTO = 472045.94724203                                   # [N] 
        WOE = 0                                                 # [N]
        h2TO = 0                                                # [N]
        h2endCruise = 0                                         # [N]
        h2endApp = 0                                            # [N]

    class PropulsionSizingParameters:
        """ Parameters stored relating to the propulsion subsystem sizing """                     
        Pfan = 0 # [W]
        Ptot = 0 # [W]
        massFlow = 0 # [W]
        Dfan = 0 # [m]
        Se = 0 # [m2]
        Di = Dfan # [m]
        De = 0 # [m]
        Dn = 0 # [m]
        Dh = 0 # [m]
        ln = 0 # [m]
        num_engines = 0 # [-]
        Vtip = 0. # [m/s]

        # # Thrust settings
        TsetTC = 1.
        TsetCL = 1.
        TsetApp = 0.15
        TsetLoiter = .5

        TsetCr = 1.0
        TsetTO = 1.0

    class FuselagePlanformParameters:
        """ Parameters related to the fuselage planform """
        sweepLE = 0. # [deg]
        sweepC4 = 0. # [deg]
        sweepC2 = 0. # [deg]
        fuselageMAC = 0. # [m]

    class WingPlanformParameters:
        """ Parameters related to the wing planform """
        wingAreaExp = 0. # [m2]
        rootChord = 0. # [m]
        kinkChord = 0. # [m]
        tipChord = 0. # [m]
        kinkLocation = 0. # [m]
        sweepC4 = 0. # [deg] 
        sweepC2 = 0. # [deg]
        sweepLE = 0. # [deg] 
        wingMAC = 0. # [m]
        distanceLEWing = 0. # [m] 
        yMAC = 0. # [m]
        wingTaper = 0. # [-] 
        aircraftTaper = 0.1 # [-]

    class PlanformParameters:
        """ Parameters related to the overall aircraft planform """
        geometricAR = 9. # [-]
        effectiveAR = 10.8 # [-] - Given initial value of 1.2 * geometricAR
        averagedSweepC2 = 0. # [deg]
        averagedSweepC4 = 0. # [deg]
        averagedSweepLE = 0. # [deg]
        liftCurveSlope = 0. # [1/deg]
        maxLiftCoefficient = 0. # [-]
        stallAngleOfAttack = 0. # [deg]
        oswaldFactor = 0. # [deg]
        stallSpeed = 60. # [m/s]
        propulsionWidth = 0. # [m]

    class ClassIIWEParameters:
        """ Parameters related to the class II Weight Estimation """
        FNENG = 0 # [-]
        FNEF = 0 # [-]
        NEW = 0 # [-]
        FTHRUST = 0. # [N]
        FNAC = 0. # [m]
        TCA = 0. # [-]
        FAERT = 0
        ULF = 3.75
        FCOMP = 0
        VMAX = 0.85
        paintDensity = 0.204816144 * 0.3 # Area density of paint [lb/ft2]
        NFLCR = 2
        HYDPR = 3000 # hydraulic system pressure [psi]
        NFLCR = 2
        W4 = 0. # [N]
        WFUS = 0. # [N]
        WWING = 0. # [N]
        WLG = 0. # [N]
        WTPNT = 0. # [N]
        WSYSEQUIPMENT = 0. # [N]
        WOPERATINGITEMS = 0. # [N]
        WVT = 0. # [N]

        propulsionWeight = 0. # [N]
        hydrogenTankWeight = 0. # [N]
        fuelCellWeight = 0. # [N]
        engineWeight = 0. # [N]
        motorWeight = 0. # [N]
        nacelleWeight = 0. # [N]

    class ControlSurfaceParameters:
        """ Parameters related to the control surface design """
        Clda = 0. # [-] - Aileron control derivative
        Clp = 0. # [-] - Roll damping coefficient
        P = 0. # [rad/s] - Steady roll rate
        rollTime = 0. # [s] - Time needed for aircraft to roll 45 degrees
        aileronArea = 0. # [m2] - Surface area of ailerons

    class EmpennageParameters:
        """ Parameters related to the empennage design """
        Lvt = 31 * 0.5  
        verticalTailSpan = 1. # [m]
        areaTail = 0. # [m2]
        sweepLE = 0. # [deg]
        sweepC4 = 0. # [deg]
        rootChordVerticalTail = 0. # [m]
        tipChordVerticalTail = 0. # [m]
        verticalTailMAC = 0.1 # [m]
        verticalTailSpanwiseLocMAC = 0. # [m]
        verticalTailHorizontalLocMAC = 0. # [m]
    
    class AerodynamicPerformanceParameters:
        """ Parameters related to the aerodynamic performance of the aircraft """
        cruiseCL = 0. # [-]
        loiterCL = 0. # [-]
        cleanCruiseCD0 = 0. # [-]
        dirtyCruiseCD0 = 0. # [-]
        cleanLoiterCD0 = 0. # [-]
        dirtyLoiterCD0 = 0. # [-]
        fuselageWettedArea = 0. # [m2]
        wingWettedArea = 0. # [m2]
        totalNacelleWettedArea = 0. # [m2] 
        totalPylonWettedArea = 0. # [m2]
        verticalTailWettedArea = 0. # [m2]

    class UndercarriageParameters:
        """ Parameters related to the undercarriage """
        noseWheelDiameter = 1.27                                              # [m]
        noseWheelWidth = 0.508                                             # [m]
        mainWheels = 4                                                 # [-]
        mainWheelDiameter = 2 * noseWheelDiameter                                           # [m]
        mainWheelWidth = 2 * noseWheelWidth                                           # [m]
        

    class HydrogenTankParameters:
        """ Parameters related to the hydrogen tank design """
        requiredVolumeTotal = 0. # [m3]
        requiredVolumePerTank = 0. # [m3]
        finalRadiusInner = 0. # [m]
        finalRadiusOuter = 0. # [m]
        availableVolumePerTank = 0. # [m3]
        lengthCylinder = 0. # [m]
        burstPressureInnerTank = 0. # [Pa]
        burstPressureOutOerTank = 0. # [Pa]
        finalThicknessInner = 0. # [m]
        finalThicknessOuter = 0. # [m]
        tankMassInnerTank = 0. # [kg]
        surfaceAreaInnerTank = 0. # [m2] 
        tankMassOuterTank = 0. # [kg] 
        surfaceAreaOuterTank = 0. # [kg]
        ambientTemperature = 0. # [K]
        thicknessInsulation = 0. # [m]
        allowedHeatFlux = 0. # [W/m2]
    
    class WingLoadings:
        """ Class to store cruise and loiter wing loadings """
        startOfCruiseWingLoading = 0. # [N/m2]
        endOfCruiseWingLoading = 0. # [ N/m2]
        startOfLoiterWingLoading = 0. # [N/m2]
        endOfLoiterWingLoading = 0. # [N/m2]

    class CGExcursionParameters:
        """ Class to store the C.G. excursion related parameters """ 
        cgOEW = 0.25 # [-]
        aftCG = 0. # [-]                                                                 
       
    
class ConversionsAndConstants:
    """
    Unit conversions, physical constants, and general constants Class
    """

    # Unit Conversions
    lbs2kg = 0.45359237
    kgTOlbs = 2.2046226218
    m3TOft3 = 35.3147
    ft2m = 0.3048 
    km2nmi = 0.5399568
    Nm2lbft2 = 0.020885434273039 
    inch2m = 0.0254

    # Physical Constants
    g = 9.80665 # [m/s2]
    ka = 1.4 # [-]
    R = 287.15 # [J/kg/K]
    Cp_air = 1000 # [J/kg/K]
    rho0 = 1.2250 # [kg/m3]
    p0 = 101325 # [Pa]
    a0 = 340.3 # [m/s]
    T0 = 288.15 # [K]
    StefanBoltzmannConstant = 5.67 * 10**(-8)               # [W/m2 K4]

    class EngineConstants:
        """ Engine Sizing Constants """
        FPR = 1.3 # [-]
        Mfan = 0.65 # [-]
        sigma = 0.3 # [-] 
        motorLengthRatio = 1.75 # [m] - 2019_Sgueglia_Alessandro.pdf
        motorPower = 4.0 * 10 ** 6 # [W]
        specificEnergyMotor = 10 * 10 ** 3  # [W/kg] https://medium.com/@jeff_60994/wright-has-begun-testing-our-2-mw-aviation-grade-motor-for-transport-category-zero-emissions-79cb01c2cfc6
        specificVolumeInverter = 20 * 10 ** 6  # [kW/m3] - https://www.weflywright.com/technology#inverters
        specificEnergyInverter = 30 * 10 ** 3  # [W/kg] https://www.electrive.com/2021/05/10/wright-electric-presents-inverter-system-for-electric-aircraft/
        additionalPower = 500 * 10 ** 3 # [W] https://nap.nationalacademies.org/read/23490/chapter/7#62
        pExitCompressor = 100000  # [N/m2] = 1 bar
        ratioLC = 0.17*(1-0.23) # [-] Thirkell_A.pdf

        beta = 0.35 # [-] - Location at which diameter is largest https://brightspace.tudelft.nl/d2l/le/content/213451/viewContent/1472042/View
        phi = 0.5 # [-]
        compositeFan = 0.2 # [-] - Fraction of weight that a composite fan has compared to a normal one
        WAw = 2.69 # [kg/m2] - Weight per unit of area of the duct lining
        rhoDuct = 2770 # [kg/m3] - Density of the aluminium used in the fan duct
        tDuct = 0.0025 # [m] - Duct thickness

        # #--- Aerodynamic Efficiencies
        fanEfficiency = 0.9535  # Fan efficiency taken from: An Examination of the Effect of Boundary Layer Ingestionon Turboelectric Distributed Propulsion SystemsJames L. Felder1, Hyun Dae Kim2, andGerald V. Brown3NASA Glenn Research Center,Cleveland,OH,44135, USA
        fanDistortion = 0.01  # Distortion taken from: An Examination of the Effect of Boundary Layer Ingestionon Turboelectric Distributed Propulsion SystemsJames L. Felder1, Hyun Dae Kim2, andGerald V. Brown3NASA Glenn Research Center,Cleveland,OH,44135, USA
        fanIsentropicEfficiency = 0.978  # https://journals-sagepub-com.tudelft.idm.oclc.org/doi/pdf/10.1177/0954410013496750

        nozzleEfficiency = 0.97 # https://link.springer.com/content/pdf/10.1007%2F978-3-030-79945-8_7.pdf

        pressureLosses = 0.998  # https://arc.aiaa.org/doi/pdfplus/10.2514/6.2012-3700

        inletEfficiency = 0.97 # https://link.springer.com/content/pdf/10.1007%2F978-3-030-79945-8_7.pdf

        # #--- Component Efficiencies
        motorEfficiency = 0.96 # [-] electrive.com/2021/05/10/wright-electric-presents-inverter-system-for-electric-aircraft/
        inverterEfficiency = 0.995 # [-] https://www.electrive.com/2021/05/10/wright-electric-presents-inverter-system-for-electric-aircraft/
        cableEfficiency = 0.996 # [-] welstead_2017
        compressorEfficiency = 0.75  # [-] Thirkell_A.pdf

        # #--- Fuel Cells
        fuelCellEnergyDensity = 2976 # [W/kg] file:///Users/stefanrooze/Downloads/no.ntnu_inspera_79771761_56970351%20(1).pdf

        # #--- Hydrogen
        specificEnergyLH = 120 * 10 ** 6 # [kJ/kg]
        fuelCellEfficiency = 0.57 # [-] pdf stationary_kpi_report_-_18052021_-_public_version_with_identifiers
        
        # #--- Weight Calculation Parameters
        climbAppAlt = averageDensity(DesignParameters.cruiseAltitude)                # [m]
        atmos = Atmosphere(climbAppAlt)
        approachSpeedOfSound = atmos.speed_of_sound                            # [m/s]
        approachMach = DesignParameters.approachSpeed / approachSpeedOfSound                                    # [-]

        atmos = Atmosphere(DesignParameters.loiterAltitude)
        loiterSpeedOfSound = atmos.speed_of_sound                         # [m/s]
        loiterMach = DesignParameters.loiterSpeed / loiterSpeedOfSound                            # [-]
        loiterDensity = atmos.density                              # [kg/m3]

        vpa = np.arcsin(DesignParameters.ClassIWEParameters.ROC /                         # [m/s]
                    (DesignParameters.cruiseSpeed))
        
        climbMach = 0.518
    
    class ClassIWEConstants:
        """ Constants for the class I Weight Estimation """
        maxLandingWeightRatio = (1 - 0.00004 * DesignParameters.designRange * 0.5399568 / 1000)
        a = 0.51396471
        b = 22121.455045

    class FuselagePlanformConstants:
        """ Fuselage Planform Constants """
        fuselageArea = 211.304 # [m2]
        fuselageWidth = 8.568                               # [m]
        rearSparXC = 0.7                                        # [x/c]
        cabinArea = fuselageArea * rearSparXC # [m2]
        XLP = 27.6 # [m]
        XLW = 21.724 # [m]
        fuselageTaper = XLW / XLP # [-]
        distanceLEFuselage = 5.685 # [m]
        fuselageHeight = 4.2 # [m]
    
    class WingPlanformConstants:
        """ Outboard Wing Planform Constants """
        b = 36. # [m]
        nk = 0.5 # [-]
        sweepInboardC4 = 51. # [deg]
        sweepOutboardC4 = 44. # [deg]
        taperInboard = 0.638
        taperOutboard = 0.426
        C1 = 0. # [-] Constant used to determine if the high AR method should be used to determine the maximum lift coefficient
        C2 = 0. # [-]

    class AirfoilParams:
        """ Airfoil Parameters """
        tcFuselage = 0.164 # [-]
        xcMaxFuselage = 0.5196 # [-] - Location of maximum thickness
        tcWing = 0.1236 # [-]
        xcMaxWing = 0.353 # [-] - Location of maximum thickness
        n = 0.95 # [-] - Airfoil efficiency factor
        DCH = 0. # [-] - Delta y is equal to 1.487 
        DaH = 9 # [deg] - Vortex lift becomes dominant
        Cl_max = 1.490 # [-] - Corresponds to max coefficient of the Eppler 325 airfoil at take-off conditions, as this is the section that stalls first
        a_0L = 0.36 # [deg]
        Clalpha = 2 * np.pi # [1/rad] - From thin airfoil theory
        Cd0 = 0.0038 # [-] - From XFLR5
    
    class ControlSurfaceConstants:
        """ Control Surface Constants """
        outboardLimit = 0.98 # [-] - Fraction of Span 
        inboardLimit = 0.5 # [-] - Inboard Fraction of Span
        tau = 0.525 # [-] - Determined from graph to calculate Clda, corresponding to a ratio of 0.3
        dAlphaUp = np.radians(35) # [rad]
        dAlpha = 0.5 * (dAlphaUp + dAlphaUp * 0.75) # [rad] - Using Differential Ailerons
        chordRatio = 0.7

    class EmpennageConstants:
        """ Empennage Constants """
        tcVerticalTail = 0.1 # [-]
        xcMaxVtail = 0.32 # [-] - Location of maximum thickness                                    # [deg] - HTAIL NOT IMPLEMENTED
        NVERT = 2                                               # [-] - Used in class II VTail weight estimation
        maxRudderDeflection = np.radians(25) # [rad]
        flapEfficiency = 4.4 # [1/rad]
        cldelta_cldeltatheory = 0.6 # [-]
        Kprime = 0.615 # [-] - Correction for nonlinear effects at bigger flap angles
        taper = 0.7
    
    class AerodynamicPerformanceConstants:
        """ Constants used to evaluate the aerodynamic performnace """
        surfaceFactor = 0.052 * 10 ** (-5) # [m] - Assume roughness corresponding to smooth molded composite
        turbulenceFraction = 0.70 # Assume 30% laminar flow
        intFacVtail = 1.01 
        intFacNacelle = 1.3 
        intFacPylon = 1.05
        kaFuselage = 0.87
        kaWing = 0.935

        McritFuselage = 0.8751
        McritWing = 0.8398
        excDrag = 0.02 #percentage of total CD0

    class UndercarriageConstants:
        """ Constants used in the sizing of the undercarriage """
        noseWheels = 2                                                 # [-]
        noseWheelStruts = 1                                           # [-]
        noseWheelStrutLength = 2.713                                       # [m]
        mainWheelStrutLength = 3.2
        wheelLoading = 42 # [tonnes / m2]  
        ratioWidthDiameter = 0.4 # [-] - Ratio between width and diameter of wheel 

    class HydrogenTankConstants:
        """ Constants used to design the hydrogen tank """
        temperatureGH2 = -240 + 273.15                          # [K]
        temperatureLH2 = -250 + 273.15                          # [K]
        minOperatingAltitude = -400.                                        # [m]
        maxOperatingAltitude = 12000.                                       # [m]
        pressureLH2 = 30 * 10 ** 5                                # [Pa]
        pressureVacuum = 1.33 * 10 ** 2                              # [Pa]
        boilOff = 0.115                                          # [-]
        densityLH2 = 71.21                                      # [kg/m3]
        specificHeatHydrogen = 13.                              # [kJ/kg/K] - Assumed from https://h2tools.org/hyarc/hydrogen-data/hydrogen-specific-heat-different-temperatures-and-pressures
        excessVolume = 0.1                                      # [-]
        safetyFactorThicknessYield = 1.15                       # [-]
        safetyFactorThicknessUltimate = 1.3                     # [-]

        #--- Material variables: Al 2024 T81 at 23K
        yieldStressMaterialInner = 538 * 10**6                  # [Pa]
        ultimateStressMaterialInner = 586 * 10**6               # [Pa]
        densityMaterialInner = 2780.                            # [kg/m3] https://www.matweb.com/search/datasheet.aspx?matguid=6441f805a3bb42758ab5b15752343138&n=1
        thermalConductivityInner = 151.                         # [W/mK] https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA2024T81
        emissivityWallMaterial = 1.                             # [-]

        #--- Material variables: LiAL 2090 at room temp
        yieldStressMaterialOuter = 520 * 10**6                  # [Pa]
        ultimateStressMaterialOuter = 550 * 10**6               # [Pa]
        densityMaterialOuter = 2590.                            # [kg/m3]
        thermalConductivityOuter = 88.                          # [W/mK] https://www.matweb.com/search/DataSheet.aspx?MatGUID=e6cc17f421d84c448f184ac392c933b6

        #--- Insulation Material variables: polyurethane foam
        insulationDensityAerogel = 100                          # [kg/m3]
        thermalConductivityInsulationAerogel = 10**(-5)         # [W/mK] (Table IV)
        emissivityInsulation = 1.

        requiredLength = 6.                                     # [m]
        numberOfTanks = 1                                       # [-]
        minimumThickness = 0.003                        # assumed 3mm minimum thickness for manufacturing
        vacuumThickness = 0.005 

    class CGExcursionConstants:
        """ Class to store the C.G. excursion related constants """
        xLEMAC = 19.                                            # [m]
        x_cg_Fuel = 21.8323 / 27.6                                # [-] - Fraction of fuselage length
        xi_wing = 0.25                                          # [-] - Fraction of MAC
        xi_sys_eq = 0.4
        xi_operating_items = 0.4
        x_cg_payload = 0.45  
        xoew_aircraft_wrt_mac = 0.2
        xi_fuel_cells = 10.11 / 27.6
