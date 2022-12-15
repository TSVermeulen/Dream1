""""
Program to estimate preliminary C.G. excursion that is taken from adsee 1

Based on:
Adsee I slides and some papers for mass fractions targeted towards blended wing
Paper 1:
Structural mass prediction in conceptual design of
blended-wing-body aircraft
Wensheng ZHU, Zhouwei FAN, Xiongqing YU

Author: Rasa
"""
import numpy as np


# hydrogen tanks should have have no fuel. LH2 weight alone is W_fuel
def Xi_into_Wrt_MAC(Xi, lemac, mac):
    return None


""" Wing components must have distance specified with respect to MAC (example, 0.4 mac, -0.25mac) """

# wing_components = np.array([[W_wing, xi_wing], [W_wing_engines, xi_wing_engines]])
""" Fuselage components must have distance with respect to fuselage nose (0.5l_fuselage , 0.4 lfuselage) """
# fuselage_components = np.array([[W_landing_gear, xi_landing_gear], [W_vertical_stabiliser, xi_vertical_stabiliser],
#                                 [ W_engine, xi_engine], [ W_fuselage, xi_fuselage] , [W_engine_duct,xi_engine_duct],
#                                 [W_hydrogen_tanks, xi_hydrogen_tanks],[ W_fuel_cells, xi_fuel_cells]])
#wing , engine
# wing_components = np.array([[0.0991, 0.4], [W_wing_engines, 0.7]])
# fuselage , vertical tail, engine duct , hydrogen tank, fuel cells
# wing_components = np.array([[
#

#xLEMAC = None


"""Using computed masses, if xLEMAC is none, the program will take adsee estimates, if the value is specified, then it 
    will calculate cg with the given xLemac """


def x_empty_operating_weight_class_II(wing_components, fuselage_components, MAC:float, xLEMAC, l_fuselage, xoew_aircraft_wrt_mac):
    # sum_Wi_total =
    sum_Wi_wing = np.zeros(wing_components.shape[0])
    sum_Wi_fuselage = np.zeros(fuselage_components.shape[0])
    sum_Wi_times_Xi_wing = np.zeros(wing_components.shape[0])
    sum_Wi_times_Xi_fuselage = np.zeros(fuselage_components.shape[0])

    for i in range(wing_components.shape[0]):
        sum_Wi_wing[i] = wing_components[i][0]
        sum_Wi_times_Xi_wing[i] = wing_components[i][0] * (wing_components[i][1] * MAC)

    for j in range(fuselage_components.shape[0]):
        sum_Wi_fuselage[j] = fuselage_components[j][0]
        sum_Wi_times_Xi_fuselage[j] = fuselage_components[j][0] * (fuselage_components[j][1] * l_fuselage)

    sum_Wi_Xi_wing = np.sum(sum_Wi_times_Xi_wing)
    #print(sum_Wi_Xi_wing)
    sum_Wi_Xi_fuselage = np.sum(sum_Wi_times_Xi_fuselage)
    #print(sum_Wi_Xi_fuselage)
    print(sum_Wi_Xi_wing)
    print("the above is a test")
    sum_Wi_wing = np.sum(sum_Wi_wing)
    sum_Wi_fuselage = np.sum(sum_Wi_fuselage)

    x_cg_wing = sum_Wi_Xi_wing / sum_Wi_wing
    x_cg_wing_over_c = x_cg_wing / MAC
    print(x_cg_wing_over_c)
    x_cg_fuselage = sum_Wi_Xi_fuselage / sum_Wi_fuselage
    sum_Wi_total = sum_Wi_wing + sum_Wi_fuselage

    if xLEMAC is None:
        xlemac = x_cg_fuselage + MAC * (x_cg_wing_over_c * (sum_Wi_wing / sum_Wi_fuselage) - xoew_aircraft_wrt_mac * (
                    1 + (sum_Wi_wing / sum_Wi_fuselage)))
        x_cg_operating_empty = xlemac + MAC * xoew_aircraft_wrt_mac
        #print("xlemac" , xlemac)

    else:
        x_cg_wing_wrt_fuselage = xLEMAC + x_cg_wing
        x_cg_operating_empty = ((x_cg_wing_wrt_fuselage * sum_Wi_wing) + (
                    x_cg_fuselage * sum_Wi_fuselage)) / sum_Wi_total
        #print("x_cg_wing", x_cg_wing_wrt_fuselage)
        x_ac = 0.4 * 10.2075 + 0.6 * ( 0.25*MAC + xLEMAC)
        #print("x_cg_operating_empty", x_cg_operating_empty, "wrt fus", x_cg_operating_empty/l_fuselage , "ac averaged", (0.4 * 9.015767153 + 0.6 * ( 0.25*MAC+xLEMAC)) )



    return x_cg_operating_empty/l_fuselage


