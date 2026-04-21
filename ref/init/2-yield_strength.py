import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator


filepath = r'--' # define the filepath to read the geotherm, and then save the data and figure


# material properties
upper = 20e3 # upper crust thickness in m
lower = 15e3 # lower crust thickness in m
mantle = 85e3 # mantle lithosphere thickness in m
astheno = 40e3 # asthenosphere thickness in m
height = upper + lower + mantle + astheno # total height in m

upper_rho = 2800 # upper crust density in kg m^(-3)
lower_rho = 2900 # lower crust density in kg m^(-3)
mantle_rho = 3250 # mantle lithosphere density in kg m^(-3)
astheno_rho = 3300 # asthenosphere density in kg m^(-3)

g = 9.81 # gravitational acceleration in m s^(-2)
R = 8.3144626 # ideal gas constant in J mol^(-1) K^(-1)

epsilon = 1.e-15 # reference strain rate in s^(-1)
cohesion = 5e6 # cohesion in Pa
crust_phi = [np.radians(26.56), np.radians(16.6), np.radians(6.64)] # internal angle of friction (undeformed, lower bound for seed, upper bound for seed)
mantle_phi = [np.radians(26.56), np.radians(26.56), np.radians(26.56)] # mantle stays the same regardless of plastic strain

# dislocation creep parameters
upper_disl_n = 4 # stress exponent of upper crust
upper_disl_A = 8.57e-28 # material constant of upper crust in P^(-n) s^(-1)
upper_disl_Q = 223.e3 # activation energy of upper crust in J mol^(-1)
upper_disl_V = 0 # activation volume of upper crust in m^3 mol^(-1)

lower_disl_n = 3 # stress exponent of lower crust
lower_disl_A = 7.13e-18 # material constant of lower crust in P^(-n) s^(-1)
lower_disl_Q = 345.e3 # activation energy of lower crust in J mol^(-1)
lower_disl_V = 0 # activation volume of lower crust in m^3 mol^(-1)

mantle_disl_n = 3.5
mantle_disl_A = 6.52e-16
mantle_disl_Q = 530.e3
mantle_disl_V = 18.e-6

astheno_disl_n = 3.5
astheno_disl_A = 5.33e-19
astheno_disl_Q = 480.e3
astheno_disl_V = 11.e-6


# diffusion creep parameters
grain_size = 1.e-3

upper_diff_A = 5.97e-19
upper_diff_Q = 223e3
upper_diff_V = 0
upper_diff_m = 2

lower_diff_A = 2.99e-25
lower_diff_Q = 159e3
lower_diff_V = 38e-6
lower_diff_m = 3

mantle_diff_A = 2.25e-9
mantle_diff_Q = 375.e3
mantle_diff_V = 6.e-6
mantle_diff_m = 0

astheno_diff_A = 1.5e-9
astheno_diff_Q = 335.e3
astheno_diff_V = 4.e-6
astheno_diff_m = 0


def disl_power_law(eps, n, A, Q, P, V, T):
    """
    calculate dislocation power law creep
    eps : strain rate in s^(-1)
    n : stress exponent
    A : material constant in P^(-n) s^(-1)
    Q : activation energy in J mol^(-1)
    P : pressure in Pa
    V : activation volume in m^3 mol^(-1)
    T : temperature in K
    """

    disl_stress_diff = (eps / A)**(1 / n) * np.exp((Q + P*V) / (n * R * T))
    return disl_stress_diff / 1e6 # convert to MPa


def diff_power_law(eps, d, m, A, Q, P, V, T):
    """
    calculate diffusion power law creep
    eps : strain rate in s^(-1)
    d : grain size in m
    m : grain size exponent
    A : material constant in Pa^(-1) s^(-1)
    Q : activation energy in J mol^(-1)
    P : pressure in Pa
    V : activation volume in m^3 mol^(-1)
    T : temperature in K
    """

    diff_stress_diff = (eps / A) * np.exp((Q + P*V) / (R * T)) * d**(m)
    return diff_stress_diff / 1e6 # convert to MPa


# load geotherm data from CSV
data = np.genfromtxt(f'{filepath}/geotherm.csv', delimiter=',', skip_header=1)
depth_km = data[:, 0]
depth = depth_km * 1.e3 # depth in m
temp_background = data[:, 2] # geotherm in K
temp_seed = data[:, 1] # geotherm in K

plastic_yield_stress = np.zeros(len(depth_km)) # yield stress for plastic deformation
disl_yield_stress = np.zeros(len(depth_km)) # yield stress for dislocation creep
diff_yield_stress = np.zeros(len(depth_km)) # yield stress for diffusion creep

density = np.zeros(len(depth_km))
pressure = np.zeros(len(depth_km))


# plot the yield strength envelope
fig, ax = plt.subplots(figsize=(6, 6))

