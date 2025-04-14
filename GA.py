import random
import re
import matplotlib.pyplot as plot
from collections import defaultdict

# Check if a date string is valid in DD/MM/YYYY format
def valid8Date(date_str):
    """
    Checks if the given date string is in DD/MM/YYYY format.
    Returns True if its valid, false otherwise.
    """
    # Check the format using regex
    if not re.match(r'^(\d{2}/\d{2}/\d{4})$', date_str):
        return False
    try:
        d_str, m_str, y_str = date_str.split("/")
        d = int(d_str)
        m = int(m_str)
        y = int(y_str)
    except ValueError:
        return False  # non-int values? no good!
    if y < 0 or y > 9999:
        return False
    if m < 1 or m > 12:
        return False
    if d < 1:
        return False
    # Check days per month
    if m in (4, 6, 9, 11) and d > 30:
        return False
    elif m == 2:
        leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
        max_day = 29 if leap else 28
        if d > max_day:
            return False
    else:
        if d > 31:
            return False
    return True


# Categorize the date based on its properties
def categore_date(d, m, y):
    """
    Categorizes a date into types (boundary, valid, invalid, etc.).
    Returns a tuple: (category, is_valid)
    """
    ds = f"{d:02d}/{m:02d}/{y:04d}"
    is_val = valid8Date(ds)
    
    # Boundary cases
    if (d, m, y) == (1, 1, 0):
        return "Boundary (Min Date)", is_val
    elif (d, m, y) == (31, 12, 9999):
        return "Boundary (Max Date)", is_val
    elif d == 1 and m == 1:
        return "Boundary (First Day of Year)", is_val
    elif d == 31 and m == 12:
        return "Boundary (Last Day of Year)", is_val

    leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
    if m == 2 and d == 29:
        if leap:
            if y % 400 == 0:
                return "Valid (Leap Year - Divisible by 400)", is_val
            return "Valid (Leap Year)", is_val
        else:
            if y % 100 == 0:
                return "Invalid (Non-Leap Century Year)", is_val
            return "Invalid (Feb 29 in Non-Leap)", is_val

    if m in [4, 6, 9, 11]:
        if d > 30:
            return f"Invalid (Day > 30 in {m})", is_val
        elif d == 30:
            return "Valid (30-Day Month)", is_val
    elif m in [1, 3, 5, 7, 8, 10, 12]:
        if d == 31:
            return "Valid (31-Day Month)", is_val
        elif d > 31:
            return f"Invalid (Day > 31 in {m})", is_val
    elif m == 2:
        if d > 29:
            return "Invalid (Day > 29 in Feb)", is_val
        elif d == 28:
            return "Valid (Feb 28)", is_val

    if m > 12:
        return "Invalid (Month > 12)", is_val
    if d > 31:
        return "Invalid (Day > 31)", is_val
    elif d < 1:
        return "Invalid (Day < 1)", is_val

    return "Valid (General Date)", is_val


# GA Component 1: Chromosome representation for a date
class DateChromo:
    def __init__(self, d=None, m=None, y=None):
        # Random init if not provided – allow for some invalid ones too
        self.d = d if d is not None else random.randint(1, 35)
        self.m = m if m is not None else random.randint(1, 14)
        self.y = y if y is not None else random.randint(0, 9999)
        # Occasionally force a boundary case
        if random.random() < 0.05:
            b_opts = [
                (1, 1, 0),       # min date
                (31, 12, 9999),  # max date
                (29, 2, 2020),   # valid leap year
                (29, 2, 2021),   # invalid leap year
                (31, 4, 2023)    # invalid April date
            ]
            self.d, self.m, self.y = random.choice(b_opts)
    
    def get_date_str(self):
        return f"{self.d:02d}/{self.m:02d}/{self.y:04d}"
    
    def get_cat(self):
        cat, valid = categore_date(self.d, self.m, self.y)
        return cat, valid
    
    def mutate(self, mut_rate=0.15):
        """Mutates the date values with given probability"""
        if random.random() < mut_rate:
            mut_type = random.randint(0, 2)
            if mut_type == 0:  # change day
                self.d += random.randint(-3, 3)
                self.d = max(1, min(35, self.d))
            elif mut_type == 1:  # change month
                self.m += random.randint(-1, 1)
                self.m = max(1, min(14, self.m))
            else:  # change year
                if random.random() < 0.8:
                    self.y += random.randint(-10, 10)
                else:
                    self.y = random.choice([0, 9999, self.y + random.randint(-1000, 1000)])
                self.y = max(0, min(9999, self.y))
        return self


