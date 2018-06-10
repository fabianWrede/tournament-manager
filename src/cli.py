import argparse
import sys
from pathlib import Path
from operator import attrgetter
from threading import Thread
from time import sleep

from controller import processes
from data import data_connector

_progress_indicator_stopped = True

# sub-command functions
def create_tournament(args):
    f = Path(data_connector._get_file_path(args.tournament[0]))

    if f.is_file():
        if not ask_yes_no('Tournament already exists. Do you want to '
                          'overwrite existing file?'):
            return
    elif f.is_dir():
        print('There is a directory with the tournament name in the data '
              'folder. Please clean that up and try again or change the '
              'tournament name.')
        return

    processes.create_tournament(args.tournament[0], args.free_round[0],
                                args.free_round[1])


def add_team(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    if processes.check_tournament_started():
        print('Tournament already started. It is not possible to add more '
              'teams.')
        processes.close_tournament()
        return

    if processes.check_team_already_exists(args.name[0]):
        if not ask_yes_no(
                'There is already a team with the same name. Do you want to '
                'overwrite existing team?'):
            processes.close_tournament()
            return
        else:
            processes.remove_team(name=args.name[0])

    processes.add_team(args.name[0], args.performance[0])
    processes.close_tournament()


def remove_team(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    if processes.check_tournament_started():
        print('Tournament has already started. It is not possible to remove '
              'teams. Just enter results as lost games.')
        processes.close_tournament()
        return

    processes.remove_team(args.name[0])
    processes.close_tournament()


def show_teams(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    teams = processes._open_tournament.teams

    max_team_name = 6 
    
    if len(teams) > 0:
        max_team_name = max(max([len(t.name) for t in teams]) + 1, 
                            max_team_name)

    max_pv = len('Performance Value')

    print('{name:{name_width}}{pv:{pv_width}}'.format(name='Name',
                                                      name_width=max_team_name,
                                                      pv='Performance Value',
                                                      pv_width=max_pv))
    print('-' * (max_team_name + max_pv))

    for t in teams:
        print('{name:{name_width}}{pv:>{pv_width}}'.format(
            name=t.name,
            name_width=max_team_name,
            pv=t.performance_value,
            pv_width=max_pv))

    processes.close_tournament()


def start_tournament(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    # check already started
    if processes.check_tournament_started():
        print('Tournament already started and cannot be started again.')
        processes.close_tournament()
        return

    # check performance values of teams and assign random values
    processes.start_tournament()
    processes.close_tournament()


def stop_tournament(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    # check not yet started
    if not processes.check_tournament_started():
        print('Tournament not started yet, so there is nothing to stop.')
        processes.close_tournament()
        return

    # check performance values of teams and assign random values
    if ask_yes_no(
            'Do you really want to stop the tournament? All progress will be '
            'deleted.'):
        processes.stop_tournament()

    processes.close_tournament()


def next_round(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    # check tournament is started
    if not processes.check_tournament_started():
        print('Tournament has not started yet. Starting the tournament with '
              '"start-tournament" command, will automatically determine the '
              'first round.')
        processes.close_tournament()
        return

    # check current round is finished
    if not processes.check_current_round_is_finished():
        print('The current round is not finished yet. Use "show-round" '
              'command to see all matches of the current round and '
              '"enter-result {game} {points_a} {points_b}" command to enter '
              'the result.')
        processes.close_tournament()
        return

    # calculate standings, calculate next round
    processes.calculate_next_round()
    processes.close_tournament()


def revert_round(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    # check tournament is started
    if not processes.check_tournament_started():
        print('Tournament has not started yet. No round to revert.')
        processes.close_tournament()
        return

    if ask_yes_no(
            'Do you really want to revert the current round? All results will '
            'be deleted.'):
        processes.revert_round()

    processes.close_tournament()


def show_round(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    # check tournament is started
    if not processes.check_tournament_started():
        print('Tournament has not started yet, so there is no round to show. '
              'Use "start-tournament" to start the tournament.')
        processes.close_tournament()
        return

    # check round number, and use latest round if none or invalid is given
    round_number = _check_round_number(args.round[0])

    teams = processes._open_tournament.teams
    max_team_name = 6 if max([len(t.name) for t in teams]) + 2 < 6 else max(
        [len(t.name) for t in teams]) + 2
    points_width = 8
    game_width = len('Number') + 2

    print('Round', str(round_number + 1))
    print('{game_number:{game_width}}{team_a:{team_width}}{team_b:{'
          'team_width}}{points_a:{points_width}}{points_b:{'
          'points_width}}'.format(game_number='Number', game_width=game_width,
                                  team_a='Team A', team_b='Team B',
                                  team_width=max_team_name, points_a='Points',
                                  points_b='', points_width=points_width))
    print('-' * (game_width + max_team_name * 2 + points_width * 2))

    for g in processes._open_tournament.rounds[round_number].games:
        print('{game_number:<{game_width}}{team_a:{team_width}}{team_b:{'
              'team_width}}{points_a:{points_width}}{points_b:{'
              'points_width}}'.format(
                game_number=g.id, game_width=game_width, team_a=g.team_a,
                team_b=g.team_b if g.team_b is not None else 'free',
                team_width=max_team_name,
                points_a='' if g.points_a == -1 else g.points_a,
                points_b='' if g.points_b == -1 else g.points_b,
                points_width=points_width))

    processes.close_tournament()


def show_standings(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    # check tournament is started
    if not processes.check_tournament_started():
        print('Tournament has not started yet, so there no standings to show. '
              'Use "start-tournament" to start the tournament.')
        processes.close_tournament()
        return

    # update standings
    processes.calculate_standings()

    teams = sorted(processes._open_tournament.teams,
                   key=attrgetter('position'))
    max_team_name = 6 if max([len(t.name) for t in teams]) + 2 < 6 else max(
        [len(t.name) for t in teams]) + 2
    position_width = len('Position') + 2
    wins_width = len('Wins') + 2
    losses_width = len('Losses') + 2
    bh_width = len('BH') + 2
    fbh_width = len('FBH') + 2
    sb_width = len('SB') + 2
    koya_width = len('Kayo') + 2
    points_diff_width = len('Points difference') + 2
    points_width = len('Points') + 2
    points_against_width = len('Points against') + 2
    fl_width = len('FR') + 2
    pv_width = len('PV') + 2
    print('{position:{position_width}}{team:{team_width}}{wins:{wins_width}}{'
          'losses:{losses_width}}{bh:{bh_width}}{fbh:{fbh_width}}{sb:{'
          'sb_width}}{koya:{koya_width}}{points_diff:{points_diff_width}}{'
          'points:{points_width}}{points_against:{points_against_width}}{fl:{'
          'fl_width}}{pv:{pv_width}}'.format(
            position='Position', position_width=position_width,
            team='Team', team_width=max_team_name,
            wins='Wins', wins_width=wins_width,
            losses='Losses', losses_width=losses_width,
            bh='BH', bh_width=bh_width, fbh='FBH', fbh_width=fbh_width,
            sb='SB', sb_width=sb_width, koya='Koya', koya_width=koya_width,
            points_diff='Points difference',
            points_diff_width=points_diff_width,
            points='Points', points_width=points_width,
            points_against='Points against',
            points_against_width=points_against_width,
            fl='FR', fl_width=fl_width, pv='PV', pv_width=pv_width))

    print('-' * (
        position_width + max_team_name + wins_width + losses_width +
        bh_width + fbh_width + sb_width + koya_width + points_diff_width +
        points_width + points_against_width + fl_width + pv_width))

    for t in teams:
        print('{position:<{position_width}}{team:{team_width}}{wins:{'
              'wins_width}}{losses:{losses_width}}{bh:{bh_width}}{fbh:{'
              'fbh_width}}{sb:{sb_width}}{koya:{koya_width}}{points_diff:{'
              'points_diff_width}}{points:{points_width}}{points_against:{'
              'points_against_width}}{fl:{fl_width}}{pv:{pv_width}}'.format(
                position=t.position, position_width=position_width,
                team=t.name, team_width=max_team_name,
                wins=t.wins, wins_width=wins_width,
                losses=t.losses, losses_width=losses_width,
                bh=t.bh, bh_width=bh_width, fbh=t.fbh, fbh_width=fbh_width,
                sb=t.sb, sb_width=sb_width, koya=t.koya, koya_width=koya_width,
                points_diff=t.points - t.points_against,
                points_diff_width=points_diff_width,
                points=t.points, points_width=points_width,
                points_against=t.points_against,
                points_against_width=points_against_width,
                fl=t.fl, fl_width=fl_width,
                pv=t.performance_value, pv_width=pv_width))

    processes.close_tournament()


def enter_result(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    # Check tournament is started
    if not processes.check_tournament_started():
        print(
            'Tournament has not been started. Use "start-tournament" command.')
        processes.close_tournament()
        return

    # check the game number exists
    if args.game[0] < 1 or args.game[0] > len(
        processes._open_tournament.rounds) * len(
        processes._open_tournament.rounds[0].games):
        print('Game number does not exist. Use "show-round" command to see '
              'games of current round.')
        processes.close_tournament()
        return

    # check points >= 0
    if args.a[0] < 0 or args.b[0] < 0:
        print('Points scored by a team must be greater or equal to 0. At the '
              'moment there is no way to enter negative scores.')
        processes.close_tournament()
        return

    # check remis
    if args.a[0] == args.b[0]:
        print(
            'At the moment remis are not supported. There has to be a winner!')
        processes.close_tournament()
        return

    # check if game already has a result and ask whether it should be
    # overwritten
    game = processes._open_tournament.get_game_by_id(args.game[0])
    if game.is_finished():
        if not ask_yes_no(
                'Result for this game has already been entered. Do you want '
                'to overwrite the result?'):
            processes.close_tournament()
            return

    # add result
    processes.add_result(game, args.a[0], args.b[0])
    processes.close_tournament()


def export_round(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return

    if not processes.check_tournament_started():
        print('Tournament has not started. Nothing to export.')
        processes.close_tournament()
        return

    # check round number, and use latest round if none is given
    round_number = _check_round_number(args.round[0])
    # create latex file and build it with pdflatex
    processes.export_round(round_number)

    processes.close_tournament()


def export_standings(args):
    try:
        processes.load_tournament(args.tournament[0])
    except FileNotFoundError:
        print('Could not open the tournament. Have you created the tournament, yet?', 
              'if not, try the "create-tournament" command.')
        return
    
    if not processes.check_tournament_started():
        print('Tournament has not started. Nothing to export.')
        processes.close_tournament()
        return

    # update standings and export them
    processes.calculate_standings()
    processes.export_standings()

    processes.close_tournament()


def ask_yes_no(msg):
    s = input(msg + " [y/N]: ")
    return s == 'y' or s == 'yes' or s == 'Y' or s == 'Yes' or s == 'YES'


def create_parser():
    parser = argparse.ArgumentParser(
        description='Manage tournaments with the swiss system.')

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.0.1a')

    parser.add_argument('tournament', metavar='Tournament', nargs=1,
                        help='The tournament for the action. Corresponds to '
                             'the file name.')

    # subparsers for the commands
    subparsers = parser.add_subparsers(title='Subcommands',
                                       description='All possible '
                                                   'subcommands, which can '
                                                   'be used on a tournament',
                                       help='Usage: Tournament {subcommand} '
                                            '{arguments for subcommand}')

    # create tournament
    parser_create_tournament = subparsers.add_parser('create-tournament',
                                                     aliases=['ct'],
                                                     help='Creates a new '
                                                          'tournament with '
                                                          'the name given in '
                                                          '"tournament" '
                                                          'argument.')
    parser_create_tournament.add_argument(
        '-f', '--free-round', metavar='Points free round', nargs=2,
        default=[13, 0],
        help='Points for free rounds. Free rounds count as a win, this '
             'can be used to set how many points the team and the "free" '
             'team "scored".')
    parser_create_tournament.set_defaults(func=create_tournament)

    # add_team
    parser_add_team = subparsers.add_parser('add-team', aliases=['at'],
                                            help='Adds a team to the '
                                                 'tournament.')
    parser_add_team.add_argument('name', metavar='Name', nargs=1,
                                 help='Name of the team.')
    parser_add_team.add_argument('-p', '--performance', metavar='Performance',
                                 type=int, nargs=1, default=[-1],
                                 help='Performance value of the team, '
                                      'used to create standings for round 1.')
    parser_add_team.set_defaults(func=add_team)

    # show_teams
    parser_show_teams = subparsers.add_parser('show-teams',
                                              help='Shows all teams.')
    parser_show_teams.set_defaults(func=show_teams)

    # remove_team
    parser_remove_team = subparsers.add_parser('remove-team', aliases=['rt'],
                                               help='Remove a team.')
    parser_remove_team.add_argument('name', metavar='Name', nargs=1,
                                    help='Name of the team.')
    parser_remove_team.set_defaults(func=remove_team)

    # start_tournament
    parser_start_tournament = subparsers.add_parser('start-tournament',
                                                    aliases=['st'],
                                                    help='Starts the '
                                                         'tournament. '
                                                         'Afterwards no '
                                                         'teams can be added '
                                                         'anymore.')
    parser_start_tournament.set_defaults(func=start_tournament)

    # stop_tournament
    parser_stop_tournament = subparsers.add_parser('stop-tournament',
                                                   help='Stops the '
                                                        'tournament. All '
                                                        'progress is deleted.')
    parser_stop_tournament.set_defaults(func=stop_tournament)

    # next_round
    parser_next_round = subparsers.add_parser('next-round', aliases=['nr'],
                                              help='Calculates the next '
                                                   'round for the '
                                                   'tournament. Only '
                                                   'possible when all '
                                                   'matches of current round '
                                                   'are finished.')
    parser_next_round.set_defaults(func=next_round)

    # revert_round
    parser_revert_round = subparsers.add_parser('revert-round', aliases=['rr'],
                                              help='Reverts the current '
                                                   'round. All results are '
                                                   'deleted.' )
    parser_revert_round.set_defaults(func=revert_round)

    # show_round
    parser_show_round = subparsers.add_parser('show-round', aliases=['sr'],
                                              help='Shows all matches of a '
                                                   'round.')
    parser_show_round.add_argument('-r', '--round', metavar='Round', nargs=1,
                                   default=[-1], type=int,
                                   help='Round to show. If not specified, '
                                        'current round is choosen.')
    parser_show_round.set_defaults(func=show_round)

    # show_standings
    parser_show_standings = subparsers.add_parser('show-standings',
                                                  aliases=['ss'],
                                                  help='Shows current '
                                                       'standings.')
    parser_show_standings.set_defaults(func=show_standings)

    # enter_result
    parser_enter_result = subparsers.add_parser('enter-result', aliases=['er'],
                                                help='Creates a new '
                                                     'tournament with the '
                                                     'name given in '
                                                     '"tournament" argument.')
    parser_enter_result.add_argument('game', metavar='Game', nargs=1, type=int,
                                     help='Game number. First column of '
                                          'output of "show-round" command.')
    parser_enter_result.add_argument('a', metavar='Points_A', nargs=1,
                                     type=int, help='Points of team A.')
    parser_enter_result.add_argument('b', metavar='Points_B', nargs=1,
                                     type=int, help='Points of team B.')
    parser_enter_result.set_defaults(func=enter_result)

    # export_round
    parser_export_round = subparsers.add_parser('export-round',
                                                aliases=['exr'],
                                                help='Export round as pdf.')
    parser_export_round.add_argument('-r', '--round', metavar='Round', nargs=1,
                                     default=[-1], type=int,
                                     help='Round to export. If not '
                                          'specified, current round is '
                                          'chosen.')
    parser_export_round.set_defaults(func=export_round)

    # export_standings
    parser_export_standings = subparsers.add_parser('export-standings',
                                                    aliases=['exs'],
                                                    help='Export standings '
                                                         'as pdf.')
    parser_export_standings.set_defaults(func=export_standings)

    return parser

# cli checks
def _check_round_number(round):
    round_number = round - 1
    if round_number < 0 or round_number >= len(
            processes._open_tournament.rounds):
        return len(processes._open_tournament.rounds) - 1
    return round_number

# main function for setup.py
def main():
    parser = create_parser()

    args = parser.parse_args() 

    try:
        args.func(args)
    except AttributeError:
        print('Check the help (-h) to see what '
              'you can do here.')
        #raise AttributeError

# starting point of the cli
if __name__ == '__main__':
    main()
