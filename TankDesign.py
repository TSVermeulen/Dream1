""""

Program to design the hydrogen tank for the blended wing body.

Based on:
[1] "Modelling and Designing Cryogenic Hydrogen Tanks for Future Aircraft Applications", 2017
by Christopher Winnefeld et al.
and
[2] "Hydrogen Aircraft Technology", 1991
by G. Daniel Brewer
and
[3] "Aerospace Design & Systems Engineering Elements I
Part: Launch Vehicle design and sizing"
and
[4] "Liquid hydrogen tank considerations for turboelectric distributed propulsion
by Paulas Raja Sekaran et al.
and
[5] "Physics for scientists and engineers"
by Douglas Giancoli
pages 562-654

Original work by Dorothé, now updated by Thomas Stephan Vermeulen
New code is verified to produce the same results as the original, with an improved numerical and runtime efficiency.

@author: Dorothé, Thomas 

"""

import numpy as np
from ambiance import Atmosphere

def TankVolumeDetermination(Params, ConvAndConst):
    """"
    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Output:
    -----
    requiredVolumeTotal, total required volume for hydrogen [m3]
    requiredVolumePerTank, required volume for hydrogen per tank [m3]
    """

    # Total Hydrogen Volume
    requiredVolumeTotal = (Params.ClassIWEParameters.WF / ConvAndConst.g) * (1 + ConvAndConst.HydrogenTankConstants.excessVolume) / ConvAndConst.HydrogenTankConstants.densityLH2
    
    # Volume Per Tank
    requiredVolumePerTank = requiredVolumeTotal / ConvAndConst.HydrogenTankConstants.numberOfTanks

    return requiredVolumeTotal, requiredVolumePerTank

def TankGeometry(Params, ConvAndConst):
    """
    Define the tank as a cylinder with two halve of an ellipsoid
    Assumption: cross-section of the tank is a circle

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    finalRadius, final cross-sectional radius of the hydrogen tank [m]
    availableVolumePerTank, available volume inside the tank [m3]
    cylL, length of the cylindrical part of the tank [m]
    """

    for r in np.arange(0., 10., 0.001): # check radius until 10 meter with accuracy of 1 mm
        # Length of cylindrical part
        cylL = ConvAndConst.HydrogenTankConstants.requiredLength - 2 * r
        #sphL = r * psi

        # Volume of cylindrical part and of endcaps
        volumeCylinder = np.pi * r ** 2 * cylL
        volumeSphere = 4/3 * np.pi * r ** 3

        # Total available volume per tank
        availableVolumePerTank = volumeSphere + volumeCylinder

        if availableVolumePerTank >= Params.HydrogenTankParameters.requiredVolumePerTank:
            finalRadius = r
            length = cylL + 2 * r
            break

    return finalRadius, availableVolumePerTank, cylL

def getPressureDifferenceInnerAndOuterTank(ConvAndConst):
    """
    Function to calculate the maximum pressures the inner and outer tank have to withstand. 

    Inputs:
    -----
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    burstPressureInnerTank, burst pressure of the inner tank [Pa]
    burstPressureOuterTank, burst pressure of the outer tank [Pa]
    """

    maxPressureDifferenceInnerTank = ConvAndConst.HydrogenTankConstants.pressureLH2 - ConvAndConst.HydrogenTankConstants.pressureVacuum          # because it has to withstand the difference between vacuum and LH2 pressure
    maxPressureDifferenceOuterTank = Atmosphere(ConvAndConst.HydrogenTankConstants.minOperatingAltitude).pressure - ConvAndConst.HydrogenTankConstants.pressureVacuum

    # add load factors: design for burst pressure
    burstPressureInnerTank = 2 * maxPressureDifferenceInnerTank
    burstPressureOuterTank = 2 * maxPressureDifferenceOuterTank

    return burstPressureInnerTank, burstPressureOuterTank

