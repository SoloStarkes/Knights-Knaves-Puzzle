"""
Puzzle Generator Module

This module implements a puzzle generator for Knights and Knaves puzzles.
It includes utilities for randomization, array manipulation, as well as the 
model classes for islanders, puzzles, statements, and the solver.
"""

import random
from typing import List, Any, cast, Optional

# ─────────────────────── Name Sets ───────────────────────────

original_name_set = [
    "Elnuman", "Solomon", "Bram", "Sidy", "Drake", "Munzir", "Ajay", "Lebron", 
    "Curry", "Bronny", "Flight", "Cash", "Draymond", "Klay", "Andrew", "Omar", "DJ Khalid"
]

def name_set() -> List[str]:
    """
    Returns a copy of the original name set.

    :return: List of available names.
    """
    return original_name_set.copy()

# ─────────────────── Random Utilities ────────────────────

def random_int(n: int) -> int:
    """
    Return a random integer in the range [0, n).

    :param n: Upper bound (exclusive) of the range.
    :return: A random integer.
    """
    return random.randrange(n)

def random_range(lo: int, hi: int) -> int:
    """
    Return a random integer between lo and hi (inclusive).

    :param lo: Lower bound.
    :param hi: Upper bound.
    :return: A random integer in the given range.
    """
    return random.randrange(lo, hi+1)

def random_element(lst: List[Any]) -> Any:
    """
    Return a random element from the given list.

    :param lst: A list of elements.
    :return: A randomly chosen element.
    """
    return random.choice(lst)

def shuffle(lst: List[Any]) -> List[Any]:
    """
    Shuffle the list in place and return it.

    :param lst: A list of elements.
    :return: The shuffled list.
    """
    random.shuffle(lst)
    return lst

# ─────────────── Array / List Utilities ────────────────

def remove_element(lst: List[Any], e: Any) -> List[Any]:
    """
    Return a new list with all instances of element e removed (using identity).

    :param lst: Input list.
    :param e: Element to remove.
    :return: New list without e.
    """
    return [x for x in lst if x is not e]

def array_without(lst: List[Any], e: Any) -> List[Any]:
    """
    Return a new list with all elements equal to e removed.

    :param lst: Input list.
    :param e: Element to remove.
    :return: New list without elements equal to e.
    """
    return [x for x in lst if x != e]

def arrays_equivalent(a: List[Any], b: List[Any]) -> bool:
    """
    Checks if two lists are equivalent (same length and each element in one is in the other).

    :param a: First list.
    :param b: Second list.
    :return: True if equivalent; otherwise False.
    """
    return len(a) == len(b) and all(x in b for x in a)

def add_unique(lst: List[Any], e: Any) -> None:
    """
    Adds an element e to the list if not already present.

    :param lst: List to add to.
    :param e: Element to add.
    """
    if e not in lst:
        lst.append(e)

def add_all_unique(a: List[Any], b: List[Any]) -> List[Any]:
    """
    Add all elements from list b into list a if they do not already exist in a.

    :param a: Original list.
    :param b: List of new elements.
    :return: The updated list a.
    """
    for x in b:
        if x not in a:
            a.append(x)
    return a

def all_sources_and_targets(islander: "Islander", stmts: List["Statement"]) -> List["Islander"]:
    """
    Returns a list of islanders directly connected to the given islander by statements,
    including the islander itself.

    :param islander: The starting islander.
    :param stmts: List of statements.
    :return: List of connected islanders.
    """
    res: List["Islander"] = [islander]
    for s in stmts:
        if s.source is islander:
            res.append(cast("Islander", s.target))
        if s.target is islander:
            res.append(cast("Islander", s.source))
    return res

