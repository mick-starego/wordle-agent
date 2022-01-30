# Wordle Agent
An agent that plays the popular word game Wordle.

## Gameplay

On each turn, the Wordle agent will provide a 5-letter guess word. The user
will respond with a string representing the validity of the guess. This
string must be five characters long and contain only the following symbols:

* `+` a positional match (green tile)
* `*` a non-positional match (yellow tile)
* `-` no match (grey tile)

### Options
* `--dict <file path>`
  * Specify a dictionary file path.
  * A dictionary file must contain a collection of five-character words with one word per line.
  * The Wordle dictionary is used by default.
* `--numeric`
  * If present, 0-9 will be used as the alphabet instead of A-Z.
* `--hard`
  * Run in hard mode, where all revealed hints must be used in subsequent guesses.
* `--target <word>`
  * Run an automated game with a specific target word.

### Example Game
Target word: `COULD`
```
>>> python wordle.py

==================================================
##################    WORDLE    ##################
--------------------------------------------------

Move 1: TRAIN
Enter result: -----

Move 2: CLOSE
Enter result: +**--

Move 3: COULD
Enter result: +++++

Solved in 3 moves! Answer is "COULD"

--------------------------------------------------
```

## Provided Dictionaries
This repo includes four dictionaries in the `dicts/` directory. The Wordle dictionary is used by default.
* Wordle dictionary
  * `wordle.txt`
  * 2,315 words
  * All possible Wordle target words
* Stanford dictionary
  * `stanford.txt`
  * 5,757 words
  * The Stanford GraphBase list of five-letter words
  * Useful for evaluating agent performance on large word list
* Primes dictionary
  * `primes.txt`
  * 8,368 words
  * The list of all prime numbers between 10,000 and 99,999
  * Useful for playing Primel
  * When using this dictionary, be sure to add the `--numeric` flag
* Hockey dictionary
  * `hockey.txt`
  * 761 words
  * The list of all five-letter NHL player last names, past and present
  * Useful for playing Gordle

### First Moves
Each dictionary is accompanied by a first-moves file. This file contains the most optimal guess options for the first move.
Because the process of generating these options is computationally expensive, they loaded from a static file. This file
must be named with the dictionary file's name suffixed with "-first-moves". If a file matching this pattern does not exist, it will be generated.

## Testing
* A testing harness is included that will simulate games and track the agent's success.
* Using the command line option `--test <num tests>` will simulate the specified number of test and print a report the agent's performance

### Test Results
Here are a few benchmark test results.

#### Wordle Dictionary 10k Games
```
--------------------------------------------------
Solved in 1 moves: 0.1%
Solved in 2 moves: 5.5%
Solved in 3 moves: 36.7%
Solved in 4 moves: 47.4%
Solved in 5 moves: 8.8%
Solved in 6 moves: 1.5%
Unsolved: 0.1%
--------------------------------------------------
Average solution length: 3.64 moves
Win rate: 99.93%
--------------------------------------------------
```

#### Wordle Dictionary 10k Games Hard Mode
```
--------------------------------------------------
Solved in 1 moves: 0.1%
Solved in 2 moves: 5.2%
Solved in 3 moves: 39.8%
Solved in 4 moves: 43.6%
Solved in 5 moves: 9.1%
Solved in 6 moves: 1.8%
Unsolved: 0.5%
--------------------------------------------------
Average solution length: 3.62 moves
Win rate: 99.55%
--------------------------------------------------
```

#### Stanford Dictionary 1k Games
```
--------------------------------------------------
Solved in 1 moves: 0.1%
Solved in 2 moves: 3.5%
Solved in 3 moves: 21.6%
Solved in 4 moves: 45.6%
Solved in 5 moves: 19.9%
Solved in 6 moves: 7.6%
Unsolved: 1.7%
--------------------------------------------------
Average solution length: 4.06 moves
Win rate: 98.30%
--------------------------------------------------
```

#### Stanford Dictionary 1k Games Hard Mode
```
--------------------------------------------------
Solved in 1 moves: 0.0%
Solved in 2 moves: 3.2%
Solved in 3 moves: 26.4%
Solved in 4 moves: 42.3%
Solved in 5 moves: 17.8%
Solved in 6 moves: 6.4%
Unsolved: 3.9%
--------------------------------------------------
Average solution length: 3.98 moves
Win rate: 96.10%
--------------------------------------------------
```