# GA Component 2: Population management & GA core
class GenAlg:
    def __init__(self, pop_size=100, mut_rate=0.15):
        self.pop_size = pop_size
        self.mut_rate = mut_rate
        self.pop = []
        self.best_cases = {'Valid': {}, 'Invalid': {}, 'Boundary': {}}
        self.cov_hist = []
        self.cats_cov = set()
    
    def initPop(self):
        """Create initial random population"""
        self.pop = [DateChromo() for _ in range(self.pop_size)]
    
    def calcFit(self, chromo):
        cat, valid = chromo.get_cat()
        unique = cat not in self.cats_cov
        if unique:
            return 10  # high reward for new category
        else:
            return 0.1  # low reward for redundancy
    
    def selParents(self):
        fits = [(c, self.calcFit(c)) for c in self.pop]
        fits.sort(key=lambda x: x[1], reverse=True)
        top_n = int(0.2 * len(fits))
        top = [fits[i][0] for i in range(top_n)]
        rest = [fits[i][0] for i in range(top_n, len(fits))]
        if rest:
            rest_sel = random.sample(rest, min(top_n, len(rest)))
        else:
            rest_sel = []
        return top + rest_sel
    
    def doCross(self, p1, p2):
        cp = random.randint(0, 2)
        if cp == 0:
            child1 = DateChromo(p1.d, p2.m, p2.y)
            child2 = DateChromo(p2.d, p1.m, p1.y)
        elif cp == 1:
            child1 = DateChromo(p2.d, p1.m, p2.y)
            child2 = DateChromo(p1.d, p2.m, p1.y)
        else:
            child1 = DateChromo(p2.d, p2.m, p1.y)
            child2 = DateChromo(p1.d, p1.m, p2.y)
        return child1, child2
    
    def updBest(self, chromo):
        cat, valid = chromo.get_cat()
        ds = chromo.get_date_str()
        if "Boundary" in cat:
            typ = "Boundary"
        elif valid:
            typ = "Valid"
        else:
            typ = "Invalid"
        if cat not in self.best_cases[typ]:
            self.best_cases[typ][cat] = ds
    
    def runGen(self):
        # Evaluate current population and update best cases
        for c in self.pop:
            cat, valid = c.get_cat()
            self.cats_cov.add(cat)
            self.updBest(c)
        parents = self.selParents()
        new_pop = []
        # Elitism: keep top 10% unchanged
        fits = [(c, self.calcFit(c)) for c in self.pop]
        fits.sort(key=lambda x: x[1], reverse=True)
        elite_count = int(0.1 * self.pop_size)
        elites = [fits[i][0] for i in range(elite_count)]
        new_pop.extend(elites)
        while len(new_pop) < self.pop_size:
            p1, p2 = random.sample(parents, 2)
            child1, child2 = self.doCross(p1, p2)
            child1.mutate(self.mut_rate)
            child2.mutate(self.mut_rate)
            new_pop.append(child1)
            new_pop.append(child2)
        self.pop = new_pop[:self.pop_size]
        target_cats = 25  # rough target number of categories
        cov = (len(self.cats_cov) / target_cats) * 100
        self.cov_hist.append(cov)
        return cov
    
    def runGA(self, max_gens=100, targ_cov=95):
        self.initPop()
        for gen in range(max_gens):
            cov = self.runGen()
            if gen % 10 == 0:
                print(f"Gen {gen}: Cov = {cov:.2f}%, Cats = {len(self.cats_cov)}")
            if cov >= targ_cov:
                print(f"Target cov reached at gen {gen}")
                break
        return cov, gen + 1
    
    def plotCovHist(self):
        plot.figure(figsize=(10, 6))
        plot.plot(range(len(self.cov_hist)), self.cov_hist)
        plot.title("Test Coverage Over Gens")
        plot.xlabel("Gen")
        plot.ylabel("Coverage (%)")
        plot.grid(True)
        plot.savefig("coverage_history.png")
        plot.close()
    
    def getBestCases(self, min_valid=10, min_invalid=10, min_bound=5):
        res = {'Valid': [], 'Invalid': [], 'Boundary': []}
        for typ, cases in self.best_cases.items():
            for cat, ds in cases.items():
                res[typ].append((ds, cat))
        # Ensure minimum valid cases
        while len(res['Valid']) < min_valid:
            c = DateChromo()
            cat, valid = c.get_cat()
            if valid:
                res['Valid'].append((c.get_date_str(), cat))
        # Ensure minimum invalid cases
        while len(res['Invalid']) < min_invalid:
            d = random.randint(29, 35)
            m = random.randint(1, 14)
            c = DateChromo(d, m)
            cat, valid = c.get_cat()
            if not valid:
                res['Invalid'].append((c.get_date_str(), cat))
        # Ensure minimum boundary cases
        while len(res['Boundary']) < min_bound:
            b_opts = [
                (1, 1, 0),
                (31, 12, 9999),
                (29, 2, 2020),
                (29, 2, 2100),
                (31, 4, 2023),
                (31, 6, 2023)
            ]
            d, m, y = random.choice(b_opts)
            c = DateChromo(d, m, y)
            cat, valid = c.get_cat()
            if "Boundary" in cat:
                res['Boundary'].append((c.get_date_str(), cat))
        return res


