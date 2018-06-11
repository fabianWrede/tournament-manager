# tournament-manager [![Build Status](https://travis-ci.com/fabianWrede/tournament-manager.svg?branch=master)](https://travis-ci.com/fabianWrede/tournament-manager) [![Snap Status](https://build.snapcraft.io/badge/fabianWrede/tournament-manager.svg)](https://build.snapcraft.io/user/fabianWrede/tournament-manager)
Tool to manage (e-)sports tournaments. It provides a CLI and supports the swiss system.

## Install
This should be as easy as running `sudo snap install tournament-manager` or `sudo snap install --edge tournament-manager` if you want the latest version.
If snaps are not available on your system, just clone the repository with `git clone git@github.com:fabianWrede/tournament-manager.git`, navigate to the source folder `src/` and run `python3 cli.py [arguments]`.
In the following, we assume that you can use `tournament-manager` to run the program, if not substitute it in your mind with `python3 cli.py`.

## Usage
This is a command-line tool, so you have to run different commands from your preferred terminal. 
In general, all commands are structured as follows:
`tournament-manager {name-of-the-tournament} {command} {arguments}`


First, you must create a tournament with
`tournament-manager your-tournament create-tournament`
The name of the tournament must be unique and you will be warned if there is already a tournament with the name.
There will be a file with the same name, which contains all necessary data in json format.


Someone will probably participate, so use the 
`tournament-manager your-tournament add-team {team-name}`
command to add a team. Again, the name must be unique for that tournament and there will be warning if the name already exists.


All teams added?
Run `tournament-manager your-tournament start-tournament` to get started.

But I still don't know who plays against each other !?
No worries: `tournament-manager your-tournament show-round`


Enter the result with `tournament-manager your-tournament {game-number} {points-team-a} {points-team-b}`


And who is the winner?
`tournament-manager your-tournament show-standings` will show you the current standings for the tournament.


There is also an export command for rounds and the standings. It uses `pdflatex` to create a PDF document, if
for example, you want to print a round so that all participants in a tournament can easily check their next match.
Consequently, if you don't have `pdflatex` installed, the export won't work. On Ubuntu the probably easiest way to install Latex is
`sudo apt install texlive-full` or `sudo apt install texlive texlive-latex-extra`.

The commands for the export are `export-round` and `export-standings` and if you have installed it as a snap, the output PDFs will be in the folder
`~/snap/tournament-manager/common/export/`.


## FAQ
### Free rounds have a result of 13-0 and there are no remis?
This tool was written with Petanque (or Boule) in mind. A game ends when one team has 13 points and there is usually always a winner. 
The result for free rounds can already be changed with the `-f` flag for the `create-tournament` command. 

### What are BH, FBH, SB, and Koya?
BH: Buchholzpunkte (number of wins of all opponents)

FBH: Feinbuchholzpunkte (number of BH of all opponents)

SB: Sonneborn-Berger (number of wins of opponents the team has won against)

Koya: Koya :) (number of wins of oppenents that have won 50% or more of their matches)

All are numbers to determine a ranking of the teams.

Check for example: <https://en.wikipedia.org/wiki/Tie-breaking_in_Swiss-system_tournaments> and <https://en.wikipedia.org/wiki/Buchholz_system>

In German: <https://de.wikipedia.org/wiki/Feinwertung>

### So how is the ranking done?
1. Number of wins
2. Buchholzpunkte (wins of opponents)
3. Feinbuchholzpunkte (Buchholzpunkte of opponents)
4. Sonneborn-Berger (wins of opponents the team won against)
5. Koya (wins of opponents that won more than or equal to 50% of their games)
6. Direct encounter
7. Point difference
8. Scored points
9. Number of free rounds (less is better)
10. Performance Value


### What is this performance value?
Each team has a performance value, which can be set with `add-team -p {number}`.
If no value is specified, there will be a value randomly assigned when the `start-tournament` command is used.
Each team with a performance value, will be higher ranked than a team without one.
This value is used to determine the matches in the first round and if all other numbers are equal. 
That might not be quite fair, but the chances that it actually plays a role are quite marginal...