def thicknessCalculation(Params, ConvAndConst):
    """"
    Based on the tank design of a launcher according to ADSEE-I
    The largest thickness is the most limiting!

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    finalThicknessInner, final thickness of the inner tank [m]
    finalThicknessOuter, final thickness of the outer tank [m]
    """

    """ Inner Tank Design """
    thicknessCylinderHoopYield = Params.HydrogenTankParameters.burstPressureInnerTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessYield * Params.HydrogenTankParameters.finalRadiusInner / ConvAndConst.HydrogenTankConstants.yieldStressMaterialInner
    thicknessCylinderHoopUltimate = Params.HydrogenTankParameters.burstPressureInnerTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessUltimate * Params.HydrogenTankParameters.finalRadiusInner / ConvAndConst.HydrogenTankConstants.ultimateStressMaterialInner

    if thicknessCylinderHoopUltimate > thicknessCylinderHoopYield:
        thicknessCylinderInner = thicknessCylinderHoopUltimate
    elif thicknessCylinderHoopUltimate < thicknessCylinderHoopYield:
        thicknessCylinderInner = thicknessCylinderHoopYield
    else:
        thicknessCylinderInner = thicknessCylinderHoopYield

    thicknessSpericalEndCapsYield = Params.HydrogenTankParameters.burstPressureInnerTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessYield * Params.HydrogenTankParameters.finalRadiusInner / (2 * ConvAndConst.HydrogenTankConstants.yieldStressMaterialInner)
    thicknessSpericalEndCapsUltimate = Params.HydrogenTankParameters.burstPressureInnerTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessUltimate * Params.HydrogenTankParameters.finalRadiusInner / (2 * ConvAndConst.HydrogenTankConstants.ultimateStressMaterialInner)

    if thicknessSpericalEndCapsUltimate > thicknessSpericalEndCapsYield:
        thicknessSphericalCapsInner = thicknessSpericalEndCapsUltimate
    elif thicknessSpericalEndCapsUltimate < thicknessSpericalEndCapsYield:
        thicknessSphericalCapsInner = thicknessSpericalEndCapsYield
    else:
        thicknessSphericalCapsInner = thicknessSpericalEndCapsYield

    # assume a constant thickness:
    if thicknessCylinderInner > thicknessSphericalCapsInner:
        finalThicknessInner = thicknessCylinderInner
    elif thicknessCylinderInner < thicknessSphericalCapsInner:
        finalThicknessInner = thicknessSphericalCapsInner
    else:
        finalThicknessInner = thicknessCylinderInner

    if finalThicknessInner < ConvAndConst.HydrogenTankConstants.minimumThickness:
        finalThicknessInner = ConvAndConst.HydrogenTankConstants.minimumThickness

    """ Outer Tank Design """
    Params.HydrogenTankParameters.finalRadiusOuter = Params.HydrogenTankParameters.finalRadiusInner + finalThicknessInner + ConvAndConst.HydrogenTankConstants.vacuumThickness
    thicknessCylinderHoopYield = Params.HydrogenTankParameters.burstPressureOuterTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessYield * Params.HydrogenTankParameters.finalRadiusOuter / ConvAndConst.HydrogenTankConstants.yieldStressMaterialOuter
    thicknessCylinderHoopUltimate = Params.HydrogenTankParameters.burstPressureOuterTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessUltimate * Params.HydrogenTankParameters.finalRadiusOuter / ConvAndConst.HydrogenTankConstants.ultimateStressMaterialOuter

    if thicknessCylinderHoopUltimate > thicknessCylinderHoopYield:
        thicknessCylinderOuter = thicknessCylinderHoopUltimate
    elif thicknessCylinderHoopUltimate < thicknessCylinderHoopYield:
        thicknessCylinderOuter = thicknessCylinderHoopYield
    else:
        thicknessCylinderOuter = thicknessCylinderHoopYield

    thicknessSpericalEndCapsYield = Params.HydrogenTankParameters.burstPressureOuterTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessYield * Params.HydrogenTankParameters.finalRadiusOuter / (2 * ConvAndConst.HydrogenTankConstants.yieldStressMaterialOuter)
    thicknessSpericalEndCapsUltimate = Params.HydrogenTankParameters.burstPressureOuterTank * ConvAndConst.HydrogenTankConstants.safetyFactorThicknessUltimate * Params.HydrogenTankParameters.finalRadiusOuter / (2 * ConvAndConst.HydrogenTankConstants.ultimateStressMaterialOuter)

    if thicknessSpericalEndCapsUltimate > thicknessSpericalEndCapsYield:
        thicknessSphericalCapsOuter = thicknessSpericalEndCapsUltimate
    elif thicknessSpericalEndCapsUltimate < thicknessSpericalEndCapsYield:
        thicknessSphericalCapsOuter = thicknessSpericalEndCapsYield
    else:
        thicknessSphericalCapsOuter = thicknessSpericalEndCapsYield

    # assume a constant thickness:
    if thicknessCylinderOuter > thicknessSphericalCapsOuter:
        finalThicknessOuter = thicknessCylinderOuter
    elif thicknessCylinderOuter < thicknessSphericalCapsOuter:
        finalThicknessOuter = thicknessSphericalCapsOuter
    else:
        finalThicknessOuter = thicknessCylinderOuter

    if finalThicknessOuter < ConvAndConst.HydrogenTankConstants.minimumThickness:
        finalThicknessOuter = ConvAndConst.HydrogenTankConstants.minimumThickness
        
    return finalThicknessInner, finalThicknessOuter

