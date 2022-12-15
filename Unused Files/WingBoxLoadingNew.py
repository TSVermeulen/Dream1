
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate, integrate
import numpy as np

def GetChordLength(spanwiseLocations):
    C1 = 27.6  # Root chord of the fuselage (in the middle of the fuselage).
    X1 = 0
    C2 = 21.724  # Chord at the side of the fuselage/start of the blending section.
    X2 = 4.284
    C3 = 12.369  # Chord at the end of the end of the blending section.
    X3 = 6.284
    C4 = 8.592  # Chord at the kink.
    X4 = 9.213
    C5 = 9.66  # Chord at the very tip of the wing.
    X5 = 18

    # Calculate chord at all points.
    points = np.genfromtxt(r'pitching_moment.txt')
    points = points[1:]

    local_chord = []

    for i in spanwiseLocations:
        if (X1 <= i <= X2) or (-X1 >= i >= -X2):
            i = np.abs(i)
            if i == X1:
                C = C1
                local_chord.append(C)
            else:
                C_begin = C1
                C_end = C2
                X_begin = X1
                X_end = X2
                C = (C_begin - C_end) / (X_end - X_begin) * (X_begin - i) + C_begin
                local_chord.append(C)


        elif (X2 <= i <= X3) or (-X2 >= i >= -X3):
            i = np.abs(i)
            if i == X2:
                C = C2
                local_chord.append(C)
            else:
                C_begin = C2
                C_end = C3
                X_begin = X2
                X_end = X3
                C = (C_begin - C_end) / (X_end - X_begin) * (X_begin - i) + C_begin
                local_chord.append(C)

        elif (X3 <= i <= X4) or (-X3 >= i >= -X4):
            i = np.abs(i)
            if i == X3:
                C = C3
                local_chord.append(C)
            else:
                C_begin = C3
                C_end = C4
                X_begin = X3
                X_end = X4
                C = (C_begin - C_end) / (X_end - X_begin) * (X_begin - i) + C_begin
                local_chord.append(C)

        elif (X4 <= i <= X5) or (-X4 >= i >= -X5):
            i = np.abs(i)
            if i == X4:
                C = C4
                local_chord.append(C)
            else:
                i = np.abs(i)
                C_begin = C4
                C_end = C5
                X_begin = X4
                X_end = X5
                C = (C_begin - C_end) / (X_end - X_begin) * (X_begin - i) + C_begin
                local_chord.append(C)

        elif i == X5 or i == -X5:
            C = C5
            local_chord.append(C)
    local_chordArr = np.array(local_chord)
    return local_chordArr

def GetDataFromExcelFile(filename, identifier):
    dirname = r'AerodynamicDataFiles/'
    if identifier == 0:
        data = pd.read_excel(filename, "Blad1")
    else:
        data = pd.read_excel((dirname + filename), "Blad1")
    return data.to_numpy()

def cop_loc(spanwiseLocation, numberOfLoadCase):
    x_cop_list = GetDataFromExcelFile("CP_8_cases.xlsx", 0)
    # Global coordinate system
    y = x_cop_list[:, 0]
    x = x_cop_list[:, numberOfLoadCase-1]
    # Interpolate function
    x_cop_func = interpolate.interp1d(y, x, fill_value="extrapolate")
    return x_cop_func(spanwiseLocation)

def AerodynamicNormalLoadingDistribution(spanwiseLocation, liftData, dragData, numberOfLoadCase):
    data = liftData[:, numberOfLoadCase]
    i = 0
    if numberOfLoadCase == 8:
        for val in data:
            data[i] = -1 * val
            i +=1

    liftFunction = interpolate.interp1d(liftData[:, 0], data, fill_value="extrapolate")
    dragFunction = interpolate.interp1d(dragData[:, 0], dragData[:, numberOfLoadCase], fill_value="extrapolate")


    liftOutput = liftFunction(spanwiseLocation)
    dragOutput = dragFunction(spanwiseLocation)
    NormalAeForce = np.cos(angleOfAttack) * liftOutput + np.sin(angleOfAttack) * dragOutput
    return NormalAeForce

