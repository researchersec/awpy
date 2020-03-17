import pytest
import pandas as pd

from csgo.parser.match_parser import CSGOMatchParser


class TestCSGOParser:
    """ Class to test the match parser
    """

    def setup_class(self):
        """ Setup class by instantiating parser
        """
        self.parser = CSGOMatchParser(demofile="tests/natus-vincere-vs-astralis-m1-dust2.dem", competition_name="IEM-Katowice-2020", match_name="Natus-Vincere-vs-Astralis", game_date="02-29-2020", game_time="13:35")

    def teardown_class(self):
        """ Set parser to none
        """
        self.parser = None

    def test_demo_error(self):
        """ Tests if the parser encountered a corrupted demofile. If it did, the
        parser would set the `demo_error` attribute to True. Since this demofile is
        not corrupted, this test should have parser.demo_error as FALSE
        """
        self.parser.parse_demofile()
        assert not self.parser.demo_error 

    def test_parse_match(self):
        """ Tests if the parser parses the match without issue. Our test demo had 21 total rounds.
        """
        self.parser.parse_match()
        assert len(self.parser.rounds) == 21

    def test_last_round_reason(self):
        """ Tests if the last round had the correct win reason. It should be "CTWin".
        """
        assert self.parser.rounds[-1].reason == "CTWin"

    def test_kills_total(self):
        """ Tests if the kill totals are correct. s1mple should have 25 kills.
        """
        self.parser.write_kills()
        kills_df = self.parser.kills_df.groupby("AttackerName").size().reset_index()
        kills_df.columns = ["AttackerName", "Kills"]
        assert kills_df[kills_df["AttackerName"] == "s1mple"].Kills.values[0] == 25

    def test_bomb_plant(self):
        """ Tests for bomb plant events. There should be a plant and a defuse event for this round.
        """
        self.parser.write_bomb_events()
        bomb_df = self.parser.bomb_df
        assert bomb_df.loc[bomb_df["RoundNum"] == 15,["Tick", "EventType"]].shape[0] == 2

    def test_clean_rounds(self):
        """ Tests for cleaning rounds
        """
        self.parser = CSGOMatchParser(demofile="pact-vs-big-dust2.dem")
        self.parser.parse_demofile()
        self.parser.parse_match()
        self.parser.clean_rounds()
        assert len(self.parser.rounds) == 23
