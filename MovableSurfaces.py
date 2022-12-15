"""

Movable surfaces design of the blended wing body
Follows the methods outlined in lecture 3 - Mobile surfaces on the wing of the 
BSc course AE2111-II at TU Delft.

The aircraft is assumed to be a class II aircraft, such that it needs to 
attain a roll performance of 45 degrees in 1.4 seconds.

@author: Thomas Vermeulen

key things missing: elevator implementation. Maybe books of DATCOM contain methods for sizing.

"""

import numpy as np
from scipy import interpolate, integrate

def chord(y, Params, ConvAndConst):
    """
    Function to return the chord at an arbitrary spanwise coordinate.

    Inputs:
    -----
    y, spanwise coordinate of interest [m]
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    c, chord at location y [m]
    """

    # Fuselage Part
    if y <= ConvAndConst.FuselagePlanformConstants.fuselageWidth / 2:
        spanwisePoints = np.array([0, ConvAndConst.FuselagePlanformConstants.fuselageWidth / 2])
        Chords = np.array([ConvAndConst.FuselagePlanformConstants.XLP, ConvAndConst.FuselagePlanformConstants.XLW])
        chordFunction = interpolate.interp1d(spanwisePoints, Chords, kind='linear')
        c = chordFunction(y)
    
    # Inboard Part of Wing
    elif ConvAndConst.FuselagePlanformConstants.fuselageWidth / 2 < y <= Params.WingPlanformParameters.kinkLocation:
        spanwisePoints = np.array([ConvAndConst.FuselagePlanformConstants.fuselageWidth / 2, Params.WingPlanformParameters.kinkLocation])
        Chords = np.array([Params.WingPlanformParameters.rootChord[0], Params.WingPlanformParameters.kinkChord[0]])
        chordFunction = interpolate.interp1d(spanwisePoints, Chords, kind='linear')
        c = chordFunction(y)
    
    # Outboard Part of Wing
    elif Params.WingPlanformParameters.kinkLocation < y <= ConvAndConst.WingPlanformConstants.b / 2:
        spanwisePoints = np.array([Params.WingPlanformParameters.kinkLocation, ConvAndConst.WingPlanformConstants.b / 2])
        Chords = np.array([Params.WingPlanformParameters.kinkChord[0], Params.WingPlanformParameters.tipChord[0]])
        chordFunction = interpolate.interp1d(spanwisePoints, Chords, kind='linear')
        c = chordFunction(y)
    
    return c

def aileronControlDerivative(Params, ConvAndConst):
    """
    Function to calculate the aileron control derivative.

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    Clda, aileron control derivative [-]
    """

    # List of spanwise datapoints
    y = np.arange(ConvAndConst.ControlSurfaceConstants.inboardLimit * ConvAndConst.WingPlanformConstants.b / 2, ConvAndConst.ControlSurfaceConstants.outboardLimit * ConvAndConst.WingPlanformConstants.b / 2 + 0.0001, (ConvAndConst.ControlSurfaceConstants.outboardLimit - ConvAndConst.ControlSurfaceConstants.inboardLimit) * ConvAndConst.WingPlanformConstants.b / 2 / 100)

    # Function data to integrate & integrated result
    func = np.zeros(len(y))
    for i in range(len(y)):
        func[i] = chord(y[i], Params, ConvAndConst) * y[i]
    interpolatedFunction = interpolate.interp1d(y, func, kind='cubic')
    integralResult, error = integrate.quad(interpolatedFunction, y[0], y[-1])
    # Calculate Aileron Control Derivative
    Clda = (2 * ConvAndConst.AirfoilParams.Clalpha * ConvAndConst.ControlSurfaceConstants.tau) / (Params.Sref * ConvAndConst.WingPlanformConstants.b) * integralResult

    return Clda

def rollDampingDerivative(Params, ConvAndConst):
    """
    Function to calculate the roll control derivative

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    Clp, roll damping coefficient [-]
    """

    # List of spanwise datapoints
    y = np.arange(0, ConvAndConst.WingPlanformConstants.b / 2 + 0.0001, ConvAndConst.WingPlanformConstants.b / 2 / 100)

    # Function data to integrate & integrated result
    func = np.zeros(len(y))
    for i in range(len(y)):
        func[i] = chord(y[i], Params, ConvAndConst) * y[i] * y[i]
    interpolatedFunction = interpolate.interp1d(y, func, kind='cubic')
    integralResult, error = integrate.quad(interpolatedFunction, y[0], y[-1])

    # Calculate Roll Damping Coefficient
    Clp = - (4 * (ConvAndConst.AirfoilParams.Clalpha + ConvAndConst.AirfoilParams.Cd0)) / (Params.Sref * ConvAndConst.WingPlanformConstants.b ** 2) * integralResult

    return Clp

def steadyRollRate(Params, ConvAndConst):
    """
    Function to calculate the steady roll-rate of the aircraft and required roll time to roll 45 degrees

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    P, the steady roll rate of the aircraft [rad/s]  
    rollTime, time needed for the aircraft to roll 45 degrees [s]
    """

    # Calculate steady roll rate
    P = - Params.ControlSurfaceParameters.Clda / Params.ControlSurfaceParameters.Clp * ConvAndConst.ControlSurfaceConstants.dAlpha * (2 * Params.PlanformParameters.stallSpeed / ConvAndConst.WingPlanformConstants.b) 

    # Calculate roll time needed
    rollTime = np.radians(45) / P

    return P, rollTime

def aileronSizing(Params, ConvAndConst):
    """
    Function to size the Ailerons.

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    aileronArea, surface area of the ailerons [m2]
    """

    # Calculate aileron control derivative and roll damping derivative
    Params.ControlSurfaceParameters.Clda = aileronControlDerivative(Params, ConvAndConst)
    Params.ControlSurfaceParameters.Clp =  rollDampingDerivative(Params, ConvAndConst)

    # Calculate steady roll rate of aircraft
    Params.ControlSurfaceParameters.P, Params.ControlSurfaceParameters.rollTime = steadyRollRate(Params, ConvAndConst)

    # Calculate aileron surface area
    if Params.ControlSurfaceParameters.rollTime <= 1.4:
        # Roll time requirement is met
        inboardSpan = ConvAndConst.ControlSurfaceConstants.inboardLimit * ConvAndConst.WingPlanformConstants.b
        outboardSpan = ConvAndConst.ControlSurfaceConstants.outboardLimit * ConvAndConst.WingPlanformConstants.b
        aileronSpan = outboardSpan - inboardSpan
        inboardChord = chord(inboardSpan / 2, Params, ConvAndConst)
        outboardChord = chord(outboardSpan / 2, Params, ConvAndConst)
        aileronArea = aileronSpan * ConvAndConst.ControlSurfaceConstants.chordRatio * (inboardChord - outboardChord) / 2
    else:
        # Roll time requirement is not met, however it is possible the iteration returns to feasible area in subsequent iterations!
        aileronArea = 20
        input("ROLL TIME REQUIREMENT NOT MET! To continue the iteration, press enter. Be wary, results may not be feasible!")

    return aileronArea