def AerodynamicTangentLoadingDistribution(spanwiseLocation, liftData, dragData, numberOfLoadCase):
    data = liftData[:, numberOfLoadCase]
    i = 0
    if numberOfLoadCase == 8:
        for val in data:
            data[i] = -1 * val
            i +=1
    liftFunction = interpolate.interp1d(liftData[:, 0], data, fill_value="extrapolate")
    dragFunction = interpolate.interp1d(dragData[:, 0], dragData[:, numberOfLoadCase], fill_value="extrapolate")
    TangentAeForce = np.cos(angleOfAttack) * dragFunction(spanwiseLocation) - np.sin(angleOfAttack) * liftFunction(spanwiseLocation)
    return TangentAeForce

def AerodynamicMomentDistribution(momentData, numberOfLoadCase):
    momentFunction = interpolate.interp1d(momentData[:, 0], momentData[:, numberOfLoadCase], fill_value="extrapolate")
    return momentFunction

def flexuralAxis(spanwiseLocation):
    if spanwiseLocation <= 6.284:
        m = -1 * np.tan(np.radians(71.74))
        b = 5.129
    elif 6.284 < spanwiseLocation < 9.209:
        m = -1 * np.tan(np.radians(49.29))
        b = -6.618
    elif spanwiseLocation >= 9.209:
        m = -1 * np.tan(np.radians(50.64))
        b = -6.091
    return m * spanwiseLocation + b

def leadingEdge(spanwiseLocation):
    if spanwiseLocation <= 6.284:
        m = -1 * np.tan(np.radians(74.05))
        b = 9.307
    elif 6.284 < spanwiseLocation < 9.209:
        m = -1 * np.tan(np.radians(52.24))
        b = -4.571
    elif spanwiseLocation >= 9.209:
        m = -1 * np.tan(np.radians(51.91))
        b = -4.71

    return m * spanwiseLocation + b

def DistanceCOPandFlexuralAxis(spanwiseLocation, numberOfLoadCase):
    # positive torque if cp behind flex axis
    Distance = []
    for i in spanwiseLocation:
        Distance.append(cop_loc(i, numberOfLoadCase) - flexuralAxis(i))
    DistanceArr = np.array(Distance)
    return DistanceArr

def DistanceEngineandFlexuralAxisInXAndZ(spanwiseLocations, thicknessToChord, radiusEngine):
    chordLocations = GetChordLength(spanwiseLocations)
    XDistance = []
    ZDistance = []
    for i in spanwiseLocations:
        flexuralAxisWRTNose = flexuralAxis(i)
        leadingEdgeWRTNose = leadingEdge(i)
        chordAtLocation = chordLocations[np.where(spanwiseLocations == i)]

        XDistance.append((flexuralAxisWRTNose - (leadingEdgeWRTNose + 0.7 * chordAtLocation))[0])
        ZDistance.append(((thicknessToChord * chordAtLocation)/2 + radiusEngine)[0])

    XDistanceArr = np.array(XDistance)
    ZDistanceArr = np.array(ZDistance)
    return XDistanceArr, ZDistanceArr

def EngineWeightLoading(spanwiseLocation, engineEnd, engineWeight):
    EngineWeightLoad = []
    for i in spanwiseLocation <= engineEnd:
        if i:
            EngineWeightLoad.append(engineWeight)
        else:
            EngineWeightLoad.append(0.)
    EngineWeightLoadArr = np.array(EngineWeightLoad)

    return EngineWeightLoadArr

def EngineThrustLoading(spanwiseLocation, engineEnd, ThrustForce):
    EngineThrustLoad = []
    for i in spanwiseLocation <= engineEnd:
        if i:
            EngineThrustLoad.append(ThrustForce)
        else:
            EngineThrustLoad.append(0.)
    EngineThrustLoadArr = np.array(EngineThrustLoad)
    return EngineThrustLoadArr

