import pulp as pl
import numpy as np
import matplotlib.pyplot as plt

def BooleanVariable(name):
  return pl.LpVariable(name, 0, 1, cat='Integer')

class BatteryStorage:
    def __init__(self, capacity=4, chargeRate=50, initialCharge=0, degradationCost=0.1):
        self.capacity = capacity
        self.chargeRate = chargeRate
        self.initialCharge = initialCharge
        self.degradationCost = degradationCost

    def register(self, solver, prefix):
        self.solver = solver
        self.prefix = prefix
        self.charging = [BooleanVariable(f"C_{prefix}_{t}") for t in range(solver.T)]
        self.discharging = [BooleanVariable(f"D_{prefix}_{t}") for t in range(solver.T)]

    @property
    def T(self): return self.solver.T

    @property
    def usageCost(self):
        return self.degradationCost * (pl.lpSum(self.charging) + pl.lpSum(self.discharging))

    @property
    def constraints(self):
        constraints = []
        constraints += [0 <= C <= 1 for C in self.charging]
        constraints += [0 <= D <= 1 for D in self.discharging]
        for Ti in range(self.T+1):
            numCharges = pl.lpSum([self.charging[t] - self.discharging[t] for t in range(Ti)])
            currentCharge = self.initialCharge + numCharges
            constraints.append(currentCharge >= 0) # can't have negative charge
            constraints.append(currentCharge <= self.capacity) # can't charge over capacity
        return constraints

    @property
    def cost(self):
        electricityCost = pl.lpSum([
            self.solver.tariffRates[t] * self.chargeRate * (
                self.charging[t] -
                self.solver.netMeteringRate * self.discharging[t])
            for t in range(self.T)])

        return electricityCost + self.usageCost

    @property
    def finalCharge(self):
        return self.initialCharge + pl.lpSum([self.charging[t] - self.discharging[t] for t in range(self.T)])

    @property
    def chargeDischargeSchedule(self):
        prefix = self.prefix
        solution = self.solver.solution
        assert len(solution)
        return [solution[f"C_{prefix}_{t}"] - solution[f"D_{prefix}_{t}"] for t in range(self.T)]


class ElectricVehicle(BatteryStorage):
    @property
    def constraints(self):
        return super().constraints + [
            self.finalCharge == self.capacity
        ]

class ResidentialSolver:
    def __init__(self,
            ders,
            tariffRates = [0.1, 0.1, 0.2, 0.3, 0.5, 0.7, 0.6, 0.4, 0.05, 0.05],
            elecUsage = [50, 50, 75, 75, 75, 100, 100, 100, 100, 75],
            netMeteringDepreciation = 0.0):

        assert len(tariffRates) == len(elecUsage)

        self.T = len(tariffRates)
        self.tariffRates = tariffRates
        self.elecUsage = elecUsage
        self.netMeteringRate = 1 - netMeteringDepreciation
        self.ders = ders

        self.prob = pl.LpProblem("DER_Solver", pl.LpMinimize)

        for i, der in enumerate(ders): der.register(self, i)

        self.prob += pl.lpSum(
            [tariffRates[t] * elecUsage[t] for t in range(self.T)] +
            [der.cost for der in ders]
        )

        for der in ders:
            for constraint in der.constraints:
                self.prob += constraint

        self.solution = {}

    def solve(self, **kwargs):
        self.prob.solve(**kwargs)
        if pl.LpStatus[self.prob.status] == "Optimal":
            for v in self.prob.variables():
                self.solution[v.name] = v.varValue
        else:
            for v in self.prob.variables():
                self.solution[v.name] = np.nan
        return self

    @property
    def status(self):
        return pl.LpStatus[self.prob.status]

    @property
    def finalCost(self):
        return pl.value(self.prob.objective)

    def plot_solution(self):
        plt.plot(self.tariffRates, label="Tariff")
        if self.status != 'Optimal':
          plt.title(f"WARNING: failed to solve\n(status = {self.status})")
        for i, der in enumerate(self.ders):
            plt.plot(der.chargeDischargeSchedule,
                    label=f"DER #{i+1} ({der.__class__.__name__})",
                     marker='o')
        plt.yticks([-1,0,1],['Discharging\nback into grid', '', 'Charging\nbattery'])
        plt.legend()
