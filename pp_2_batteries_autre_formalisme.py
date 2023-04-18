import pandapower as pp
import numpy as np
import random

net = pp.create_empty_network()

# Création des bus :
bus1 = pp.create_bus(net, vn_kv=0.4, name='Générateur')  # pour le générateur et grid
bus2 = pp.create_bus(net, vn_kv=0.4, name='Stockage1')  # pour les stockages
bus3 = pp.create_bus(net, vn_kv=0.4, name='Stockage2')  # pour le stockage 1
bus4 = pp.create_bus(net, vn_kv=0.4, name='Charge')  # pour le stockage 2
bus5 = pp.create_bus(net, vn_kv=0.4, name='Charge')  # pour la charge

# Création des composants
pp.create_ext_grid(net, bus=1, vm_pu=1.0, va_degree=0)

pv = pp.create_sgen(net, bus=bus1, p_mw=0.05, index=1, q_mvar=0, type='PV', slack=True)  # Ajouter un PV

storage1 = pp.create_storage(net, bus=bus2, p_mw=0.00, index=2, min_p_mw=-0.1, max_p_mw=0.05, min_e_mwh=0, max_e_mwh=0.2,
                             q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1, soc_percent=50, controllable=True)
storage2 = pp.create_storage(net, bus=bus3, p_mw=0.00, index=3, min_p_mw=-0.1, max_p_mw=0.05, min_e_mwh=0, max_e_mwh=0.2,
                             q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1, soc_percent=50, controllable=True)

load1 = pp.create_load(net, bus=bus4, p_mw=0.02, index=3,  q_mvar=0.1)  # Ajouter une charge à la maison


# LINE1 : Ajouter une connexion entre le front de batteries et le générateur photovoltaïque
line1 = pp.create_line(net, from_bus=bus1, to_bus=bus2, length_km=0.01, std_type='NAYY 4x50 SE', name='line1')
sw1 = pp.create_switch(net, bus=bus1, element=line1, et='l', closed=True)

# LINE2 : Ajouter une connexion entre le bus 2 et bus 3 (batterie1)
line2 = pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=0.01, std_type='NAYY 4x50 SE', name='line2')
sw2 = pp.create_switch(net, bus=bus2, element=line2, et='l', closed=True)

# LINE3 : Ajouter une connexion entre le bus 2 et bus 4 (batterie2)
line3 = pp.create_line(net, from_bus=bus2, to_bus=bus4, length_km=0.01, std_type='NAYY 4x50 SE', name='line3')
sw3 = pp.create_switch(net, bus=bus4, element=line3, et='l', closed=True)

# LINE4 : Ajouter une connexion entre la batterie2 et la charge
line4 = pp.create_line(net, from_bus=bus3, to_bus=bus4, length_km=0.01, std_type='NAYY 4x50 SE', name='line4')
sw4 = pp.create_switch(net, bus=bus3, element=line4, et='l', closed=True)

# LINE5 : Ajouter une connexion entre le pv et la charge
line5 = pp.create_line(net, from_bus=bus1, to_bus=bus4, length_km=0.01, std_type='NAYY 4x50 SE', name='line5')
sw5 = pp.create_switch(net, bus=bus1, element=line5, et='l', closed=True)

# LINE6 : Ajouter une connexion entre les deux batteries
line6 = pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=0.01, std_type='NAYY 4x50 SE', name='line6')
sw6 = pp.create_switch(net, bus=bus2, element=line6, et='l', closed=True)

pp.runpp(net)
