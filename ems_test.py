import energy_management_system as ems

# Création du panneau solaire
pv = ems.PV(Pmax=500, Vmp=48)

# Création de la batterie
battery = ems.Battery(Q=1000, V=48, capacity=100, eta_c=0.9, eta_d=0.9)

# Création de la charge
load = ems.Load(Pmin=0, Pmax=500)

# Création de la règle d'optimisation
rule = ems.OptimizationRule()

# Ajout des composants au système
system = ems.System()
system.add_components(pv, battery, load)

# Définition des flux de puissance
pv_to_battery = ems.Flow(pv, battery, rule, 'PV to Battery')
battery_to_load = ems.Flow(battery, load, rule, 'Battery to Load')

# Ajout des flux de puissance au système
system.add_flows(pv_to_battery, battery_to_load)

# Définition des objectifs d'optimisation
system.set_objective(ems.Objective.Minimize, ems.FlowCost(pv_to_battery) + ems.FlowCost(battery_to_load))

# Résolution de la règle d'optimisation
solution = ems.solve(rule)

# Affichage des résultats
print(f"PV production: {pv.P:.2f} W")
print(f"Battery charge: {battery.Q:.2f} Ah")
print(f"Load consumption: {load.P:.2f} W")
