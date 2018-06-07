from operator import attrgetter
from collections import Counter
from itertools import permutations
import random
import logging

from data.model import Tournament, Team, Game, Round
from controller.helper import get_games_of_team, get_game_of_teams
from controller.errors import NoMatchError


__logger = logging.getLogger('swiss_system')


def check_and_fix_initial_performance_values(tournament):
    # first check whether there is already a correct ranking
    performance_value_count = Counter(
        [t.performance_value for t in tournament.teams])
    if performance_value_count['-1'] == 0 and \
            performance_value_count.most_common(1)[0][1] == 1:
        return

    __logger.info("No valid inital order of teams. Fix performance values.")

    teams_without_performance_value = []
    teams_with_performance_value = []
    for t in tournament.teams:
        if t.performance_value == -1:
            teams_without_performance_value.append(t)
        else:
            teams_with_performance_value.append(t)

    # any team with performance value should be higher ranked than teams
    # without, so we just add the number of teams without performance value to
    # the performance value of the other teams
    number_of_teams_without_performance_value = len(
        teams_without_performance_value)
    if number_of_teams_without_performance_value > 0:
        for t in teams_with_performance_value:
            t.performance_value += number_of_teams_without_performance_value

        # assign random performance value to teams without one, in the range
        #  0 .. len(teams_without_performance_value)
        random_performance_values = random.sample(
            range(0, number_of_teams_without_performance_value),
            number_of_teams_without_performance_value)
        for t in teams_without_performance_value:
            t.performance_value = random_performance_values.pop()

    # fix several teams with same value
    # if all values are unique, we are done
    if len(teams_with_performance_value) > 1:
        performance_value_count_2 = Counter(
            [t.performance_value for t in teams_with_performance_value])
        if performance_value_count_2.most_common(1)[0][1] == 1:
            return

        # so there are some teams with the same value
        for t in teams_with_performance_value:
            same_performance_value = {t}

            for t2 in teams_with_performance_value:
                if t.performance_value == t2.performance_value:
                    same_performance_value.add(t2)

            # this performance value is unique
            if len(same_performance_value) == 1:
                continue

            # here we have some duplicates, so we shift all other teams with a
            # higher performance value
            _shift_performance_values(teams_with_performance_value,
                                    len(same_performance_value) - 1,
                                    t.performance_value)

            # and randomly order teams with same value
            random_shift = random.sample(range(0, len(same_performance_value)),
                                        len(same_performance_value))
            for t3 in same_performance_value:
                t3.performance_value = t3.performance_value \
                                       + random_shift.pop()


def _shift_performance_values(teams, value, threshold):
    for t in teams:
        if t.performance_value > threshold:
            t.performance_value = t.performance_value + value


