from RugratsRand import RugratsRand
import matplotlib.pyplot as plt

rands = []
cycle = []
rand = RugratsRand()
for i in range(1000):
    rands.append(rand.next8())
    cycle.append(i)

plt.scatter(cycle, rands)
plt.plot(cycle, rands)
plt.show()