def landingGearWeightLoading(spanwiseLocation, landingGearWeight, landingGearSpanwiseLocation):
    # Step function resulting in shear value of 3250
    # beyond z=2.2 m (location of mlg).
    LGload = []
    for i in spanwiseLocation <= landingGearSpanwiseLocation:
        if i:
            # Model weight of landing gear as a point load,
            # 1/3 of total LG weight.
            LGload.append(landingGearWeight)
        else:
            landingGearWeight = 0 # LG load is zero at all points
            # before location of landing gear
            LGload.append(landingGearWeight)
    LGloadArr = np.array(LGload)
    return LGloadArr

def verticalWingTipLoading(spanwiseLocations, verticalWingTipWeight):
    VWloadArr = np.zeros_like(spanwiseLocations)
    VWloadArr[-1] = verticalWingTipWeight

    return VWloadArr

def landingGearTorqueLoading(spanwiseLocation, landingGearSpanwiseLocation, landingGearLocationWRTFlexuralAxis, landingGearWeight):
    # Step function resulting in shear value of 3250
    # beyond z=2.2 m (location of mlg).
    LGtorque = []
    for i in spanwiseLocation <= landingGearSpanwiseLocation:
        if i:
            LGtorque.append(landingGearWeight * landingGearLocationWRTFlexuralAxis)
        else:
            landingGearWeight = 0 #
            # before location of landing gear
            LGtorque.append(landingGearWeight)
    LGtorqueArr = np.array(LGtorque)
    return LGtorqueArr

def NormalShearIntegral(spanwiseLocations, span, NormalForceDistributionFunction):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        res = integrate.quad(NormalForceDistributionFunction, val, span/2, limit=1000)
        result[i] = res[0]
        #print("The error of shear integration is ", res[1])

    #result = integrate.quad(NormalForceDistributionFunction, spanwiseLocations[0], span/2, limit=1000)

    return result

def TangentShearIntegral(spanwiseLocations, span, TangentForceDistributionFunction):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        res = integrate.quad(TangentForceDistributionFunction, val, span/2, limit=1000)
        result[i] = res[0]
        #print("The error of shear integration is ", res[1])
    return result

def UpwardMomentIntegral(spanwiseLocations, span, NormalShearFunction):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        res = integrate.quad(NormalShearFunction, val, span/2, limit=1000)
        result[i] = res[0]
        #print("The error of moment integration is ", res[1])
    return result

def ForwardMomentIntegral(spanwiseLocations, span, TangentShearFunction):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        res = integrate.quad(TangentShearFunction, val, span/2, limit=1000)
        result[i] = res[0]
        #print("The error of moment integration is ", res[1])
    return result

def TorqueIntegral(spanwiseLocations, span, TorqueFunction):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        T = integrate.quad(TorqueFunction, val, span/2, limit=1000)
        result[i] = T[0]
        #print("The error of torque integration is ", T[1])
    return result


def GetRotationMatrix(spanwiseLocation):
    """
    Inputs:
    Quarter chord sweep angle [rad]
    Output:
    Rotation matrix for rotation around z
    """
    if spanwiseLocation <= 6.284:
        matrixZ = np.array([[np.cos(np.radians(66.77)), np.sin(np.radians(66.77)), 0.],
                                [-1 * np.sin(np.radians(66.77)), np.cos(np.radians(66.77)), 0.],
                                [0., 0., 1.]])

    elif 6.284 < spanwiseLocation < 9.209:
        matrixZ = np.array([[np.cos(np.radians(44.08)), np.sin(np.radians(44.08)), 0.],
                                [-1 * np.sin(np.radians(44.08)), np.cos(np.radians(44.08)), 0.],
                                [0., 0., 1.]])

    elif spanwiseLocation >= 9.209:
        matrixZ = np.array([[np.cos(np.radians(48.62)), np.sin(np.radians(48.62)), 0.],
                                [-1 * np.sin(np.radians(48.62)), np.cos(np.radians(48.62)), 0.],
                                [0., 0., 1.]])
    return matrixZ

