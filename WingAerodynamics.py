"""

Implementation of wing Aerodynamics
Mainly based on the DATCOM method, as taught during the ADSEE-II course

@author: Thomas

"""

import numpy as np
from scipy import interpolate

def PlanformParameterization(ConvAndConst):
    """
    Function to calculate the needed sweep angles and Mean Aerodynamic Chord of the fuselage 
    for the main iteration.

    Inputs:
    -----
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    sweepLE, leading edge sweep [deg]
    sweepc4, quarter chord sweep [deg]
    sweepc2, half chord sweep [deg]
    MAC, mean aerodynamic chord [m]
    """

    # Calculate halfspan of fuselage
    y = ConvAndConst.FuselagePlanformConstants.fuselageWidth / 2

    # Calculate sweep angles of fuselage
    sweepLE = np.degrees(np.arctan2(ConvAndConst.FuselagePlanformConstants.distanceLEFuselage, y))
    sweepc4 = np.degrees(np.arctan(np.tan(np.radians(sweepLE)) - 0.25 * 2 * ConvAndConst.FuselagePlanformConstants.XLP / ConvAndConst.FuselagePlanformConstants.fuselageWidth * (1 - ConvAndConst.FuselagePlanformConstants.fuselageTaper)))
    sweepc2 = np.degrees(np.arctan(np.tan(np.radians(sweepLE)) - 0.5 * 2 * ConvAndConst.FuselagePlanformConstants.XLP / ConvAndConst.FuselagePlanformConstants.fuselageWidth * (1 - ConvAndConst.FuselagePlanformConstants.fuselageTaper)))
    
    # Calculate Mean Aerodynamic Chord of Fuselage
    MAC = (2/3) * ConvAndConst.FuselagePlanformConstants.XLP * ((1 + ConvAndConst.FuselagePlanformConstants.fuselageTaper + ConvAndConst.FuselagePlanformConstants.fuselageTaper ** 2) / (1 + ConvAndConst.FuselagePlanformConstants.fuselageTaper))
        
    return sweepLE, sweepc4, sweepc2, MAC