def all_reachable(islander: "Islander", stmts: List["Statement"], seen: Optional[List["Islander"]] = None) -> List["Islander"]:
    """
    Recursively finds all islanders reachable from a given islander.

    :param islander: The starting islander.
    :param stmts: List of statements.
    :param seen: Already seen islanders.
    :return: List of reachable islanders.
    """
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
    """
    Divides islanders into connected sets based on statements connectivity.

    :param islanders: List of islanders to process.
    :param all_islanders: The complete list of islanders.
    :param stmts: List of statements.
    :param sets: Collected sets so far.
    :param seen: Islander processed so far.
    :return: List of connected sets.
    """
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
    """
    Removes duplicate (mutually redundant) statements from the list.

    :param stmts: List of statements.
    :return: Pruned list of statements.
    """
    extras: List["Statement"] = []
    for s in stmts:
        for t in stmts:
            if t is not s and t.source is s.target and t.target is s.source:
                extras.append(t)
    return [s for s in stmts if s not in extras]

def remove_statement_with(a: "Islander", b: "Islander", stmts: List["Statement"]) -> List["Statement"]:
    """
    Removes the first encountered statement connecting two islanders.

    :param a: First islander.
    :param b: Second islander.
    :param stmts: List of statements.
    :return: List of statements with the specified connection removed.
    """
    for s in stmts:
        if (s.source is a or s.source is b) and (s.target is a or s.target is b):
            return [x for x in stmts if x is not s]
    return stmts

def pretty_print_list(lst: List[str]) -> str:
    """
    Returns a human-readable string for a list of strings.

    :param lst: List of strings.
    :return: A formatted string.
    """
    if not lst:
        return "(none)"
    if len(lst) == 1:
        return lst[0]
    return ", ".join(lst[:-1]) + " and " + lst[-1]

# ─────────────────────── Model ──────────────────────────

class Puzzle:
    """
    Base class for puzzles.
    """
    def __init__(self):
        self.islanders: List[Islander] = []
        self.statements: List[Statement] = []
        self.knights: List[Islander] = []
        self.knaves: List[Islander] = []

    def knight_names(self) -> List[str]:
        """
        Returns the names of the knights.

        :return: List of knight names.
        """
        return [k.name for k in self.knights]

    def knave_names(self) -> List[str]:
        """
        Returns the names of the knaves.

        :return: List of knave names.
        """
        return [k.name for k in self.knaves]

class SimplePuzzle(Puzzle):
    """
    A simple Knights and Knaves puzzle.
    """
    def __init__(self, count: int, names: List[str]=None):
        """
        Initialize a SimplePuzzle.

        :param count: Number of islanders.
        :param names: List of names to use.
        """
        super().__init__()
        self.count = count
        if names is None:
            names = name_set()
        self.name_set = names.copy()
        # determine liar count based on count value
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
        """
        Generate statements for the puzzle based on islanders' interactions.

        :return: A shuffled list of statements.
        """
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
        # connect disconnected sets if any exist
        sets = connected_sets(self.islanders, self.islanders, stmts)
        if len(sets) > 1:
            for other in sets[1:]:
                joiner = sets[0][0]
                joinee = other[0]
                stmts.append(joinee.statement_for(joiner))
        return shuffle(stmts)

    def complete_with_match(self) -> None:
        """
        Completes the puzzle by adding a matching statement.
        """
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
        """
        Completes the puzzle by adding a compound statement.
        """
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
        """
        Randomly completes the puzzle using either a match or compound method.
        """
        if random_int(2) == 0:
            self.complete_with_match()
        else:
            self.complete_with_compound()