# xoew_aircraft_wrt_mac = 0.2 #ignore
# l_fuselage = 27.6
# l_eng = 2.75
# n_eng_fus = 7
# n_eng_wing = 4
# M_nacelle = 50.4
# M_eng = 426.9
# M_motor = M_eng-M_nacelle

# xi_cg_wrt_eng = ((0.4*l_eng*M_nacelle + 0.6*l_eng*M_motor)/(M_motor+M_nacelle)) / (l_eng) #fraction

# MAC_w = 7.476994637
# LE_sweep = 51.95731491 # deg
# y_mac = (MAC_w - 8.592)*((8.787)/(8.592 *(-1+(3.660/8.592))) ) + 9.213

# MAC_v = 3.1435932
# b_v = 5.72688109
# y_mac_v = 1.34750143
# sweep_v = 55.72420769


# X_ac_fuselage = 9.015767153

# M_wing = 5105.38699 # kg
# M_vertical_tail = 1793.463043 # kg
# M_eng_w = 4 * M_eng

# xi_wing = 0.25 #of MAC
# xi_vertical_tail = (np.tan(np.radians(LE_sweep))*(18 - y_mac)+0.42*MAC_v + y_mac_v*np.tan(np.radians(sweep_v)))/MAC_w
# xi_engines_mac = (0.7*8.592 - np.tan(np.radians(LE_sweep))*(y_mac - 9.213))/MAC_w #engine cg location is 0.7 kink chord need to find wrt mac

# wing_components = np.array([[M_wing, xi_wing], [M_vertical_tail, xi_vertical_tail],  [M_eng_w, xi_engines_mac]])


# M_eng_f = 7 * M_eng
# M_fuselage = 9382.76102 + 15844.14706 # kg
# M_fuel_tank_1 = 1053.2819 #1032.586 # kg
# M_fuel_tank_2 = 1053.2819 #1032.586 # kg
# M_fuel_tank_3 = 8531.4546#8364.182

# #kg
# M_fuel_cells = 344 * 42 #kg
# M_sys_eq = 9227.222003
# M_operating_items = 555.6506533

# xi_cg_eng_fus = (0.7*l_fuselage+xi_cg_wrt_eng*l_eng)/l_fuselage #fraction
# xi_fuselage = ((0.4*24.77866861)+(l_fuselage - 24.77866861 ))/l_fuselage
# #print("xi_cg_eng_fus:", xi_cg_eng_fus*l_fuselage, "xi_fuselage:", xi_fuselage*l_fuselage)
# xi_fuel_tank_1 = 18.1544/l_fuselage
# xi_fuel_tank_2 = 18.1544/l_fuselage
# xi_fuel_tank_3 = 23.6430/l_fuselage
# """CHANGE THIS"""
# xi_fuel_cells = 10.11/l_fuselage
# xi_sys_eq = 0.4
# xi_operating_items = 0.4

