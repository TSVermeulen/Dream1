import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate, integrate
import numpy as np

def GetDataFromExcelFile(filename):
    dirname = r'C:/Users/dsruy/PycharmProjects/DSE/DesignIteration/AerodynamicDataFiles/'
    data = pd.read_excel(dirname + filename)
    return data.to_numpy()


# def InterpolateData(dataArray, spanwiseLocation):
#     function = interpolate.interp1d(dataArray[:, 0], dataArray[:, 1])
#     forceAtSpanwiseLocation = function(spanwiseLocation)
#
#     return forceAtSpanwiseLocation


# def AerodynamicAxisToBodyAxis(lift, drag, angleOfAttack):
#     """
#     Inputs:
#     Lift force [N/m]
#     Drag force [N/m]
#     Angle of attack [rad]
#     Outputs:
#     Normal force [N/m]
#     Tangent force [N/m]
#     """
#
#     normalAerodynamicForce = np.cos(angleOfAttack) * lift + np.sin(angleOfAttack) * drag
#     tangentAerodynamicForce = np.cos(angleOfAttack) * drag - np.sin(angleOfAttack) * lift
#     return normalAerodynamicForce, tangentAerodynamicForce


def GetLoadingFromEngines(spanWiseLocation, totalThurst, engineSpan, totalWeightEngines):
    """
    Engine alignment is assumed as follows:
                 _______________
               /                 \
              /                    \
    The first engine kink is the one on the left, the second kink the one on the right
    The angle of the two sides is assumed to equal the sweep angle of the leading edge of the wing
    Positive thrust is assumed to point towards the nose of the aircraft

    Inputs:
    Requested spanwise location [m]
    Total thrust [N]
    Span of all the engines [m]
    Total weight of all the engines [N]
    startEngines, spanwise location where the engines start [m]
    endEngines, spanwise location where the engines end [m]
    Sweep Angle [rad]
    Outputs:
    Thrust distributed loading in Y [N/m]
    Engine weight distributed loading in Z [N/m]
    """

    startEngines = -(span - engineSpan)/2
    endEngines = (span - engineSpan)/2

    if startEngines <= spanWiseLocation <= endEngines:
        thrustLoadingY = totalThurst / engineSpan  # [N/m]
        engineWeightLoadingZ = totalWeightEngines / engineSpan  # [N/m]
    else:
        thrustLoadingY = 0.
        engineWeightLoadingZ = 0.

    return thrustLoadingY, engineWeightLoadingZ

# def GetTotalNormalLoading(spanwiseLocation, liftData, dragData):
#     lift = InterpolateData(liftData, spanwiseLocation)
#     drag = InterpolateData(dragData, spanwiseLocation)
#     return AerodynamicAxisToBodyAxis(lift, drag, angleOfAttack)[0] - GetLoadingFromEngines(spanwiseLocation, totalThrust, engineSpan, totalWeightEngines)[1]
#
# def GetTotalTangentLoading(spanwiseLocation, liftData, dragData):
#     lift = InterpolateData(liftData, spanwiseLocation)
#     drag = InterpolateData(dragData, spanwiseLocation)
#     return GetLoadingFromEngines(spanwiseLocation, totalThrust, engineSpan, totalWeightEngines)[0] - AerodynamicAxisToBodyAxis(lift, drag, angleOfAttack)[1]
#
# def GetShearDiagram(spanwiseLocation, span, liftData, dragData):
#     # lift = InterpolateData(liftData, spanwiseLocation)
#     # drag = InterpolateData(dragData, spanwiseLocation)
#     #
#     # normalForce = AerodynamicAxisToBodyAxis(lift, drag, angleOfAttack)[0]
#     # tangentForce = AerodynamicAxisToBodyAxis(lift, drag, angleOfAttack)[1]
#     #
#     # thrustLoading, engineWeightLoading = GetLoadingFromEngines(spanwiseLocation, totalThrust, engineSpan, totalWeightEngines)
#
#
#
#
#     shearNormal1 = integrate.quad(GetTotalNormalLoading, spanwiseLocation, ((span/2)-spanwiseLocation)/3, args=(liftData, dragData), limit=1000, epsabs=1e-4, epsrel=1e-8)
#     shearNormal2 = integrate.quad(GetTotalNormalLoading, ((span/2)-spanwiseLocation)/3, 2*((span/2)-spanwiseLocation)/3, args=(liftData, dragData), limit=1000, epsabs=1e-4, epsrel=1e-8)
#     shearNormal3 = integrate.quad(GetTotalNormalLoading, 2*((span/2)-spanwiseLocation)/3, span/2, args=(liftData, dragData), limit=1000, epsabs=1e-4, epsrel=1e-8)
#
#     shearNormal = shearNormal1[0], shearNormal2[0], shearNormal3[0]
#
#     #shearTangent = integrate.quad(GetTotalTangentLoading, spanwiseLocation, span/2, args=(liftData, dragData), limit=1000, epsabs=1e-4, epsrel=1e-8)
#
#     # print("Error of shear in Z: ", shearInZ[1])
#     # print("Error of shear in Y: ", shearInY[1])
#
#     return shearNormal


