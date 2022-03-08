# Wordle Agent
An agent that plays the popular word game Wordle.

## Installation
* Requires Python 3
* Requires package `progressbar2`
  * Run `pip install progressbar2` to install

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
* `--start <word>`
  * Run with a specific start word
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
Here are a few benchmark test results. Unless otherwise specified, the number
of games simulated is equal to the size of the dictionary.

Note that the `primes.txt` dictionary is too large to efficiently test with the current version of the algorithm. There is room here for future improvements.

#### Wordle Dictionary
````
--------------------------------------------------
Start Word: TRACE
--------------------------------------------------
Solved in 1 moves: 0.0%
Solved in 2 moves: 3.8%
Solved in 3 moves: 48.4%
Solved in 4 moves: 44.8%
Solved in 5 moves: 3.0%
Solved in 6 moves: 0.0%
Unsolved: 0.0%
--------------------------------------------------
Average solution length: 3.47 moves
Win rate: 100.00%
--------------------------------------------------
````

#### Hockey Dictionary
````
--------------------------------------------------
Solved in 1 moves: 0.0%
Solved in 2 moves: 10.0%
Solved in 3 moves: 63.6%
Solved in 4 moves: 26.1%
Solved in 5 moves: 0.3%
Solved in 6 moves: 0.0%
Unsolved: 0.0%
--------------------------------------------------
Average solution length: 3.17 moves
Win rate: 100.00%
--------------------------------------------------
````

[comment]: <> (#### Wordle Dictionary 10k Games &#40;v1&#41;)

[comment]: <> (```)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Solved in 1 moves: 0.1%)

[comment]: <> (Solved in 2 moves: 5.5%)

[comment]: <> (Solved in 3 moves: 36.7%)

[comment]: <> (Solved in 4 moves: 47.4%)

[comment]: <> (Solved in 5 moves: 8.8%)

[comment]: <> (Solved in 6 moves: 1.5%)

[comment]: <> (Unsolved: 0.1%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Average solution length: 3.64 moves)

[comment]: <> (Win rate: 99.93%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (```)

[comment]: <> (#### Wordle Dictionary 10k Games Hard Mode &#40;v1&#41;)

[comment]: <> (```)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Solved in 1 moves: 0.1%)

[comment]: <> (Solved in 2 moves: 5.2%)

[comment]: <> (Solved in 3 moves: 39.8%)

[comment]: <> (Solved in 4 moves: 43.6%)

[comment]: <> (Solved in 5 moves: 9.1%)

[comment]: <> (Solved in 6 moves: 1.8%)

[comment]: <> (Unsolved: 0.5%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Average solution length: 3.62 moves)

[comment]: <> (Win rate: 99.55%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (```)

[comment]: <> (#### Stanford Dictionary 1k Games &#40;v1&#41;)

[comment]: <> (```)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Solved in 1 moves: 0.1%)

[comment]: <> (Solved in 2 moves: 3.5%)

[comment]: <> (Solved in 3 moves: 21.6%)

[comment]: <> (Solved in 4 moves: 45.6%)

[comment]: <> (Solved in 5 moves: 19.9%)

[comment]: <> (Solved in 6 moves: 7.6%)

[comment]: <> (Unsolved: 1.7%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Average solution length: 4.06 moves)

[comment]: <> (Win rate: 98.30%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (```)

[comment]: <> (#### Stanford Dictionary 1k Games Hard Mode &#40;v1&#41;)

[comment]: <> (```)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Solved in 1 moves: 0.0%)

[comment]: <> (Solved in 2 moves: 3.2%)

[comment]: <> (Solved in 3 moves: 26.4%)

[comment]: <> (Solved in 4 moves: 42.3%)

[comment]: <> (Solved in 5 moves: 17.8%)

[comment]: <> (Solved in 6 moves: 6.4%)

[comment]: <> (Unsolved: 3.9%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (Average solution length: 3.98 moves)

[comment]: <> (Win rate: 96.10%)

[comment]: <> (--------------------------------------------------)

[comment]: <> (```)