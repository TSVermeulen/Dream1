import numpy as np
from ambiance import Atmosphere
import matplotlib.pyplot as plt
import time


def getMaximumPressureDifference(maximumAltitude, cabinPressureHeight):
    """
    Inputs:
    maximum operating altitude [m]
    cabinPressureHeight [m]

    """

    pressuredifference = Atmosphere(cabinPressureHeight).pressure - Atmosphere(maximumAltitude).pressure
    return pressuredifference


def Nodeanalysis(beta, gamma, epsilon, pressuredifference, Radius1, Radius2, Radius3):
    """
    Returns the forces in the trapezoidal structure
    Inputs:
    beta,gamma,epsilon: Angles of geometry [rad]
    Radius1,2,3 Radii of the 3 parts of the ellipse considered as cylindrical.
    pressure difference [N/M2]

    Returns:
    Fc Tension force in ceiling
    Fw Tension force in wall
    Ff Tension force in floor

    """
    Fres1 = pressuredifference * (Radius1 - Radius2)
    Fres2 = pressuredifference * (Radius3 - Radius2)
    # Fw = ((np.sin(alpha) * np.cos(beta) / np.cos(alpha) - np.sin(beta)) * Fres1) / (
    #         np.sin(alpha) * np.sin(gamma) / np.cos(alpha) - np.cos(gamma))
    # Fc = (np.sin(gamma) / np.cos(alpha) * Fw - np.cos(beta) / np.cos(alpha) * Fres1)
    # Ff = -Fres2 * np.cos(epsilon) - Fw * np.sin(gamma)
    Fwtop = Fres1 * np.sin(beta) / np.sin(gamma)
    Fceiling = np.cos(gamma) * Fwtop - np.cos(beta) * Fres1
    Fwlow = np.sin(epsilon) / np.sin(gamma) * Fres2
    Ffloor = -1 * (Fwlow * np.cos(gamma) + Fres2 * np.cos(epsilon))
    return Fwtop, Fceiling, Fwlow, Ffloor


def Areamomentarc(theta1, theta2, radius, yr, t):
    """
    Determine area moments for the arcs

    Inputs:
    theta1: [Rad] angle between the vertical axis and the left most point of the arc
    theta2: [Rad] angle between the vertical axis and the right most point of the arc
    Radius: [m] Radius of the fitted arc
    yr: [m] distance from the chosen initial axis system to the circle centre (normal xyz axis system)
    t : [m] Thickness of the arc

    outputs:
    Ixx : [m**4] Area moment of the arc around its own centroid
    y: Distance between the chosen axis system and the cg for the arc

    """
    y = yr + radius * (np.sin(theta2) - np.sin(theta1)) / (theta2 - theta1)
    yp = yr - y
    Ixx = radius * t * (
            (radius ** 2) / 4 * (np.sin(2 * theta2) - np.sin(2 * theta1)) + ((radius ** 2) / 2 + yp ** 2) * (
            theta2 - theta1) + 2 * radius * yp * (np.sin(theta2) - np.sin(theta1)))
    return Ixx, y


def Areamomentwalls(t, h, angle, y):
    """
    Areamoment of the wall

    input:
    thicknesss:  [mm]
    h : [m] Length of the section
    angle : [rad] Angle defined as seen in structures for rotated beams
    y : [m] vertical distance from the centroid for the chosen point
    """
    Ixx = t * (h ** 3) * (np.sin(angle) ** 2) / 12
    return Ixx, y


def steiner(Area, y):
    Ixx = Area * y ** 2
    return Ixx


def SteinerArc(theta1, theta2, t, Radius, y):
    """
    Calculate steiner term for the arc
    """
    Area = (theta2 - theta1) / (2 * np.pi) * (2 * np.pi * t * Radius - np.pi * t ** 2)
    Ixx = steiner(Area, y)
    return Area, Ixx


"Defining Loads for longitudinal bending"

def Wingloading(Moment, h, d, n):
    """
    calculates the normal forces in the trapezoidal structure in the horizontal members

    Input:
    Moment : [Nm] moment induced by the wing bending minus the bending relief from mounted engines/landing gear
    h: [m] height of the trapezoidal area
    d: [m] length of the connection between the wing and the fuselage
    n: [] Load factor
    """

    Fn = n * Moment / (h * d)
    return Fn


