"""

Welcome one and all to the central design iteration program. 
This file calls upon the different functions made to size/design the subsystems 
putting everything into a loop until a converged design is achieved. 
The resulting design can then be checked against the requirements!

@author: Thomas

"""

import numpy as np

#Loading classes
from DesignParameters import ConversionsAndConstants, DesignParameters

#Loading all the different functions
from ClassI_WE import classIWeight
from ClassII_BWB import classIIWeightEstimation
from PropulsionIterationV3 import PropulsionIteration
from Empennage import verticalTailDesign
from WingAerodynamics import PlanformParameterization, OutboardWingSizing, AerodynamicAnalysis
from Undercarriage import UnderCarriageSizing
from MovableSurfaces import aileronSizing
from AerodynamicPerformance import DragPolar, calculateLiftCoefficients
from CGExcursion import CGExcursion

""" General Setup - Iteration Parameters"""
Iterate = True # Iteration stop/go parameter
nIter = 1 # Iteration number counter
convPoint = False
wingLoadingArr = np.array([1800, 2000, 2100, 2150, 2150]) # Wing Loadings for each iteration until the design point is converged
thrustLoadingArr = np.array([0.26, 0.273, 0.254, 0.249, 0.249]) # Thrust Loadings for each iteration until the design point is converged        