class CompoundPuzzle(Puzzle):
    """
    A compound puzzle made by joining multiple simple puzzles.
    """
    def __init__(self):
        super().__init__()
        self.puzzles: List[SimplePuzzle] = []

    def join(self, other: Puzzle):
        """
        Joins another puzzle with this compound puzzle. Merges islanders, statements,
        knights, and knaves ensuring unique names.
        
        :param other: A Puzzle instance to join.
        """
        self.puzzles.append(other)
        add_all_unique(self.knights, other.knights)
        add_all_unique(self.knaves, other.knaves)
        add_all_unique(self.islanders, other.islanders)
        add_all_unique(self.statements, other.statements)
        self.ensure_unique_names()

    def ensure_unique_names(self) -> None:
        """
        Ensures that all islanders have unique names by appending a suffix for duplicates.
        """
        seen = {}
        for islander in self.islanders:
            name = islander.name
            if name in seen:
                seen[name] += 1
                islander.name = f"{name}_{seen[name]}"
            else:
                seen[name] = 0

    def join_with_match(self, other: Puzzle):
        """
        Joins another puzzle and adds a matching statement between random islanders.
        
        :param other: Puzzle to join with.
        """
        a = random_element(self.islanders)
        b = random_element(other.islanders)
        self.join(other)
        self.statements.append(a.match_statement_for(b))

    def join_with_compound(self, other: Puzzle):
        """
        Joins another puzzle and adds a compound statement between random islanders.
        
        :param other: Puzzle to join with.
        """
        a = random_element(self.islanders)
        b = random_element(other.islanders)
        self.join(other)
        self.statements.append(a.compound_statement_for(b))

    def random_join(self, other: Puzzle):
        """
        Randomly joins another puzzle using either a match or compound join method.
        
        :param other: Puzzle to join with.
        """
        if random_int(2) == 0:
            self.join_with_match(other)
        else:
            self.join_with_compound(other)

# ─────────────────── Islanders & Statements ───────────────────

class Islander:
    """
    Represents an islander in the puzzle.
    """
    def __init__(self, name: str):
        """
        Initializes an islander with the given name.

        :param name: Name of the islander.
        """
        self.name = name

    def is_knight(self) -> bool:
        """
        Determines if the islander is a knight.

        :return: True if knight, False otherwise.
        """
        raise NotImplementedError

    def match_statement_for(self, other: "Islander"):
        """
        Returns a matching statement for the given other islander.
        Chooses a Same or Different statement based on types.

        :param other: Other islander.
        :return: A Statement instance.
        """
        if other.is_knight():
            return Same(self, other)
        else:
            return Different(self, other)

    def __str__(self):
        """
        Returns the string representation of the islander.

        :return: The islander's name.
        """
        return self.name

class Knave(Islander):
    """
    Represents a knave (liar) islander.
    """
    def is_knight(self) -> bool:
        """
        Knaves are not knights.

        :return: False.
        """
        return False

    def statement_for(self, other: "Islander"):
        """
        Returns a statement for the other islander based on knave logic.

        :param other: The target islander.
        :return: A Statement instance.
        """
        if other.is_knight():
            return Accusation(self, other)
        else:
            return Affirmation(self, other)

    def compound_statement_for(self, other: "Islander"):
        """
        Returns a compound statement for the other islander.

        :param other: The target islander.
        :return: A Joint statement.
        """
        return Joint(self, other)

    def type(self):
        """
        Returns the type of the islander.

        :return: "knave"
        """
        return "knave"

class Knight(Islander):
    """
    Represents a knight (truthful) islander.
    """
    def is_knight(self) -> bool:
        """
        Knights are truthful.

        :return: True.
        """
        return True

    def statement_for(self, other: "Islander"):
        """
        Returns a statement for the other islander based on knight logic.

        :param other: The target islander.
        :return: A Statement instance.
        """
        if other.is_knight():
            return Affirmation(self, other)
        else:
            return Accusation(self, other)

    def compound_statement_for(self, other: "Islander"):
        """
        Returns a compound statement for the other islander.

        :param other: The target islander.
        :return: A Disjoint statement.
        """
        return Disjoint(self, other)

    def type(self):
        """
        Returns the type of the islander.

        :return: "knight"
        """
        return "knight"

class Statement:
    """
    Abstract base class for all statements made by islanders.
    """
    def __init__(self, source: Islander, target: Islander):
        """
        Initializes a statement with a source and target islander.

        :param source: The islander making the statement.
        :param target: The islander about whom the statement is made.
        """
        self.source = source
        self.target = target
        self.text = self.build_statement()

    def build_statement(self) -> str:
        """
        Builds the textual content of the statement.

        :return: The statement as a string.
        """
        raise NotImplementedError

    def full_statement(self) -> str:
        """
        Returns the full statement in a readable format.

        :return: A formatted statement string.
        """
        return f"{self.source.name} says: {self.text}."

