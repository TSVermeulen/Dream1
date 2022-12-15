import numpy as np
import scipy as sc
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import Crosssectionfitter as csf
import FuselageFunctionsV2 as FP
import DesignIteration.WingBoxLoadingNew as WBL

plt.plot(WBL.y,WBL.ForwardMomentFunctionBodyAxis(WBL.y))
plt.title("Forward")
plt.show()

plt.plot(WBL.y,WBL.UpwardMomentFunctionBodyAxis(WBL.y))
plt.title("Upward")
plt.show()

plt.plot(WBL.y,WBL.TorqueFunctionBodyAxis(WBL.y))
plt.title("Torque")
plt.show()

y=np.arange(0,WBL.halfWidthFuselage)
Lift_fuselage=WBL.GetShearDistribution(y, WBL.span, WBL.engineSpan, WBL.totalWeightEngines, WBL.totalThrust, WBL.landingGearWeight, WBL.landingGearSpanwiseLocation, WBL.quarterChordSweepAngle, WBL.weightPerVerticalWingTip)[2](y)

plt.plot(y,Lift_fuselage)
plt.title("shear")
plt.show()

