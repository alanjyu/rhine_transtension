import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator


filepath = r'--' # define the filepath to save the data and figure


# material properties
upper = 20e3 # upper crust thickness in m
lower = 15e3 # lower crust thickness in m
mantle = 85e3 # mantle thickness in m
astheno = 40e3 # asthenosphere thickness in m
height = upper + lower + mantle + astheno # total height in m


# geotherm parameters
t1 = 273 # ground surface temperature in k

k1 = 2.5 # thermal conductivity of upper crust in W m^(-1) K^(-1)
k2 = 2.5 # thermal conductivity of lower crust in W m^(-1) K^(-1)
k3 = 3.0 # thermal conductivity of mantle lithosphere in W m^(-1) K^(-1)
k4 = 100 # thermal conductivity of asthenosphere in W m^(-1) K^(-1)

H1 = 1.5e-6 # rate of heat generation per volume of upper crust in W m^(-3)
H2 = 4e-7 # rate of heat generation per volume of lower crust in W m^(-3)
H3 = 2e-8 # rate of heat generation per volume of mantle lithosphere in W m^(-3)
H4 = 0 # rate of heat generation per volume of asthenosphere in W m^(-3)

q1 = [0.06, 0.055] # top surface heat flux of upper crust in W m^(-2)
q2 = [0.039, 0.039] # top surface heat flux of lower crust in W m^(-2)
q3 = [0.0264117646, 0.0278235295] # top surface heat flux of mantle lithosphere in W m^(-2)
q4 = [0, 0] # top surface heat flux of asthenosphere in W m^(-2)


# depth range from 0 to 600 km in 600 data points
depth = np.linspace(0, height, 600)

def calculate_geotherm(_q1, _q2, _q3, _q4, d):
    """
    calculate temperature at a given depth
    _q1, _q2, _q3, _q4 are the top surface heat flux of the layer
    """
    if d >= (height - upper):
        return t1 + (_q1/k1)*(height-d) - (H1*(height-d)**2) / (2*k1)
    elif (height-upper-lower) <= d < (height-upper):
        t2 = t1 + (_q1/k1)*upper - (H1*upper**2) / (2*k1)
        return t2 + (_q2/k2)*(height-d-upper) - (H2*(height-d-upper)**2) / (2*k2)
    elif (height-upper-lower-mantle) <= d < (height-upper-lower):
        t3 = t1 + (_q1/k1)*upper - (H1*upper**2) / (2*k1) + (_q2/k2)*lower - (H2*lower**2) / (2*k2)
        return t3 + (_q3/k3)*(height-d-upper-lower) - (H3*(height-d-upper-lower)**2) / (2*k3)
    else:
        t4 = t1 + (_q1/k1)*upper - (H1*upper**2) / (2*k1) + (_q2/k2)*lower - (H2*lower**2) / (2*k2) + (_q3/k3)*mantle - (H3*mantle**2) / (2*k3)
        return t4 + (_q4/k4)*(height-d-upper-lower-mantle)

temp_typical = [calculate_geotherm(q1[0], q2[0], q3[0], q4[0], d) for d in depth]
temp_cold = [calculate_geotherm(q1[1], q2[1], q3[1], q4[1], d) for d in depth]

depth_km = (height-depth) / 1e3 # convert depth to km for the plot
data = np.column_stack((depth_km, temp_typical, temp_cold))


np.savetxt(f'{filepath}\geotherm.csv', data, delimiter=',', header='Depth (km), Temperature (K)', comments='')

# calculate the bottom temperature for each layer
layers_depths = [upper, upper+lower, upper+lower+mantle, height]
layers = ['Upper crust', 'Lower crust', 'Mantle lithosphere', 'Asthenosphere']

fig, ax = plt.subplots(figsize=(6, 5))

ax.plot(temp_cold, depth_km, label='Background', color='gray', linestyle='--')
ax.plot(temp_typical, depth_km, label='Graben', color='black')

ax.invert_yaxis()
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

minor_locator_x = AutoMinorLocator(4)
ax.xaxis.set_minor_locator(minor_locator_x)
minor_locator_y = AutoMinorLocator(1)
ax.yaxis.set_minor_locator(minor_locator_y)

x_min = min(temp_typical)
x_max = max(temp_typical)
y_min = 0
y_max = height/1e3

ax.set_xlim(min(temp_typical), max(temp_typical))

ax.set_ylim(y_max, y_min)
ax.set_yticks([y_min, upper/1e3, (upper+lower)/1e3, (upper+lower+mantle)/1e3, y_max])

ax.set(xlabel='Temperature (K)', ylabel='Depth (km)')

ax.set_title('Initial continental geotherm', fontweight='bold', fontsize=14)

# fill the entire plot with white background first
ax.fill_betweenx(depth_km, min(temp_typical), max(temp_typical), where=(depth_km >= 0), color='#fff', alpha=1)

# shade the layers
# ax.fill_betweenx(depth_km, min(temp_typical), max(temp_typical), where=(depth_km <= upper/1e3), color='#222e63', alpha=0.2)
# ax.fill_betweenx(depth_km, min(temp_typical), max(temp_typical), where=(depth_km > upper/1e3) & (depth_km <= (upper+lower)/1e3), color='#6c2f92', alpha=0.2)
# ax.fill_betweenx(depth_km, min(temp_typical), max(temp_typical), where=(depth_km > (upper+lower)/1e3) & (depth_km <= (upper+lower+mantle)/1e3), color='#8d2542', alpha=0.2)
# ax.fill_betweenx(depth_km, min(temp_typical), max(temp_typical), where=(depth_km > (upper+lower+mantle)/1e3), color='#fac351', alpha=0.2)

ax.legend(loc='lower left')

plt.tight_layout()
plt.savefig(f'{filepath}\initial geotherm.png', dpi=300, transparent=True)
plt.show()