def GetNormalForceDistribution(spanwiseLocation, liftData, dragData, angleOfAttack):
    liftFunction = interpolate.interp1d(liftData[:, 0], liftData[:, 1])
    dragFunction = interpolate.interp1d(dragData[:, 0], dragData[:, 1])

    return np.cos(angleOfAttack) * liftFunction(spanwiseLocation) + np.sin(angleOfAttack) * dragFunction(spanwiseLocation) \
           - GetLoadingFromEngines(spanwiseLocation, totalThrust, engineSpan, totalWeightEngines)[1]


def TangentForceDistribution(spanwiseLocation, liftData, dragData, angleOfAttack):
    liftFunction = interpolate.interp1d(liftData[:, 0], liftData[:, 1])
    dragFunction = interpolate.interp1d(dragData[:, 0], dragData[:, 1])

    return GetLoadingFromEngines(spanwiseLocation, totalThrust, engineSpan, totalWeightEngines)[0] - \
           (np.cos(angleOfAttack) * dragFunction(spanwiseLocation) - np.sin(angleOfAttack) * liftFunction(spanwiseLocation))


def GetNormalShear(spanwiseLocation, span, landingGearSpanwiseLocation, landingGearWeight):
    shearNormalIntegration = integrate.quad(NormalForceDistribution, spanwiseLocation, span / 2,
                                 args=(dataLift, dataDrag, angleOfAttack), limit=1000)
    shearNormal = shearNormalIntegration[0]

    if spanwiseLocation <= landingGearSpanwiseLocation:
        shearNormal -= landingGearWeight

    print("The error of the shear integration is: ", shearNormalIntegration[1])
    return shearNormal


def GetTangentShear(spanwiseLocation, span):
    shearTangent = integrate.quad(TangentForceDistribution, spanwiseLocation, span / 2,
                                 args=(dataLift, dataDrag, angleOfAttack), limit=1000)
    print("The error of the shear integration is: ", shearTangent[1])
    return shearTangent[0]

def GetUpwardBending(spanwiseLocation, span):
    upwardBending = integrate.dblquad(NormalForceDistribution, spanwiseLocation, span / 2,
                                 args=(dataLift, dataDrag, angleOfAttack))
    print("The error of the bending integration is: ", upwardBending[1])
    return upwardBending[0]

def GetForwardBending(spanwiseLocation, span):
    forwardBending = integrate.quad(GetTangentShear, spanwiseLocation, span/2, args=(span))
    print("The error of the bending integration is: ", forwardBending[1])
    return forwardBending[0]

def AerodynamicLoadingDistribution(spanwiseLocation, liftData, dragData):
    liftFunction = interpolate.interp1d(liftData[:, 0], liftData[:, 1])
    dragFunction = interpolate.interp1d(dragData[:, 0], dragData[:, 1])

    return np.cos(angleOfAttack) * liftFunction(spanwiseLocation) + np.sin(angleOfAttack) * dragFunction(spanwiseLocation)

def EngineWeightLoading(spanwiseLocation, engineEnd, engineWeight):
    EngineWeightLoad = []
    for i in spanwiseLocation <= engineEnd:
        if i:
            EngineWeightLoad.append(engineWeight)
        else:
            EngineWeightLoad.append(0.)
    EngineWeightLoadArr = np.array(EngineWeightLoad)

    return EngineWeightLoadArr

def landingGearLoading(spanwiseLocation, landingGearWeight, landingGearSpanwiseLocation):
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


