import math

import numpy as np
import scipy as sc
import matplotlib.pyplot as plt
import Crosssectionfitter as csf
import FuselageFunctionsV2 as FP
import DesignIteration.WingBoxLoadingNew as WBL
import cg_range_longitudinal as cg


"Fuselage Design Parameters (Cross section)"

"Assumed is that all parts of the fuselage cross section behave as "

"For the paramaters below refer to the fuselage cross section drawing"
h = csf.height
El_major = 8.568054  # [m] major axis of the ellipse
El_minor = 4.2  # [m] minor axis of the ellipse
El_height = 0.622402  # [m] height of the ellipse from the floor

radius_top_arc = csf.radius_top_arc  # [m] Radius of top skin
centre_top_arc_ = csf.centre_top_arc  # [m] distance from the floor to the circle for the top skin
radius_side_arc = csf.radius_side_arc  # [m] Radius of side skin
centre_side_arc = csf.centre_side_arc  # [m] distance from the floor to the circle for the side skin
radius_bottom_arc = csf.radius_bottom_arc  # [m] Radius of bottom skin
centre_bottom_arc = csf.centre_bottom_arc  # [m] distance from the floor to the circle for the bottom skin

theta1side = csf.theta_1_side
theta2side = csf.theta_2_side
theta1floor = csf.theta_1_floor
theta2floor = csf.theta_2_floor
theta1ceiling = csf.theta_1_ceiling
theta2ceiling = csf.theta_2_ceiling

beta = csf.angle_ceiling_skin  # [degrees] angle between the ceiling and the fuselage skin in Top Node
gamma = csf.alpha  # [degrees] angle between the floor and the wall
epsilon = csf.angle_floor_skin  # [degrees] angle between the floor and the fuselage skin in Bottom Node
floorwidth = csf.length_floor  # [m] Width of the floor
ceilingwidth = csf.length_ceiling  # [m] Width of the ceiling
cabinlength = 14  # [m] length of the passenger cabin
fuselagelength = 27.6  # [m] length of the fuselage
walllength = csf.length_wall

Cabinstart = 0
CabinEnd = 15

"Determined by requirements"
cabinPressureHeight = 2500  # [m] Pressure cabin height
maximumAltitude = 11000  # [m] Maximum operating altitude
PAXcount = 150
PAXweight = 105
Weight_furnish = 1000  # [kg]
Fz_passenger=FP.PassengerLoads(PAXcount,PAXweight)+Weight_furnish*9.81

"Needed constants"
gravity = 9.81  # [m/s2]

"Wing lift distribution"
BmWing = -WBL.UpwardMomentFunctionBodyAxis(WBL.y)[0]
Lift_wing =2*WBL.NormalShearFunctionBodyAxis(WBL.y)[0]
Torsional_moment_wing = -WBL.TorqueFunctionBodyAxis(WBL.y)[0]
y=np.arange(0,WBL.halfWidthFuselage,0.1)
Lift_fuselage=2*WBL.GetShearDistribution(y, WBL.dataLift, WBL.dataDrag, WBL.span, WBL.engineSpan, WBL.totalWeightEngines, WBL.totalThrust, WBL.landingGearWeight, WBL.landingGearSpanwiseLocation, WBL.weightPerVerticalWingTip, WBL.numberOfLoadCase)[2]
Lift_

"Wingbox system"
Wingbox_centre = 15.5  # [m]
Wingbox_leading_x = 0.1*fuselagelength  # [m]
Wingbox_trailing_x = 0.7*fuselagelength  # [m]
fuselagewingconnection = Wingbox_trailing_x-Wingbox_leading_x  # [m] length of the connection between the "fuselage" and the "wing"

"Landing gear configuration"
Landing_gear_nose_weight = 391  # [kg]
Landing_gear_nose_position = 2  # [m] Position from the nose of the aircraft
Landing_gear__nose_longitudinal_length = 0.5  # [m]

