"""

Data Storage file to store the outputs of the converged design.

@author: Thomas Stephan Vermeulen

"""

import pandas as pd

def dataOut(Params):
    """
    Function to store the data from the Params class to an excel sheet. 
    """
    
    # Class I WE Parameters
    classIWEParameters_frame = pd.DataFrame({'Parameter':["WTO", "WML", "WOE", "WF", "WPL"], 
                                             'Unit':["N", "N", "N", "N", "N"], 
                                             'Value':[Params.ClassIWEParameters.WTO[0], Params.ClassIWEParameters.WmaxLand[0], Params.ClassIWEParameters.WOE[0], Params.ClassIWEParameters.WF[0], Params.payloadWeight]})
    # Propulsion System Parameters
    propulsionParameters_frame = pd.DataFrame({'Parameter':["Number of Engines", "Di", "Dh", "Dfan", "Dn", "De", "ln", "TsetApp", "TsetLoiter", "TsetCr"], 
                                               'Unit':["-", "m", "m", "m", "m", "m", "m", "-", "-", "-"], 
                                               'Value':[Params.PropulsionSizingParameters.num_engines, Params.PropulsionSizingParameters.Di[0], Params.PropulsionSizingParameters.Dh[0], Params.PropulsionSizingParameters.Dfan[0], Params.PropulsionSizingParameters.Dn[0], Params.PropulsionSizingParameters.De[0], Params.PropulsionSizingParameters.ln[0], Params.PropulsionSizingParameters.TsetApp, Params.PropulsionSizingParameters.TsetLoiter[0], Params.PropulsionSizingParameters.TsetCr[0]]})
    # Fuselage Planform Parameters
    fuselagePlanform_frame = pd.DataFrame({'Parameter':["sweepLE", "sweepC4", "sweepC2", "MAC"],
                                           'Unit':["deg", "deg", "deg", "m"],
                                           'Value':[Params.FuselagePlanformParameters.sweepLE, Params.FuselagePlanformParameters.sweepC4, Params.FuselagePlanformParameters.sweepC2, Params.FuselagePlanformParameters.fuselageMAC]})
    # Wing Planform Parameters
    wingPlanform_frame = pd.DataFrame({'Parameter':["wingAreaExp", "rootChord", "kinkChord", "tipChord", "kinkLocation", "sweepLE", "sweepC4", "sweepC2", "wingMAC"],
                                       'Unit':["m2", "m", "m", "m", "m", 'deg', 'deg', 'deg', "m"],
                                       'Value':[Params.WingPlanformParameters.wingAreaExp[0], Params.WingPlanformParameters.rootChord[0], Params.WingPlanformParameters.kinkChord[0], Params.WingPlanformParameters.tipChord[0], Params.WingPlanformParameters.kinkLocation, Params.WingPlanformParameters.sweepLE[0], Params.WingPlanformParameters.sweepC4[0], Params.WingPlanformParameters.sweepC2[0], Params.WingPlanformParameters.wingMAC[0]]}) 
    # Planform Parameters
    planform_frame = pd.DataFrame({'Parameter':["Geometric AR", "Effective AR", "CLa", "CLmax", "stallAoA", "e", "Vstall"],
                                   'Unit':["-", "-", "rad^-1", "-", "deg", "-", "m/s"],
                                   'Value':[Params.PlanformParameters.geometricAR[0], Params.PlanformParameters.effectiveAR[0], Params.PlanformParameters.liftCurveSlope[0], Params.PlanformParameters.maxLiftCoefficient[0], Params.PlanformParameters.stallAngleOfAttack[0], Params.PlanformParameters.oswaldFactor[0], Params.PlanformParameters.stallSpeed[0]]}) 
    # Subsystem Weight Parameters
    classIIWEParameters_frame = pd.DataFrame({'Parameter':["Wfus", "Wwing", "Wvt", "WLG", "Wpnt", "Wsyseq", "Woper", "Wprop", "Wtank", "Wfuelcells"],
                                              'Unit':["N", "N", "N", "N", "N", "N", "N", "N", "N", "N"],
                                              'Value':[Params.ClassIIWEParameters.WFUS[0], Params.ClassIIWEParameters.WWING[0], Params.ClassIIWEParameters.WVT[0], Params.ClassIIWEParameters.WLG[0], Params.ClassIIWEParameters.WTPNT[0], Params.ClassIIWEParameters.WSYSEQUIPMENT[0], Params.ClassIIWEParameters.WOPERATINGITEMS, Params.ClassIIWEParameters.propulsionWeight[0], Params.ClassIIWEParameters.hydrogenTankWeight[0], Params.ClassIIWEParameters.fuelCellWeight[0]]})
    # Control Surfaces Parameters
    controlSurfaceParameters_frame = pd.DataFrame({'Parameter':["Clda", "Clp", "P", "rollTime", "aileronArea"],
                                                   'Unit':["-", "-", "rad/s", "s", "m2"],
                                                   'Value':[Params.ControlSurfaceParameters.Clda[0], Params.ControlSurfaceParameters.Clp[0], Params.ControlSurfaceParameters.P[0], Params.ControlSurfaceParameters.rollTime[0], Params.ControlSurfaceParameters.aileronArea]})
    # Empennage Parameters
    empennageParameters_frame = pd.DataFrame({'Parameter':["Lvt", "spanVT", "areaVT", "sweepLE", "sweepC4", "rootChordVT", "tipChordVT", "VTMAC"],
                                              'Unit':["m", "m", "m2", "deg", "deg", "m", "m", "m"],
                                              'Value':[Params.EmpennageParameters.Lvt[0], Params.EmpennageParameters.verticalTailSpan[0], Params.EmpennageParameters.areaTail[0], Params.EmpennageParameters.sweepLE, Params.EmpennageParameters.sweepC4[0], Params.EmpennageParameters.rootChordVerticalTail[0], Params.EmpennageParameters.tipChordVerticalTail[0], Params.EmpennageParameters.verticalTailMAC[0]]})
    # Aerodynamic Performance Parameters
    aerodynamicPerformanceParameters_frame = pd.DataFrame({'Parameters':["cruiseCL", "loiterCL", "cleanCruiseCD0", "cleanLoiterCD0", "dirtyLoiterCD0"],
                                                           'Unit':["-", "-", "-", "-", "-"],
                                                           'Value':[Params.AerodynamicPerformanceParameters.cruiseCL[0], Params.AerodynamicPerformanceParameters.loiterCL[0], Params.AerodynamicPerformanceParameters.cleanCruiseCD0[0], Params.AerodynamicPerformanceParameters.cleanLoiterCD0[0], Params.AerodynamicPerformanceParameters.dirtyLoiterCD0[0]]})  
    # Undercarriage Parameters
    undercarriageParameters_frame = pd.DataFrame({'Parameter':["noseWheelDiameter", "noseWheelWidth", "mainWheels", "mainWheelDiameter", "mainWheelWidth"],
                                                  'Unit':["m", "m", "-", "m", "m"],
                                                  'Value':[Params.UndercarriageParameters.noseWheelDiameter[0], Params.UndercarriageParameters.noseWheelWidth[0], Params.UndercarriageParameters.mainWheels[0], Params.UndercarriageParameters.mainWheelDiameter[0], Params.UndercarriageParameters.mainWheelWidth[0]]})
    # Hydrogen Tank Parameters
    hydrogenTankParameters_frame = pd.DataFrame({'Parameter':['finalRadiusInner', 'finalRadiusOuter', 'finalThicknessInner', 'finalThicknessOuter', 'lengthCylinder'],
                                                 'Unit':['m', 'm', 'm', 'm', 'm'],
                                                 'Value':[Params.HydrogenTankParameters.finalRadiusInner, Params.HydrogenTankParameters.finalRadiusOuter, Params.HydrogenTankParameters.finalThicknessInner, Params.HydrogenTankParameters.finalThicknessOuter, Params.HydrogenTankParameters.lengthCylinder]})
    # CG Excursion Parameters
    cgExcursionParameters_frame = pd.DataFrame({'Parameter':['cgOEW', 'aftCG'],
                                                'Unit':['-', '-'],
                                                'Value':[Params.CGExcursionParameters.cgOEW[0], Params.CGExcursionParameters.aftCG]})  

    # Create Excel writer object
    with pd.ExcelWriter(r"C:\Users\thoma\OneDrive\Documenten\TU Delft Aerospace Engineering\Bsc3\Lightning2_optimization\DesignIteration\Dream1\output.xlsx") as writer:
        classIWEParameters_frame.to_excel(writer, sheet_name="ClassIWE", index=False)
        propulsionParameters_frame.to_excel(writer, sheet_name="PropulsionSystem", index=False)
        fuselagePlanform_frame.to_excel(writer, sheet_name="FuselagePlanform", index=False)
        wingPlanform_frame.to_excel(writer, sheet_name="WingPlanform", index=False)
        planform_frame.to_excel(writer, sheet_name="PlanformParameters", index=False)
        classIIWEParameters_frame.to_excel(writer, sheet_name="ClassIIWE", index=False)
        controlSurfaceParameters_frame.to_excel(writer, sheet_name="ControlSurfaces", index=False)
        empennageParameters_frame.to_excel(writer, sheet_name="Empennage", index=False)
        aerodynamicPerformanceParameters_frame.to_excel(writer, sheet_name="AerodynamicPerformance", index=False)
        undercarriageParameters_frame.to_excel(writer, sheet_name="Undercarriage", index=False)
        hydrogenTankParameters_frame.to_excel(writer, sheet_name="HydrogenTank", index=False)
        cgExcursionParameters_frame.to_excel(writer, sheet_name="CGExcursion", index=False)
                          