def RotateShearArray(spanwiseLocation, NormalShearFunctionBodyAxis, TangentShearFunctionBodyAxis):

    rotationMatrix = GetRotationMatrix(spanwiseLocation)
    shearMatrix = np.array([[TangentShearFunctionBodyAxis(spanwiseLocation)],
                             [0],
                             [NormalShearFunctionBodyAxis(spanwiseLocation)]])

    rotatedShearMatrix = rotationMatrix @ shearMatrix

    TangentShearInX = rotatedShearMatrix[0]
    NormalForceInY = rotatedShearMatrix[1]
    NormalShearInZ = rotatedShearMatrix[2]

    return TangentShearInX[0], NormalForceInY[0], NormalShearInZ[0]

def RotateMomentArray(spanwiseLocation, UpwardMomentFunctionBodyAxis, ForwardMomentFunctionBodyAxis):
    rotationMatrix = GetRotationMatrix(spanwiseLocation)
    shearMatrix = np.array([[UpwardMomentFunctionBodyAxis(spanwiseLocation)],
                            [0.],
                            [ForwardMomentFunctionBodyAxis(spanwiseLocation)]])

    rotatedMomentMatrix = rotationMatrix @ shearMatrix

    UpwardMoment = rotatedMomentMatrix[0]
    Torque = rotatedMomentMatrix[1]
    ForwardBending = rotatedMomentMatrix[2]

    return UpwardMoment[0], Torque[0], ForwardBending[0]



