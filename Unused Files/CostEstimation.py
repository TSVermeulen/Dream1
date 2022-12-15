import numpy as np

ms_to_kts = 1.943844
lbs_to_kg = 0.45359237
km_to_nm = 0.53996

def costEstimation(Neng, Ptotmax, Dfan, Pem, Wduct):
    """
    Inputs:
    Neng, number of engines [-]
    Ptotmax, total maximum power [W]
    Dfan, fan diameter [m]
    Pem, power electric motor [W]
    Outputs:
    Total propulsion cost [$]
    """

    CPI = 1.28

    Cem = 174 * Neng * (Pem * 0.00134102) * CPI
    Cin = (Neng * (Pem /1000)) / 2.7
    Cfan = 210 * Neng * (Dfan * 0.3045) ** 2 * ((Pem * 0.00134102) / (Dfan * 0.3045)) ** 0.12
    Cfc = (Ptotmax / 1000) / 65
    Cpms = 150 * Neng * (Pem * 0.00134102) * CPI
    Ccomp = (Ptotmax / 1000) / (52 * CPI)
    Ccos = (Ptotmax / 1000) / 5
    Cduct = (Wduct * 2.68569) / 0.07 * Neng

    Ceng = Cem + Cin + Cfan + Cduct
    C1eng = Ceng / Neng

    Ctot = Cem + Cin + Cfan + Cduct + Cfc + Cpms + Ccomp + Ccos


    print("---------------")
    print("Total propulsion system cost:", Ctot, "[$]")

    return Ctot, C1eng


def estimate_design_cost(empty_weight, propulsion_weight, v_cruise, man_hour_rate):
    """
    Based on Roskam part VIII
    Inflation is not included!
    Inputs:
    mtow, maximum take-off weight [kg]
    v_cruise, design cruise velocity [m/s]
    man_hour_rate, manhour rate [$/h]

    Variables
    w_ampr, Aeronautical Manufacturers Report Weight, assumed to equal the MTOW [lbs]
    f_diff, a measure for the use of advanced tech [-]
    f_cad, measure for using CAD models at manufacturer [-]
    v_c, design cruise speed [kts]
    n_rdte, number of aircraft produced for the RDTE phase

    Outputs:
    costs_design_phase, total costs for the design phase [$]
    """
    w_ampr = (empty_weight - propulsion_weight) / lbs_to_kg
    v_c = v_cruise * ms_to_kts
    f_diff = 2
    f_cad = 0.8
    n_rdte = 5

    man_hours_design_phase = 0.0396 * w_ampr ** 0.791 + v_c ** 1.526 * n_rdte ** 0.183 * f_diff * f_cad
    costs_design_phases1970 = man_hours_design_phase * man_hour_rate
    return costs_design_phases1970, man_hours_design_phase


def estimate_certification_and_test_cost(empty_weight, propulsion_weight, v_cruise, man_hour_rate_tooling, man_hour_rate_manufacturing, cost_engine, cost_avionics):
    """
    f_mat, measure for type of materials: 2.-2.5 for conventional composites
    n_r_r, production rate per month, typical value is 0.33
    n_st, number of static aircraft (without engines, propellers and avionics)
    f_obs, factor depending on importance on having low observables (3. for stealthy aircraft)
    """

    w_ampr = (empty_weight - propulsion_weight) / lbs_to_kg
    v_c = v_cruise * ms_to_kts
    f_diff = 2
    n_rdte = 5
    f_mat = 2.5
    n_r_r = 0.33
    n_st = 0
    f_obs = 1

    man_hours_manufacturing = 28.984 * w_ampr ** 0.74 * v_c ** 0.543 * n_rdte ** 0.524 * f_diff
    manufacturing_cost_flight_test_aircraft = man_hours_manufacturing * man_hour_rate_manufacturing

    material_cost_for_flight_test_aircraft = 37.632 * f_mat * w_ampr ** 0.689 * v_c ** 0.624 * n_rdte ** 0.792

    man_hours_tooling = 4.0127 * w_ampr ** 0.764 * v_c ** 0.899 * n_rdte ** 0.178 * n_r_r ** 0.066 * f_diff
    tooling_cost = man_hours_tooling * man_hour_rate_tooling

    quality_control_cost = 0.13 * manufacturing_cost_flight_test_aircraft

    development_support_and_testing_cost = 0.008325 * w_ampr ** 0.873 * v_c ** 1.89 * n_rdte ** 0.346 * f_diff
    flight_test_aircraft_cost = (cost_engine + cost_avionics) + manufacturing_cost_flight_test_aircraft + material_cost_for_flight_test_aircraft + tooling_cost + quality_control_cost
    flight_test_operating_cost = 0.001244 * w_ampr ** 1.16 * v_c ** 1.371 * (n_rdte - n_st) ** 1.281 * f_diff * f_obs

    certification_and_test_cost = (flight_test_aircraft_cost + flight_test_operating_cost + development_support_and_testing_cost) / 0.5

    other_certification_costs = certification_and_test_cost - (flight_test_aircraft_cost + flight_test_operating_cost + development_support_and_testing_cost)

    return certification_and_test_cost, flight_test_aircraft_cost, development_support_and_testing_cost, flight_test_operating_cost, other_certification_costs


