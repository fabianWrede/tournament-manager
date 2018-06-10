from data.model import Tournament, Team
from data.data_connector import save, load
from controller import swiss_system
from controller import export


_open_tournament = None


def create_tournament(name, points_fr_win=13, points_fr_loss=0):
    global _open_tournament
    _open_tournament = Tournament(name=name, points_fr_win=points_fr_win,
                           points_fr_loss=points_fr_loss)
    save(_open_tournament)


def load_tournament(name):
    global _open_tournament
    _open_tournament = load(name)


def close_tournament():
    global _open_tournament
    save(_open_tournament)
    _open_tournament = None


def add_team(name, performance_value=-1):
    if _open_tournament is not None and not _open_tournament.is_started():
        team = Team(name=name, performance_value=performance_value)
        _open_tournament.add_team(team)


def remove_team(team=None, name=''):
    if _open_tournament is not None and not _open_tournament.is_started():
        if team is not None:
            _open_tournament.remove_team(team)
        elif name != '':
            for t in _open_tournament.teams:
                if t.name == name:
                    _open_tournament.remove_team(t)


def start_tournament():
    if _open_tournament is not None and not _open_tournament.is_started():
        swiss_system.check_and_fix_initial_performance_values(_open_tournament)
        swiss_system.calculate_next_round(_open_tournament)


def stop_tournament():
    if _open_tournament is not None and _open_tournament.is_started():
        _open_tournament.reset()
        swiss_system.calculate_standings(_open_tournament)

def revert_round():
    if _open_tournament is not None \
            and len(_open_tournament.rounds) > 0:
        _open_tournament.rounds.pop()
        swiss_system.calculate_standings(_open_tournament)
        

def add_result(game, points_a, points_b):
    game.add_result(points_a, points_b)


def calculate_standings():
    swiss_system.calculate_standings(_open_tournament)


def calculate_next_round():
    swiss_system.calculate_next_round(_open_tournament)


# export 
def export_round(round_number):
    if _open_tournament is not None:
        export.export_round(_open_tournament, round_number)


# export 
def export_standings():
    if _open_tournament is not None:
        export.export_standings(_open_tournament)


# some status checks
def check_team_already_exists(name):
    if _open_tournament is not None:
        return name in [x.name for x in _open_tournament.teams]
    return False


def check_tournament_started():
    if _open_tournament is not None:
        return _open_tournament.is_started()
    return False


def check_current_round_is_finished():
    if _open_tournament is not None:
        return all(
            game.is_finished() for game in _open_tournament.rounds[-1].games)
    return False