def GetShearDistribution(y, dataLift, dataDrag, span, engineSpan, totalWeightEngines, totalThrust, landingGearWeight, landingGearSpanwiseLocation, verticalWingTipWeight, numberOfLoadCase):
    """
    Inputs:
    y, a vector of spans in body axis system [m]
    span, total wing span in body axis system [m]
    Total weight of the engines [N]
    Total thrust [N]
    Landing gear weight [N]
    Landing gear spanwise location in the body axis system [m]
    Quarter chord sweep angle [rad]
    Outputs:
    Normal force distribution in the body axis system [N]
    Normal Force Distribution Function, takes span location (in body axis system!) [m] as input and returns the normal force (in body axis system) at that location [N]
    Tangent Force Distribution in the body axis system [N],
    Tangent Force Distribution Function, takes span location (in body axis system!) [m] as input and returns the tangent force (in body axis system) at that location [N]
    Tangent Shear Function In X, takes span location (in body axis system!) [m] as input and returns the tangent shear force (in wing box axis system!) at that location [N]
    Normal Force Function In Y, takes span location (in body axis system!) [m] as input and returns the normal force at (in wing box axis system!) that location [N]
    Normal Shear Function In Z, takes span location (in body axis system!) [m] as input and returns the normal shear force (in wing box axis system!) at that location [N]
    """

    # Get the aerodynamic forces from XFLR5 data. Note this is in the aerodynamic axis system
    # dataDrag = GetDataFromExcelFile('Drag-new.xlsx')
    # dataLift = GetDataFromExcelFile('Lift-new.xlsx')

    print("Working on Shear")

    # Get the normal force distribution and its interpolated function by first transforming lift, drag to body axis system
    # to the normal force and then subtracting the engine distributed weight
    EngineWeightOutput = EngineWeightLoading(y, (span-engineSpan)/2, totalWeightEngines/engineSpan)
    AerodynamicNormalLoadingOutput = AerodynamicNormalLoadingDistribution(y, dataLift, dataDrag, numberOfLoadCase)
    NormalForceDistribution = EngineWeightOutput - AerodynamicNormalLoadingOutput
    NormalForceDistributionFunctionBodyAxis = interpolate.interp1d(y, NormalForceDistribution, fill_value="extrapolate")

    # Get tangent force distribution and its interpolated function by first transforming lift, drag to body axis system
    # to the tangent force and subtracting that from the thrust distributed force
    TangentForceDistribution = EngineThrustLoading(y, (span-engineSpan)/2, totalThrust/engineSpan) - AerodynamicTangentLoadingDistribution(y, dataLift, dataDrag, numberOfLoadCase)
    TangentForceDistributionFunctionBodyAxis = interpolate.interp1d(y, TangentForceDistribution, fill_value="extrapolate")

    # Integrate the force distributions to shear. Note that the shear is still in the body axis system
    LandingGearWeightLoadingOutput = landingGearWeightLoading(y, landingGearWeight, landingGearSpanwiseLocation)
    VerticalWingTipLoadingOuput = verticalWingTipLoading(y, verticalWingTipWeight)
    NormalShearIntegrated = NormalShearIntegral(y, span, NormalForceDistributionFunctionBodyAxis)
    NormalShearOutput = NormalShearIntegrated + LandingGearWeightLoadingOutput - VerticalWingTipLoadingOuput
    NormalShearFunctionBodyAxis = interpolate.interp1d(y, NormalShearOutput, fill_value="extrapolate")

    TangentShearOutput = TangentShearIntegral(y, span, TangentForceDistributionFunctionBodyAxis)
    TangentShearFunctionBodyAxis = interpolate.interp1d(y, TangentShearOutput, fill_value="extrapolate")

    rotatedTangentShear = []
    rotatedNormalForce = []
    rotatedNormalShear = []
    for location in y:
        TangentShearInX, NormalForceInY, NormalShearInZ = RotateShearArray(location, NormalShearFunctionBodyAxis, TangentShearFunctionBodyAxis)
        rotatedTangentShear.append(TangentShearInX)
        rotatedNormalForce.append(NormalForceInY)
        rotatedNormalShear.append(NormalShearInZ)


    # # Put shear in a matrix: Tangent shear should be positive x in Body axis system and Normal shear should be negative z
    # shearMatrix = np.array([[TangentShearOutput],
    #                         [0.],
    #                         [NormalShearOutput]])
    # # Get the rotation matrix to go from body axis system to wing box axis system
    # rotationMatrix = GetRotationMatrix(quarterChordSweepAngle)
    #
    # # Do rotation
    # RotatedShearMatrix = rotationMatrix @ shearMatrix

    # Interpolate the rotated shears into actual function. Note: while the shears are in the wing box axis system, the span is not!
    # This means that you have to use the span of the body axis system to get the shear in the wing box axis system!!!
    TangentShearFunctionInXWingBoxAxis = interpolate.interp1d(y, np.array(rotatedTangentShear), fill_value="extrapolate")
    NormalForceFunctionInYWingBoxAxis = interpolate.interp1d(y, np.array(rotatedNormalForce), fill_value="extrapolate")
    NormalShearFunctionInZWingBoxAxis = interpolate.interp1d(y, np.array(rotatedNormalShear), fill_value="extrapolate")

    return NormalForceDistributionFunctionBodyAxis, TangentForceDistributionFunctionBodyAxis, NormalShearFunctionBodyAxis, \
           TangentShearFunctionBodyAxis, TangentShearFunctionInXWingBoxAxis, NormalForceFunctionInYWingBoxAxis, NormalShearFunctionInZWingBoxAxis