class TypeStatement(Statement):
    """
    A statement that can be processed by the solver to deduce types.
    """
    def done(self, solver: "Solver") -> bool:
        """
        Checks if the statement has been fully processed by the solver.

        :param solver: The puzzle solver.
        :return: True if processed; otherwise False.
        """
        return (self.source in solver.knights or self.source in solver.knaves) and \
               (self.target in solver.knights or self.target in solver.knaves)

    def process(self, known: Islander, solver: "Solver"):
        """
        Process the statement given a known islander status.

        :param known: An islander whose type is known.
        :param solver: The puzzle solver.
        """
        if known is self.source or known is self.target:
            unknown = self.target if known is self.source else self.source
            solver.reasoning.append(self.reasoning(known))
            if unknown.is_knight():
                add_unique(solver.knights, unknown)
            else:
                add_unique(solver.knaves, unknown)

    def solve(self, solver: "Solver"):
        """
        Registers the TypeStatement for later processing by the solver.

        :param solver: The puzzle solver.
        """
        solver.type_statements.append(self)

class Accusation(TypeStatement):
    """
    Represents an accusation statement by a knave.
    """
    def build_statement(self):
        opts = [" is lying", " is a knave", " always lies", " never tells the truth", " lies", " is untruthful"]
        return self.target.name + random_element(opts)

    def reasoning(self, known: Islander) -> str:
        """
        Provides reasoning based on the accusation.

        :param known: The known islander used to infer the type.
        :return: A reasoning string.
        """
        unknown = self.target if known is self.source else self.source
        s = ("All islanders call an opposite-type a knave. "
             f"When {self.source.name} says {self.target.name} is a knave, they differ. "
             f"Since {known.name} is a {known.type()}, {unknown.name} is a {unknown.type()}.")
        return s

class Affirmation(TypeStatement):
    """
    Represents an affirmation statement by a knight.
    """
    def build_statement(self):
        opts = [" is truthful", " is a knight", " always tells the truth", " never lies", " tells the truth"]
        return self.target.name + random_element(opts)

    def reasoning(self, known: Islander) -> str:
        """
        Provides reasoning based on the affirmation.

        :param known: The known islander for inference.
        :return: A reasoning string.
        """
        unknown = self.target if known is self.source else self.source
        s = ("All islanders call same-type a knight. "
             f"When {self.source.name} says {self.target.name} is a knight, they match. "
             f"Since {known.name} is a {known.type()}, {unknown.name} is a {unknown.type()}.")
        return s

class Same(Statement):
    """
    Statement indicating that two islanders are of the same type.
    """
    def build_statement(self):
        return self.target.name + " is the same type"

    def solve(self, solver: "Solver"):
        """
        Directly adds the target as a knight based on the same type logic.

        :param solver: The puzzle solver.
        """
        solver.reasoning.append(
            f"{self.source.name} says they are same type as {self.target.name}, so {self.target.name} is a knight."
        )
        add_unique(solver.knights, self.target)

class Different(Statement):
    """
    Statement indicating that two islanders are of different types.
    """
    def build_statement(self):
        return self.target.name + " is a different type"

    def solve(self, solver: "Solver"):
        """
        Directly adds the target as a knave based on the different type logic.

        :param solver: The puzzle solver.
        """
        solver.reasoning.append(
            f"{self.source.name} says they are different type than {self.target.name}, so {self.target.name} is a knave."
        )
        add_unique(solver.knaves, self.target)