def estimate_manufacturing_cost_airframe(empty_weight, propulsion_weight, v_cruise, n_program, man_hours_design_phase, man_hour_rate):
    """
    Based on Roskam part VIII
    Inflation is not included!
    Inputs:
    mtow, maximum take-off weight [kg]
    n_program, number of aircraft produced during an aircraft program [-]
    v_cruise, design cruise velocity [m/s]
    man_hour_rate, manhour rate [$/h]
    man_hours_design_phase, previously calculated [hr]

    Variables
    w_ampr, Aeronautical Manufacturers Report Weight, assumed to equal the MTOW [lbs]
    f_diff, a measure for the use of advanced tech [-]
    f_cad, measure for using CAD models at manufacturer [-]
    v_c, design cruise speed [kts]

    Outputs:
    costs_airframe, cost for the manufacturing of the airframe [$]
    """
    w_ampr = (empty_weight - propulsion_weight) / lbs_to_kg
    v_c = v_cruise * ms_to_kts
    f_diff = 2
    f_cad = 0.8

    total_man_hours = 0.0396 * w_ampr ** 0.791 + v_c ** 1.526 * n_program ** 0.183 * f_diff * f_cad
    costs_airframe = (total_man_hours - man_hours_design_phase) * man_hour_rate

    return costs_airframe, total_man_hours


def estimate_tank_cost(totalkwh):
    """
    Outputs in $
    """
    price = 35 * totalkwh
    return price


def estimate_break_even_point(empty_weight, propulsion_weight, v_cruise, man_hour_rate_design1970, man_hour_rate_tooling1970,
                              man_hour_rate_manufacturing1970, n_total, number_of_engines, max_total_power, Wduct,
                              fan_diameter,maximum_motor_power, total_kwh, cost_avionics1970, unit_price2022, cef19702022):

    costs_design_phases1970, man_hours_design_phase = estimate_design_cost(empty_weight, propulsion_weight, v_cruise, man_hour_rate_design1970)

    costs_design_phases2022 = costs_design_phases1970 * cef19702022 * 1.3

    cost_airframe1970, total_man_hours = estimate_manufacturing_cost_airframe(empty_weight, propulsion_weight, v_cruise, n_total, man_hours_design_phase,
                                                             man_hour_rate_manufacturing1970)
    cost_airframe2022 = cost_airframe1970 * cef19702022


    cost_propulsion = costEstimation(number_of_engines, max_total_power, fan_diameter,
                                                                 maximum_motor_power, Wduct)
    cost_propulsion_system2022 = cost_propulsion[0]
    cost_engine2022 = cost_propulsion[1]

    cost_tanks2022 = estimate_tank_cost(total_kwh)

    cost_engine1970 = cost_engine2022 / cef19702022

    cost_landing_gear2022 = 1760000

    certification_and_test_cost1970, flight_test_aircraft_cost1970, development_support_and_testing_cost1970, flight_test_operating_cost1970, \
    other_certification_costs1970 = estimate_certification_and_test_cost(empty_weight, propulsion_weight, v_cruise, man_hour_rate_tooling1970, man_hour_rate_manufacturing1970, cost_engine1970, cost_avionics1970)

    certification_and_test_cost2022 = certification_and_test_cost1970 * cef19702022 * 1.3
    flight_test_aircraft_cost2022 =  flight_test_aircraft_cost1970 * cef19702022
    development_support_and_testing_cost2022 = development_support_and_testing_cost1970 * cef19702022
    flight_test_operating_cost2022 = flight_test_operating_cost1970 * cef19702022
    other_certification_costs2022 = other_certification_costs1970 * cef19702022

    total_fixed_costs2022 = costs_design_phases2022 + certification_and_test_cost2022

    manufacturing_cost2022 = (cost_airframe2022 + cost_propulsion_system2022 + cost_tanks2022 + cost_landing_gear2022) * 1.3

    unit_cost2022 = (total_fixed_costs2022 / n_total + manufacturing_cost2022)

    bep = total_fixed_costs2022 / (unit_price2022 - unit_cost2022)

    print("Airframe costs: ", cost_airframe2022,  " $")
    print("Tank costs: ", cost_tanks2022, " $")
    print("Landing gear costs: ", cost_landing_gear2022, " $")
    print("Manufacturing costs: ", manufacturing_cost2022,  " $")

    print(" ")
    print("Cost of design phase: ", costs_design_phases2022, " $")
    print("Costs of manufacturing flight test aircraft: ", flight_test_aircraft_cost2022, " $")
    print("Costs of flight test: ", flight_test_operating_cost2022, " $")
    print("Development support and testing costs: ", development_support_and_testing_cost2022, " $")
    print("Other testing costs: ", other_certification_costs2022, " $")
    print("Certification and Testing cost: ", certification_and_test_cost2022, " $")
    print("Total fixed costs: ", total_fixed_costs2022, " $")

    print(" ")
    print("Unit cost: ", unit_cost2022, " $")

    return bep, cost_engine1970, total_fixed_costs2022, unit_cost2022