def GetMomentDistribition(y, dataLift, dataDrag, dataMoment, span, engineSpan, totalWeightEngines, totalThrust, landingGearSpanwiseLocation, landingGearWeight, thicknessToChord, radiusEngine,
                          landingGearLocationWRTFlexuralAxis, NormalShearFunctionBodyAxis, TangentShearFunctionBodyAxis, numberOfLoadCase):
    # dataDrag = GetDataFromExcelFile('Drag-new.xlsx')
    # dataLift = GetDataFromExcelFile('Lift-new.xlsx')
    # dataMoment = GetDataFromExcelFile('Moment-new.xlsx')

    print("Working on Moments ")

    UpwardMomentOutput = UpwardMomentIntegral(y, span, NormalShearFunctionBodyAxis)
    UpwardMomentFunctionBodyAxis = interpolate.interp1d(y, UpwardMomentOutput, fill_value="extrapolate")

    ForwardMomentOutput = ForwardMomentIntegral(y, span, TangentShearFunctionBodyAxis)
    ForwardMomentFunctionBodyAxis = interpolate.interp1d(y, ForwardMomentOutput, fill_value="extrapolate")

    #AerodynamicTorqueFunction = AerodynamicMomentDistribution(dataMoment, numberOfLoadCase)
    # AerodyncamicTorqueIntegral = integrate.quad(AerodynamicTorqueFunction, 0, span/2, limit=1000)
    # print("For Jorian: ", AerodyncamicTorqueIntegral)

    #TorqueDistributionAerodynamicNormal = (AerodynamicNormalLoadingDistribution(y, dataLift, dataDrag, numberOfLoadCase)) * DistanceCOPandFlexuralAxis(y, numberOfLoadCase)
    # TorqueDistributionAerodynamicTangential = AerodynamicTangentLoadingDistribution(y, dataLift, dataDrag) * DistanceCOPandFlexuralAxis(y)

    # XDistanceEngine, ZDistanceEngine = DistanceEngineandFlexuralAxisInXAndZ(y, thicknessToChord, radiusEngine)
    # TorqueDistributionEngineThrust = EngineThrustLoading(y, (span-engineSpan)/2, totalThrust/engineSpan) * ZDistanceEngine
    # TorqueDistributionEngineWeight = EngineWeightLoading(y, (span-engineSpan)/2, totalWeightEngines/engineSpan) * XDistanceEngine
    # TorqueDistributionAerodynamicMoment = AerodynamicTorqueFunction(y)

    # TorqueDistribution = TorqueDistributionAerodynamicNormal - TorqueDistributionEngineThrust - TorqueDistributionEngineWeight + TorqueDistributionAerodynamicMoment
    #
    # TorqueFunctionForIntegral = interpolate.interp1d(y, TorqueDistribution, fill_value="extrapolate")
    #
    # landingGearTorqueOutput = landingGearTorqueLoading(y, landingGearSpanwiseLocation, landingGearLocationWRTFlexuralAxis, landingGearWeight)
    # TorqueOutput = TorqueIntegral(y, span, TorqueFunctionForIntegral) + landingGearTorqueOutput
    # TorqueFunctionBodyAxis = interpolate.interp1d(y, TorqueOutput, fill_value="extrapolate")


    rotatedUpwardBending = []
    rotatedTorque = []
    rotatedForwardBending = []
    for location in y:
        UpwardMoment, Torque, ForwardBending = RotateMomentArray(location, UpwardMomentFunctionBodyAxis, ForwardMomentFunctionBodyAxis)

        rotatedUpwardBending.append(UpwardMoment)
        rotatedTorque.append(Torque)
        rotatedForwardBending.append(ForwardBending)


    ForwardBendingFunctionZInWingBoxAxis = interpolate.interp1d(y, np.array(rotatedForwardBending), fill_value="extrapolate")
    UpwardBendingFunctionXInWingBoxAxis = interpolate.interp1d(y, np.array(rotatedUpwardBending), fill_value="extrapolate")
    AdditionalTorqueFunctionYInWingBoxAxis = interpolate.interp1d(y, np.array(rotatedTorque), fill_value="extrapolate")

    return ForwardMomentFunctionBodyAxis, UpwardMomentFunctionBodyAxis, ForwardBendingFunctionZInWingBoxAxis, \
           UpwardBendingFunctionXInWingBoxAxis, AdditionalTorqueFunctionYInWingBoxAxis


##################################Inputs#############################33
span = 36                                       # [m]
totalThrust = 223256.4782                       # [N]
totalWeightEngines = 7829.2576 * 9.81            # [N]
weightPerVerticalWingTip = 1793.463043 / 2 * 9.81           # [N]
engineSpan = 20.2465                            # [m]
landingGearSpanwiseLocation = 3.2025                # [m]
halfWidthFuselage = 8.568 / 2                   # [m]
bla = flexuralAxis(landingGearSpanwiseLocation)
landingGearLocationWRTFlexuralAxis = -1 * abs(16.84 - abs(bla))         # [m] 16.84
landingGearWeight = 3682.1818/2 * 9.81          # [N]
#quarterChordSweepAngle = np.radians(47.130373) # [rad]
thicknessToChord = 0.1264                       # [-]
radiusEngine = 1.79059 / 2                      # [m]