def calculateTankMass(Params, ConvAndConst):
    """
    Function to calculate the tank mass of the inner and outer tanks
    Based on the tank design of a launcher according to ADSEE-I

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    tankMassInnerTank, mass of the inner tank [kg]
    surfaceAreaInnerTank, surface area of the inner tank [m2]
    tankMassOuterTank, mass of the outer tank [kg]
    surfaceAreaOuterTank, surface area of the outer tank [m2]
    """

    """ Inner Tank """
    volumeInside = np.pi * Params.HydrogenTankParameters.finalRadiusInner ** 2 * Params.HydrogenTankParameters.lengthCylinder + 4/3 * np.pi * Params.HydrogenTankParameters.finalRadiusInner **3
    volumeOutside = np.pi * (Params.HydrogenTankParameters.finalRadiusInner + Params.HydrogenTankParameters.finalThicknessInner) ** 2 * Params.HydrogenTankParameters.lengthCylinder + 4/3 * np.pi * (Params.HydrogenTankParameters.finalRadiusInner + Params.HydrogenTankParameters.finalThicknessInner) ** 3
    shellVolume = volumeOutside - volumeInside
    tankMassInnerTank = shellVolume * ConvAndConst.HydrogenTankConstants.densityMaterialInner

    circumferenceTank = 2 * np.pi * Params.HydrogenTankParameters.finalRadiusInner                                            # circumference of a circle
    surfaceAreaInnerTank = circumferenceTank * Params.HydrogenTankParameters.lengthCylinder + 4 * np.pi * Params.HydrogenTankParameters.finalRadiusInner ** 2      # area of rectangle + surface area of sphere
    
    """ Outer Tank """
    volumeInside = np.pi * Params.HydrogenTankParameters.finalRadiusOuter ** 2 * Params.HydrogenTankParameters.lengthCylinder + 4/3 * np.pi * Params.HydrogenTankParameters.finalRadiusOuter **3
    volumeOutside = np.pi * (Params.HydrogenTankParameters.finalRadiusOuter + Params.HydrogenTankParameters.finalThicknessOuter) ** 2 * Params.HydrogenTankParameters.lengthCylinder + 4/3 * np.pi * (Params.HydrogenTankParameters.finalRadiusOuter + Params.HydrogenTankParameters.finalThicknessOuter) ** 3
    shellVolume = volumeOutside - volumeInside
    tankMassOuterTank = shellVolume * ConvAndConst.HydrogenTankConstants.densityMaterialOuter

    circumferenceTank = 2 * np.pi * Params.HydrogenTankParameters.finalRadiusOuter                                            # circumference of a circle
    surfaceAreaOuterTank = circumferenceTank * Params.HydrogenTankParameters.lengthCylinder + 4 * np.pi * Params.HydrogenTankParameters.finalRadiusOuter ** 2      # area of rectangle + surface area of sphere

    return tankMassInnerTank, surfaceAreaInnerTank, tankMassOuterTank, surfaceAreaOuterTank