def estimate_operation_costs(total_range, total_time, man_hour_rate_maintenance1990, empty_weight, engine_weight,
                             cost_engine1970, cef19701990, unit_price1990, take_off_weight, cef19902022, lh2_price, lh2_mass):
    """
    Inputs:
    total_range, range which includes taxi, takeoff, climb, cruise, descent, landing, taxi [nautical miles]
    total_time, total time similar defined as the range above [hrs]
    Aircraft empty weight [kg]
    Engine weight [kg]
    Variables:
    tef, travel expense factor [-]
    ah, number of flight hours per year [hrs]
    w_a, some calculated weight [lbs]
    esppf, engine spare parts price factor [-], assumed from Roskam
    h_em, attained period between engine overhauls [hrs]
    """

    cef19891990 = 1.05
    salary_pilot1989 = 49700  # [$]
    salary_copilot1989 = 29400  # [$]
    cef19892022 = 2.36
    salary_copilot2022 = salary_copilot1989 * cef19892022
    salary_pilot2022 = salary_pilot1989 * cef19892022
    ah = 800  # [hrs]
    tef_1990 = 7.  # [$/bl hrs]
    f_amb_lab = 1.2
    f_amb_mat = 0.55
    esppf = 1.5
    h_em = 4000  # [hrs]
    cost_engine1990 = cost_engine1970 * cef19701990
    cost_avionics1990 = cost_avionics1970 * cef19701990
    atf = 1
    afp = unit_price1990 - number_of_engines * cost_engine1990

    v_block = total_range / total_time
    empty_weightlbs = empty_weight / lbs_to_kg
    engine_weightlbs = engine_weight / lbs_to_kg
    take_off_weightlbs = take_off_weight / lbs_to_kg

    # crew: assumed 1 pilot and 1 co-pilot
    pilot_cost1990 = ((1 + 0.26) / v_block) * (salary_pilot1989 * cef19891990) / ah + tef_1990 / v_block
    copilot_cost1990 = ((1 + 0.26) / v_block) * (salary_copilot1989 * cef19891990) / ah + tef_1990 / v_block
    total_crew_cost1990 = pilot_cost1990 + copilot_cost1990

    # maintenance
    w_a = empty_weightlbs - number_of_engines * engine_weightlbs  # [lbs]
    airframe_maintenance_man_hours_block = 1.7 + 0.067 * w_a / 1000
    labor_cost_airframe_maintenance = 1.03 * airframe_maintenance_man_hours_block * man_hour_rate_maintenance1990 / v_block

    k_h_em = 0.021 * h_em / 100 + 0.769
    maintenance_materials_engine_cost_block = (5.43 * 10 ** (-5) * cost_engine1970 * cef19701990 * esppf - 0.47) / k_h_em
    maintenance_materials_airframe_cost_block = 30. * cef19891990 * atf + 0.475 * 10 ** (-5) * afp

    engine_maintenance_man_hours_block = (0.0765 * (engine_weightlbs / 1000) ** 2 + 0.2495 * engine_weightlbs / 1000) * (0.7 / k_h_em + 0.3)

    labor_cost_engines_maintenance = 1.03 * 1.3 * number_of_engines * engine_maintenance_man_hours_block * man_hour_rate_maintenance1990 / v_block

    cost_maintenance_materials_airframe = 1.03 * maintenance_materials_airframe_cost_block / v_block

    cost_maintenance_materials_engines = 1.03 * 1.3 * number_of_engines * maintenance_materials_engine_cost_block / v_block

    maintenance_burden = 1.03 * (
                f_amb_lab * (airframe_maintenance_man_hours_block * man_hour_rate_maintenance1990 + number_of_engines *
                             engine_maintenance_man_hours_block * man_hour_rate_maintenance1990) + f_amb_mat *
                (maintenance_materials_airframe_cost_block + number_of_engines * maintenance_materials_engine_cost_block)) / v_block

    total_maintenance_cost1990 = labor_cost_airframe_maintenance + labor_cost_engines_maintenance + cost_maintenance_materials_airframe +\
                                 cost_maintenance_materials_engines + maintenance_burden

    # fuel
    total_fuel_cost2022 = (lh2_price * lh2_mass)/ total_range       # [$/nm]
    total_fuel_cost1990 = total_fuel_cost2022 / cef19902022

    # insurance
    u_ann_bl = 10**3 * (3.4546 * total_time + 2.994 - (12.289 * total_time**2 + 5.6626 * total_time + 8.964)**(1/2))
    total_insurance_cost1990 = 0.0175 * unit_price1990 / (u_ann_bl * v_block)

    # depreciation
    airframe_depreciation = 0.85 * (unit_price1990 - number_of_engines * cost_engine1990 - cost_avionics1990) / (10 * u_ann_bl * v_block)
    avionics_depreciation = 1 * cost_avionics1990 / (5 * u_ann_bl * v_block)
    spare_parts_depreciation = 0.85 * 0.1 * (unit_price1990 - number_of_engines * cost_engine1990) / (10 * u_ann_bl * v_block)
    engine_depreciation = 1.0 * number_of_engines * cost_engine1990 / (7 * u_ann_bl * v_block)
    total_depreciation_cost1990 = airframe_depreciation + avionics_depreciation + spare_parts_depreciation + engine_depreciation # assume complete depreciation of engines

    # landing fees
    f_lf = 0.036 + 4 * 10**(-8) * take_off_weightlbs
    cost_navigation_fee1990 = 10 / (v_block * total_time)
    f_rt = 0.001 + 10**(-8) * take_off_weightlbs

    # financing
    f_fin = 0.07

    # indirect costs
    f_ic = 0.7

    direct_cost1990 = (total_crew_cost1990 * 1.3 + total_fuel_cost1990 + total_insurance_cost1990 *1.3 + total_maintenance_cost1990 * 1.3
                       + total_depreciation_cost1990 * 1.3 + cost_navigation_fee1990 * 1.3)/(1 - f_lf - f_rt - f_fin)
    indirect_cost1990 = f_ic * direct_cost1990

    total_operational_cost1990 = direct_cost1990 + indirect_cost1990
    total_operational_cost2022 = total_operational_cost1990 * cef19902022

    total_crew_cost2022 = total_crew_cost1990 * cef19902022
    total_maintenance_cost2022 = total_maintenance_cost1990 * cef19902022
    total_insurance_cost2022 = total_insurance_cost1990 * cef19902022
    total_depreciation_cost2022 = total_depreciation_cost1990 * cef19902022

    cost_landing_fee1990 = f_lf * direct_cost1990
    registry_taxes_cost1990 = f_rt * direct_cost1990
    total_landing_fee_cost1990 = cost_landing_fee1990 + cost_navigation_fee1990 + registry_taxes_cost1990


    total_landing_fee_cost2022 = total_landing_fee_cost1990 * cef19902022
    total_financing_cost2022 = f_fin * direct_cost1990 * cef19902022
    indirect_cost2022 = indirect_cost1990 * cef19902022
    direct_cost2022 = direct_cost1990 * cef19902022


    print("Crew costs per nm: ", total_crew_cost2022)
    print("Maintenance /nm: ", total_maintenance_cost2022)
    print("Fuel cost /nm: ", total_fuel_cost2022)
    print("Insurance/nm: ", total_insurance_cost2022)
    print("Depreciation/nm: ", total_depreciation_cost2022)
    print("Landing fee/nm: ", total_landing_fee_cost2022)
    print("Financing cost/nm: ", total_financing_cost2022)
    print("Direct cost /nm: ", direct_cost2022)
    print("Indirect cost/nm: ", indirect_cost2022)
    print("The total operational costs per nm: ", total_operational_cost2022, " $")

    return total_operational_cost2022


