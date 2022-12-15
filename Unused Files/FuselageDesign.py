"""
Fuselage and Cabin design for the Blended Wing Body concept

Based off the articles:
"A Sizing Methodology for the Conceptual Design of Blended-Wing-Body Transports"
by Kevin R. Bradley

"The Flight Optimization System Weights Estimation Method"
by Douglas P. Wells and Bryce L. Horvath

@author: Thomas
"""

import numpy as np
import matplotlib.pyplot as plt

""" Inputs """
nPax = 150 #[-]
seatPitch = 0.86 #[m]
nPaxAbrest = 10 #[-]
sweepLE = 45 #[rad]
kCabin = 1.08 #[m]
nAisle = 3 #[-]

def cabinWidthProperties():
    """ 
    Computes the (classical) cabin width and headroomwidth as taught in the ADSEE-I course. 
    
    Inputs:
    ----
    global params

    Outputs:
    -----
    cabinWidth, cabin width [m]
    """
    
    seatWidth = 0.508 #[m]
    armRest = 0.0508 #[m]
    aisleWidth = 0.51 #[m]
    clearance = 0.02 #[m]
    
    cabinWidth = (nPaxAbrest * seatWidth + (nPaxAbrest + nAisle + 1) * armRest + nAisle * aisleWidth + 2 * clearance) #[m]
    return cabinWidth

def cabinDesign(cabinWidth, sweepLE):
    """
    Function to find main geometrical cabin design parameters 
    based on width and sweep of LE

    Inputs:
    -----
    cabinWidth, width of the cabin,  in [m]
    sweepLE, sweep of the leading edge of the cabin, in [deg]

    Outputs:
    -----
    XLW, wall length at edge of cabin, in [m]
    XLP, length of cabin at centerline, in [m]
    cabinArea, surface area of cabin, in [m2]
    """
    
    #Compute centerline cabin length, wall length
    XLW = nPax / nPaxAbrest * seatPitch * kCabin #[m], length for rectangular part
    XLP = XLW + cabinWidth / 2 * np.tan(np.radians(sweepLE)) #[m], length of centerline cabin

    #Compute cabinArea
    cabinArea = XLW * cabinWidth + 0.5 * cabinWidth * (XLP - XLW) #[m2], area for rectangular part + area for triangle part

    return XLW, XLP, cabinArea

def fuselageDesign(ACABIN, rearSparXC, XLP, XLW):
    """
    Simple function to find fuselage geometric design parameters based on 
    cabin design data. 

    Input: 
    -----
    ACABIN, cabin surface area, in [m2]
    rearSparXC, location of rear spar (which is the end of the cabin), as fraction of chord
    XLP, length of cabin at centerline, in [m]
    XLW, wall length at edge of cabin, in [m]

    Output:
    -----
    fuselageArea, surface area of the fuselage, in [m2]
    fuselageLength, length of fuselage at centerline, in [m]
    wallLength, length of fuselage at edge of cabin, in [m]
    """

    #Fuselage area
    fuselageArea = ACABIN / rearSparXC #[m]
    
    #Fuselage sizes
    fuselageLength = XLP / rearSparXC #[m]
    outerLength = XLW / rearSparXC #[m]

    return fuselageArea, fuselageLength, outerLength

def draw_fuselage(fuselageWidth, XLP_full, XLP, XLW):
    """
    Simple function to plot the fuselage / cabin area
    Used during verification / debugging

    Inputs:
    -----
    fuselageWidth, width of the fuselage, equal to cabinWidth, in [m]
    XLP_full, full fuselage length, in [m]
    XLP, cabin length at centerline, in [m]
    XLW, wall length of cabin at edge of fuselage, in [m]

    Outputs:
    -----
    Plot of cabin and fuselage layout
    """

    # full fuselage 
    chord_07_plane = [fuselageWidth/2,0]
    wide_height = [fuselageWidth/2, XLW]
    chord07_to_top = XLP
    top_point = [0, chord07_to_top]
    bottom_fuselage = [0,-(XLP_full-XLP)] 
    wall_aft_07 = [fuselageWidth/2, -XLW/0.7*0.3]

    right_side_x = np.array([top_point[0], wide_height[0],chord_07_plane[0], wall_aft_07[0], bottom_fuselage[0]])
    left_side_x = (-1)*right_side_x
    x =  np.concatenate((right_side_x, left_side_x))
    y = np.array([top_point[1], wide_height[1],chord_07_plane[1], wall_aft_07[1], bottom_fuselage[1],  bottom_fuselage[1],  wall_aft_07[1],chord_07_plane[1], wide_height[1], top_point[1]]) 

    x_07 = np.array([ chord_07_plane[0], -1*chord_07_plane[0]])
    y_07 = np.array([0, 0])
    plt.plot(x, y)
    plt.plot(x_07, y_07)
    plt.axis('equal')
    plt.show() 

    return


#The runtime parameter controls wether or not the cabin/fusulage layout gets printed to the user. 
#It is essentially a simple parameter to control debugging of the file. 
#set to "debug" to print, set to "normal" for normal operations. 
runtimeFuselageDesign = "normal" 
if runtimeFuselageDesign == "debug":
    cabinWidth = cabinWidthProperties()
    XLW, XLP, cabinArea = cabinDesign(cabinWidth, sweepLE)
    fuselageArea, fuselageLength, outerLength = fuselageDesign(cabinArea, 0.7, XLP, XLW)
    print("Cabin Area:", cabinArea, "[m2]")
    print("Fuselage Area:", fuselageArea, "[m2]")
    print("Fuselage Length", fuselageLength, "[m]")
    print("Outer Length:", outerLength, "[m]")
    print(XLW, XLP)
    #draw_fuselage(cabinWidth, fuselageLength, XLP, XLW)