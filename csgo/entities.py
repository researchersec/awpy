""" Classes for CSGO entities
"""


class Game:
    """ Hold game information

    Attributes:
        - game_id (string)  : Game id
        - map_name (string) : Map name
        - rounds (list)     : List of round objects
        - players (dict)    : Dictionary where key is player SteamID
    """

    def __init__(self, game_id="", map_name=""):
        """ Initialize a game
        """
        self.game_id = game_id
        self.map_name = map_name
        self.rounds = []
        self.players = {}


class Round:
    """ Hold round information

    Attributes:
        - start_tick (int)           : Tick on ROUND START event
        - end_tick (int)             : Tick on ROUND END event
        - end_ct_score (int)         : Ending CT score
        - end_t_score (int)          : Ending T score
        - start_t_score (int)        : Starting T score
        - start_ct_score (int)       : Starting CT score
        - round_winner_side (string) : T/CT for round winner
        - round_winner (string)      : Winning team name
        - round_loser (string)       : Losing team name
        - reason (int)               : Corresponds to how the team won (defuse, killed other team, etc.)
        - ct_cash_spent_total (int)  : CT total cash spent by this point of the game
        - ct_cash_spent_round (int)  : CT total cash spent in current round
        - ct_eq_val (int)            : CT equipment value at end of freezetime
        - t_cash_spent_total (int)   : T total cash spent by this point of the game
        - t_cash_spent_round (int)   : T total cash spent in current round
        - t_eq_val (int)             : T equipment value at end of freezetime
        - frames (list)              : List of GameFrame objects
    """

    def __init__(
        self,
        start_tick=0,
        end_tick=0,
        end_ct_score=0,
        end_t_score=0,
        start_ct_score=0,
        start_t_score=0,
        round_winner_side="",
        round_winner="",
        round_loser="",
        reason=0,
        ct_cash_spent_total=0,
        ct_cash_spent_round=0,
        ct_eq_val=0,
        t_cash_spent_total=0,
        t_cash_spent_round=0,
        t_eq_val=0,
        frames=[],
    ):
        """ Initialize a round
        """
        self.start_tick = start_tick
        self.end_tick = end_tick
        self.end_ct_score = end_ct_score
        self.end_t_score = end_t_score
        self.start_ct_score = start_ct_score
        self.start_t_score = start_t_score
        self.round_winner_side = round_winner_side
        self.round_winner = round_winner
        self.round_loser = round_loser
        self.reason = reason
        self.ct_cash_spent_total = (ct_cash_spent_total,)
        self.ct_cash_spent_round = (ct_cash_spent_round,)
        self.ct_eq_val = (ct_eq_val,)
        self.t_cash_spent_total = (t_cash_spent_total,)
        self.t_cash_spent_round = (t_cash_spent_round,)
        self.t_eq_val = t_eq_val
        if self.round_winner_side == "CT":
            self.start_ct_score = self.end_ct_score - 1
            self.start_t_score = self.start_t_score
        if self.round_winner_side == "T":
            self.start_ct_score = self.end_ct_score
            self.start_t_score = self.start_t_score - 1

class GameFrame:
    """ Discrete round snapshot

    Attributes:
        - tick (int)            : Tick corresponding to game frame
        - seconds_elapsed (int) : Seconds elapsed since round start
        - clock_time (string)   : Clock time
        - ct (Team)             : Team object corresponding to Counter-Terrorists
        - t (Team)              : Team object corresponding to Terrorists
        - bomb_planted (bool)   : Flag for if the bomb is planted
        - plant_site (string)   : String indicating the plant site
        - has_ended (bool)      : Flag for when the round has ended, but not officially
    """

    def __init__(self, tick=0, seconds_elapsed=0, clock_time="00:00", ct=None, t=None, bomb_planted=False, plant_site=""):
        """ Initialize a game frame
        """
        self.tick = tick
        self.seconds_elapsed = seconds_elapsed
        self.clock_time = clock_time
        self.ct = ct
        self.t = t
        self.bomb_planted = bomb_planted
        self.plant_site = plant_site

class Team:
    """ Hold team information

    Attributes:
        - name (string)        : Team name
        - players (dict)       : Dictionary where key is SteamID, value is player name
        - alive_players (dict) : Dictionary where key is SteamID, value is Player object
        - dead_players (dict)  : Dictionary where key is SteamID, value is Player object
    """

    def __init__(self, name="", players={}, alive_players={}, dead_players={}):
        """ Initialize a team
        """
        self.name = name
        self.players = players
        self.alive_players = alive_players
        self.dead_players = dead_players