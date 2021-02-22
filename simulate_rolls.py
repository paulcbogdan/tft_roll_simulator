from random import random
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from matplotlib import colors
from tqdm import tqdm

class Lobby_Units:
    def __init__(self):

        self.chosen_odds = 0.5
        self.num_units = {1: 13, 2: 13, 3: 13, 4: 11, 5: 8}
        self.pool_sizes = {1: 29, 2: 22, 3: 18, 4: 12, 5: 10}
        self.roll_odds = {1: {1: 1.0},
                          2: {1: 1.0},
                          3: {1: 0.75, 2: 0.25},
                          4: {1: 0.55, 2: 0.30, 3: 0.15},
                          5: {1: 0.45, 2: 0.33, 3: 0.20, 4: 0.02},
                          6: {1: 0.35, 2: 0.35, 3: 0.25, 4: 0.05},
                          7: {1: 0.22, 2: 0.35, 3: 0.30, 4: 0.12, 5: 0.01},
                          8: {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.20, 5: 0.05},
                          9: {1: 0.10, 2: 0.15, 3: 0.30, 4: 0.30, 5: 0.15}}

        self.pool_org = {}
        self.pool = {}

        for i in range(1, 6):
            cost_pool_org = {}
            cost_pool = []
            for chr_num in range(65, 65+self.num_units[i]):
                cost_pool_org[str(i) + chr(chr_num)] = self.pool_sizes[i]
                cost_pool.extend([str(i) + chr(chr_num)]*self.pool_sizes[i])
            self.pool_org[i] = cost_pool_org
            self.pool[i] = cost_pool

    def get_shop_unit(self, level, is_chosen=False, shop_unit_indices=None):
        # this shop_unit_indices captures cases where the exact same unit index is pulled twice by the shop
        # very rare edge case
        if is_chosen:
            roll_odds = self.roll_odds[level]
        else:
            roll_odds = self.roll_odds[level]
        rnd = random()
        running_thresh = 0
        for cost in range(1, 6):
            running_thresh += roll_odds[cost]
            if rnd < running_thresh:
                break
        cost_pool = self.pool[cost]
        rnd_unit_idx = None
        while (rnd_unit_idx is None) or (rnd_unit_idx in shop_unit_indices):
            rnd_unit_idx = int(random()*len(cost_pool))
            unit = cost_pool[rnd_unit_idx]
            unit = unit + 'X' if is_chosen else unit
        return unit, rnd_unit_idx

    def buy(self, unit, is_chosen=False, buy_cnt=None):
        cost = int(unit[0])
        if buy_cnt is not None:
            for _ in range(buy_cnt):
                self.pool[cost].remove(unit)
        elif is_chosen or 'X' in unit:
            unit = unit.replace('X', '')
            for _ in range(3):
                self.pool[cost].remove(unit)
        else:
            #print('-', unit)
            #print(self.pool)
            self.pool[cost].remove(unit)

    def get_full_shop(self, level, have_chosen=False):
        shop_units = []
        shop_units_indices = []
        has_chosen = (random() < self.chosen_odds) and (not have_chosen)
        if has_chosen:
            shop_units.append(self.get_shop_unit(level, is_chosen=True))
        for _ in range(5-int(has_chosen)):
            shp_rnd_unit, unit_idx = self.get_shop_unit(level, shop_unit_indices=shop_units_indices)
            shop_units.append(shp_rnd_unit)
            shop_units_indices.append(unit_idx)
        return shop_units

    def get_remaining(self, cost, consumed):
        max_pool = self.pool_sizes[cost]
        return max_pool - consumed

    def consume_random(self, cost, number):
        while number > 0:
            rnd_unit_num = 1+int(random()*(self.pool_sizes[cost]-2)) # avoids the A units, which are the target
            rnd_unit_letter = chr(65+rnd_unit_num)
            rnd_unit = str(cost) + rnd_unit_letter
            if rnd_unit not in self.pool[cost]:
                continue
            self.buy(rnd_unit)
            number -= 1