Landing_gear_main_weight = 3682
Landing_gear_main_position = 15
Landing_gear_main_longitudinal_length = 0.5

"Propulsion system"
Propulsion_weight = 7/11*26296  # [kg]
Propulsion_position_x = 15  # [m]
Propulsion_length = 2.08  # [m]

"Cargo bay"
Cargobay_start=0 #[m]
Cargobay_length=7. #[m]
CargobayWeight = 1000 #[kg]

"Fuel Cell"
Fuelcell_start=0.582
Fuelcell_end=10.47
Fuelcell_weight=10000 #[kg]

"Fuel Tank"
Fuel_tank_weight_1 = 1032 #[kg]
x_fuel_tank_1 = 18.1544 #[m]
x_fuel_tank_1_end = x_fuel_tank_1 + 1
Fuel_tank_weight_2 = 1032 #[kg]
x_fuel_tank_2 = 18.1544 #[m]
x_fuel_tank_2_end = x_fuel_tank_2 + 1
Fuel_tank_weight_3 = 8364 #[kg]
x_fuel_tank_3 = 23.643
x_fuel_tank_3_end = x_fuel_tank_3 + 1

"Structural weight"
Structure_weight= 9382+15844 #[kg] assumed from class II weight estimation and iteration

"Stiffener inputs"
yield_stiffener = 503 * 10 ** 6
poisson_stiffener = 0.334
E_stiffener = 72 * 10 ** 9

"12 and 56"
t_12_stiffener=2 *10**(-3)
b_12_stiffener=20 *10**(-3)
C_12=0.425
A_12=t_12_stiffener*b_12_stiffener

"23 and 45"
t_23_stiffener=2 *10**(-3)
b_23_stiffener=35 *10**(-3)
C_23=4
A_23=t_23_stiffener*b_23_stiffener

"34"
t_34_stiffener=2 *10**(-3)
b_34_stiffener=20 *10**(-3)
C_34=4
A_34=t_34_stiffener*b_34_stiffener

A_stiffener_trimmed= 2 * A_12 + 2 * A_23 + A_34
A_stiffener=A_stiffener_trimmed+2*t_12_stiffener*t_23_stiffener+2*t_23_stiffener*t_34_stiffener
C_skin=6.98

"Iteration Inputs/Outputs"
"Materialproperties"
E_face = 73 * 10 ** 9  # [Pa] Youngs modulus
fatiguestrength_face = 138 * 10 ** 6  # [Pa] ALU 2024
j = 1.3  # Safetyfactor
density = 2780
rho_face = 2780
poisson_face = 0.33

E_core = 0.54 * 10 ** 6  # [Pa]
G_core = 84 * 10 ** 6  # [Pa]
rho_core = 200
cell_size_core = 3.2 * 10 ** (-3)
poisson_core = 0.389

t_face_wall = 0.5 * 10 ** (-3)  # m
t_core_wall = 4 * 10 ** (-3)  # m

t_face_floor = 4 * 10 ** (-3)  # m
t_core_floor = 25 * 10 ** (-3)  # m

t_core_ceiling = 10 * 10 ** (-3)  # m
t_face_ceiling = 3 * 10 ** (-3)  # m


pitch_stringer = 0.4 #[m]
t_smeared_stringer = A_stiffener / pitch_stringer

Area_frame = 0
frame_spacing = 1
t_smeared_frame = Area_frame / frame_spacing

t_skin = 1.5 * 10 ** (-3)  # m
E_skin = E_face
yield_skin= fatiguestrength_face
poisson_skin=0.334

tshell = t_skin + t_smeared_frame + t_smeared_stringer

weight_structure = 10000  # kg

t_floor_smeared = 2 * t_face_floor + t_core_floor
t_ceiling_smeared = 2 * t_face_ceiling + t_core_ceiling
t_top_arc_smeared = tshell  # [m]
t_side_arc_smeared = tshell  # [m]
t_bottom_arc_smeared = tshell  # [m]
t_wall_smeared = t_core_wall + 2 * t_face_wall  # [m]

