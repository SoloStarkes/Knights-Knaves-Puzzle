import random
from typing import List, Any, cast, Optional

# ─────────────────────── Name Sets ───────────────────────

original_name_set = [
    "Elnuman", "Solomon", "Bram", "Sidy", "Drake", "Munzir", "Ajay", "Lebron", 
    "Curry", "Bronny", "Flight", "Cash", "Draymond", "Klay", "Andrew", "Omar", "DJ Khalid"]


def name_set() -> List[str]:
    return original_name_set.copy()

# ─────────────────── Random Utilities ────────────────────

def random_int(n: int) -> int:
    return random.randrange(n)

def random_range(lo: int, hi: int) -> int:
    return random.randrange(lo, hi+1)

def random_element(lst: List[Any]) -> Any:
    return random.choice(lst)

def shuffle(lst: List[Any]) -> List[Any]:
    random.shuffle(lst)
    return lst

# ─────────────── Array / List Utilities ────────────────

def remove_element(lst: List[Any], e: Any) -> List[Any]:
    return [x for x in lst if x is not e]

def array_without(lst: List[Any], e: Any) -> List[Any]:
    return [x for x in lst if x != e]

def arrays_equivalent(a: List[Any], b: List[Any]) -> bool:
    return len(a) == len(b) and all(x in b for x in a)

def add_unique(lst: List[Any], e: Any) -> None:
    if e not in lst:
        lst.append(e)

def add_all_unique(a: List[Any], b: List[Any]) -> List[Any]:
    for x in b:
        if x not in a:
            a.append(x)
    return a

def all_sources_and_targets(islander: "Islander", stmts: List["Statement"]) -> List["Islander"]:
    res: List["Islander"] = [islander]
    for s in stmts:
        if s.source is islander:
            res.append(cast("Islander", s.target))
        if s.target is islander:
            res.append(cast("Islander", s.source))
    return res

def all_reachable(islander: "Islander", stmts: List["Statement"], seen: Optional[List["Islander"]] = None) -> List["Islander"]:
    if seen is None:
        seen = []
    reach = set(seen) | set(all_sources_and_targets(islander, stmts))
    if reach == set(seen):
        return seen
    out: List["Islander"] = list(cast(List["Islander"], reach))
    for nbr in list(cast(List["Islander"], reach)):
        for r in all_reachable(nbr, stmts, list(cast(List["Islander"], reach))):
            if r not in out:
                out.append(r)
    return out

def connected_sets(islanders: List["Islander"], all_islanders: List["Islander"], stmts: List["Statement"], sets: Optional[List[List["Islander"]]] = None, seen: Optional[List["Islander"]] = None) -> List[List["Islander"]]:
    if sets is None:
        sets = []
    if seen is None:
        seen = []
    comp: List["Islander"] = all_reachable(islanders[0], stmts, [])
    sets.append(comp)
    seen2: List["Islander"] = seen + comp
    if arrays_equivalent(all_islanders, seen2):
        return sets
    rest: List["Islander"] = [x for x in islanders if x not in seen2]
    return connected_sets(rest, all_islanders, stmts, sets, seen2)

def prune_statements(stmts: List["Statement"]) -> List["Statement"]:
    extras: List["Statement"] = []
    for s in stmts:
        for t in stmts:
            if t is not s and t.source is s.target and t.target is s.source:
                extras.append(t)
    return [s for s in stmts if s not in extras]

def remove_statement_with(a: "Islander", b: "Islander", stmts: List["Statement"]) -> List["Statement"]:
    for s in stmts:
        if (s.source is a or s.source is b) and (s.target is a or s.target is b):
            return [x for x in stmts if x is not s]
    return stmts

def pretty_print_list(lst: List[str]) -> str:
    if not lst:
        return "(none)"
    if len(lst) == 1:
        return lst[0]
    return ", ".join(lst[:-1]) + " and " + lst[-1]

# ─────────────────────── Model ──────────────────────────