def saveTestCasesToFile(cases, fname='ga_test_cases.csv'):
    with open(fname, 'w') as f:
        f.write("Date,Category,Validity\n")
        for typ, case_list in cases.items():
            for ds, cat in case_list:
                valid_str = "Valid" if valid8Date(ds) else "Invalid"
                f.write(f"{ds},{cat},{valid_str}\n")
    print(f"Test cases saved to {fname}")


def localSearchRefine(cases, max_iter=100):
    # Refine test cases with local search to boost coverage
    covered = set()
    for typ, clist in cases.items():
        for _, cat in clist:
            covered.add(cat)
    res = {
        'Valid': cases['Valid'].copy(),
        'Invalid': cases['Invalid'].copy(),
        'Boundary': cases['Boundary'].copy()
    }
    init_cov = len(covered)
    imp_count = 0
    interesting_d = [0, 1, 28, 29, 30, 31, 32]
    interesting_m = [0, 1, 2, 4, 6, 9, 11, 12, 13]
    interesting_y = [0, 1, 4, 100, 400, 1900, 2000, 2020, 2100, 9999]
    for d in interesting_d:
        for m in interesting_m:
            for y in interesting_y:
                if imp_count >= 10 or len(covered) >= init_cov + 20:
                    break
                new_c = DateChromo(d, m, y)
                new_cat, new_valid = new_c.get_cat()
                if new_cat not in covered:
                    ds = new_c.get_date_str()
                    if "Boundary" in new_cat:
                        typ_new = "Boundary"
                    elif new_valid:
                        typ_new = "Valid"
                    else:
                        typ_new = "Invalid"
                    res[typ_new].append((ds, new_cat))
                    covered.add(new_cat)
                    imp_count += 1
    rem_iter = max_iter - (len(interesting_d) * len(interesting_m) * len(interesting_y))
    for _ in range(rem_iter):
        if imp_count >= 20:
            break
        strat = random.choice(['random', 'boundary', 'mutation'])
        if strat == 'random':
            d = random.randint(0, 35)
            m = random.randint(0, 14)
            y = random.randint(0, 9999)
        elif strat == 'boundary':
            d = random.choice([0, 1, 28, 29, 30, 31, 32])
            m = random.choice([0, 1, 2, 4, 6, 9, 11, 12, 13])
            y = random.choice([0, 1, 4, 100, 400, 1900, 2000, 2020, 2100, 9999])
        else:
            typ_choice = random.choice(['Valid', 'Invalid', 'Boundary'])
            if not res[typ_choice]:
                continue
            idx = random.randint(0, len(res[typ_choice]) - 1)
            ds, _ = res[typ_choice][idx]
            d, m, y = map(int, ds.split('/'))
            d = max(0, min(35, d + random.randint(-2, 2)))
            m = max(0, min(14, m + random.randint(-1, 1)))
            if random.random() < 0.2:
                y = random.choice([0, 1, 4, 100, 400, 1900, 2000, 2020, 2100, 9999])
            else:
                y = max(0, min(9999, y + random.randint(-10, 10)))
        new_c = DateChromo(d, m, y)
        new_cat, new_valid = new_c.get_cat()
        if new_cat not in covered:
            ds = new_c.get_date_str()
            if "Boundary" in new_cat:
                typ_new = "Boundary"
            elif new_valid:
                typ_new = "Valid"
            else:
                typ_new = "Invalid"
            res[typ_new].append((ds, new_cat))
            covered.add(new_cat)
            imp_count += 1
    print(f"Local search added {imp_count} new test cases in {len(covered) - init_cov} new categories")
    return res