"Load factor requirements"
nload = 2.5

"Calculating smeared thicknesses"
t_side_arc_wall_smeared = FP.smear([t_side_arc_smeared, t_wall_smeared],
                                   [FP.arclength(radius_side_arc, theta1side, theta2side), walllength])
t_to_smear = np.array([
    t_wall_smeared, t_ceiling_smeared, t_floor_smeared, t_side_arc_smeared, t_side_arc_smeared, t_top_arc_smeared,
    t_bottom_arc_smeared])
l_to_smear = np.array([
    walllength, ceilingwidth, floorwidth, FP.arclength(radius_side_arc, theta1side, theta2side),
    FP.arclength(radius_side_arc, theta1side, theta2side), FP.arclength(
        radius_top_arc, theta1ceiling, theta2ceiling), FP.arclength(radius_bottom_arc, theta1floor, theta2floor)])
t_smear = FP.smear(t_to_smear, l_to_smear)

"Calculating structural component properties"
Iyywall, zwall = FP.Areamomentwalls(t_wall_smeared, walllength, np.radians(-gamma), 0.5 * csf.height)
Iyyfloor = 1 / 12 * floorwidth * t_floor_smeared ** 3
Iyyceiling = 1 / 12 * ceilingwidth * t_ceiling_smeared ** 3
IyyArcside, z_side_arc = FP.Areamomentarc(theta1side, theta2side, radius_side_arc, centre_side_arc, tshell)
IyyArctop, z_top_arc = FP.Areamomentarc(theta1ceiling, theta2ceiling, radius_top_arc, centre_top_arc_, tshell)
IyyArcbot, z_bot_arc = FP.Areamomentarc(theta1floor, theta2floor, radius_bottom_arc, centre_bottom_arc, tshell)

"calculating the cg of the fuselage cross section"
zdA = zwall * t_wall_smeared * walllength * 2 + t_ceiling_smeared * csf.height * ceilingwidth + np.pi * tshell * (
        tshell + El_major + El_minor) * El_height
dA = t_wall_smeared * walllength * 2 + t_ceiling_smeared * ceilingwidth + t_floor_smeared * floorwidth + np.pi * tshell * (
        tshell + El_major + El_minor)
ztilde = zdA / dA

"Calculating section properties"
Iyy_wall_steiner = FP.steiner(t_wall_smeared * walllength, zwall - ztilde)
Iyy_floor_steiner = FP.steiner(t_floor_smeared * floorwidth, 0 - ztilde)
Iyy_ceiling_steiner = FP.steiner(t_ceiling_smeared * ceilingwidth, csf.height - ztilde)
Iyy_arc_side_steiner = FP.SteinerArc(theta1side, theta2side, tshell, radius_side_arc, z_side_arc - ztilde)[1]
Iyy_arc_top_steiner = FP.SteinerArc(theta1ceiling, theta2ceiling, tshell, radius_top_arc, z_top_arc - ztilde)[1]
Iyy_arc_bot_steiner = FP.SteinerArc(theta1floor, theta2floor, tshell, radius_bottom_arc, z_bot_arc - ztilde)[1]

Iyy = 2 * (Iyywall + Iyy_wall_steiner) + \
      Iyyfloor + Iyy_floor_steiner + \
      Iyy_ceiling_steiner + Iyy_ceiling_steiner + \
      IyyArcbot + Iyy_arc_bot_steiner + \
      2 * (IyyArcside + Iyy_arc_side_steiner) + \
      IyyArctop + Iyy_arc_top_steiner

"Retrieving loads from Wingboxloading"
"Calculating the normal forces introduced by the wing bending"
Flat = BmWing / csf.height / fuselagewingconnection

"Calculating the axial forces in the trapezoidal structure"
pressure_difference = FP.getMaximumPressureDifference(maximumAltitude, cabinPressureHeight)
Fw, Fc, Fw2, Ff = FP.Nodeanalysis(beta, gamma, epsilon, pressure_difference, radius_top_arc, radius_side_arc,
                                  radius_bottom_arc)
