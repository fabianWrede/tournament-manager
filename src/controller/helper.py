def get_games_of_team(tournament, team):
    result = []
    for r in tournament.rounds:
        for g in r.games:
            if g.is_involved(team):
                result.append(g)
    return result


def get_game_of_teams(tournament, team_a, team_b):
    for r in tournament.rounds:
        for g in r.games:
            if (g.team_a == team_a.name and g.team_b == team_b.name) or (
                    g.team_b == team_a.name and g.team_a == team_b.name):
                return g
    return None