def main():
    print("==== Starting Genetic Algorithm for Test Case Generation ====")
    ga = GenAlg(pop_size=100, mut_rate=0.15)
    coverage, gens = ga.runGA(max_gens=100, targ_cov=95)
    test_cases = ga.getBestCases(min_valid=10, min_invalid=10, min_bound=5)
    
    print("\n==== Best Test Cases from Genetic Algorithm ====")
    print(f"Coverage Achieved: {coverage:.2f}%")
    print(f"Generations Executed: {gens}")
    
    print("\nValid Test Cases:")
    for ds, cat in test_cases['Valid'][:5]:
        print(f"{ds} -> {cat}")
    if len(test_cases['Valid']) > 5:
        print(f"... and {len(test_cases['Valid']) - 5} more valid cases")
    
    print("\nInvalid Test Cases:")
    for ds, cat in test_cases['Invalid'][:5]:
        print(f"{ds} -> {cat}")
    if len(test_cases['Invalid']) > 5:
        print(f"... and {len(test_cases['Invalid']) - 5} more invalid cases")
    
    print("\nBoundary Test Cases:")
    for ds, cat in test_cases['Boundary']:
        print(f"{ds} -> {cat}")
    
    saveTestCasesToFile(test_cases, 'ga_test_cases.csv')
    ga.plotCovHist()
    
    ga_cats = set()
    for typ, clist in test_cases.items():
        for _, cat in clist:
            ga_cats.add(cat)
    print(f"\nGenetic Algorithm found {len(ga_cats)} unique categories.")
    
    print("\n==== Refining Test Cases with Local Search ====")
    refined_cases = localSearchRefine(test_cases, max_iter=200)
    refined_cats = set()
    for typ, clist in refined_cases.items():
        for _, cat in clist:
            refined_cats.add(cat)
    new_cats = refined_cats - ga_cats
    print(f"Local Search found {len(new_cats)} additional categories:")
    for cat in new_cats:
        print(f"  - {cat}")
    
    print("\nRefined Test Case Counts:")
    print(f"Valid: {len(refined_cases['Valid'])} (was {len(test_cases['Valid'])})")
    print(f"Invalid: {len(refined_cases['Invalid'])} (was {len(test_cases['Invalid'])})")
    print(f"Boundary: {len(refined_cases['Boundary'])} (was {len(test_cases['Boundary'])})")
    total_before = sum(len(clist) for clist in test_cases.values())
    total_after = sum(len(clist) for clist in refined_cases.values())
    print(f"Total: {total_after} (was {total_before})")
    
    saveTestCasesToFile(refined_cases, 'refined_test_cases.csv')
    
    ga_eff = len(ga_cats) / gens
    comb_eff = len(refined_cats) / (gens + 1)  # +1 for local search iteration
    print("\n==== Effectiveness Comparison ====")
    print(f"GA: {ga_eff:.3f} categories/generation")
    print(f"GA+LocalSearch: {comb_eff:.3f} categories/generation")
    print(f"Improvement: {(comb_eff/ga_eff - 1)*100:.1f}%")

if __name__ == "__main__":
    main()
