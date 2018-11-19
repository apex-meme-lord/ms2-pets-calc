import curses


D_BONUS = 3000


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
        market = 5000
    class Rare(Rarity):
        exp = 3000
        cost = 5000
        market = 50000
    class Exceptional(Rarity):
        exp = 12000
        cost = 10000
        market = 400000
    class Epic(Rarity):
        __metaclass__ = _EpicNope
        cost = 30000


class PetCalculator(object):
    def __init__(self, target):
        if not issubclass(target, Pet.Rarity):
            raise Exception("Must provide target pet rarity")
        self.target = target
        self.exp = 0
        self.cost = 0
        self.last_exp = 0
        self.last_cost = 0
        self.bonus = 24
        self.multi = 1.0
        self.count = {
            Pet.Normal: 0,
            Pet.Rare: 0,
            Pet.Exceptional: 0,
            Pet.Epic: 0
        }

    def fuse(self, fodder):
        self.last_exp = 0

        if self.bonus:
            self.last_exp += D_BONUS
            self.bonus -= 1

        elif self.multi > 0.2:
            self.multi -= 0.02

        self.last_exp += self.multi * getattr(fodder, 'exp')
        self.count[fodder] += 1
        self.last_cost = getattr(self.target, 'cost') + getattr(fodder, 'market')
        self.cost += self.last_cost
        self.exp += self.last_exp


if __name__ == "__main__":
    calc = PetCalculator(Pet.Normal)        

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

            stdscr.addstr(height - 4, 0, "1 for normal, 2 for rare, 3 for exceptional, 'q' to quit")
            
            stdscr.refresh()

            k = stdscr.getch()

    main_loop()