def determineAllowedHeatFlux(Params, ConvAndConst):
    """
    Function to calculate the allowed heat flux for the hydrogen tanks.

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    allowedHeatFlux, the allowed heatflux [W/m2]
    ambientTemperature, the ambient temperature at the minimum operating altitude [K]
    """
    
    ambientTemperature = Atmosphere(ConvAndConst.HydrogenTankConstants.minOperatingAltitude).temperature[0]

    allowedBoilOffMassPerTank = (ConvAndConst.HydrogenTankConstants.boilOff * Params.ClassIWEParameters.WF / ConvAndConst.g) / ConvAndConst.HydrogenTankConstants.numberOfTanks

    allowedHeatExchange = allowedBoilOffMassPerTank * ConvAndConst.HydrogenTankConstants.specificHeatHydrogen * abs(ConvAndConst.HydrogenTankConstants.temperatureGH2 - ConvAndConst.HydrogenTankConstants.temperatureLH2)

    allowedHeatFlux = allowedHeatExchange / Params.flightTime         # assume constant boil-off

    return allowedHeatFlux, ambientTemperature

def insulationThickness(Params, ConvAndConst):
    """
    Based on a thesis from Verstraete.

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    thicknessInsulation, thickness of the insulation [m]
    T1, temperature at the outer wall of the inner tank [K]
    T2, temperature at the inner wall of the outer tank [K]
    T3, temperature at the outer wall of the outer tank [K]
    T4, temperature at the outside of the insulation [K]
    """

    # Determine the heat flux per layer
    heatFluxInner = 0.15 * Params.HydrogenTankParameters.allowedHeatFlux
    heatFluxOuter = 0.15 * Params.HydrogenTankParameters.allowedHeatFlux
    heatFluxVacuum = 0.1 * Params.HydrogenTankParameters.allowedHeatFlux
    heatFluxInsulation = 0.5 * Params.HydrogenTankParameters.allowedHeatFlux
    heatFluxExternal = 0.1 * Params.HydrogenTankParameters.allowedHeatFlux

    # Determine the thermal resistance for the two walls by conduction
    thermalResistanceInner = Params.HydrogenTankParameters.finalThicknessInner / (ConvAndConst.HydrogenTankConstants.thermalConductivityInner * Params.HydrogenTankParameters.surfaceAreaInnerTank)
    thermalResistanceOuter = Params.HydrogenTankParameters.finalThicknessOuter / (ConvAndConst.HydrogenTankConstants.thermalConductivityOuter * Params.HydrogenTankParameters.surfaceAreaOuterTank)

    # Determine the temperature at the outer wall of the inner tank (Conduction)
    deltaTemp1 = heatFluxInner * thermalResistanceInner
    T1 = ConvAndConst.HydrogenTankConstants.temperatureLH2 + deltaTemp1

    # Determine the temperature at the inner wall of the outer tank (Radiation)
    T2 = ((heatFluxVacuum / (ConvAndConst.HydrogenTankConstants.emissivityWallMaterial * ConvAndConst.StefanBoltzmannConstant * Params.HydrogenTankParameters.surfaceAreaInnerTank)) + T1 ** 4) ** (1 / 4)

    # Determine the temperature at the outer wall of the outer tank (Conduction)
    deltaTemp3 = heatFluxOuter * thermalResistanceOuter
    T3 = T2 + deltaTemp3

    # Determine the temperature at the outside of the insulation (Radiation)
    T4 = (Params.HydrogenTankParameters.ambientTemperature ** 4 - (heatFluxExternal / (ConvAndConst.HydrogenTankConstants.emissivityInsulation * ConvAndConst.StefanBoltzmannConstant * Params.HydrogenTankParameters.surfaceAreaOuterTank))) ** (1 / 4)

    # Determine the thermal resistance and thickness for the insulation (Conduction)
    thermalResistanceInsulation = (T4 - T3) / heatFluxInsulation
    thicknessInsulation = ConvAndConst.HydrogenTankConstants.thermalConductivityInsulationAerogel * Params.HydrogenTankParameters.surfaceAreaOuterTank * thermalResistanceInsulation

    return thicknessInsulation, T1, T2, T3, T4