def NormalShearIntegral(spanwiseLocations, span):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        res = integrate.quad(NormalForceDistribution, val, span/2)
        result[i] = res[0]
        print("The error of shear integration is ", res[1])
    return result

def TangentShearIntegral(spanwiseLocations, span):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        res = integrate.quad(TangentForceDistribution, val, span/2)
        result[i] = res[0]
        print("The error of shear integration is ", res[1])
    return result

def UpwardMomentIntegral(spanwiseLocations, span):
    result = np.zeros_like(spanwiseLocations)
    for i, val in enumerate(spanwiseLocations):
        res = integrate.quad(NormalShearFunction, val, span/2)
        result[i] = res[0]
        print("The error of moment integration is ", res[1])
    return result

# def TorqueIntegral(y):
#     result = np.zeros_like(y)
#     for i, val in enumerate(y):
#         T = integrate.quad(torqueFunction, val, 18)
#         result[i] = T[0]
#         print("The error of torque integration is ", T[1])
#     return result




##################################Inputs#############################33
span = 43.2  # [m]
totalThrust = 155 * 10 ** 3  # [N]
totalWeightEngines = 6600 * 9.81  # [N]
angleOfAttack = 0.                  # [rad]
engineSpan = 19.                # [m]
landingGearWeight = 1617.7005 * 9.81 / 2
landingGearSpanwiseLocation = 12.       # [m]
halfWidthFuselage = 4.284

###################### Main ##############################

dataDrag = GetDataFromExcelFile('drag.xlsx')
dataLift = GetDataFromExcelFile('lift.xlsx')

y = np.arange(halfWidthFuselage, span/2, 1)

NormalForceDistribution = AerodynamicLoadingDistribution(y, dataLift, dataDrag) - EngineWeightLoading(y, (span-engineSpan)/2, totalWeightEngines/engineSpan)
NormalDistributionFunction = interpolate.interp1d(y, NormalForceDistribution)

NormalShearOutput = NormalShearIntegral(y, span) - landingGearLoading(y, landingGearWeight, landingGearSpanwiseLocation)
NormalShearFunction = interpolate.interp1d(y, NormalShearOutput)

UpwardMomentOutput = -1 * UpwardMomentIntegral(y, span)
UpwardMomentFunction = interpolate.interp1d(y, UpwardMomentOutput)



# spanlist = []
# shearForcesNormalList = []
# shearForcesTangentList = []
# normalForceList = []
# tangentForceList = []
#
# for spanwiseLocation in np.arange(halfWidthFuselage, span/2, 1):
#
#      spanlist.append(spanwiseLocation)
#
#      shearNormal = GetUpwardBending(spanwiseLocation, span)
#      #shearTangent = GetTangentShear(spanwiseLocation, span)
#
#      shearForcesNormalList.append(shearNormal)
#      #shearForcesTangentList.append(shearTangent)
#
# plt.plot(spanlist, shearForcesNormalList)
# plt.show()




# lift = InterpolateData(dataLift, spanwiseLocation)
# drag = InterpolateData(dataDrag, spanwiseLocation)
# normalForce, tangentForce = AerodynamicAxisToBodyAxis(lift, drag, angleOfAttack)
#
# normalForceList.append(normalForce)
# tangentForceList.append(tangentForce)
#
#     shearNormal, shearTangent= GetShearDiagram(spanwiseLocation, span, dataLift, dataDrag)
#
#     shearForcesNormalList.append(shearNormal)
#     shearForcesTangentList.append(shearTangent)
#     # normalForceList.append(normalForce)
#     # tangentForceList.append(tangentForce)
#
# # fig, axs = plt.subplots(2, 2)
# # axs[0, 0].plot(spanlist, normalForceList)
# # axs[0, 0].set_title('Normal Force')
# # axs[1, 0].plot(spanlist, shearForcesNormalList, label='Shear')
# # axs[1, 0].set_title('Normal Shear')
# # axs[0, 1].plot(spanlist, tangentForceList)
# # axs[0, 1].set_title('Tangent Force')
# # axs[1, 1].plot(spanlist, shearForcesTangentList, label='Shear')
# # axs[1, 1].set_title('Tangent Shear')
# plt.show()

#shearNormal = integrate.quad(GetTotalNormalLoading, 2, 13, args=(dataLift, dataDrag), limit=1000, epsabs=1e-4, epsrel=1e-8)