#fuselage_components = np.array([[M_eng_f, xi_cg_eng_fus], [M_fuselage, xi_fuselage], [M_fuel_tank_3, xi_fuel_tank_3], [M_fuel_tank_2, xi_fuel_tank_2], [M_fuel_tank_1, xi_fuel_tank_1], [M_fuel_cells, xi_fuel_cells], [M_sys_eq, xi_sys_eq], [M_operating_items, xi_operating_items]])
""" CHANGE THIS """
#xLEMAC = 19#
#print("ymac", y_mac)
#print("mac", MAC_w)

#print("lemac offset from root", np.tan(np.radians(LE_sweep)*(y_mac-6.284)),",", 15.369+np.tan(np.radians(LE_sweep)*(y_mac-6.284)) ," >lemac >" , 10.039+ np.tan(np.radians(LE_sweep)*(y_mac-6.284)))



#xi_cg = x_empty_operating_weight_class_II(wing_components, fuselage_components, MAC_w, xLEMAC, l_fuselage, xoew_aircraft_wrt_mac)
#print(xi_cg)

def cg_excursion_classII(W_fuel, x_cg_fuel, W_operating_empty, X_cg_operating_empty, W_payload, X_cg_payload, l_fuselage):

    W_x_fuel = W_fuel*(x_cg_fuel*l_fuselage)
    W_x_operating_empty = W_operating_empty * X_cg_operating_empty*l_fuselage
    W_x_payload = W_payload*(X_cg_payload*l_fuselage)

    x_cg_oe_fuel = (W_x_fuel + W_x_operating_empty)/(W_fuel + W_operating_empty)
    x_cg_oe_payload = (W_x_payload + W_x_operating_empty)/(W_payload + W_operating_empty)
    x_cg_all = (W_x_payload + W_x_operating_empty + W_x_fuel)/(W_payload + W_operating_empty + W_fuel)
    #print(W_x_fuel, W_x_operating_empty,  W_x_payload)
    x_cg_excursion = [x_cg_all, x_cg_oe_payload, x_cg_oe_fuel]
    #print("all cg:", x_cg_all, ", x_cg w payload:", x_cg_oe_payload, ", x_cg w fuel:", x_cg_oe_fuel, ", xcf original:", X_cg_operating_empty*l_fuselage)
    forward_cg = min(x_cg_excursion)
    aft_cg = max(x_cg_excursion)

    return forward_cg, x_cg_all, aft_cg, X_cg_operating_empty*l_fuselage

# l_fuselage = 38.03835218

# M_fuel = 5649.030295
# x_cg_fuel = ((M_fuel_tank_1*xi_fuel_tank_1+M_fuel_tank_2*xi_fuel_tank_2+M_fuel_tank_3*xi_fuel_tank_3)/(M_fuel_tank_3+M_fuel_tank_2+M_fuel_tank_1))
# #print("fuel:", x_cg_fuel*l_fuselage)
# M_operating_empty = 806265.7296/9.80665
# X_cg_operating_empty = xi_cg #25.02334592/l_fuselage
# M_payload = 154454.7375/9.80665
# X_cg_payload = 0.45

# forward_cg, x_cg_all, aft_cg, x_cg_i= cg_excursion_classII(M_fuel, x_cg_fuel, M_operating_empty, X_cg_operating_empty, M_payload, X_cg_payload, l_fuselage)
#
#print(forward_cg, x_cg_all, aft_cg , x_cg_i)
#print("Margin:" , (0.4 * 9.015767153 + 0.6 * ( 0.25*MAC_w+xLEMAC)) - aft_cg )
#
# def loading_diagram(n_passengers, m_passenger, isle_configuration, number_of_rows, w_fuel, cargo_compartments, ):
#     #front_to_back
#
#     #back_to_front
#
#     return None


#, 590 all aircraft , 318 wing only

# 48 t
# L = W  L = 1/2 * rho * V^2 * S * cl at sea level 99.14 knots max cl
# rho ar cruise = 0.364805 cl = 0.2481 236.154