F_floor_normal = Ff - Flat * nload
F_ceiling_normal = Fc + Flat * nload
F_wall_normal = Fw

"Loading over fuselage length"
res = 0.01  # resolution of the loading distribution in longtidunal direction
x = np.arange(0,fuselagelength/res).astype(int)
Fz = np.zeros(len(x))

"Forces over fuselage length"
FP.xdistributor(Fz, Landing_gear_nose_weight * 9.81, Landing_gear_nose_position, Landing_gear_nose_position + Landing_gear__nose_longitudinal_length, res)
FP.xdistributor(Fz,CargobayWeight*9.81,Cargobay_start,Cargobay_start+Cargobay_length,res)
FP.xdistributor(Fz,Fuelcell_weight*9.81,Fuelcell_start,Fuelcell_end,res)
FP.xdistributor(Fz,Fz_passenger,Cabinstart,CabinEnd,res)
qfloor=np.max(Fz)/floorwidth
FP.xdistributor(Fz,Landing_gear_main_weight*9.81,Landing_gear_main_position,Landing_gear_main_position+Landing_gear_main_longitudinal_length
                ,res)
FP.xdistributor(Fz,Structure_weight*9.81,0,fuselagelength,res)
FP.xdistributor(Fz,Fuel_tank_weight_1*9.81,x_fuel_tank_1,x_fuel_tank_1_end,res)
FP.xdistributor(Fz,Fuel_tank_weight_2*9.81,x_fuel_tank_2,x_fuel_tank_2_end,res)
FP.xdistributor(Fz,Fuel_tank_weight_3*9.81,x_fuel_tank_3,x_fuel_tank_3_end,res)
# FP.xdistributor(Fz,Propulsion_weight*9.81,Propulsion_position_x,Propulsion_position_x+Propulsion_length,res)
MTOW_check=np.sum(Fz)/9.81
print("Sanity check for MTOW:" , np.sum(Fz)/9.81, "kg")
# Lift_fuselage=-0.6*MTOW_check*9.81
# Lift_wing=-0.4*MTOW_check*9.81
FP.xdistributor(Fz,Lift_fuselage,0,fuselagelength,res)
FP.xdistributor(Fz,Lift_wing,Wingbox_leading_x,Wingbox_trailing_x,res)
plt.plot(x,Fz)
plt.show


"Shear stresses over fuselage length"
Vz = np.zeros(len(x))
for i in x:
    Vz[i] = Vz[i - 1] + Fz[i]

"Longitudinal bending moment"

interpolation=sc.interpolate.interp1d(x,Vz)
My=np.zeros(len(x))
for i in x:
    if i<1:
        My[i:]=sc.integrate.quad(interpolation,0,i,limit=1000)[0]
    else:
        My[i:]+=sc.integrate.quad(interpolation,i-1,i,limit=1000)[0]
    print(i)

# for i in x:
#     for j in range(0,i):
#         My[i] += Fz[j]*(x[i]-x[j])*res
#         # print(i,j,Fz[j],(x[i]-x[j]))

"Calculating shear flows over the longitudinal direction"
q1 = FP.shear(0, Vz, Iyy, radius_top_arc, t_top_arc_smeared, 0, theta2ceiling)
q2 = q1 - FP.shear(0, Vz, Iyy, radius_side_arc, t_side_arc_wall_smeared, theta1side, theta2side)
q3 = q2 - FP.shear(0, Vz, Iyy, radius_bottom_arc, t_bottom_arc_smeared, theta1floor, np.pi)

"Calculating shear stresses over the longitudinal direction"
Tau_hoop_long_top = q1 / t_top_arc_smeared
Tau_hoop_long_bottom = q3 / t_bottom_arc_smeared
Tau_hoop_long_side_arc = q2 * t_side_arc_smeared / t_side_arc_wall_smeared ** 2
Tau_lat_long_wall = q2 * t_wall_smeared / t_side_arc_wall_smeared ** 2