####################################### Main ######################################33
# Inputs
inflation_rate_1970_2022 = 7.51
inflation_rate_1970_2012 = 5.91
inflation_rate_1970_1989 = 3.19
inflation_rate_1989_2012 = 1.85
inflation_rate_1970_1990 = 3.37
inflation_rate_1990_2022 = 2.23
inflation_rate_1990_2012 = 1.76
unit_price2022 = 90 * 10 ** 6  # [$]
unit_price1990 = unit_price2022 / inflation_rate_1990_2022
total_aircraft_sold = 1800  # [-]
g = 9.80665

# Inputs from iteration
cruise_velocity = 236.154 * np.sqrt(0.3652/1.225)   # [m/s]
number_of_engines = 11                              # [-]
max_total_power = 42.48 * 10 ** 6                   # [W]
fan_diameter = 1.79059457                           # [m]
maximum_motor_power = 4 * 10 ** 6                   # [W]
total_kwh = 3.3577103 * 10 ** 11 * 2.7777777778 * 10 ** (-7)  # [kWh]
total_rangekm = 4151.88763                          # [km]
total_rangenm = total_rangekm * km_to_nm            # [nm]
total_time = 349 / 60                               # [hrs]

empty_weightkg = 806265.7296 / g                    # [kg]
propulsion_weightkg = 26296.71045                   # [kg]
engine_weightkg = 7829.2576 / number_of_engines                          # [kg]
maximum_take_off_weightkg = 1008892.696 / g         # [kg]
lh2_masskg = 5649.030295                            # [kg]
lh2_price = 5                                       # [$/kg], https://home.kpmg/xx/en/home/insights/2020/11/the-hydrogen-trajectory.html
Wduct = 50.18116283                                 # [kg]