def calculate_next_round(tournament):
    calculate_standings(tournament)
    rnd = Round()
    teams = sorted(tournament.teams, key=attrgetter('position'))
    
    if len(tournament.rounds) > 0:  # some round in the tournament
        game_id = len(tournament.rounds) * len(tournament.rounds[0].games) + 1

        # determine free round
        if len(tournament.teams) % 2 == 1:
            min_free_rounds = min([t.fl for t in teams])
            for t in reversed(teams):
                if (t.fl == min_free_rounds):
                    t.fl = t.fl + 1
                    game = Game(game_id, t, None, 13, 0)
                    game_id += 1
                    rnd.games.append(game)
                    teams.remove(t)
                    break

        # used for fallback if pool matching fails
        teams_without_free_round = list(teams)
        game_id_fallback = game_id

        # go through all pools (teams with same number of wins) and
        # determine games
        max_wins = max([t.wins for t in teams])
        min_wins = min([t.wins for t in teams])

        games = []

        for wins in range(max_wins, min_wins - 1, -1):
            pool = [x for x in teams if x.wins == wins]

            hl_candidates = sorted([x for x in teams if x.wins == wins - 1],
                                   key=attrgetter('hl', 'position'))

            try:
                games_in_pool = match_pool(tournament, pool, hl_candidates,
                                            game_id)
                game_id += len(games_in_pool)
                games += games_in_pool
            except:
                # not possible to find matches for a pool
                # abandon pool system and try to find any possible way for next
                # round
                __logger.info('Pool system does not produce valid round.' 
                              'Try any possibility for matches.')
                try:
                    games = match_teams_greedy(tournament, 
                                    teams_without_free_round, game_id_fallback)
                except NoMatchError:
                    __logger.error('No valid round could be determined.')
                    print('No valid round could be determined. Maybe you want '
                          'to play too many rounds for too few teams? '
                          'Usually no match between two teams is repeated.')
                    return
                break
            else:
                # remove already matched teams from list of teams
                #for team_a, team_b in [(tournament.get_team_by_name(g.team_a), tournament.get_team_by_name(g.team_b)) for g in rnd.games]:
                for team in [tournament.get_team_by_name(g.team_a) for g in rnd.games] + [tournament.get_team_by_name(g.team_b) for g in rnd.games]:
                    try:
                        teams.remove(team)
                    except ValueError:
                        pass                    
    else:   # special case first round
        game_id = 1
        # free round for team in the middle
        if len(teams) % 2 == 1:
            t = teams[len(teams) // 2]
            t.fl = t.fl + 1
            game = Game(game_id, t, None, 13, 0)
            game_id += 1
            rnd.games.append(game)
            teams.remove(t)

        # split teams in two and play 1. of upper half against 1. of lower
        # half and so on
        try:
            rnd.games += match_teams_half_split(tournament, teams, game_id)
        except NoMatchError:
            __logger.error('Something went horribly wrong.'
                           'No match possible in first round.')      
            raise NoMatchError

    rnd.games += games
    tournament.rounds.append(rnd)


def match_pool(tournament, pool, hl_candidates, game_id):
    try: 
        # if uneven number, one team plays against a team with less
        # wins. Take best team from next pool that has not played in a 
        # higher pool before.
        if len(pool) % 2 == 1:
            return _match_pool_uneven(tournament, pool, hl_candidates, game_id)
        else:
            return _match_pool_even(tournament, pool, game_id)
    except NoMatchError:
        raise NoMatchError


def _match_pool_uneven(tournament, pool, hl_candidates, game_id):
    
    games = []

    # there is an uneven number of teams in the pool
    # go through all candidates
    while len(hl_candidates) > 0:
        hl_candidate = hl_candidates.pop(0)

        # find opponent for that team
        candidates_for_hl = sorted(pool, key=lambda x: (x.games_against_hl,
                                                        x.position * -1))

        # go through all possible opponents
        while len(candidates_for_hl) > 0:
            team_a = candidates_for_hl.pop(0)
            if get_game_of_teams(tournament, team_a, hl_candidate) is None:
                game = Game(game_id, team_a, hl_candidate)
                game_id += 1
                games.append(game)

                tmp_pool = list(pool)
                tmp_pool.remove(team_a)
                # try to match the rest
                try:
                    games += _match_pool_even(tournament, tmp_pool, game_id)
                except NoMatchError:
                    # that did not work out, so try the next
                    game_id -= 1
                    games.pop()
                    continue
                else:
                    # matching worked
                    hl_candidate.hl += 1
                    team_a.games_against_hl += 1
                    return games
            else:
                continue
    
    # no possible matching with all candidates
    raise NoMatchError
        

def _match_pool_even(tournament, pool, game_id):
    # first try two split
    try:
        return match_teams_half_split(tournament, pool, game_id)
    except NoMatchError:
        # split did not work, so try greedy
        try:
            return match_teams_greedy(tournament, pool, game_id)
        except NoMatchError:
            # that did not work either...
            raise NoMatchError


def match_teams_half_split(tournament, teams, game_id):
    upper_half = teams[:len(teams)//2]
    lower_half = teams[len(teams)//2:]

    # permute lower half and try to match them with upper half
    for l in [l for l in permutations(lower_half)]:   
        try:
            games = _match_teams_half_split_iteration(tournament, upper_half,
                                              l, game_id)
        except NoMatchError:
            # go on with next iteration         
            continue
        else:
            # there were all valid matches, so we can end the loop by 
            # returning all games
            return games

    raise NoMatchError


def _match_teams_half_split_iteration(tournament, upper_half, lower_half,
                                      game_id):
    games = []
    for team_a, team_b in zip(upper_half, lower_half):
        if get_game_of_teams(tournament, team_a, team_b) is None:
            game = Game(game_id, team_a, team_b)
            game_id += 1
            games.append(game)
        else:
            raise NoMatchError

    return games


def match_teams_greedy(tournament, teams, game_id):
    games = []

    for per_teams in [perm for perm in permutations(teams)]:
        try:
            games = _match_teams_greedy_iteration(tournament, per_teams, 
                                                  game_id)
        except NoMatchError:
            continue
        else:
            return games
    
    raise NoMatchError


def _match_teams_greedy_iteration(tournament, teams, game_id):
    games = []
    teams = list(teams)
    while len(teams) > 0:
        team_a = teams.pop(0)
        for team_b in teams:
            if get_game_of_teams(tournament, team_a, team_b) is None:
                game = Game(game_id, team_a, team_b)
                game_id += 1
                games.append(game)                
                teams.remove(team_b)
                break
        else:  # no break so there was no match
            raise NoMatchError

    return games


def _move_hl_team_to_end(candidates, min_games_against_hl):
    if len(candidates) % 2 == 1:
        min_games_against_hl = min(candidates,
                                   key=attrgetter('games_against_hl'))
        for index, c in enumerate(reversed(candidates)):
            if c.games_against_hl == min_games_against_hl:
                candidates.append(candidates.pop(index))
                break


def calculate_standings(tournament):
    # wins and points
    for team in tournament.teams:
        calculate_wins_and_points_for_team(tournament, team)

    for team in tournament.teams:
        calculate_bh_for_team(tournament, team)

    for team in tournament.teams:
        calculate_fbh_for_team(tournament, team)

    for team in tournament.teams:
        calculate_sb_for_team(tournament, team)

    for team in tournament.teams:
        calculate_koya_for_team(tournament, team)

    calculate_standings_for_all_teams(tournament)


def calculate_wins_and_points_for_team(tournament, team):
    games = get_games_of_team(tournament, team)
    wins, losses, points, points_against, fr = 0, 0, 0, 0, 0
    for g in [game for game in games if game.is_finished()]:
        if g.get_winner() == team.name:
            wins += 1
        else:
            losses += 1
        if g.is_free_round():
            fr += 1
        points += g.get_points(team)
        points_against += g.get_points_against(team)
    team.wins = wins
    team.losses = losses
    team.points = points
    team.points_against = points_against
    team.fl = fr


def calculate_bh_for_team(tournament, team):
    games = get_games_of_team(tournament, team)
    bh = 0
    for g in [game for game in games if game.is_finished()]:
        opponent = tournament.get_team_by_name(g.get_opponent(team))
        if opponent is not None:
            bh += opponent.wins
    team.bh = bh


def calculate_fbh_for_team(tournament, team):
    games = get_games_of_team(tournament, team)
    fbh = 0
    for g in [game for game in games if game.is_finished()]:
        opponent = tournament.get_team_by_name(g.get_opponent(team))
        if opponent is not None:
            fbh += opponent.bh
    team.fbh = fbh


def calculate_sb_for_team(tournament, team):
    games = get_games_of_team(tournament, team)
    team.sb = 0
    for g in [game for game in games if game.is_finished()]:
        if g.get_winner() == team.name:
            opponent = tournament.get_team_by_name(g.get_looser())
            if opponent is not None:
                team.sb += opponent.wins


def calculate_koya_for_team(tournament, team):
    games = get_games_of_team(tournament, team)
    team.koya = 0
    number_of_games = len(tournament.rounds)
    for g in [game for game in games if game.is_finished()]:
        opponent = tournament.get_team_by_name(g.get_opponent(team)) 
        if opponent is not None:
            if opponent.wins >= number_of_games / 2:
                team.koya += opponent.wins


def calculate_standings_for_all_teams(tournament):
    # 1. Wins
    # 2. BH
    # 3. FBH
    # 4. SB
    # 5. Koya
    # 6. Direct comparison
    # 7. point difference
    # 8. points
    # 9. number of free rounds
    # 10. use initial performance value: this leads to correct standings for
    #  the first round and makes it possible reconstruct standings for later
    #  rounds, because no randomness is introduced
    # During the tournament, it creates better matches because better teams
    # are ranked higher and play against teams, which are good in the
    # tournament.
    # Only for the final standings this becomes unfair, but also very
    # unlikely to play any role.

    # 1. - 5. and 7. - 10. can be done with simple sorting
    standing = sorted(tournament.teams, key=_sort_teams_for_standing_key,
                      reverse=True)

    # 6. direct comparison
    # direct comparison only, if there are exactly two teams with equal
    # wins, bh, fbh and sb.
    index = 0
    while index < len(standing) - 1:
        # get teams
        team_a = standing[index]
        team_b = standing[index + 1]

        # check if the teams are equal in the standing
        if _check_same_position_for_direct_comparison(team_a, team_b):
            # there must not be more than two teams equal
            more_equal_teams = []
            for team in standing[index + 2:]:
                if _check_same_position_for_direct_comparison(team_a, team):
                    more_equal_teams.append(team)
                else:
                    break

            # only two teams --> try to apply direct comparison
            if len(more_equal_teams) == 0:
                game = get_game_of_teams(tournament, team_a, team_b)
                if game is not None and game.is_finished():
                    standing[index] = tournament.get_team_by_name(
                                          game.get_winner())
                    standing[index + 1] = tournament.get_team_by_name(
                                              game.get_looser())
                    
                    __logger.info('Direct comparison: {} wins against {}.'
                        .format(game.get_winner(), game.get_looser()))

                index = index + 2
                continue
            # no direct comparison so skip all teams, which are equal here
            # 2 for current teams + all other equal teams
            else:
                index = index + 2 + len(more_equal_teams)
                continue

        # check next teams
        else:
            index = index + 1

    # set position in team
    for index, team in enumerate(standing):
        team.position = index + 1


def _sort_teams_for_standing_key(team):
    return (team.wins, team.bh, team.fbh, team.sb, team.koya,
            team.points - team.points_against, team.points, team.fl * -1,
            team.performance_value)


def _check_same_position_for_direct_comparison(team_a, team_b):
    return team_a.wins == team_b.wins and team_a.bh == team_b.bh and \
           team_a.fbh == team_b.fbh and team_a.sb == team_b.sb and \
           team_a.koya == team_b.koya