class Disjoint(Statement):
    """
    Compound statement from a knight.
    """
    def build_statement(self):
        t = "knight" if self.target.is_knight() else "knave"
        return f"{self.target.name} is a {t} or I am a knave"

    def solve(self, solver: "Solver"):
        """
        Processes the disjoint statement and infers the source as a knight.
        
        :param solver: The puzzle solver.
        """
        solver.reasoning.append(
            f"{self.source.name} said '{self.text}', which must be true. So {self.source.name} is a knight."
        )
        add_unique(solver.knights, self.source)
        if self.target.is_knight():
            add_unique(solver.knights, self.target)
        else:
            add_unique(solver.knaves, self.target)

class Joint(Statement):
    """
    Compound statement from a knave.
    """
    def build_statement(self):
        t = "knave" if self.target.is_knight() else "knight"
        return f"{self.target.name} is a {t} and I am a knave"

    def solve(self, solver: "Solver"):
        """
        Processes the joint statement by inferring the source as a knave.
        
        :param solver: The puzzle solver.
        """
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
    """
    Solves the Knights and Knaves puzzle by processing statements
    and deducing the identities of islanders.
    """
    def __init__(self, puzzle: Puzzle):
        """
        Initializes the solver with the given puzzle.

        :param puzzle: The puzzle instance to solve.
        """
        self.puzzle = puzzle
        self.reasoning: List[str] = []
        self.type_statements: List[TypeStatement] = []
        self.knights: List[Islander] = []
        self.knaves: List[Islander] = []

    def solve(self) -> None:
        """
        Solves the puzzle by processing all statements and verifying
        the final assignment.
        """
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

        # 3) final validation step
        self.validate()

    def validate(self):
        """
        Validates the solver's assignment against the true puzzle assignment.
        """
        if arrays_equivalent(self.knights, self.puzzle.knights) and \
           arrays_equivalent(self.knaves, self.puzzle.knaves):
            print("✔ Solver found correct assignment.")
        else:
            print("✘ Solver assignment mismatch!")
            print("  Solver:", [x.name for x in self.knights], [x.name for x in self.knaves])
            print("  True:  ", self.puzzle.knight_names(), self.puzzle.knave_names())

# ─────────────────── Puzzle Generator ────────────────────

class PuzzleGenerator:
    """
    Generates puzzles of varying difficulty.
    """
    def __init__(self):
        """
        Initializes the PuzzleGenerator.
        """
        self.puzzle: Puzzle = None

    def easy(self) -> Puzzle:
        """
        Generates an easy puzzle.

        :return: A Puzzle instance.
        """
        choice = random_int(3)
        if choice == 0:
            return self.easy0()
        if choice == 1:
            return self.easy1()
        return self.easy2()

    def easy0(self):
        """
        Generates an easy puzzle variant 0.

        :return: A Puzzle instance.
        """
        p = SimplePuzzle(2, name_set())
        p.complete_with_match()
        return p

    def easy1(self):
        """
        Generates an easy puzzle variant 1.

        :return: A Puzzle instance.
        """
        p = SimplePuzzle(2, name_set())
        p.complete_with_compound()
        return p

    def easy2(self):
        """
        Generates an easy puzzle variant 2.

        :return: A Puzzle instance.
        """
        p = SimplePuzzle(3, name_set())
        p.random_completion()
        return p

    def medium(self) -> Puzzle:
        """
        Generates a medium difficulty puzzle.

        :return: A Puzzle instance.
        """
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
        """
        Generates a hard difficulty puzzle.

        :return: A Puzzle instance.
        """
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
    # Instantiate generator and produce a medium puzzle.
    pg = PuzzleGenerator()
    puzzle = pg.easy()
    
    # Display islanders and their names.
    print("Islanders:", [i.name for i in puzzle.islanders])
    
    # List all statements in full.
    print("\nStatements:")
    for s in puzzle.statements:
        print(" -", s.full_statement())

    # Solve the puzzle and show reasoning.
    solver = Solver(puzzle)
    solver.solve()

    print("\nTrue Knights:", puzzle.knight_names())
    print("True Knaves: ", puzzle.knave_names())
    print("\nReasoning steps:")
    for step in solver.reasoning:
        print(" •", step)