def sim_getting_target(level, cost):
    target_unit = str(cost) + 'A'
    #LU.buy(target_unit + 'X', is_chosen=True)
    LU.buy(target_unit, buy_cnt=NUM_UNITS_STARTING + OTHERS_HAVE)
    target_cnt = NUM_UNITS_STARTING
    for roll in range(1, 201):
        shop_units = LU.get_full_shop(level, have_chosen=True)
        shop_target_cnt = shop_units.count(target_unit)
        target_cnt += shop_target_cnt
        for _ in range(shop_target_cnt):
            LU.buy(target_unit, is_chosen=False)
        if target_cnt >= TARGET_NUMBER_OF_UNITS:
            break
    return roll

def sim_4cost():
    LEVEL = 7
    TARGET = '4A'
    TARGET_CNT = 0
    for roll in range(10):
        shop_units = LU.get_full_shop(LEVEL)
        shop_target_cnt = shop_units.count(TARGET)
        TARGET_CNT += shop_target_cnt
        print(TARGET_CNT)

def darken_color(color, mod=0.15):
    if isinstance(color, str):
        color = colors.to_rgb(color)
    return tuple([x-mod if x > mod*2 else x/2 for x in color])


def add_horz(percentile, all_sim_vals, color='k'):
    breakpoint = all_sim_vals[int(len(all_sim_vals)*percentile)]
    plt.plot([0, len(all_sim_vals)], [breakpoint, breakpoint], color=color, linestyle='--')
    color = darken_color(color)
    plt.annotate('{val} ({p:.0%})'.format(val=breakpoint, p=percentile),
                 (int(len(all_sim_vals)*percentile), breakpoint+1), fontsize=15,
                 ha='right', va='bottom', color=color)

NUM_SIMS = 2500
NUM_X_TICKS = 10
NUM_UNITS_STARTING = 8
TARGET_NUMBER_OF_UNITS = 9
UNIT_COST_TARGET = 1
CURRENT_LEVEL = 5
OTHERS_HAVE = 5

NUMBER_OF_OTHERS_CONSUMED = 50

LU = Lobby_Units()


REMAINING_IN_POOL = LU.get_remaining(UNIT_COST_TARGET, NUM_UNITS_STARTING + OTHERS_HAVE)
ADDITIONAL_NEEDED = TARGET_NUMBER_OF_UNITS - NUM_UNITS_STARTING

print('Number available =', REMAINING_IN_POOL)
assert REMAINING_IN_POOL >= ADDITIONAL_NEEDED, 'There are not enough units in the pool for this!'


if __name__ == '__main__':
    all_sim_vals = []
    for sim in tqdm(range(NUM_SIMS)):
        LU = Lobby_Units()
        LU.consume_random(UNIT_COST_TARGET, NUMBER_OF_OTHERS_CONSUMED)
        rolls_needed = sim_getting_target(CURRENT_LEVEL, UNIT_COST_TARGET)
        all_sim_vals.append(rolls_needed)
    all_sim_vals.sort()
    add_horz(0.25, all_sim_vals, color='g')
    add_horz(0.5, all_sim_vals, color='orange')
    add_horz(0.75, all_sim_vals, color='r')
    add_horz(0.9, all_sim_vals, color='maroon')

    #all_sim_vals = savgol_filter(all_sim_vals, NUM_SIMS//50+1, 1)
    plt.plot(all_sim_vals)
    plt.title('lvl = {lvl:}. Have = {have} (${cost:}) units. Others have = {other} ({oany}). Need = {needed} more'.format(
                lvl=CURRENT_LEVEL,
                cost=UNIT_COST_TARGET,
                have=NUM_UNITS_STARTING,
                other=OTHERS_HAVE,
                oany=NUMBER_OF_OTHERS_CONSUMED,
                needed=TARGET_NUMBER_OF_UNITS-NUM_UNITS_STARTING))
    x_tick_spots = [x for x in range(0, NUM_SIMS + 1, int(NUM_SIMS/NUM_X_TICKS))]
    x_tick_labels = ['{:.0%}'.format(x/100) for x in range(0, 101, 100 // NUM_X_TICKS)]

    plt.ylabel('Number of rolls needed')
    plt.xticks(ticks=x_tick_spots, labels=x_tick_labels)
    plt.xlabel('Percentile (0% = ideal, 100% = worst)')
    plt.grid()
    plt.show()