def Lateralbeammoment(q, L):
    """
    Calculates lateral stress with loading as distributed
    """

    y = L / 2
    Mlateral = q * L / 2 * y - q * y ** 2 / 2
    return Mlateral


def PassengerLoads(passengercount, paxweight):
    yzload = passengercount * paxweight * 9.81
    return yzload


def Furnishingloads(Wfurnishing, cabinwidth, cabinlength):
    yzload = Wfurnishing / cabinwidth / cabinlength
    return yzload


def Fuselageliftloads(Total_lift, fuselagelength):
    zload = Total_lift / fuselagelength
    return zload


def shear(q0, V, Iyy, r, t, alpha, alpha1):
    q = q0 - V / Iyy * r ** 2 * t * (np.sin(alpha) - np.sin(alpha1))
    return q


def smear(t, length):
    n = 0
    d = 0
    for i in range(len(t)):
        n += t[i] * length[i]
        d += length[i]
    t = n / d
    return t


def arclength(r, theta1, theta2):
    s = r * (theta2 - theta1)
    return s


def Longitudinal_normal(M, z, I, t):
    N = M * z * t / I
    return N


def vonMises(sigma_lat, sigma_long, tau_lat_long):
    sigma = np.sqrt(sigma_lat ** 2 - sigma_long * sigma_lat + sigma_long ** 2 + 3 * tau_lat_long ** 2)
    return sigma


def wingloadFZ(F, x1, x2, res, M0):
    # M=F*(xf-(x2+x1)/2)+M0
    f1=F/(x2-x1)-6*M0/(x2-x1)**2
    f2=F/(x2-x1)+6*M0/(x2-x1)**2
    xlin=np.arange(x1,x2,res)
    Fz_append=np.linspace(f1*res,f2*res,len(xlin))
    return xlin,Fz_append

def DimplingLoad(Eface,tface,Poisson12,Poisson21,s):
    Ndimp=2*Eface*tface**3/(1-Poisson12*Poisson21)/s**2
    return Ndimp

def CrimnplingLoad(tcore,Gcore):
    Ncrimp=tcore*Gcore
    return Ncrimp

def Wrinklingload(Eface,Ecore,Gcore):
    Nwrink=0.79*(Eface*Ecore*Gcore)**(1/3)
    return Nwrink

def GlobalBucklingLoad(tcore,tface,Gcore,Eface,L):
    Ns=Gcore*(tcore+tface)**2/tcore
    Ne=Eface*np.pi**2/L**2*((tface**3)/6+tface*((tcore+tface)**2)/2)
    Nef=Eface*np.pi**2/L**2*tface**3/6
    Nglobal=Ne*((1+Nef/Ns-(Nef/Ns)**2)/(1+Ns/Ns-Nef/Ns))
    return Nglobal

def pressurizationforces(pressure_difference,radius):
    N_p_long=pressure_difference*radius/2,
    N_p_hoop=pressure_difference*radius
    return N_p_long,N_p_hoop

def N_cr_shell(Lframe,radius,tshell,poisson,Eshell,t_eq):
    Z=Lframe**2/(radius*tshell)*np.sqrt(1-poisson**2)
    phi=1/16*np.sqrt(radius/tshell)
    theta=1-0.731*(1-np.exp(-phi))
    if Z>2.85:
        kx=4*np.sqrt(3)/np.pi**2*theta*Z
    else:
        kx = 1+12*theta**2*Z**2/np.pi**4
    D=Eshell*t_eq**3/(12*(1-poisson**2))
    N_cr_shell=kx*np.pi**2*D/Lframe**2
    return N_cr_shell

def Buckling(C,sigma_yield,E,poisson,t,b):
    Sigma_cc=0.8*(C/sigma_yield*np.pi**2*E/(12*(1-poisson**2))*(t/b)**2)**(0.4)
    if Sigma_cc<1:
        S=Sigma_cc*sigma_yield
    else:
        S=sigma_yield
    return S,Sigma_cc

def Effective_sheet_width(t,C,poisson,E,sigma_cc):
    We=(t/2*np.sqrt((C*np.pi**2)/(12*(1-poisson**2)))*np.sqrt(E/sigma_cc))
    return We

def xdistributor(Fz,F,x_start,x_end,res):
    F=F/(x_end-x_start)*res
    x=np.arange(x_start/res,x_end/res).astype(int)
    print(F)
    for i in x:
        Fz[i]+=F
    return Fz