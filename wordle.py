import string
import random
from sys import argv
from functools import reduce
from os.path import exists


class Wordle:
    """
    Class representing an agent that can play the popular word game "Wordle"
    """

    def __init__(self, dict_file_name):
        # Data structures that define the dictionary of five-letter words
        self.words_tree, self.all_words = self.parse_dictionary(dict_file_name)

        # The words that are still valid at the current stage of the game. This
        # is the only instance variable that is updated during gameplay. To reset
        # this field to its original value, use self.reset()
        self.valid_words = self.all_words.copy()

    @classmethod
    def parse_dictionary(cls, file_name):
        """
        Parses the provided dictionary file and provides two useful data structures.

        The first object returned is a dict with the following structure:
            {
                "A": {
                    "NOT": <Set of all words not containing 'A'>
                    "ALL-0": <Set of all words containing 'A' NOT at index 0>,
                    ...
                    "ALL-4": <Set of all words containing 'A' NOT at index 4>,
                    0: <Set of all words with 'A' at index 0>
                    ...
                    4: <Set of all words with 'A' at index 4>
                },
                ...
                "Z": { ... }
            }

        The second object is a set that contains all of the words in the dictionary.

        :returns dict with aforementioned structure and set of all words
        """
        # Construct dict
        words_tree = {}
        for letter in string.ascii_uppercase:
            words_tree[letter] = {k: set() for k in ["ALL-0", "ALL-1", "ALL-2", "ALL-3", "ALL-4", "NOT", 0, 1, 2, 3, 4]}

        # Read in dictionary file
        with open(file_name) as file:
            all_words = set((s.strip() for s in file.readlines()))

        # Fill with data
        for word in all_words:
            for letter in words_tree:
                if letter in word:
                    for i in range(5):
                        if word[i] != letter:
                            words_tree[letter]["ALL-%d" % i].add(word)
                else:
                    words_tree[letter]["NOT"].add(word)
            for index, member in enumerate(word):
                words_tree[member][index].add(word)
        return words_tree, all_words

    @classmethod
    def get_constraint_input(cls, guess):
        """
        After a guess has been made, the user must respond with a string representing
        the validity of each letter in the guess string. The user input must be 5 characters
        long and consist of only '+', '*', and '-'.

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

        # Compute constraints
        constraints = []
        for i, s in enumerate(result):
            if s == "+":
                # Positional match
                constraints.append((guess[i], i))
            elif s == "*":
                # Non-positional match
                constraints.append((guess[i], "ALL-%d" % i))
            else:
                # No match
                constraints.append((guess[i], "NOT"))
        return constraints, result == "+++++"

    @classmethod
    def get_constraint_input_automated(cls, guess, target):
        """
        Same purpose as above method, but designed to be used by an automated tester.
        Thus, instead of receiving user input, this method takes the target word as
        a parameter.

        :param guess: the guess that has just been made
        :param target: the word that the agent is trying to guess
        :return: a list of new constraints, a boolean representing whether the puzzle is
                 solved (i.e. result == target)
        """
        # Compute constraints
        constraints = []
        for i, s in enumerate(guess):
            if s == target[i]:
                # Positional match
                constraints.append((guess[i], i))
            elif s in target:
                # Non-positional match
                constraints.append((guess[i], "ALL-%d" % i))
            else:
                # No match
                constraints.append((guess[i], "NOT"))
        return constraints, guess == target

    def reset(self):
        """
        Reset instance variables so that the game can be played again.
        """
        self.valid_words = self.all_words.copy()

    def calculate_elims(self, constraints):
        """
        Calculate the number of words that can be eliminated from self.valid_words
        given the set of constraints. For more info on the format and meaning
        of constraints, see documentation of self.sample_valid_words()

        :param constraints: the constraints
        :return: number of eliminations
        """
        possibility_sets = [self.words_tree[c[0]][c[1]] for c in constraints]

        # If self.valid_words contains every word in the dictionary, it is not necessary
        # to add this set to the collection of possibilities
        if len(self.valid_words) < len(self.all_words):
            possibility_sets.append(self.valid_words)

        # It is more efficient to process the smaller sets first
        possibility_sets.sort(key=len)
        return len(self.valid_words) - len(reduce(lambda a, b: a.intersection(b), possibility_sets))

    def sample_valid_words(self, num_samples):
        """
        Score each valid word based on the number of valid words it is expected to eliminate. I.e.
        for every scenario that can occur on the next move (a scenario consists of a guess word and
        a target word), which guess word results in the greatest reduction in the size of
        self.valid_words on average?

        Since it is extremely inefficient to test all possible guess/target pairs, instead
        for each guess word a random sample of num_samples target words are selected.

        For each scenario (guess, target), a collection of constraints is generated. This
        is information that would be provided to the agent by the user if this guess were
        made and the target value is target. A constraint is a tuple that represents a two-level
        index into self.words_tree. The set that is retrieved by computing
        self.words_tree[c[0]][c[1]] for constraint c is the set of all words that are possible
        given that constraint. Thus, the set of all valid words is the intersection of all the
        constraint sets and the current self.valid_words.

        :param num_samples: Number of scenarios to test per word in self.valid_words
        :return: A dict mapping each word to its score. Higher is better.
        """
        words_scores = {word: 0 for word in self.valid_words}
        for guess in self.valid_words:
            for target in random.sample(list(self.valid_words), num_samples):
                constraints = []
                positional_matches = set()
                for i in range(5):
                    if guess[i] == target[i]:
                        positional_matches.add(guess[i])
                        constraints.append((guess[i], i))
                shared_letters = set(guess).intersection(set(target))
                constraints.extend(
                    [(s, "ALL-%d" % guess.index(s)) for s in shared_letters.difference(positional_matches)] +
                    [(s, "NOT") for s in set(guess).difference(shared_letters)]
                )
                words_scores[guess] += self.calculate_elims(constraints)
        return words_scores

    def next_guess(self, move, first_moves_file, max_samples=50):
        """
        Compute the next guess.

        Because of the runtime of this algorithm on the first move, it is recommended to provide
        a static file that contains one or more words that the first move can be selected from.
        If this file is not present, it will be generated. This generation process will take
        approximately 3-5 minutes.

        :param move: move number, starts at 0
        :param first_moves_file: file containing viable first move options
        :param max_samples: the maximum number of samples to send to self.sample_valid_words()
                            used to prevent egregiously long runtimes.
        :return: the next guess word
        """
        # If this is the first move, return randomly-selected word from first_moves_file
        # if that file exists.
        if move == 0 and exists(first_moves_file):
            with open(first_moves_file) as file:
                move = random.choice([s.strip() for s in file.readlines()])
                if move in self.valid_words:
                    return move
        elif move == 5:
            return random.choice(list(self.valid_words))

        # Tell the user to be patient if generating first moves
        if move == 0:
            print("Hold tight. Generating first move options. This will take about 5 mins.")

        # Compute scores
        words_scores = self.sample_valid_words(min(len(self.valid_words), max_samples))

        # Write first move data to file if necessary
        if move == 0:
            with open(first_moves_file, "w+") as file:
                file.write("\n".join(sorted(words_scores, key=words_scores.get, reverse=True)[0:100]))

        # Compute max score and return move
        max_score = max(words_scores.values())
        return random.choice([k for k in words_scores if words_scores[k] == max_score])

    def update_valid_words(self, new_constraints):
        """
        Update self.valid_words based on a new set of constraints.
        :param new_constraints: new constraints
        """
        possibility_sets = [self.words_tree[c[0]][c[1]] for c in new_constraints]
        possibility_sets.append(self.valid_words)
        possibility_sets.sort(key=len)
        self.valid_words = reduce(lambda a, b: a.intersection(b), possibility_sets)

    def run_test_games(self, num_games, first_moves_file):
        """
        Testing harness that will simulate running num_games games. Win/lose statistics
        will be printed once all simulations are complete.

        :param num_games: number of games to run
        :param first_moves_file: file containing first moves
        """
        results = {k: 0 for k in range(-1, 6)}
        for _ in range(num_games):
            moves = self.cpu_play_automated(random.choice(list(self.all_words)), first_moves_file)
            results[moves] += 1
            self.reset()
        for i in range(-1, 6):
            if i >= 0:
                print("Solved in %d moves: %0.1f%%" % (i + 1, results[i] * 100.0 / num_games))
            else:
                print("Unsolved: %0.1f%%" % (results[i] * 100.0 / num_games))

    def cpu_play_automated(self, target, first_moves_file):
        """
        Automated game runner method designed to be used with self.run_test_games().

        :param target: the target word
        :param first_moves_file: file containing first moves
        :return: number of moves if win, -1 if loss
        """
        for move in range(0, 6):
            guess = self.next_guess(move, first_moves_file)
            new_constraints, is_solved = self.get_constraint_input_automated(guess, target)
            if is_solved:
                return move
            self.update_valid_words(new_constraints)
        return -1

    def cpu_play(self, first_moves_file):
        """
        Game runner method.

        :param first_moves_file: file containing first moves
        :return:
        """
        for move in range(1, 7):
            guess = self.next_guess(move - 1, first_moves_file)
            print("Move %d: %s" % (move, guess))
            new_constraints, is_solved = self.get_constraint_input(guess)
            if is_solved:
                print("Solved in %d moves! Answer is \"%s\"" % (move, guess))
                return
            self.update_valid_words(new_constraints)
            if len(self.valid_words) == 0:
                print("I'm all out of possibilities! Double check your input.")
                return
            print()
        print("Sorry, no solution was reached in 6 moves")


def main():
    # Parse command line args
    dictionary_file = "dict.txt"
    first_moves_file = "first-moves.txt"
    is_test_mode = False
    num_tests = 0
    for i, arg in enumerate(argv):
        if arg == "--test" and len(argv) > i + 1:
            is_test_mode = True
            num_tests = int(argv[i + 1])
        elif arg == "--first-moves" and len(argv) > i + 1:
            first_moves_file = argv[i + 1]
        elif arg == "--dict" and len(argv) > i + 1:
            dictionary_file = argv[i + 1]

    # Run wordle
    wordle = Wordle(dictionary_file)
    if is_test_mode:
        wordle.run_test_games(num_tests, first_moves_file)
    else:
        wordle.cpu_play(first_moves_file)


if __name__ == "__main__":
    main()
