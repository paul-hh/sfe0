class Battery:
    def __init__(self, capacity, voltage, charge):
        self.capacity = capacity  # capacité en Ah
        self.voltage = voltage  # tension en V
        self.charge = charge  # charge actuelle

    def discharge(self, current, time):
        # Décharge la batterie en fonction du courant et du temps
        discharged = current * time
        self.charge -= discharged
        if self.charge < 0:
            self.charge = 0

        return discharged

    def recharge(self, current, time):
        # Recharge la batterie en fonction du courant et du temps
        charged = current * time / 1000.0  # convertit courant de mA en A et temps en h
        self.charge += charged
        if self.charge > self.capacity:
            self.charge = self.capacity


        return charged

    def set_charge(self, charge):
        self.charge = charge

    def get_charge(self):
        return self.charge


class Source:
    def __init__(self, voltage=48):
        self.voltage = voltage

    def set_voltage(self, voltage):
        self.voltage = voltage

    def get_voltage(self):
        return self.voltage

    def get_current(self, resistance):
        return self.voltage / resistance / 2


class Resistor:
    def __init__(self, resistance):
        self.resistance = resistance

    def set_resistance(self, resistance):
        self.resistance = resistance

    def get_resistance(self):
        return self.resistance