"Checking stresses in trapezoidal structure components"
"Floor"
SigmaF_lat_floor = F_floor_normal / (2 * t_face_floor) - FP.Lateralbeammoment(qfloor,
                                                                              floorwidth) * t_floor_smeared / 2 / (
                           1 / 12 * t_floor_smeared ** 3)
SigmaF_lon_floor = FP.Longitudinal_normal(My, -ztilde, Iyy, t_smear) / (2 * t_face_floor)

Von_mises_floor = FP.vonMises(SigmaF_lat_floor, SigmaF_lon_floor, 0)

Dimpling_Floor = FP.DimplingLoad(E_face, t_face_floor, poisson_face, poisson_core, cell_size_core)
Crimpling_Floor = FP.CrimnplingLoad(t_core_floor, G_core)
Wrinkling_Floor = FP.Wrinklingload(E_face, E_core, G_core)
Global_Floor = FP.GlobalBucklingLoad(t_core_floor, t_face_floor, G_core, E_face, floorwidth)
print("Von mises floor: ", abs(np.max(Von_mises_floor)) * 10 ** (-6), abs(np.min(Von_mises_floor)) * 10 ** (-6),
      fatiguestrength_face * 10 ** (-6))
print("Dimpling load floor: ", Dimpling_Floor - abs(F_floor_normal))
print("Crimpling load floor: ", Crimpling_Floor - abs(F_floor_normal))
print("Wrinkling load floor", Wrinkling_Floor - abs(F_floor_normal))
print("Global load floor: ", Global_Floor)
print("")

"Ceiling"
qceiling = 0
SigmaF_lat_ceiling = F_ceiling_normal / (2 * t_face_ceiling) - FP.Lateralbeammoment(qceiling,
                                                                                    ceilingwidth) * t_ceiling_smeared / 2 / (
                             1 / 12 * t_ceiling_smeared ** 3)
SigmaF_lon_ceiling = FP.Longitudinal_normal(My, csf.height - ztilde, Iyy, t_smear) / (2 * t_face_ceiling)
Von_mises_ceiling = FP.vonMises(SigmaF_lat_ceiling, SigmaF_lon_ceiling, 0)

Dimpling_Ceiling = FP.DimplingLoad(E_face, t_face_ceiling, poisson_face, poisson_core, cell_size_core)
Crimpling_Ceiling = FP.CrimnplingLoad(t_core_ceiling, G_core)
Wrinkling_Ceiling = FP.Wrinklingload(E_face, E_core, G_core)
Global_Ceiling = FP.GlobalBucklingLoad(t_core_ceiling, t_face_ceiling, G_core, E_face, ceilingwidth)

print("Von mises Ceiling: ", abs(np.max(Von_mises_ceiling)) * 10 ** (-6), abs(np.min(Von_mises_ceiling)) * 10 ** (-6),
      fatiguestrength_face * 10 ** (-6))
print("Dimpling load Ceiling: ", Dimpling_Ceiling - abs(F_ceiling_normal))
print("Crimpling load Ceiling: ", Crimpling_Ceiling - abs(F_ceiling_normal))
print("Wrinkling load Ceiling", Wrinkling_Ceiling - abs(F_ceiling_normal))
print("Global load Ceiling: ", Global_Ceiling)
print("")
"Walls"
SigmaF_lat_wall = F_wall_normal / (2 * t_face_wall)
SigmaF_lon_wall_1 = FP.Longitudinal_normal(My, csf.height - ztilde, Iyy, t_smear) / (2 * t_face_wall)
SigmaF_lon_wall_2 = FP.Longitudinal_normal(My, -ztilde, Iyy, t_smear) / (2 * t_face_wall)

Von_mises_wall_1 = FP.vonMises(SigmaF_lat_wall, SigmaF_lon_wall_1, Tau_lat_long_wall)
Von_mises_wall_2 = FP.vonMises(SigmaF_lat_wall, SigmaF_lon_wall_2, Tau_lat_long_wall)

