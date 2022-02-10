import string
import random
import progressbar
from sys import argv
from functools import reduce, lru_cache
from os.path import exists

cache = lru_cache(maxsize=None)


class Wordle:
    """
    An agent that can play the popular word game "Wordle"
    """

    def __init__(self, dict_file, first_moves_file, alphabet):
        # Data structures that define the dictionary of five-letter words
        self.constraint_tree, self.all_words = self.parse_dictionary(dict_file, alphabet)

        # File containing first move options
        self.first_moves_file = first_moves_file

        # If true will prevent printing game info
        self.silent = False

        # The words that are still valid at the current point in the game
        self.valid_words = self.all_words.copy()

    @classmethod
    def parse_dictionary(cls, dict_file, alphabet):
        """
        Parses the provided dictionary file and constructs two useful data structures.

        The first object returned is a two-level dictionary named constraint_tree. The
        first-level of constraint_tree maps each letter of the alphabet to a second-level
        dictionary. The second-level maps a key describing a constraint to a set of words
        known as a constraint set. A constraint set contains all words that are valid given
        a constraint.

        Each constraint can be represented by a two-element tuple. There are five types
        of constraints:

        * (l, i)          ->  The set of words where letter l is at index i
        * (l, "NOT-i")    ->  The set of words containing letter l not at index i
        * (l, "MULT-n")   ->  The set of words containing exactly n occurrences of letter l
        * (l, "MULT-n+)   ->  The set of words containing at least n occurrences of letter l
        * (l, "NONE")     ->  The set of words not containing letter l

        The constraint set for constraint c can be found at constraint_tree[c[0]][c[1]].

        The second object returned is a set that contains all of the words in the dictionary.

        :param dict_file: the dictionary file
        :param alphabet: string representing alphabet
        :returns constraint_tree and all_words
        """
        # Construct dict
        constraint_set_keys = ["0", "1", "2", "3", "4",
                               "NOT-0", "NOT-1", "NOT-2", "NOT-3", "NOT-4",
                               "MULT-1", "MULT-2", "MULT-3", "MULT-4", "MULT-5",
                               "MULT-2+", "MULT-3+", "MULT-4+",
                               "NONE"]
        constraint_tree = {letter: {k: set() for k in constraint_set_keys} for letter in alphabet}

        # Read in dictionary file
        with open(dict_file) as file:
            all_words = set((s.strip().upper() for s in file.readlines()))

        # Fill with data
        for word in all_words:
            for letter in alphabet:
                if letter in word:
                    # "NOT-i" sets
                    for i in range(5):
                        if word[i] != letter:
                            constraint_tree[letter]["NOT-%d" % i].add(word)

                    # "MULT-i" sets
                    count = word.count(letter)
                    constraint_tree[letter]["MULT-%d" % count].add(word)
                    for n in range(2, count + 1):
                        constraint_tree[letter]["MULT-%d+" % n].add(word)
                else:
                    # "NONE" set
                    constraint_tree[letter]["NONE"].add(word)

            # index sets
            for i, s in enumerate(word):
                constraint_tree[s]["%d" % i].add(word)
        return constraint_tree, all_words

    @classmethod
    @cache
    def get_constraints_from_user(cls, guess):
        """
        Generate constraints from user input. The input must be 5 characters long and consist
        only of '+', '*', and '-'.

        '+' represents a character match that is in the correct position
        '*' represents a character match that is NOT in the correct position
        '-' represents a character that does not match

        :param guess: the guess that the user is responding to
        :return: a list of new constraints generated from the user's input, a boolean representing
                 whether the puzzle is solved (i.e. the user entered '++++++')
        """
        # Fetch valid user input
        result = ""
        while not (len(result) == result.count("+") + result.count("*") + result.count("-") == 5):
            result = input("Enter result: ")
        return cls.get_constraints_from_pattern(guess, result), result == "+++++"

    @classmethod
    @cache
    def get_constraints_from_pattern(cls, guess, pattern):
        # Compute letter frequencies
        guess_frequencies = {g: guess.count(g) for g in set(guess)}
        target_frequencies = {t: 0 for t in set(guess)}

        # Compute positional constraints
        constraints = []
        for i, s in enumerate(pattern):
            if s == "+":
                # Positional match
                constraints.append((guess[i], "%d" % i))
                target_frequencies[guess[i]] += 1
            elif s == "*":
                # Incorrect position match
                constraints.append((guess[i], "NOT-%d" % i))
                target_frequencies[guess[i]] += 1

        # Compute non-positional constraints
        for g in guess_frequencies:
            if target_frequencies[g] == 0:
                # No match
                constraints.append((g, "NONE"))
            elif guess_frequencies[g] > target_frequencies[g]:
                # Exact multiplicity
                constraints.append((g, "MULT-%d" % target_frequencies[g]))
            elif guess_frequencies[g] > 1:
                # Multiplicity lower bound
                constraints.append((g, "MULT-%d+" % guess_frequencies[g]))
        return constraints

    @classmethod
    @cache
    def get_constraints_from_target(cls, guess, target):
        """
        Same purpose as above method, but using a known target.

        :param guess: the guess that has just been made
        :param target: the word that the agent is trying to guess
        :return: a list of new constraints
        """
        # Compute letter frequencies
        guess_frequencies = {g: guess.count(g) for g in set(guess)}
        target_frequencies = {t: target.count(t) for t in set(target)}

        # Compute positional constraints
        constraints = []
        for i in range(5):
            if guess[i] == target[i]:
                # Positional match
                constraints.append((guess[i], "%d" % i))
            elif guess[i] in target_frequencies:
                # Incorrect position match
                constraints.append((guess[i], "NOT-%d" % i))

        # Compute non-positional constraints
        for g in guess_frequencies:
            if g not in target_frequencies:
                # No match
                constraints.append((g, "NONE"))
            elif guess_frequencies[g] > target_frequencies[g]:
                # Exact multiplicity
                constraints.append((g, "MULT-%d" % target_frequencies[g]))
            elif guess_frequencies[g] > 1:
                # Multiplicity lower bound
                constraints.append((g, "MULT-%d+" % guess_frequencies[g]))
        return constraints

    @classmethod
    @cache
    def get_pattern_from_target(cls, guess, target):
        pattern = list("-----")

        # Compute letter frequencies
        frequencies = {g: min(target.count(g), guess.count(g)) for g in set(guess)}

        for i in range(5):
            if guess[i] == target[i]:
                # Positional match
                pattern[i] = "+"
                frequencies[guess[i]] -= 1

        for i in range(5):
            if guess[i] in frequencies and frequencies[guess[i]] > 0 and pattern[i] == "-":
                # Incorrect position match
                pattern[i] = "*"
                frequencies[guess[i]] -= 1

        return "".join(pattern)

    def log(self, s="", override=False):
        """
        Log function for internal use. To be used instead of print() so that output can
        be controlled by self.silent.

        :param s: the string to print
        :param override: if true, will print regardless of self.silent
        :return:
        """
        if not self.silent or override:
            print(s)

    def reset(self):
        """
        Reset instance variables so that the game can be played again.
        """
        self.silent = False
        self.valid_words = self.all_words.copy()

    def update_valid_words(self, new_constraints):
        """
        Update self.valid_words based on a new set of constraints. For more info
        on the format and meaning of constraints, see documentation of
        self.parse_dictionary().

        The collection of valid words after the new constraints are applied is defined
        as the set intersection of all the constraint sets and the current
        self.valid_words.

        If this is the first move, self.first_move_subset will be updated.

        :param new_constraints: new constraints
        """
        possibility_sets = [self.constraint_tree[c[0]][c[1]] for c in new_constraints]
        possibility_sets.append(self.valid_words)
        possibility_sets.sort(key=len)
        self.valid_words = reduce(lambda a, b: a.intersection(b), possibility_sets)

    def next_guess(self, move, is_hard_mode):
        """
        Compute the next guess.

        Due to the lengthy runtime of this algorithm on the initial move, that guess will
        be selected at random from the static file pointed to by self.fist-moves-file.
        If the given file is not present, it will be generated. This generation process will take
        approximately 3-5 minutes.

        This method will score each possible guess based on the number of valid words it is expected
        to eliminate. I.e. for every scenario that can occur on the next move (a scenario consists
        of a guess word and a target word), which guess word results in the greatest reduction in
        the size of self.valid_words on average?

        Since it is extremely inefficient to test all possible guess/target pairs, a random sample
        of size num_samples is taken from self.valid_words and used as the possible targets for each
        potential guess.

        :param move: move number, starts at 0
        :param is_hard_mode: true if the game is in hard mode
        :return: the next guess word
        """
        if move == 0 and exists(self.first_moves_file):
            # If this is the first move, return randomly-selected word from first_moves_file
            # if that file exists. Otherwise, continue on and that file will be generated.
            with open(self.first_moves_file) as file:
                return random.choice([s.strip() for s in file.readlines()])
        elif move == 5:
            # If this is the last move, return a random choice from the remaining valid words.
            return random.choice(list(self.valid_words))
        elif len(self.valid_words) <= 2:
            # In any case where there is only one or two valid word(s), return a random one.
            return self.valid_words.copy().pop()

        # Tell the user to be patient if generating first moves
        if move == 0:
            self.log("\nHold tight. Generating first move options. This may take a few minutes.", True)

        # Determine the set of possible guesses. If in hard mode, use self.valid_words.
        # If in standard mode, use self.all_words.
        guess_set = self.valid_words if is_hard_mode else self.all_words

        # Compute scores
        words_scores = {word: 0 for word in guess_set}
        min_score = float('inf')
        for guess in guess_set:
            # Compute the occurrence frequency of each result pattern
            pattern_frequencies = {}
            for target in self.valid_words:
                pattern = self.get_pattern_from_target(guess, target)
                if pattern in pattern_frequencies:
                    pattern_frequencies[pattern] += 1
                elif pattern != "+++++":
                    pattern_frequencies[pattern] = 1

            # Compute the size of valid_words after the result pattern has been processed
            for pattern in sorted(pattern_frequencies, key=pattern_frequencies.get, reverse=True):
                constraints = self.get_constraints_from_pattern(guess, pattern)
                possibility_sets = [self.constraint_tree[c[0]][c[1]] for c in constraints]
                result_size = sum(int(all(word in s for s in possibility_sets)) for word in self.valid_words)
                words_scores[guess] += result_size * (pattern_frequencies[pattern] / float(len(self.valid_words)))

                # Break if it is impossible for the score to beat the best so far
                if words_scores[guess] > min_score + 0.1:
                    break

            # Keep track of the best score so far
            if words_scores[guess] < min_score:
                min_score = words_scores[guess]

        # Write first move data to file if necessary
        if move == 0:
            self.log("Finished generating first move options.\n", True)
            with open(self.first_moves_file, "w+") as file:
                file.write("\n".join(sorted(words_scores, key=words_scores.get)[0:15]))

        # Compute min score and return move
        sorted_words = sorted(words_scores, key=words_scores.get)
        return sorted_words[0]

    def test(self, is_hard_mode, start, max_games=None):
        """
        Testing harness that will simulate num_games games. Win/lose statistics
        will be printed once all simulations are complete.

        :param max_games: maximum number of games to run
        :param is_hard_mode: true if the game is in hard mode
        :param start: starting move
        """
        # Simulate games
        results = {k: 0 for k in range(-1, 6)}
        all_words_list = list(self.all_words)
        random.shuffle(all_words_list)
        for i in progressbar.progressbar(range(min(max_games, len(self.all_words)))):
            moves = self.play(is_hard_mode, start, all_words_list[i], True)
            results[moves] += 1
            self.reset()

        # Print start word, if necessary
        if start is not None:
            self.log("-" * 50)
            self.log("Start Word: %s" % start)

        # Print game length breakdown
        self.log("-" * 50)
        for i in range(0, 6):
            self.log("Solved in %d moves: %0.1f%%" % (i + 1, results[i] * 100.0 / len(self.all_words)))
        self.log("Unsolved: %0.1f%%" % (results[-1] * 100.0 / len(self.all_words)))

        # Print result stats
        solved_games = sum((v for k, v in results.items() if k >= 0))
        weighted_avg = sum(((k + 1) * (v / solved_games) for k, v in results.items() if k >= 0))
        self.log("-" * 50)
        self.log("Average solution length: %0.2f moves" % weighted_avg)
        self.log("Win rate: %0.2f%%" % (100 - (results[-1] * 100.0 / len(self.all_words))))
        self.log("-" * 50 + "\n")

    def play(self, is_hard_mode=False, start=None, target=None, silent=False):
        """
        Game runner method.

        :param is_hard_mode: If True, the agent will only make guesses that are valid target words.
        :param start: starting word
        :param target: The word that the agent is trying to guess. Not required.
        :param silent: If true, will not print any game info
        """
        # Capture initial value of silent, then update
        init_silent = self.silent
        self.silent = silent

        self.log("\n" + "=" * 50)
        self.log(("#" * 18) + (" " * 4) + "WORDLE" + (" " * 4) + ("#" * 18))
        self.log("-" * 50 + "\n")
        for move in range(0, 6):
            # Compute next guess
            if move == 0 and start is not None:
                guess = start
            else:
                guess = self.next_guess(move, is_hard_mode)
            self.log("Move %d: %s" % (move + 1, guess))

            # Get new constraints, check if solved
            if target is None:
                new_constraints, is_solved = self.get_constraints_from_user(guess)
            else:
                new_constraints = self.get_constraints_from_target(guess, target)
                is_solved = guess == target

            # Update valid word set
            self.update_valid_words(new_constraints)

            # Check if solved or impossible
            if is_solved:
                self.log("\nSolved in %d moves! Answer is \"%s\"\n" % (move + 1, guess))
                self.log("-" * 50 + "\n")
                self.silent = init_silent
                return move
            elif len(self.valid_words) == 0:
                self.log("\nI'm out of possibilities! Double check your input.\n")
                self.log("-" * 50 + "\n")
                self.silent = init_silent
                return -1
            self.log()

        # If loop completes without returning, the puzzle is unsolved
        self.log("\nSorry, no solution was reached in 6 moves.\n")
        self.log("-" * 50 + "\n")
        self.silent = init_silent
        return -1


def main():
    # Parse command line args
    dictionary_file = "dicts/wordle.txt"
    first_moves_file = "dicts/wordle-first-moves.txt"
    alphabet = string.ascii_uppercase
    is_test_mode = False
    is_hard_mode = False
    start = None
    target = None
    max_num_tests = None
    for i, arg in enumerate(argv):
        if arg == "--test":
            is_test_mode = True
            if len(argv) > i + 1:
                max_num_tests = int(argv[i + 1])
        elif arg == "--dict" and len(argv) > i + 1:
            dictionary_file = argv[i + 1]
            first_moves_file = dictionary_file.split(".")[0] + "-first-moves.txt"
        elif arg == "--target" and len(argv) > i + 1:
            target = argv[i + 1].upper()
        elif arg == "--start" and len(argv) > i + 1:
            start = argv[i + 1].upper()
        elif arg == "--hard":
            is_hard_mode = True
        elif arg == "--numeric":
            alphabet = "0123456789"

    # Run wordle
    wordle = Wordle(dictionary_file, first_moves_file, alphabet)
    if is_test_mode:
        wordle.test(is_hard_mode, start, max_num_tests)
    else:
        wordle.play(is_hard_mode, start, target)


if __name__ == "__main__":
    main()
