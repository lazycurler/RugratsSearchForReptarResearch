import argparse

_DEFAULT_SEED = 0x02DCF1A5
_DEFAULT_MULTIPLIER = 0x343FD
_DEFAULT_INCREMENT = 0x0269EC3
_DEFAULT_MODULUS = 1 << 32

class RugratsRand():
    DEFAULT_SEED = _DEFAULT_SEED
    DEFAULT_MULTIPLIER = _DEFAULT_MULTIPLIER
    DEFAULT_INCREMENT = _DEFAULT_INCREMENT
    DEFAULT_MODULUS = _DEFAULT_MODULUS
    # First three random numbers numbers observed in game during startup
    # 0x07cae9d4
    # 0xc5831547
    # 0xc1193aee

    def __init__(self, seed: int=DEFAULT_SEED):
        self.seed = seed
        self.multiplier = self.DEFAULT_MULTIPLIER
        self.increment = self.DEFAULT_INCREMENT
        self.modulus = self.DEFAULT_MODULUS


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
    def lookup32(seed, multiplier=_DEFAULT_MULTIPLIER, increment=_DEFAULT_INCREMENT, modulus=_DEFAULT_MODULUS):
        return (seed * multiplier + increment) % modulus

    @staticmethod
    def lookup8(seed, multiplier=_DEFAULT_MULTIPLIER, increment=_DEFAULT_INCREMENT, modulus=_DEFAULT_MODULUS):
        next_val = RugratsRand.lookup32(seed, multiplier, increment, modulus)
        return ((next_val >> 0x10) & 0xFF)


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
    parser.add_argument("-i", "--start_seed", help="Seed to start with. Overridden by hex_start_seed", type=int, default=_DEFAULT_SEED)
    parser.add_argument("-x", "--hex_start_seed", help="Seed to start with expected in LE order. Overrides (int) start_seed", type=str, default=None)
    parser.add_argument("-l", "--length", help="Number of random numbers to print", type=int, default=100)
    parser.add_argument("-b", "--print_byte", help="If True, prints the single byte version (as opposed to default 4)", default=False, action="store_true")
    args = parser.parse_args()

    # hacky override of the start_seed parameter to provide the option of int or hex
    if args.hex_start_seed is not None:
        args.start_seed =  int(args.hex_start_seed, 16)

    main(args.start_seed, args.length, args.print_byte)