Dimpling_wall = FP.DimplingLoad(E_face, t_face_ceiling, poisson_face, poisson_core, cell_size_core)
Crimpling_wall = FP.CrimnplingLoad(t_core_ceiling, G_core)
Wrinkling_wall = FP.Wrinklingload(E_face, E_core, G_core)
Global_wall = FP.GlobalBucklingLoad(t_core_ceiling, t_face_ceiling, G_core, E_face, ceilingwidth)

print("Von mises wall_1: ", abs(np.max(Von_mises_wall_1)) * 10 ** (-6), abs(np.min(Von_mises_wall_1)) * 10 ** (-6),
      fatiguestrength_face * 10 ** (-6))
print("Von mises wall_2: ", abs(np.max(Von_mises_wall_2)) * 10 ** (-6), abs(np.min(Von_mises_wall_2)) * 10 ** (-6),
      fatiguestrength_face * 10 ** (-6))
print("Dimpling load wall: ", Dimpling_wall - abs(F_wall_normal))
print("Crimpling load wall: ", Crimpling_wall - abs(F_wall_normal))
print("Wrinkling load wall", Wrinkling_wall - abs(F_wall_normal))
print("Global load wall: ", Global_wall)
print("")

"Checking buckling of the Skin"
"Buckling of the stiffeners"
B_12=FP.Buckling(C_12,yield_stiffener,E_stiffener,poisson_stiffener,t_12_stiffener,b_12_stiffener)[0]
B_23=FP.Buckling(C_23,yield_stiffener,E_stiffener,poisson_stiffener,t_23_stiffener,b_23_stiffener)[0]
B_34=FP.Buckling(C_34,yield_stiffener,E_stiffener,poisson_stiffener,t_34_stiffener,b_34_stiffener)[0]

sigma_cc_stiffener= (2*A_12*B_12+2*A_23*B_23+A_34*B_34) / A_stiffener_trimmed
P_cc_stiffener=sigma_cc_stiffener*(2*A_12+2*A_23+A_34+2*t_12_stiffener*t_23_stiffener+2*t_23_stiffener*t_34_stiffener)
effective_sheet_width=FP.Effective_sheet_width(t_skin,C_skin,poisson_stiffener,E_stiffener,sigma_cc_stiffener)
B_skin=C_skin*np.pi**2*E_skin/12/(1-poisson_skin**2)*(t_skin/pitch_stringer)**2

sigma_cc_panel= (sigma_cc_stiffener * (A_stiffener_trimmed + effective_sheet_width * t_skin * 2) + B_skin * (pitch_stringer - effective_sheet_width * 2) * t_skin) / (A_stiffener_trimmed + effective_sheet_width * t_skin * 2 + (pitch_stringer - 2 * effective_sheet_width) * t_skin)
print("Sigma_cc_panel", sigma_cc_panel/10**6)

"Calculate mass of the fuselage"
AreaCrosssection = FP.SteinerArc(theta1ceiling, theta2ceiling, tshell, radius_top_arc, z_top_arc - ztilde)[0] + \
                   2 * FP.SteinerArc(theta1side, theta2side, tshell, radius_side_arc, z_side_arc - ztilde)[0] + \
                   FP.SteinerArc(theta1floor, theta2floor, tshell, radius_bottom_arc, z_bot_arc - ztilde)[0]

Fuselageweight = AreaCrosssection * fuselagelength * density
Fuselageweight += (t_core_floor * rho_core + 2 * t_face_floor * rho_face) * floorwidth * fuselagelength
Fuselageweight += (t_core_ceiling * rho_core + 2 * t_face_ceiling * rho_face) * ceilingwidth * fuselagelength
Fuselageweight += 2 * (t_core_wall * rho_core + 2 * t_face_wall * rho_face) * ceilingwidth * fuselagelength
print("Fuselage weight: ", Fuselageweight)