###################### Main ##############################

y = np.arange(0, span/2, 0.5)

dataDrag = GetDataFromExcelFile('Drag_8_cases.xlsx', 1)
dataLift = GetDataFromExcelFile('Lift_8_cases.xlsx', 1)
dataMoment = GetDataFromExcelFile('Moment_8_cases.xlsx', 1)

whichLoadCase = int(input("Fill in 1 for the most critical positive load case and 0 for the most negative and fill in 2 for Maarten : "))

if whichLoadCase == 1:
    numberOfLoadCase = 7
    angleOfAttack = np.radians(1.2)
elif whichLoadCase == 0:
    numberOfLoadCase = 2
    angleOfAttack = np.radians(10.5)
elif whichLoadCase == 2:
    numberOfLoadCase = 8
    angleOfAttack = np.radians(1.2)
else:
    print("You fucked up")
    exit()



NormalForceDistributionFunctionBodyAxis, TangentForceDistributionFunctionBodyAxis, NormalShearFunctionBodyAxis, \
           TangentShearFunctionBodyAxis, TangentShearFunctionInXWingBoxAxis, NormalForceFunctionInYWingBoxAxis, NormalShearFunctionInZWingBoxAxis = \
    GetShearDistribution(y, dataLift, dataDrag, span, engineSpan, totalWeightEngines, totalThrust, landingGearWeight, landingGearSpanwiseLocation, weightPerVerticalWingTip, numberOfLoadCase)

ForwardMomentFunctionBodyAxis, UpwardMomentFunctionBodyAxis, ForwardBendingFunctionZInWingBoxAxis, \
           UpwardBendingFunctionXInWingBoxAxis, AdditionalTorqueFunctionYInWingBoxAxis = \
    GetMomentDistribition(y, dataLift, dataDrag, dataMoment, span, engineSpan, totalWeightEngines, totalThrust, landingGearSpanwiseLocation, landingGearWeight, thicknessToChord, radiusEngine,
                          landingGearLocationWRTFlexuralAxis, NormalShearFunctionBodyAxis, TangentShearFunctionBodyAxis, numberOfLoadCase)



print("Finished")

# fig, axs = plt.subplots(2, 4)
#
# axs[0, 0].plot(y, NormalForceDistributionFunctionBodyAxis(y))
# axs[0, 0].set_title("Normal Force Distribution in Body Axis system", fontdict={'fontsize': 7})
#
# axs[1, 0].plot(y, NormalShearFunctionInZWingBoxAxis(y))
# axs[1, 0].set_title("Normal Shear Force in Wing box axis system", fontdict={'fontsize': 7})
#
# axs[0, 1].plot(y, TangentForceDistributionFunctionBodyAxis(y))
# axs[0, 1].set_title("Tangent Force Distribution in Body axis system", fontdict={'fontsize': 7})
#
# axs[1, 1].plot(y, TangentShearFunctionInXWingBoxAxis(y))
# axs[1, 1].set_title("Tangent Shear Force in Wing box axis system", fontdict={'fontsize': 7})
#
# axs[0, 2].plot(y, ForwardBendingFunctionZInWingBoxAxis(y))
# axs[0, 2].set_title("Bending around Z in Wing box axis system", fontdict={'fontsize': 7})
#
# axs[1, 2].plot(y, UpwardBendingFunctionXInWingBoxAxis(y))
# axs[1, 2].set_title("Bending around X in Wing box axis system", fontdict={'fontsize': 7})
#
# axs[0, 3].plot(y, NormalForceFunctionInYWingBoxAxis(y))
# axs[0, 3].set_title("Normal force in Wing box axis system", fontdict={'fontsize': 7})
#
# axs[1, 3].plot(y, TorqueFunctionYInWingBoxAxis(y))
# axs[1, 3].set_title("Torque around y in Wing box axis system", fontdict={'fontsize': 7})
#
#
# plt.savefig("Loading.png")
# plt.show()

