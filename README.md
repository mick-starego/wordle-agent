# Wordle Agent
An agent that can play the popular word game Wordle.

### Gameplay

On each turn, the Wordle agent will provide a 5-letter guess word. The user
will respond with a string representing the validity of the guess. This
string must be five characters long and contain only the following symbols:

* `+` a positional match
* `*` a non-positional match
* `-` no match

#### Example Game
Target word: `KNOLL`
```
>>> python wordle.py
Move 1: STELA
Enter result: ---+-

Move 2: DOILY
Enter result: -*-+-

Move 3: HULLO
Enter result: --*+*

Move 4: KNOLL
Enter result: +++++
Solved in 4 moves! Answer is "KNOLL"
```

### Input Files
All necessary input files are provided in this repo. If you are just interested in playing the game, skip this section.
* `dict.txt`
  * The dictionary of five-letter words provided to the agent
  * The provided file contains all valid five-letter scrabble words
  * To specify a different dictionary file use the command line option `--dict <filename>`
* `first-moves.txt`
  * This file contains the 100 best first moves computed by the agent
  * Due to the runtime of computing the first move data, the agent will select the first move from this static file at random
  * If this file is not present, the agent will generate it. This process will take approximately 5 minutes.
  * To specify a different first moves file, use the command line option `--first-moves <filename>`

### Testing
* A testing harness is included that will simulate games and track the agent's success.
* Using the command line option `--test <num tests>` will simulate the specified number of test and print a report the agent's performance

#### Test Results
Here are the results of simulating 500 games. In this test, the agent achieved a win rate of 92.4%.
```
Solved in 1 moves: 0.0%
Solved in 2 moves: 1.6%
Solved in 3 moves: 19.4%
Solved in 4 moves: 41.6%
Solved in 5 moves: 20.4%
Solved in 6 moves: 9.4%
Unsolved: 7.6%
```