""" Main program """
while Iterate:
    if nIter == 1:
        MTOW_diff = 0
    else:
        WTO_classII = DesignParameters.ClassIWEParameters.WOE + DesignParameters.payloadWeight + DesignParameters.ClassIWEParameters.WF
        MTOW_diff = (WTO_classII - DesignParameters.ClassIWEParameters.WTO) / DesignParameters.ClassIWEParameters.WTO * 100.0
        if abs(MTOW_diff) < 0.5:
            print("Iteration Completed")
            break

    print("----------")
    print("Iteration Status")
    print("Iteration Number:", nIter)
    print("Difference with Previous Iteration:", MTOW_diff, "[%]" )
    print("----------")
    
    #---------------------------------
    # Class I Weight Estimation
    #---------------------------------

    DesignParameters.ClassIWEParameters.WTO, DesignParameters.ClassIWEParameters.WOE, DesignParameters.ClassIWEParameters.WF, DesignParameters.ClassIWEParameters.h2TO, DesignParameters.ClassIWEParameters.h2endCruise, DesignParameters.ClassIWEParameters.h2endApp = classIWeight(DesignParameters, ConversionsAndConstants, nIter)

    print("Current design state")
    print("WTO", DesignParameters.ClassIWEParameters.WTO, "[N]")
    print("WOE", DesignParameters.ClassIWEParameters.WOE, "[N]")
    print("WF", DesignParameters.ClassIWEParameters.WF, "[N]")
    print("-----")
    
    #---------------------------------
    # Design point
    #---------------------------------

    if nIter < 5:
        DesignParameters.wingLoading = wingLoadingArr[nIter - 1]
        DesignParameters.thrustLoading = thrustLoadingArr[nIter - 1]
    # if convPoint != True:
    #     DesignParameters.wingLoading= float(input("enter wing loading"))
    #     DesignParameters.thrustLoading = float(input("enter thrustloading"))
    #     convPoint = input("enter if design point is converged")
    else:
        DesignParameters.wingLoading = wingLoadingArr[-1]
        DesignParameters.thrustLoading = thrustLoadingArr[-1]
    
    DesignParameters.Sref = DesignParameters.ClassIWEParameters.WTO / DesignParameters.wingLoading
    DesignParameters.totalThrustRequired = DesignParameters.thrustLoading * DesignParameters.ClassIWEParameters.WTO

    #---------------------------------
    # Functions that only need to be run during iteration 1
    #---------------------------------

    if nIter == 1:
        # Fuselage planform remains constant, so only calculate during first run
        DesignParameters.FuselagePlanformParameters.sweepLE, DesignParameters.FuselagePlanformParameters.sweepC4, DesignParameters.FuselagePlanformParameters.sweepC2, DesignParameters.FuselagePlanformParameters.fuselageMAC = PlanformParameterization(ConversionsAndConstants)
        # Wing loadings need to be defined for later use. 
        calculateLiftCoefficients(DesignParameters)


    #---------------------------------
    # Propulsion Sizing
    #---------------------------------

    DesignParameters.PropulsionSizingParameters.num_engines = PropulsionIteration(DesignParameters, ConversionsAndConstants)
               
    #---------------------------------
    # Outboard Wing Planform Design
    #---------------------------------
 
    DesignParameters.WingPlanformParameters.wingAreaExp = DesignParameters.Sref - ConversionsAndConstants.FuselagePlanformConstants.fuselageArea
    DesignParameters.PlanformParameters.geometricAR = ConversionsAndConstants.WingPlanformConstants.b ** 2 / DesignParameters.Sref
    
    DesignParameters.WingPlanformParameters.rootChord, DesignParameters.WingPlanformParameters.kinkChord, DesignParameters.WingPlanformParameters.tipChord, DesignParameters.WingPlanformParameters.kinkLocation, DesignParameters.WingPlanformParameters.sweepC4, DesignParameters.WingPlanformParameters.sweepC2, DesignParameters.WingPlanformParameters.sweepLE, DesignParameters.WingPlanformParameters.wingMAC, DesignParameters.WingPlanformParameters.distanceLEWing, DesignParameters.WingPlanformParameters.yMAC, DesignParameters.WingPlanformParameters.wingTaper, DesignParameters.WingPlanformParameters.aircraftTaper = OutboardWingSizing(DesignParameters, ConversionsAndConstants)
    DesignParameters.PlanformParameters.liftCurveSlope, DesignParameters.PlanformParameters.maxLiftCoefficient, DesignParameters.PlanformParameters.stallAngleOfAttack, DesignParameters.PlanformParameters.oswaldFactor, DesignParameters.PlanformParameters.stallSpeed = AerodynamicAnalysis(0.25, DesignParameters, ConversionsAndConstants)
        
    DesignParameters.ClassIIWEParameters.TCA = (ConversionsAndConstants.AirfoilParams.tcFuselage * ConversionsAndConstants.FuselagePlanformConstants.fuselageArea * np.cos(np.radians(DesignParameters.FuselagePlanformParameters.sweepC4)) + ConversionsAndConstants.AirfoilParams.tcWing * DesignParameters.WingPlanformParameters.wingAreaExp * np.cos(np.radians(DesignParameters.WingPlanformParameters.sweepC4))) / DesignParameters.Sref
    
    #---------------------------------
    # Moving Surfaces Design
    #---------------------------------
    
    DesignParameters.ControlSurfaceParameters.aileronArea = aileronSizing(DesignParameters, ConversionsAndConstants)

    #---------------------------------
    # Empennage Design
    #---------------------------------

    DesignParameters.EmpennageParameters.areaTail, DesignParameters.EmpennageParameters.sweepLE, DesignParameters.EmpennageParameters.verticalTailSpan, DesignParameters.EmpennageParameters.rootChordVerticalTail, DesignParameters.EmpennageParameters.tipChordVerticalTail, DesignParameters.EmpennageParameters.verticalTailMAC, DesignParameters.EmpennageParameters.verticalTailSpanwiseLocMAC, DesignParameters.EmpennageParameters.verticalTailHorizontalLocMAC = verticalTailDesign(DesignParameters, ConversionsAndConstants)    
    
    #---------------------------------
    # Undercarriage Sizing
    #---------------------------------

    DesignParameters.UndercarriageParameters.noseWheelDiameter, DesignParameters.UndercarriageParameters.noseWheelWidth, DesignParameters.UndercarriageParameters.mainWheels, DesignParameters.UndercarriageParameters.mainWheelDiameter, DesignParameters.UndercarriageParameters.mainWheelWidth = UnderCarriageSizing(DesignParameters, ConversionsAndConstants)

    #---------------------------------
    # Aerodynamic Performance
    #---------------------------------

    DesignParameters.ClassIWEParameters.cruiseLD, DesignParameters.ClassIWEParameters.loiterLD = DragPolar(DesignParameters, ConversionsAndConstants)

    #---------------------------------
    # Class II Weight Estimation 
    #---------------------------------

    classIIWeightEstimation(DesignParameters, ConversionsAndConstants)

    #---------------------------------
    #C.G. Excursion
    #---------------------------------
    
    CGExcursion(DesignParameters, ConversionsAndConstants)

    #---------------------------------
    #Converged Iteration Parameters
    #---------------------------------
    
    nIter += 1
    print("DesignPoint stuff")
    print("CLmax", DesignParameters.PlanformParameters.maxLiftCoefficient)
    print("EffectiveAR", DesignParameters.PlanformParameters.effectiveAR)
    print("Oswald", DesignParameters.PlanformParameters.oswaldFactor)
    print("thrust setting", DesignParameters.PropulsionSizingParameters.TsetCr)
    print("CD0 cruise", DesignParameters.AerodynamicPerformanceParameters.cleanCruiseCD0)

#SWEEP ANGLE CHECK



