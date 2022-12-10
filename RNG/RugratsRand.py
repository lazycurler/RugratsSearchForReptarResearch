class RugratsRand():
    # First three random numbers numbers observed in game during startup
    # 0x07cae9d4
    # 0xc5831547
    # 0xc1193aee

    DEFAULT_SEED = 0x02DCF1A5
    DEFAULT_MULTIPLIER = 0x343FD
    DEFAULT_INCREMENET = 0x0269EC3
    DEFAULT_MODULUS = 1 << 32

    def __init__(self, seed=DEFAULT_SEED):
        self.seed = seed
        self.multiplier = RugratsRand.DEFAULT_MULTIPLIER
        self.increment = RugratsRand.DEFAULT_INCREMENET
        self.modulus = RugratsRand.DEFAULT_MODULUS


    def peek32(self):
        return (self.seed * self.multiplier + self.increment) % self.modulus

    def peek8(self):
        return ((self.peek32() >> 0x10) & 0xFF)

    def next32(self):
        self.seed = (self.seed * self.multiplier + self.increment) % self.modulus
        return self.seed
    
    def next8(self):
        return ((self.next32() >> 0x10) & 0xFF)


    @staticmethod
    def lookup32(seed, multiplier=DEFAULT_MULTIPLIER, increment=DEFAULT_INCREMENET, modulus=DEFAULT_MODULUS):
        return (seed * multiplier + increment) % modulus

    @staticmethod
    def lookup8(seed, multiplier=DEFAULT_MULTIPLIER, increment=DEFAULT_INCREMENET, modulus=DEFAULT_MODULUS):
        next = RugratsRand.lookup32(seed, multiplier, increment, modulus)
        return ((next >> 0x10) & 0xFF)


def main():
    rand = RugratsRand()

    print("\n")
    for _ in range(10):
        print(f'0x{rand.next32():02X}')
    print("\n")

if __name__ == "__main__":
    main()