cost_avionics1989 = 196030 + 7225 + 18840 + 3910 + 10705 + 30336 + 30080 + 19348 + 18512 + 24520 + 39236 + 19703 + 31040 + 163214 + 7664
cost_avionics1970 = cost_avionics1989 / inflation_rate_1970_1989

man_hour_rate_maintenance2012 = 60  # [$/hr], based on Cost Estimation Methods for Hybrid-Electric General Aviation Aircraft
man_hour_rate_manufacturing2012 = 53  # [$/hr], based on Cost Estimation Methods for Hybrid-Electric General Aviation Aircraft
man_hour_rate_tooling2012 = 61  # [$/hr], based on Cost Estimation Methods for Hybrid-Electric General Aviation Aircraft
man_hour_rate_design2012 = 92  # [$/hr], based on Cost Estimation Methods for Hybrid-Electric General Aviation Aircraft

man_hour_rate_design1989 = man_hour_rate_design2012 / inflation_rate_1989_2012
man_hour_rate_tooling1989 = man_hour_rate_tooling2012 / inflation_rate_1989_2012
man_hour_rate_manufacturing1989 = man_hour_rate_manufacturing2012 / inflation_rate_1989_2012
man_hour_rate_maintenance1989 = man_hour_rate_maintenance2012 / inflation_rate_1989_2012

man_hour_rate_maintenance1990 = man_hour_rate_maintenance2012 / inflation_rate_1990_2012

break_even_point, cost_engine1970, total_fixed_costs2022, unit_cost2022 = \
    estimate_break_even_point(empty_weightkg, propulsion_weightkg, cruise_velocity, man_hour_rate_design1989, man_hour_rate_tooling1989,
                              man_hour_rate_manufacturing1989, total_aircraft_sold, number_of_engines, max_total_power, Wduct,
                              fan_diameter, maximum_motor_power, total_kwh, cost_avionics1970, unit_price2022, inflation_rate_1970_2022)

total_operational_cost2022 = estimate_operation_costs(total_rangenm, total_time, man_hour_rate_maintenance1990, empty_weightkg, engine_weightkg,
                             cost_engine1970, inflation_rate_1970_1990, unit_price1990, maximum_take_off_weightkg, inflation_rate_1990_2022, lh2_price, lh2_masskg)