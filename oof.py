import curses


class _EpicNope(type):
    def __getattr__(cls, key):
        if key in ('exp', 'market'):
            raise Exception("Nobody would fuse an epic lol")
        else:
            raise AttributeError


class Pet(object):
    class Rarity(object):
        pass

    class Normal(Rarity):
        exp = 1500
        cost = 3000

        # change this value to match market rate of normal pets
        market = 5000

        per_level = 22000

    class Rare(Rarity):
        exp = 3000
        cost = 5000

        # change this value to match market rate of rare pets
        market = 40000

        per_level = 55000

    class Exceptional(Rarity):
        exp = 12000
        cost = 10000

        # change this value to match market rate of exceptional pets
        market = 650000

        per_level = 90000

    class Epic(Rarity):
        __metaclass__ = _EpicNope
        cost = 30000
        per_level = 90000


D_BONUS = 3000


TARGET_PET_RARITY = Pet.Epic  # change this value to match your main pet


class PetCalculator(object):
    def __init__(self, target, bonus=24, multi=1.0):
        if not issubclass(target, Pet.Rarity):
            raise Exception("Must provide target pet rarity")
        self.target = target
        self.exp = 0
        self.cost = 0
        self.last_exp = 0
        self.last_cost = 0
        self.bonus = bonus
        self.multi = multi
        self.count = {
            Pet.Normal: 0,
            Pet.Rare: 0,
            Pet.Exceptional: 0,
            Pet.Epic: 0
        }

    def stage_fuse(self, fodder):
        last_exp = 0
        last_cost = 0

        if self.bonus:
            last_exp += D_BONUS

        last_exp += self.multi * getattr(fodder, 'exp')
        last_cost = getattr(self.target, 'cost') + getattr(fodder, 'market')
        return last_exp, last_cost

    def do_fuse(self, fodder, last_exp, last_cost):
        if self.bonus:
            self.bonus -= 1

        elif self.multi > 0.2:
            self.multi -= 0.02

        self.count[fodder] += 1
        self.cost += last_cost
        self.exp += last_exp

    def fuse(self, fodder):
        self.last_exp, self.last_cost = self.stage_fuse(fodder)
        self.do_fuse(fodder, self.last_exp, self.last_cost)

    def fuse_proxy_into(self, into, fodder):
        proxy = PetCalculator(into, self.bonus, self.multi)
        while 1:
            last_exp, last_cost = proxy.stage_fuse(fodder)
            if proxy.exp + last_exp > getattr(into, 'per_level'):
                break
            proxy.do_fuse(fodder, last_exp, last_cost)

        self.fuse(into)
        self.last_exp += proxy.exp * 0.8
        self.last_cost += proxy.cost
        self.exp += proxy.exp * 0.8
        self.cost += proxy.cost
        self.bonus = proxy.bonus
        self.multi = proxy.multi
        for rarity in proxy.count:
            self.count[rarity] += proxy.count[rarity]


if __name__ == "__main__":
    calc = PetCalculator(TARGET_PET_RARITY)

    def main_loop():
        k = 0
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()

        while k != ord('q'):

            if k == ord('1'):
                calc.fuse(Pet.Normal)

            if k == ord('2'):
                calc.fuse(Pet.Rare)

            if k == ord('3'):
                calc.fuse(Pet.Exceptional)

            if k == ord('4'):
                calc.fuse_proxy_into(Pet.Normal, Pet.Normal)

            if k == ord('5'):
                calc.fuse_proxy_into(Pet.Rare, Pet.Normal)

            stdscr.clear()
            height, width = stdscr.getmaxyx()

            stdscr.addstr(0, 0, "Exp: {} (+{})".format(calc.exp, calc.last_exp))
            stdscr.addstr(1, 0, "Cost (in mesos): {} (+{})".format(calc.cost, calc.last_cost))
            stdscr.addstr(2, 0, "Last Cost/exp (in mesos): {}".format(calc.last_cost / (calc.last_exp or 1)))
            stdscr.addstr(3, 0, "Bonus remaining: {}".format(calc.bonus))
            stdscr.addstr(4, 0, "Multiplier: {}".format(calc.multi))
            stdscr.addstr(7, 0, "Fused: {} normal, {} rare, {} exceptional".format(
                calc.count[Pet.Normal],
                calc.count[Pet.Rare],
                calc.count[Pet.Exceptional],
            ))

            stdscr.addstr(height - 10, 0, "1 for normal, 2 for rare, 3 for exceptional")
            stdscr.addstr(height - 9, 0, "4 for normal proxied into normal (fusing a normal proxy pet to almost level 2 before fusing into your main pet)")
            stdscr.addstr(height - 8, 0, "5 for normal proxied into rare (fusing a rare proxy pet to almost level 2 before fusing into your main pet)")
            stdscr.addstr(height - 7, 0, "'q' to quit")
            
            stdscr.refresh()

            k = stdscr.getch()

    main_loop()