def OutboardWingSizing(Params, ConvAndConst):
    """
    Function to size the outboard wing planform
    Sizes the planform as a double tapered wing

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    Cr, root chord [m]
    Ck, kink chord [m]
    Ct, tip chord [m]
    yk, spanwise location of the kink, measured from the aircraft centerline [m]
    sweepWingC4, area averaged quarter chord sweep of the outboard wing [deg]
    sweepWingC2, area averaged half chord sweep of the outboard wing [deg]
    sweepWingLE, area averaged leading edge chord sweep of the outboard wing [deg]
    MAC_wing, mean aerodynamic chord of the wing [m]
    LEdistWing, distance between the leading edge of the wing root and the wing tip [m]
    yMAC, spanwise location of the mean aerodynamic chord [m]
    wingTaper, taper ratio of the outboard wing [-]
    aircraftTaper, taper ratio of the entire aircraft [-]
    """    

    # Inboard and Outboard Span
    bi = (ConvAndConst.WingPlanformConstants.b - ConvAndConst.FuselagePlanformConstants.fuselageWidth) * ConvAndConst.WingPlanformConstants.nk
    bo = (ConvAndConst.WingPlanformConstants.b - ConvAndConst.FuselagePlanformConstants.fuselageWidth) * (1 - ConvAndConst.WingPlanformConstants.nk)

    # Root Chord of the Wing
    Cr = Params.WingPlanformParameters.wingAreaExp / (bi / 2 * (1 + ConvAndConst.WingPlanformConstants.taperInboard) + bo / 2 * ConvAndConst.WingPlanformConstants.taperInboard * (1 + ConvAndConst.WingPlanformConstants.taperOutboard)) #[m]

    # Kink Chord
    Ck = Cr * ConvAndConst.WingPlanformConstants.taperInboard # [m]
    
    # Tip Chord
    Ct = Ck * ConvAndConst.WingPlanformConstants.taperOutboard # [m]

    # Spanwise distance of kink, measured from centerline
    yk = bi / 2  + ConvAndConst.FuselagePlanformConstants.fuselageWidth / 2 # [m]

    # Sweep angles of the leading edge and c/2 of the inboard part of the outboard wing and the outboard part
    sweepInboardLE = np.degrees(np.arctan(np.tan(np.radians(ConvAndConst.WingPlanformConstants.sweepInboardC4)) + Cr / (2 * bi) * (1 - ConvAndConst.WingPlanformConstants.taperInboard)))
    sweepOutboardLE = np.degrees(np.arctan(np.tan(np.radians(ConvAndConst.WingPlanformConstants.sweepOutboardC4)) + Ck / (2 * bo) * (1 - ConvAndConst.WingPlanformConstants.taperOutboard)))
    sweepInboardC2 = np.degrees(np.arctan(np.tan(np.radians(sweepInboardLE)) - Cr / (bi) * (1 - ConvAndConst.WingPlanformConstants.taperInboard)))
    sweepOutboardC2 = np.degrees(np.arctan(np.tan(np.radians(sweepOutboardLE)) - Ck / (bo) * (1 - ConvAndConst.WingPlanformConstants.taperOutboard)))
    
    # Inboard area and outboard area
    Sin = (bi / 2) * Cr * (1 + ConvAndConst.WingPlanformConstants.taperInboard) # [m2]
    Sout = (bo / 2) * Ck * (1 + ConvAndConst.WingPlanformConstants.taperOutboard) # [m2]

    # Mean Aerodynamic Chords of both parts
    MAC_in = 2 / 3 * Cr * ((1 + ConvAndConst.WingPlanformConstants.taperInboard + ConvAndConst.WingPlanformConstants.taperInboard ** 2) / (1 + ConvAndConst.WingPlanformConstants.taperInboard))
    MAC_out = 2 / 3 * Ck * ((1 + ConvAndConst.WingPlanformConstants.taperOutboard + ConvAndConst.WingPlanformConstants.taperOutboard ** 2) / (1 + ConvAndConst.WingPlanformConstants.taperOutboard))

    # Mean Aerodynamic chord of the total outboard wing
    MAC_wing = (Sin*MAC_in + Sout*MAC_out) / Params.WingPlanformParameters.wingAreaExp # [m]

    # Distance between leading edge of the root and leading edge of the tip of the outboard wing
    LEdistWing = np.tan(np.radians(sweepInboardLE)) * bi / 2 + np.tan(np.radians(sweepOutboardLE)) * bo / 2

    # Area-averaged sweep angles of the outboard wing
    sweepWingC2 = (sweepInboardC2 * Sin + sweepOutboardC2 * Sout) / (Params.WingPlanformParameters.wingAreaExp)
    sweepWingC4 = (ConvAndConst.WingPlanformConstants.sweepInboardC4 * Sin + ConvAndConst.WingPlanformConstants.sweepOutboardC4 * Sout) / (Params.WingPlanformParameters.wingAreaExp)
    sweepWingLE = (sweepInboardLE * Sin + sweepOutboardLE * Sout) / (Params.WingPlanformParameters.wingAreaExp)

    # Y_mac calculations
    yMacInboard = (bi / 6) * ((1 + 2 * ConvAndConst.WingPlanformConstants.taperInboard) / (1 + ConvAndConst.WingPlanformConstants.taperInboard))
    yMacOutboard = (bo / 6) * ((1 + 2 * ConvAndConst.WingPlanformConstants.taperOutboard) / (1 + ConvAndConst.WingPlanformConstants.taperOutboard))
    yMAC = (yMacInboard * Sin + (0.5 * bi + yMacOutboard) * Sout) / Params.WingPlanformParameters.wingAreaExp

    # Planform Parameters
    wingTaper = Ct / Cr # [-]
    aircraftTaper = Ct / ConvAndConst.FuselagePlanformConstants.XLP # [-]

    return Cr, Ck, Ct, yk, sweepWingC4, sweepWingC2, sweepWingLE, MAC_wing, LEdistWing, yMAC, wingTaper, aircraftTaper

