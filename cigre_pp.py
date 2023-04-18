import json
import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import pandapower as pp
import pandapower.networks as nw


net = pp.create_empty_network()

# Création des bus :
bus1 = pp.create_bus(net, vn_kv=0.4, name='Générateur')  # pour le générateur
bus2 = pp.create_bus(net, vn_kv=0.4, name='Stockage1')  # pour le stockage1
bus3 = pp.create_bus(net, vn_kv=0.4, name='Stockage2')  # pour la stockage 2
bus4 = pp.create_bus(net, vn_kv=0.4, name='Charge')  # pour la charge

# Création des composants
pv = pp.create_sgen(net, bus=bus1, p_mw=0.05, index=1, q_mvar=0, type='PV', slack=True)  # Ajouter un PV

storage1 = pp.create_storage(net, bus=bus2, p_mw=0.00, index=2, min_p_mw=-0.1, max_p_mw=0.05, min_e_mwh=0, max_e_mwh=0.2,
                             q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1, soc_percent=50, controllable=True)
storage2 = pp.create_storage(net, bus=bus3, p_mw=0.00, index=3, min_p_mw=-0.1, max_p_mw=0.05, min_e_mwh=0, max_e_mwh=0.2,
                             q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1, soc_percent=50, controllable=True)

load1 = pp.create_load(net, bus=bus4, p_mw=0.02, index=3,  q_mvar=0.1)  # Ajouter une charge à la maison


# LINE1 : Ajouter une connexion entre la batterie1 et le générateur photovoltaïque
line1 = pp.create_line(net, from_bus=bus1, to_bus=bus2, length_km=0.01, std_type='NAYY 4x50 SE', name='line1')
sw1 = pp.create_switch(net, bus=bus1, element=line1, et='l', closed=True)

# LINE2 : Ajouter une connexion entre le générateur photovoltaïque et la batterie2
line2 = pp.create_line(net, from_bus=bus1, to_bus=bus3, length_km=0.01, std_type='NAYY 4x50 SE', name='line2')
sw2 = pp.create_switch(net, bus=bus1, element=line2, et='l', closed=True)

# LINE3 : Ajouter une connexion entre la batterie1 et la charge
line3 = pp.create_line(net, from_bus=bus2, to_bus=bus4, length_km=0.01, std_type='NAYY 4x50 SE', name='line3')
sw3 = pp.create_switch(net, bus=bus2, element=line3, et='l', closed=True)

# LINE4 : Ajouter une connexion entre la batterie2 et la charge
line4 = pp.create_line(net, from_bus=bus3, to_bus=bus4, length_km=0.01, std_type='NAYY 4x50 SE', name='line4')
sw4 = pp.create_switch(net, bus=bus3, element=line4, et='l', closed=True)

# LINE5 : Ajouter une connexion entre le pv et la charge
line5 = pp.create_line(net, from_bus=bus1, to_bus=bus4, length_km=0.01, std_type='NAYY 4x50 SE', name='line5')
sw5 = pp.create_switch(net, bus=bus1, element=line5, et='l', closed=True)

# LINE6 : Ajouter une connexion entre les deux batteries
line6 = pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=0.01, std_type='NAYY 4x50 SE', name='line6')
sw6 = pp.create_switch(net, bus=bus2, element=line6, et='l', closed=True)


def convert_timeseries_to_dict(net, input_file):
    # set the load type in the cigre grid, since it is not specified
    net["load"].loc[:, "type"] = "residential"
    # change the type of the last sgen to wind
    net.sgen.loc[:, "type"] = "pv"
    net.sgen.loc[8, "type"] = "wind"

    # read the example time series
    time_series = pd.read_json(input_file)
    time_series.sort_index(inplace=True)
    # this example time series has a 15min resolution with 96 time steps for one day
    n_timesteps = time_series.shape[0]

    n_load = len(net.load)
    n_sgen = len(net.sgen)
    p_timeseries = np.zeros((n_timesteps, n_load + n_sgen), dtype=float)
    # p
    load_p = net["load"].loc[:, "p_mw"].values
    sgen_p = net["sgen"].loc[:7, "p_mw"].values
    wind_p = net["sgen"].loc[8, "p_mw"]

    p_timeseries_dict = dict()
    for t in range(n_timesteps):
        # print(time_series.at[t, "residential"])
        p_timeseries[t, :n_load] = load_p * time_series.at[t, "residential"]
        p_timeseries[t, n_load:-1] = - sgen_p * time_series.at[t, "pv"]
        p_timeseries[t, -1] = - wind_p * time_series.at[t, "wind"]
        p_timeseries_dict[t] = p_timeseries[t, :].tolist()

    time_series_file = os.path.join(tempfile.gettempdir(), "timeseries.json")
    with open(time_series_file, 'w') as fp:
        json.dump(p_timeseries_dict, fp)

    return net, p_timeseries_dict


# open the cigre mv grid
net = net
# convert the time series to a dict and save it to disk
input_file = "cigre_timeseries_15min.json"
net, p_timeseries = convert_timeseries_to_dict(net, input_file)
# run the PowerModels.jl optimization
# n_time steps = 96 and time_elapsed is a quarter of an hour (since the time series are in 15min resolution)
try:
    storage_results = pp.runpm_storage_opf(net, n_timesteps=96, time_elapsed=0.25)
except:
    print("Cannot be performed due to [WinError 3] - Can't find file python39.dll")


def store_results(storage_results, grid_name):
    for key, val in storage_results.items():
        file = grid_name + "_strg_res" + str(key) + ".json"
        print("Storing results to file {}".format(file))
        print(val)
        val.to_json(file)
# store the results to disk optionally
#store_results(storage_results, "cigre_ts")


def plot_storage_results(storage_results):
    n_res = len(storage_results.keys())
    fig, axes = plt.subplots(n_res, 2)
    if n_res == 1:
        axes = [axes]
    for i, (key, val) in enumerate(storage_results.items()):
        res = val
        axes[i][0].set_title("Storage {}".format(key))
        el = res.loc[:, ["p_mw", "q_mvar", "soc_mwh"]]
        el.plot(ax=axes[i][0])
        axes[i][0].set_xlabel("time step")
        axes[i][0].legend(loc=4)
        axes[i][0].grid()
        ax2 = axes[i][1]
        patch = plt.plot([], [], ms=8, ls="--", mec=None, color="grey", label="{:s}".format("soc_percent"))
        ax2.legend(handles=patch)
        ax2.set_label("SOC percent")
        res.loc[:, "soc_percent"].plot(ax=ax2, linestyle="--", color="grey")
        ax2.grid()

    plt.show()
# plot the result
#plot_storage_results(storage_results)
