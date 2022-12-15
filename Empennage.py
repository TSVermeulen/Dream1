""" 

This file contains the function used to size the empennage. 
In the current implementation of the blended wing body, there is no horizontal tail, so only a vertical tail is designed.

Based on the lecture notes Aircraft Design from the OER - HOOU.
Accessible on: https://www.fzt.haw-hamburg.de/pers/Scholz/HOOU/AircraftDesign_11_EmpennageSizing.pdf

@author: Thomas Stephan Vermeulen

"""

import numpy as np
from math import atan

def verticalTailDesignControl(Params, ConvAndConst):
    """
    Function to design the vertical tail of the blended wing body according to the control requirement.

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    areaTail, total tail surface area according to the control requirement [m2]
    """

    # Determine the distance between the failed engines and the plane of symmetry
    failWidth = (Params.PropulsionSizingParameters.Dn + 0.05) * Params.PropulsionSizingParameters.num_engines / 4 / 2 # Assumes 1/4 of all the engines dies on the same side. This is the width of the failed engines
    yE = Params.PlanformParameters.propulsionWidth / 2 - 0.5 * failWidth #Distance between the failed engine and plane of symmetry

    # Moment caused by the still active engines
    NE = Params.totalThrustRequired / Params.PropulsionSizingParameters.num_engines * yE * 4
    NV = NE * 1.25 # Accounts for windmilling

    # Minimum Control Speed
    Vmc = Params.PlanformParameters.stallSpeed * 1.2

    # Sweep Correction Factor
    Params.EmpennageParameters.sweepC4 = Params.PlanformParameters.averagedSweepC4 + 5
    Klambda = (1 - 0.08 * np.cos(np.radians(Params.EmpennageParameters.sweepC4)) ** 2) * np.cos(np.radians(Params.EmpennageParameters.sweepC4)) ** (3/4)

    # Calculate tail required area according to control requirement
    areaTail = NV / (0.5 * ConvAndConst.rho0 * Vmc ** 2 * ConvAndConst.EmpennageConstants.maxRudderDeflection * ConvAndConst.EmpennageConstants.cldelta_cldeltatheory * ConvAndConst.EmpennageConstants.flapEfficiency * ConvAndConst.EmpennageConstants.Kprime * Klambda * Params.EmpennageParameters.Lvt)

    return areaTail

def verticalTailDesign(Params, ConvAndConst):
    """
    Function to size the vertical tail,, assumes two vertical tails each mounted on a wingtip.

    Inputs:
    -----
    Params, class of design parameters [-]
    ConvAndConst, class of conversion factors, physical & general constants [-]

    Outputs:
    -----
    areaTail, total area of the vertical tails combined [m2]
    verticalTailsweepLE, leading edge sweep of the vertical tail [deg]
    verticalTailSpan, span of the vertical tail [m]
    rootChordVerticalTail, root chord of the vertical tail [m]
    tipChordVerticalTail, tip chord of the vertical tail [m]
    verticalTailMAC, mean aerodynamic chord of the vertical tail [m]
    verticalTailSpanwiseLocMAC, spanwise location of the mean aerodynamic chord [m]
    verticalTailHorizontalLocMAC, distance of leading edge of the mean aerodynamic chord from the leading edge of the root of the vertical tail [m]
    """

    # Vertical Tail Area
    areaTail = verticalTailDesignControl(Params, ConvAndConst)

    # Vertical Tail Dimensioning
    rootChordVerticalTail = Params.WingPlanformParameters.tipChord
    tipChordVerticalTail = rootChordVerticalTail * ConvAndConst.EmpennageConstants.taper
    verticalTailSpan = areaTail / (rootChordVerticalTail + tipChordVerticalTail)
    verticalTailMAC = (2 / 3) * rootChordVerticalTail * ((1 + ConvAndConst.EmpennageConstants.taper + ConvAndConst.EmpennageConstants.taper ** 2) / (1 + ConvAndConst.EmpennageConstants.taper))
    verticalTailSpanwiseLocMAC = (verticalTailSpan / 6) * ((1 + 2 * ConvAndConst.EmpennageConstants.taper)/ (1 + ConvAndConst.EmpennageConstants.taper))
    verticalTailsweepLE = np.degrees(atan(np.tan(np.radians(Params.EmpennageParameters.sweepC4)) + rootChordVerticalTail / (2 * verticalTailSpan) * (1 - ConvAndConst.EmpennageConstants.taper)))
    verticalTailHorizontalLocMAC = verticalTailSpanwiseLocMAC* np.tan(np.radians(verticalTailsweepLE))

    return areaTail, verticalTailsweepLE, verticalTailSpan, rootChordVerticalTail, tipChordVerticalTail, verticalTailMAC, verticalTailSpanwiseLocMAC, verticalTailHorizontalLocMAC

