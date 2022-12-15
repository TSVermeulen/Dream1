import numpy as np

"Input"
height=1.9  #[m]

length_ceiling = 6.8 #[m]
length_floor = 8.183087 #[m]
radius_side_arc = 1.664395

"Outputs"
half_length_ceiling=0.5*length_ceiling
half_length_floor=0.5*length_floor

length_wall = np.sqrt(height**2+(half_length_floor-half_length_ceiling)**2)
alpha=np.arctan(height/(half_length_floor-half_length_ceiling))
theta=np.arcsin(length_wall/2/radius_side_arc)
gamma=np.arccos(length_wall/2/radius_side_arc)
delta=alpha-gamma
beta=np.pi/2-delta
eta=np.pi-2*theta-beta #angle between ceiling and fuselage skin in the top node

radius_bottom_arc= half_length_floor / np.cos(delta)
radius_top_arc= half_length_ceiling / np.sin(eta)

centre_bottom_arc= radius_bottom_arc * np.sin(delta)
centre_top_arc= height-radius_top_arc * np.cos(eta)
centre_side_arc=radius_side_arc*np.sin(delta)

theta_1_ceiling=-np.arcsin(0.5*length_ceiling/radius_top_arc)
theta_2_ceiling=+np.arcsin(0.5*length_ceiling/radius_top_arc)

theta_1_floor=np.pi-np.arcsin(0.5*length_floor/radius_bottom_arc)
theta_2_floor=np.pi+np.arcsin(0.5*length_floor/radius_bottom_arc)

theta_1_side=theta_2_ceiling
theta_2_side=theta_1_floor

angle_ceiling_skin=eta
angle_floor_skin=np.pi-eta