def yield_strength_envelope(depth, temp, crust_phi, mantle_phi):
    """
    Calculate and plot the yield strength envelope for a given temperature profile.
    depth: array of depths in m
    temp: array of temperatures in K (same length as depth)
    label: label for the plot
    color: color for the plot line
    """
    plastic_yield_stress = np.zeros(len(depth))
    disl_yield_stress = np.zeros(len(depth))
    diff_yield_stress = np.zeros(len(depth))
    density = np.zeros(len(depth))
    pressure = np.zeros(len(depth))

    for i, d in enumerate(depth):
        if d <= upper: # upper crust
            density[i] = upper_rho
            pressure[i] = g * density[i] * d
            plastic_yield_stress[i] = (cohesion * np.cos(crust_phi) + pressure[i] * np.sin(crust_phi)) / 1e6
            disl_yield_stress[i] = disl_power_law(epsilon, upper_disl_n, upper_disl_A, upper_disl_Q, pressure[i], upper_disl_V, temp[i])
            diff_yield_stress[i] = diff_power_law(epsilon, grain_size, upper_diff_m, upper_diff_A, upper_diff_Q, pressure[i], upper_diff_V, temp[i])
        elif d <= (upper + lower): # lower crust
            density[i] = lower_rho
            pressure[i] = g * (density[i] * (d - upper) + upper_rho * upper)
            plastic_yield_stress[i] = (cohesion * np.cos(crust_phi) + pressure[i] * np.sin(crust_phi)) / 1e6
            disl_yield_stress[i] = disl_power_law(epsilon, lower_disl_n, lower_disl_A, lower_disl_Q, pressure[i], lower_disl_V, temp[i])
            diff_yield_stress[i] = diff_power_law(epsilon, grain_size, lower_diff_m, lower_diff_A, lower_diff_Q, pressure[i], lower_diff_V, temp[i])
        elif d <= (upper + lower + mantle): # mantle lithosphere
            density[i] = mantle_rho
            pressure[i] = g * (density[i] * (d - upper - lower) + lower_rho * lower + upper_rho * upper)
            plastic_yield_stress[i] = (cohesion * np.cos(mantle_phi) + pressure[i] * np.sin(mantle_phi)) / 1e6
            disl_yield_stress[i] = disl_power_law(epsilon, mantle_disl_n, mantle_disl_A, mantle_disl_Q, pressure[i], mantle_disl_V, temp[i])
            diff_yield_stress[i] = diff_power_law(epsilon, grain_size, mantle_diff_m, mantle_diff_A, mantle_diff_Q, pressure[i], mantle_diff_V, temp[i])
        else: # asthenosphere
            density[i] = astheno_rho
            pressure[i] = g * (density[i] * (d - upper - lower - mantle) + mantle_rho * mantle + lower_rho * lower + upper_rho * upper)
            plastic_yield_stress[i] = (cohesion * np.cos(mantle_phi) + pressure[i] * np.sin(mantle_phi)) / 1e6
            disl_yield_stress[i] = disl_power_law(epsilon, astheno_disl_n, astheno_disl_A, astheno_disl_Q, pressure[i], astheno_disl_V, temp[i])
            diff_yield_stress[i] = diff_power_law(epsilon, grain_size, astheno_diff_m, astheno_diff_A, astheno_diff_Q, pressure[i], astheno_diff_V, temp[i])

    min_diff_stress = np.minimum.reduce([plastic_yield_stress, disl_yield_stress, diff_yield_stress])
    return plastic_yield_stress, disl_yield_stress, diff_yield_stress, min_diff_stress

temp_background_yield_stress = yield_strength_envelope(depth, temp_background, crust_phi[0], mantle_phi[0])
temp_seed_lower_bound = yield_strength_envelope(depth, temp_background, crust_phi[1], mantle_phi[1])
temp_seed_higher_bound = yield_strength_envelope(depth, temp_seed, crust_phi[2], mantle_phi[2])

ax.invert_yaxis()
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

minor_locator_x = AutoMinorLocator(2)
ax.xaxis.set_minor_locator(minor_locator_x)
minor_locator_y = AutoMinorLocator(1)
ax.yaxis.set_minor_locator(minor_locator_y)

x_min = 0
x_max = 700
y_min = 0
y_max = height/1e3

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_max, y_min) # y-axis is flipped
ax.set_yticks([y_min, upper/1e3, (upper+lower)/1e3, (upper+lower+mantle)/1e3, y_max])

ax.set_xlabel('Yield stress (MPa)')
ax.set_ylabel('Depth (km)')

# fill the entire plot with white background first
ax.fill_betweenx(depth_km, x_min, x_max, where=(depth_km >= x_min), color='#fff', alpha=1)

# shade the layers
ax.fill_betweenx(depth_km, x_min, x_max, where=(depth_km < upper/1e3), color='#e9e5e3')
ax.fill_betweenx(depth_km, x_min, x_max, where=(depth_km >= upper/1e3) & (depth_km < (upper+lower)/1e3), color='#afa1a1')
ax.fill_betweenx(depth_km, x_min, x_max, where=(depth_km >= (upper+lower)/1e3) & (depth_km < (upper+lower+mantle)/1e3), color='#97b998')
ax.fill_betweenx(depth_km, x_min, x_max, where=(depth_km > (upper+lower+mantle)/1e3), color='#edcaaf')

# fill the weak zone
ax.fill_betweenx(depth_km, temp_seed_lower_bound[3], temp_seed_higher_bound[3], color='black', alpha=0.5, edgecolor='none', label=r'Weakened')

# plot the yield strength envelope
ax.plot(temp_background_yield_stress[3], depth_km, color='blue', linestyle='--', label=r'Undeformed')

ax.legend(loc='lower right')


plt.tight_layout()
plt.savefig(f'{filepath}/initial yield strength.png', dpi=300, transparent=True)
plt.show()