def determineMassInsulation(Params, ConvAndConst):
    """"
    Function to calculate the mass of the insulation.

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    massInsulation, Mass of the insulation [kg]
    """

    volumeExcludingInsulation =  np.pi * Params.HydrogenTankParameters.finalRadiusOuter ** 2 * Params.HydrogenTankParameters.lengthCylinder + 4 / 3 * np.pi * Params.HydrogenTankParameters.finalRadiusOuter ** 2 * Params.HydrogenTankParameters.finalRadiusOuter                    #volume cylinder plus volume sphere
    volumeIncludingInsulation = np.pi * (Params.HydrogenTankParameters.finalRadiusOuter + Params.HydrogenTankParameters.thicknessInsulation) ** 2 * Params.HydrogenTankParameters.lengthCylinder + 4/3 * np.pi * (Params.HydrogenTankParameters.finalRadiusOuter + Params.HydrogenTankParameters.thicknessInsulation) ** 2 * Params.HydrogenTankParameters.finalRadiusOuter

    volumeInsulationMaterial = volumeIncludingInsulation - volumeExcludingInsulation
    massInsulation = volumeInsulationMaterial * ConvAndConst.HydrogenTankConstants.insulationDensityAerogel

    return massInsulation

def HydrogenTankWeightEstimation(Params, ConvAndConst):
    """
    Function to calculate the weight of the hydrogen tank(s).

    Inputs:
    -----
    Params, class of design parameters
    UnitConversion, class containing unit conversions and constants

    Outputs:
    -----
    tankWeight, total weight of the hydrogen tanks, including a mounting penalty [N]  
    """

    # Get burst pressures of inner and outer tank
    Params.HydrogenTankParameters.burstPressureInnerTank, Params.HydrogenTankParameters.burstPressureOuterTank = getPressureDifferenceInnerAndOuterTank(ConvAndConst)

    # Get volume of hydrogen tank required
    Params.HydrogenTankParameters.requiredVolumeTotal, Params.HydrogenTankParameters.requiredVolumePerTank = TankVolumeDetermination(Params, ConvAndConst)

    # Get tank geometry
    Params.HydrogenTankParameters.finalRadiusInner, Params.HydrogenTankParameters.availableVolumePerTank, Params.HydrogenTankParameters.lengthCylinder = TankGeometry(Params, ConvAndConst)

    # Get tank thicknesses
    Params.HydrogenTankParameters.finalThicknessInner, Params.HydrogenTankParameters.finalThicknessOuter = thicknessCalculation(Params, ConvAndConst)

    # Calculate tank mass
    tankMassInnerTank, Params.HydrogenTankParameters.surfaceAreaInnerTank, tankMassOuterTank, Params.HydrogenTankParameters.surfaceAreaOuterTank = calculateTankMass(Params, ConvAndConst)

    # Determine allowed heat flux
    Params.HydrogenTankParameters.allowedHeatFlux, Params.HydrogenTankParameters.ambientTemperature = determineAllowedHeatFlux(Params, ConvAndConst)
    
    # Calculate insulation thickness
    Params.HydrogenTankParameters.thicknessInsulation, T1, T2, T3, T4 = insulationThickness(Params, ConvAndConst)

    # Determine insulation mass
    massInsulation = determineMassInsulation(Params, ConvAndConst)

    # Calculate overall Hydrogen tank weight
    totalMassTankPerTank = 1.02 * (tankMassInnerTank + tankMassOuterTank + massInsulation) # Accounts for 2% weight penalty with mounting
    totalMass = totalMassTankPerTank * ConvAndConst.HydrogenTankConstants.numberOfTanks # [kg]
    tankWeight = totalMass * ConvAndConst.g # [N]

    return tankWeight