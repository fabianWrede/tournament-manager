class BaseData:
    def encode_json(self):
        dct = {'_type': self.__class__.__name__}
        return dct

    @classmethod
    def decode_json(cls, dct):
        return BaseData()


class Tournament(BaseData):
    def __init__(self, name, teams=[], rounds=[], playoffs=[]):
        self.id = name
        self.name = name
        self.teams = teams
        self.rounds = rounds
        self.playoffs = playoffs

    def is_started(self):
        return len(self.rounds) > 0

    def reset(self):
        self.rounds = []
        for t in self.teams:
            t.reset()

    def add_team(self, team):
        self.teams.append(team)

    def remove_team(self, team):
        self.teams.remove(team)

    def get_game_by_id(self, id):
        for g in [game for round in self.rounds for game in round.games]:
            if g.id == id:
                return g
        return None

    def get_team_by_name(self, id):
        for t in self.teams:
            if t.name == id:
                return t
        return None

    def encode_json(self):
        dct = {'_type': self.__class__.__name__, 'name': self.name,
               'teams': self.teams, 'rounds': self.rounds,
               'playoffs': self.playoffs}
        return dct

    @classmethod
    def decode_json(cls, dct):
        return Tournament(name=dct.get('name'), teams=dct.get('teams'),
                          rounds=dct.get('rounds'),
                          playoffs=dct.get('playoffs'))


class Round(BaseData):
    def __init__(self, games=[]):
        self.games = games

    def encode_json(self):
        dct = {'_type': self.__class__.__name__}
        dct['games'] = self.games
        return dct

    @classmethod
    def decode_json(cls, dct):
        return Round(games=dct.get('games'))


class Team(BaseData):
    def __init__(self, name, wins=0, losses=0, bh=0, fbh=0, sb=0, koya=0,
                 points=0, points_against=0, position=-1, games_against_hl=0,
                 hl=0, fl=0, performance_value=-1):
        self.name = name
        self.position = position
        self.wins = wins
        self.losses = losses
        self.bh = bh
        self.fbh = fbh
        self.sb = sb
        self.koya = koya
        self.points = points
        self.points_against = points_against
        self.games_against_hl = games_against_hl
        self.hl = hl
        self.fl = fl
        self.performance_value = performance_value

    def reset(self):
        self.position = -1
        self.wins = 0
        self.losses = 0
        self.bh = 0
        self.fbh = 0
        self.sb = 0
        self.koya = 0
        self.points = 0
        self.points_against = 0
        self.games_against_hl = 0
        self.hl = 0
        self.fl = 0

    def encode_json(self):
        dct = {'_type': self.__class__.__name__, 'name': self.name,
               'position': self.position, 'wins': self.wins,
               'losses': self.losses, 'bh': self.bh, 'fbh': self.fbh,
               'sb': self.sb, 'koya': self.koya, 'points': self.points,
               'points_against': self.points_against,
               'games_against_hl': self.games_against_hl, 'hl': self.hl,
               'fl': self.fl, 'performance_value': self.performance_value}
        return dct

    @classmethod
    def decode_json(cls, dct):
        return Team(name=dct.get('name'), position=dct.get('position'),
                    wins=dct.get('wins'),
                    losses=dct.get('losses'), bh=dct.get('bh'),
                    fbh=dct.get('fbh'), sb=dct.get('sb'), koya=dct.get('koya'),
                    points=dct.get('points'),
                    points_against=dct.get('points_against'),
                    games_against_hl=dct.get('games_against_hl'),
                    hl=dct.get('hl'), fl=dct.get('fl'),
                    performance_value=dct.get('performance_value'))


class Game(BaseData):
    def __init__(self, id=-1, team_a=None, team_b=None, points_a=-1,
            points_b=-1):
        self.id = id

        # use string or Team, then just store unique name
        if isinstance(team_a, Team):
            self.team_a = team_a.name
        else:
            self.team_a = team_a

        if isinstance(team_b, Team):
            self.team_b = team_b.name
        else:
            self.team_b = team_b

        self.points_a = points_a
        self.points_b = points_b

    def is_finished(self):
        return self.points_a > -1 and self.points_b > -1

    def is_involved(self, team):
        return (self.team_a is not None and self.team_a == team.name) \
               or (self.team_b is not None and self.team_b == team.name)

    def add_result(self, points_a, points_b):
        self.points_a = points_a
        self.points_b = points_b

    def get_winner(self):
        return self.team_a if self.points_a > self.points_b else self.team_b

    def get_looser(self):
        return self.team_a if self.points_a < self.points_b else self.team_b

    def get_points(self, team):
        if team.name == self.team_a:
            return self.points_a
        elif team.name == self.team_b:
            return self.points_b
        else:
            return -1

    def get_points_against(self, team):
        if team.name == self.team_a:
            return self.points_b
        elif team.name == self.team_b:
            return self.points_a
        else:
            return -1

    def get_opponent(self, team):
        if team.name == self.team_a:
            return self.team_b
        elif team.name == self.team_b:
            return self.team_a
        else:
            return None

    def is_free_round(self):
        return self.is_finished() and (self.team_a is None \
            or self.team_b is None)

    def encode_json(self):
        dct = {'_type': self.__class__.__name__, 'id': self.id,
               'team_a': self.team_a, 'team_b': self.team_b,
               'points_a': self.points_a, 'points_b': self.points_b}
        return dct

    @classmethod
    def decode_json(cls, dct):
        return Game(id=dct.get('id'), team_a=dct.get('team_a'),
                    team_b=dct.get('team_b'), points_a=dct.get('points_a'),
                    points_b=dct.get('points_b'))

