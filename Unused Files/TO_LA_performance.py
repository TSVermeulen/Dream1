import numpy as np

#######################################
# Iterative parameters
#######################################
T_TO = 142160
CLmaxTO = 0.9
CLmaxAP = 0.9
A = 4.33
e = 0.99
Cd0 = 0.007749
Vto = 75.27
Sref = 336
MTOW = 48215
WS_TO = 1440
WS_AP = 1440
TW = 0.33
LW = 21
gamma_climb = 12.7

# Density at airport altitude
rho = 1.225

#######################################
# Constants
#######################################
rho0 = 1.225
gamma_app = 3 # [deg]
h_obs = 15.2
g = 9.80665
mu_ground = 0.015 # https://www.sciencedirect.com/science/article/pii/S0360319922019243
mu_brake = -0.5

#######################################
# Calculated constants
#######################################
Vavg_TO = Vto / np.sqrt(2)
Vmin_TO = np.sqrt((2 * WS_TO) / (rho * CLmaxTO))
Vto = 1.05 * Vmin_TO

Vmin_ap = np.sqrt((2 * WS_AP) / (rho * CLmaxAP))
Vapp = 1.3 * Vmin_ap

#######################################
# Difference approach
#######################################
# landing
CDto = Cd0 + (CLmaxTO ** 2)/ (np.pi * e * A)
D = 0.5 * Sref * CDto * rho0 * Vavg_TO ** 2
L = 0.5 * Sref * CLmaxTO * rho0 * Vavg_TO ** 2

aavg = (1 / MTOW) * (T_TO - D - mu_ground * (MTOW * g - L))
x_ground = Vto ** 2 / (2* aavg)

x_trans = (Vto ** 2) / ((LW - 1) * g) * np.sin(np.deg2rad(gamma_climb))
x_climb = (h_obs - (1 - np.cos(np.deg2rad(gamma_climb))) * (Vto ** 2 / ((LW -1) * g))) / np.tan(np.deg2rad(gamma_climb))
x_airborne = x_trans + x_climb
x_tot = x_ground + x_airborne

print("Take-off distance:", x_tot, "[m]")


# landing
ttr = 2
xtr = ttr * Vmin_ap

gamma_ap = 3 # [deg]
delta_n = 0.10 * g

R = (1.3 ** 2) *((WS_AP * 2) / (rho * CLmaxAP * delta_n * g))
xapp_airborne = R * np.sin(np.deg2rad(gamma_ap)) + (h_obs - (1 - np.cos(np.deg2rad(gamma_ap))) * R) / np.tan(np.deg2rad(gamma_ap))

CDmaxAP = Cd0 + (CLmaxAP ** 2) / (np.pi * e * A)
D_ap_avg = 0.5 * rho * Sref * (CDmaxAP + 0.00) * (Vapp / np.sqrt(2)) ** 2
L_ap_avg = 0.5 * rho * Sref * CLmaxAP * (Vapp / np.sqrt(2)) ** 2
a_app_avg = (1 / MTOW) * (- D_ap_avg - (-mu_brake) * ((MTOW * g) - L_ap_avg))

x_brake = - (Vapp ** 2) / (2 * a_app_avg)


x_ap_tot = xtr + xapp_airborne + x_brake
print("Braking distance:", x_brake, "[m]")
print("Landing distance:", x_ap_tot, "[m]")