class Puzzle:
    def __init__(self):
        self.islanders: List[Islander] = []
        self.statements: List[Statement] = []
        self.knights: List[Islander] = []
        self.knaves: List[Islander] = []

    def knight_names(self) -> List[str]:
        return [k.name for k in self.knights]

    def knave_names(self) -> List[str]:
        return [k.name for k in self.knaves]

class SimplePuzzle(Puzzle):
    def __init__(self, count: int, names: List[str]=None):
        super().__init__()
        self.count = count
        if names is None:
            names = name_set()
        self.name_set = names.copy()
        # determine liar count
        if count == 1:
            liar_count = 1
        elif count < 4:
            liar_count = random_int(count)
        else:
            liar_count = random_range(count//2 - 1, count - 2)
        # pick knaves
        for _ in range(liar_count):
            n = self.name_set.pop(random_int(len(self.name_set)))
            k = Knave(n)
            self.knaves.append(k)
            self.islanders.append(k)
        # pick knights
        for _ in range(count - liar_count):
            n = self.name_set.pop(random_int(len(self.name_set)))
            k = Knight(n)
            self.knights.append(k)
            self.islanders.append(k)
        shuffle(self.islanders)
        self.statements = self.generate_statements()

    def generate_statements(self):
        if len(self.islanders) < 2:
            return []
        stmts = []
        prev = None
        for tgt in self.islanders:
            rem = [x for x in self.islanders if x is not tgt]
            if prev:
                rem = [x for x in rem if x is not prev]
                if not rem:
                    rem = [x for x in self.islanders if x is not tgt]
            src = random_element(rem)
            stmts.append(src.statement_for(tgt))
            prev = src
        stmts = prune_statements(stmts)
        # connect disconnected sets
        sets = connected_sets(self.islanders, self.islanders, stmts)
        if len(sets) > 1:
            for other in sets[1:]:
                joiner = sets[0][0]
                joinee = other[0]
                stmts.append(joinee.statement_for(joiner))
        return shuffle(stmts)

    def complete_with_match(self) -> None:
        if len(self.islanders) < 2:
            return
        src = random_element(self.islanders)
        rem = [x for x in self.islanders if x is not src]
        nbrs = all_sources_and_targets(src, self.statements)
        left = [x for x in rem if x not in nbrs]
        tgt = random_element(left or rem)
        self.statements.append(src.match_statement_for(tgt))
        shuffle(self.statements)

    def complete_with_compound(self) -> None:
        if len(self.islanders) < 2:
            return
        src = random_element(self.islanders)
        rem = [x for x in self.islanders if x is not src]
        nbrs = all_sources_and_targets(src, self.statements)
        left = [x for x in rem if x not in nbrs]
        tgt = random_element(left or rem)
        self.statements = remove_statement_with(src, tgt, self.statements)
        self.statements.append(src.compound_statement_for(tgt))
        shuffle(self.statements)

    def random_completion(self) -> None:
        if random_int(2) == 0:
            self.complete_with_match()
        else:
            self.complete_with_compound()

class CompoundPuzzle(Puzzle):
    def __init__(self):
        super().__init__()
        self.puzzles: List[SimplePuzzle] = []

    def join(self, other: Puzzle):
        self.puzzles.append(other)
        add_all_unique(self.knights, other.knights)
        add_all_unique(self.knaves, other.knaves)
        add_all_unique(self.islanders, other.islanders)
        add_all_unique(self.statements, other.statements)

    def join_with_match(self, other: Puzzle):
        a = random_element(self.islanders)
        b = random_element(other.islanders)
        self.join(other)
        self.statements.append(a.match_statement_for(b))

    def join_with_compound(self, other: Puzzle):
        a = random_element(self.islanders)
        b = random_element(other.islanders)
        self.join(other)
        self.statements.append(a.compound_statement_for(b))

    def random_join(self, other: Puzzle):
        if random_int(2) == 0:
            self.join_with_match(other)
        else:
            self.join_with_compound(other)

# ─────────────────── Islanders & Statements ───────────────────

class Islander:
    def __init__(self, name: str):
        self.name = name

    def is_knight(self) -> bool:
        raise NotImplementedError

    def match_statement_for(self, other):
        if other.is_knight():
            return Same(self, other)
        else:
            return Different(self, other)

    def __str__(self):
        return self.name

class Knave(Islander):
    def is_knight(self) -> bool:
        return False

    def statement_for(self, other):
        if other.is_knight():
            return Accusation(self, other)
        else:
            return Affirmation(self, other)

    def compound_statement_for(self, other):
        return Joint(self, other)

    def type(self):
        return "knave"

class Knight(Islander):
    def is_knight(self) -> bool:
        return True

    def statement_for(self, other):
        if other.is_knight():
            return Affirmation(self, other)
        else:
            return Accusation(self, other)

    def compound_statement_for(self, other):
        return Disjoint(self, other)

    def type(self):
        return "knight"
    
class Statement:
    def __init__(self, source: Islander, target: Islander):
        self.source = source
        self.target = target
        self.text = self.build_statement()

    def build_statement(self) -> str:
        raise NotImplementedError

    def full_statement(self) -> str:
        return f"{self.source.name} says: {self.text}."

class TypeStatement(Statement):
    def done(self, solver: "Solver") -> bool:
        return (self.source in solver.knights or self.source in solver.knaves) and \
               (self.target in solver.knights or self.target in solver.knaves)

    def process(self, known: Islander, solver: "Solver"):
        if known is self.source or known is self.target:
            unknown = self.target if known is self.source else self.source
            solver.reasoning.append(self.reasoning(known))
            if unknown.is_knight():
                add_unique(solver.knights, unknown)
            else:
                add_unique(solver.knaves, unknown)

    def solve(self, solver: "Solver"):
        solver.type_statements.append(self)

class Accusation(TypeStatement):
    def build_statement(self):
        opts = [" is lying"," is a knave"," always lies"," never tells the truth"," lies"," is untruthful"]
        return self.target.name + random_element(opts)

    def reasoning(self, known: Islander) -> str:
        unknown = self.target if known is self.source else self.source
        s = ("All islanders call an opposite-type a knave. "
             f"When {self.source.name} says {self.target.name} is a knave, they differ. "
             f"Since {known.name} is a {known.type()}, {unknown.name} is a {unknown.type()}.")
        return s

class Affirmation(TypeStatement):
    def build_statement(self):
        opts = [" is truthful"," is a knight"," always tells the truth"," never lies"," tells the truth"]
        return self.target.name + random_element(opts)

    def reasoning(self, known: Islander) -> str:
        unknown = self.target if known is self.source else self.source
        s = ("All islanders call same-type a knight. "
             f"When {self.source.name} says {self.target.name} is a knight, they match. "
             f"Since {known.name} is a {known.type()}, {unknown.name} is a {unknown.type()}.")
        return s

class Same(Statement):
    def build_statement(self):
        return self.target.name + " is the same type"
    def solve(self, solver: "Solver"):
        solver.reasoning.append(
            f"{self.source.name} says they are same type as {self.target.name}, so {self.target.name} is a knight."
        )
        add_unique(solver.knights, self.target)

class Different(Statement):
    def build_statement(self):
        return self.target.name + " is a different type"
    def solve(self, solver: "Solver"):
        solver.reasoning.append(
            f"{self.source.name} says they are different type than {self.target.name}, so {self.target.name} is a knave."
        )
        add_unique(solver.knaves, self.target)

class Disjoint(Statement):
    def build_statement(self):
        t = "knight" if self.target.is_knight() else "knave"
        return f"{self.target.name} is a {t} or I am a knave"
    def solve(self, solver: "Solver"):
        solver.reasoning.append(
            f"{self.source.name} said '{self.text}', which must be true. So {self.source.name} is a knight."
        )
        add_unique(solver.knights, self.source)
        if self.target.is_knight():
            add_unique(solver.knights, self.target)
        else:
            add_unique(solver.knaves, self.target)

class Joint(Statement):
    def build_statement(self):
        t = "knave" if self.target.is_knight() else "knight"
        return f"{self.target.name} is a {t} and I am a knave"
    def solve(self, solver: "Solver"):
        solver.reasoning.append(
            f"{self.source.name} said '{self.text}', which must be false. So {self.source.name} is a knave."
        )
        add_unique(solver.knaves, self.source)
        if self.target.is_knight():
            add_unique(solver.knights, self.target)
        else:
            add_unique(solver.knaves, self.target)

# ─────────────────────── Solver ─────────────────────────

class Solver:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.reasoning: List[str] = []
        self.type_statements: List[TypeStatement] = []
        self.knights: List[Islander] = []
        self.knaves: List[Islander] = []

    def solve(self) -> None:
        # 1) initial pass: solve all non-TypeStatements
        for stmt in self.puzzle.statements:
            if not isinstance(stmt, TypeStatement):
                stmt.solve(self)
            else:
                self.type_statements.append(stmt)

        # 2) iteratively process TypeStatements
        remaining = self.type_statements.copy()
        while remaining:
            next_rem = []
            for s in remaining:
                if s.done(self):
                    continue
                for k in self.knaves + self.knights:
                    s.process(k, self)
                    if s.done(self):
                        break
                if not s.done(self):
                    next_rem.append(s)
            remaining = next_rem

        # 3) final validation
        self.validate()

    def validate(self):
        if arrays_equivalent(self.knights, self.puzzle.knights) and \
           arrays_equivalent(self.knaves, self.puzzle.knaves):
            print("✔ Solver found correct assignment.")
        else:
            print("✘ Solver assignment mismatch!")
            print("  Solver:", [x.name for x in self.knights], [x.name for x in self.knaves])
            print("  True:  ", self.puzzle.knight_names(), self.puzzle.knave_names())

# ─────────────────── Puzzle Generator ────────────────────

class PuzzleGenerator:
    def __init__(self):
        self.puzzle: Puzzle = None

    def easy(self) -> Puzzle:
        choice = random_int(3)
        if choice == 0:
            return self.easy0()
        if choice == 1:
            return self.easy1()
        return self.easy2()

    def easy0(self):
        p = SimplePuzzle(2, name_set())
        p.complete_with_match()
        return p

    def easy1(self):
        p = SimplePuzzle(2, name_set())
        p.complete_with_compound()
        return p

    def easy2(self):
        p = SimplePuzzle(3, name_set())
        p.random_completion()
        return p

    def medium(self) -> Puzzle:
        choice = random_int(3)
        if choice == 0:
            # join two random SimplePuzzles
            a = SimplePuzzle(3, name_set())
            b = SimplePuzzle(1, name_set())
            a.random_completion()
            cp = CompoundPuzzle()
            cp.join(a)
            cp.random_join(b)
            return cp
        if choice == 1:
            a = SimplePuzzle(3, name_set())
            a.complete_with_match()
            cp = CompoundPuzzle()
            cp.join(a)
            return cp
        # choice == 2
        a = SimplePuzzle(1, name_set())
        b = SimplePuzzle(3, name_set())
        cp = CompoundPuzzle()
        cp.join(a)
        cp.join_with_compound(b)
        return cp

    def hard(self) -> Puzzle:
        choice = random_int(2)
        a = SimplePuzzle(3, name_set())
        b = SimplePuzzle(3, name_set())
        if choice == 0:
            cp = CompoundPuzzle()
            cp.join(a)
            cp.join_with_compound(b)
            return cp
        a.complete_with_match()
        cp = CompoundPuzzle()
        cp.join(a)
        cp.join_with_match(b)
        return cp

# ───────────────────────── CLI Demo ────────────────────────

if __name__ == "__main__":
    pg = PuzzleGenerator()
    puzzle = pg.medium()
    print("Islanders:", [i.name for i in puzzle.islanders])
    print("\nStatements:")
    for s in puzzle.statements:
        print(" -", s.full_statement())

    solver = Solver(puzzle)
    solver.solve()

    print("\nTrue Knights:", puzzle.knight_names())
    print("True Knaves: ", puzzle.knave_names())
    print("\nReasoning steps:")
    for step in solver.reasoning:
        print(" •", step)