def AerodynamicAnalysis(M, Params, ConvAndConst):
    """ 
    Function to perform the required aerodynamic analyses of the blended wing body aircraft.
    Based on the DATCOM 1978 method and the Lecture "Lift & Drag Estimation" of the BSc course AE2111-II at TU Delft.

    Inputs:
    -----
    M, freestream Mach number [-]
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-

    Outputs:
    -----
    CL_a, aircraft lift curve slope [1/deg] 
    CL_max, maximum aircraft lift coefficient [-]
    a_stall, aircraft stall angle of attack [-]
    e, Oswald efficiency factor [-]
    """

    # Mean Aerodynamic Sweep Angles
    Params.PlanformParameters.averagedSweepC2 = (Params.WingPlanformParameters.sweepC2 * Params.WingPlanformParameters.wingAreaExp + Params.FuselagePlanformParameters.sweepC2 * ConvAndConst.FuselagePlanformConstants.fuselageArea) / (Params.Sref)
    Params.PlanformParameters.averagedSweepLE = (Params.WingPlanformParameters.sweepLE * Params.WingPlanformParameters.wingAreaExp + Params.FuselagePlanformParameters.sweepLE * ConvAndConst.FuselagePlanformConstants.fuselageArea) / (Params.Sref)
    Params.PlanformParameters.averagedSweepC4 = (Params.WingPlanformParameters.sweepC4 * Params.WingPlanformParameters.wingAreaExp + Params.FuselagePlanformParameters.sweepC4 * ConvAndConst.FuselagePlanformConstants.fuselageArea) / (Params.Sref)

    # Determining Overall Aircraft Lift Curve Slope
    beta = np.sqrt(1 - M ** 2) # [-] - Compressibility Correction Factor
    CL_a = (2 * np.pi * Params.PlanformParameters.effectiveAR)/(2 + np.sqrt(4 + (Params.PlanformParameters.effectiveAR * beta / ConvAndConst.AirfoilParams.n) * (1 + (np.tan(np.radians(Params.PlanformParameters.averagedSweepC2)) ** 2) / beta ** 2))) # [1/rad] Lift curve slope
    
    # Determining Overall Aircraft Maximum Lift Coefficient and Stall Angle Of Attack
    if Params.PlanformParameters.effectiveAR > (3/((ConvAndConst.WingPlanformConstants.C1 + 1) * np.cos(np.radians(Params.PlanformParameters.averagedSweepLE)))):
        # Used if the High Aspect Ratio Criteria is met  
        # The value of CL / Cl is a function of LE sweep angle, so we reconstruct the graph and interpolate
        horizontal = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60])
        dataPoints = np.array([0.9, 0.91, 0.92, 0.95, 0.97, 0.99, 1.0, 1.02, 1.08, 1.11, 1.15, 1.18, 1.25])
        interpolatedCurveCLCl = interpolate.interp1d(horizontal, dataPoints, kind="linear", fill_value="extrapolate")
        CL_Cl = interpolatedCurveCLCl(Params.PlanformParameters.averagedSweepLE)
        CL_max = ConvAndConst.AirfoilParams.Cl_max * CL_Cl + ConvAndConst.AirfoilParams.DCH 
        a_stall = CL_max / (CL_a * (np.pi / 180) ) + ConvAndConst.AirfoilParams.a_0L + ConvAndConst.AirfoilParams.DaH
    else:
        print("LOW ASPECT RATIO")
        # Used if the High Aspect Ratio Criteria is NOT met
        # For low aspect ratios, the value of C_L_max_base is a function of (c1 + 1) * A / beta * cos(sweepLE), so we make an interpolation to approximate the graph
        horizontal = np.array([1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8])
        dataPoints = np.array([1.12, 1.06, 1.0, 0.95, 0.91, 0.88, 0.85, 0.83, 0.82])
        interpolatedCurveCLmaxBase = interpolate.interp1d(horizontal, dataPoints, kind="linear", fill_value="extrapolate")
        horizontal = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        dataPoints = np.array([-0.12, -0.1, -0.08, -0.04, 0, 0.075, 0.12, 0.18, 0.23, 0.29, 0.33, 0.37, 0.36, 0.3])
        interpolatedCurveDeltaCLmax = interpolate.interp1d(horizontal, dataPoints, kind="linear", fill_value="extrapolate")

        # Calculate x Coordinate of point of interest & determine CL_max_base
        pointOfInterest1 = (ConvAndConst.WingPlanformConstants.C1 + 1) * Params.PlanformParameters.effectiveAR / beta * np.cos(np.radians(Params.PlanformParameters.averagedSweepLE))
        CL_max_base = interpolatedCurveCLmaxBase(pointOfInterest1)
        pointOfInterest2 = (ConvAndConst.WingPlanformConstants.C2 + 1) * Params.PlanformParameters.effectiveAR * np.tan(np.radians(Params.PlanformParameters.averagedSweepLE))
        deltaCL_max = interpolatedCurveDeltaCLmax(pointOfInterest2)

        CL_max = CL_max_base + deltaCL_max

        # Estimating the stall angle of attack
        horizontal = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8])
        dataPoints = np.array([35, 35, 35, 31.5, 29, 26, 24, 22])
        interpolatedCurveAlphaStallBase = interpolate.interp1d(horizontal, dataPoints, kind="cubic", fill_value="extrapolate")        
        alphaStallBase = interpolatedCurveAlphaStallBase(pointOfInterest1)
        a_stall = alphaStallBase + ConvAndConst.AirfoilParams.DaH

    # Determining Oswald Efficiency Factor
    e = 4.61 * (1 - 0.045 * Params.PlanformParameters.effectiveAR ** 0.68) * (np.cos(np.radians(Params.PlanformParameters.averagedSweepLE))) ** 0.15 - 3.1

    # Determining Sea Level Stall Speed
    stallSpeed = np.sqrt(2 * Params.ClassIWEParameters.WTO / (ConvAndConst.rho0 * Params.Sref * CL_max))

    return CL_a, CL_max, a_stall, e, stallSpeed
