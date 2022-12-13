import argparse

DEFAULT_SEED = 0x02DCF1A5
DEFAULT_MULTIPLIER = 0x343FD
DEFAULT_INCREMENET = 0x0269EC3
DEFAULT_MODULUS = 1 << 32

class RugratsRand():
    # First three random numbers numbers observed in game during startup
    # 0x07cae9d4
    # 0xc5831547
    # 0xc1193aee

    def __init__(self, seed: int=DEFAULT_SEED):
        self.seed = seed
        self.multiplier = DEFAULT_MULTIPLIER
        self.increment = DEFAULT_INCREMENET
        self.modulus = DEFAULT_MODULUS


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


def main(start_seed: int, length: int, print_byte: bool):
    rand = RugratsRand(seed=start_seed)

    print("\n")
    for i in range(length):
        if print_byte:
            print(f'{i:>3}) 0x{rand.next8():02X}')
        else:
            print(f'{i:>3}) 0x{rand.next32():08X}')
    print("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--start_seed", help="Seed to start with. Overriden by hex_start_seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("-x", "--hex_start_seed", help="Seed to start with expected in LE order. Overrides (int) start_seed", type=str, default=None)
    parser.add_argument("-l", "--length", help="Number of random numbers to print", type=int, default=100)
    parser.add_argument("-b", "--print_byte", help="If True, prints the single byte version (as opposed to default 4)", default=False, action="store_true")
    args = parser.parse_args()

    # hacky override of the start_seed parameter to provide the option of int or hex
    if args.hex_start_seed is not None:
        args.start_seed =  int(args.hex_start_seed, 16)

    main(args.start_seed, args.length, args.print_byte)
