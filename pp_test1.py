import pandapower as pp
import pandapower.networks as nw

net = nw.create_cigre_network_mv()

# Ajouter une charge à la maison
pp.create_load(net, bus=2, p_mw=0.2, q_mvar=0.1)

# Ajouter une batterie
storage = pp.create_storage(net, bus=1, p_mw=0.05, min_e_mwh=0, max_e_mwh=0.2, q_mvar=0, soc_percent=50, controllable=True)

# Ajouter un générateur photovoltaïque
pv = pp.create_sgen(net, bus=1, p_mw=0.05, q_mvar=0, type='PV')

# Ajouter une connexion entre la batterie et le générateur photovoltaïque
pp.create_line(net, from_bus=1, to_bus=2, length_km=0.01, std_type='NAYY 4x150 SE', name='battery_pv_connection')

# Ajouter une connexion entre le générateur photovoltaïque et la charge
pp.create_line(net, from_bus=1, to_bus=2, length_km=0.01, std_type='NAYY 4x150 SE', name='pv_load_connection')

# Ajouter une connexion entre la batterie et la charge
pp.create_line(net, from_bus=1, to_bus=2, length_km=0.01, std_type='NAYY 4x150 SE', name='battery_load_connection')

# Résoudre le réseau électrique
pp.runpp(net)

# Afficher la puissance de charge/décharge de la batterie
print("Puissance de charge/décharge de la batterie : ", net.storage.p_mw.values[0])

# Afficher la puissance générée par le générateur photovoltaïque
print("Puissance générée par le générateur photovoltaïque : ", net.sgen.p_mw.values[0])
