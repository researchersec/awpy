"""Calculates the Kill, Assist, Survival, Trade %."""

import pandas as pd

from awpy import Demo


def calculate_trades(kills: pd.DataFrame, trade_ticks: int = 128 * 5) -> pd.DataFrame:
    """Calculates if kills are trades.

    A trade is a kill where the attacker of a player who recently died was
    killed shortly after the initial victim was killed.

    Args:
        kills (pd.DataFrame): A parsed Awpy kills dataframe.
        trade_ticks (int, optional): Length of trade time in ticks. Defaults to 128*5.

    Returns:
        pd.DataFrame: Adds `was_traded` columns to kills.
    """
    # Get all rounds
    rounds = kills["round"].unique()

    was_traded = []

    for r in rounds:
        kills_round = kills[kills["round"] == r]
        for _, row in kills_round.iterrows():
            kills_in_trade_window = kills_round[
                (kills_round["tick"] >= row["tick"] - trade_ticks)
                & (kills_round["tick"] <= row["tick"])
            ]
            if row["victim_name"] in kills_in_trade_window["attacker_name"].to_numpy():
                last_kill_by_attacker = None
                for __, attacker_row in kills_in_trade_window.iterrows():
                    if attacker_row["attacker_name"] == row["victim_name"]:
                        last_kill_by_attacker = attacker_row.name
                was_traded.append(last_kill_by_attacker)

    kills["was_traded"] = False
    kills.loc[was_traded, "was_traded"] = True

    return kills


def kast(demo: Demo, trade_ticks: int = 128 * 5) -> pd.DataFrame:
    """Calculates Kill-Assist-Survival-Trade %.

    Args:
        demo (awpy.demo.Demo): A parsed Awpy demo.
        trade_ticks (int, optional): Length of trade time in ticks. Defaults to 128*5.

    Returns:
        pd.DataFrame: A dataframe of the player info + kast.
    """
    kills_with_trades = calculate_trades(demo.kills, trade_ticks)

    # Get rounds where a player had a kill
    kills_total = (
        kills_with_trades.loc[:, ["attacker_name", "attacker_steamid", "round"]]
        .drop_duplicates()
        .rename(columns={"attacker_name": "name", "attacker_steamid": "steamid"})
    )
    kills_ct = (
        kills_with_trades.loc[
            kills_with_trades["attacker_side"] == "CT",
            ["attacker_name", "attacker_steamid", "round"],
        ]
        .drop_duplicates()
        .rename(columns={"attacker_name": "name", "attacker_steamid": "steamid"})
    )
    kills_t = (
        kills_with_trades.loc[
            kills_with_trades["attacker_side"] == "TERRORIST",
            ["attacker_name", "attacker_steamid", "round"],
        ]
        .drop_duplicates()
        .rename(columns={"attacker_name": "name", "attacker_steamid": "steamid"})
    )

    # Get rounds where a player had an assist
    assists_total = (
        kills_with_trades.loc[:, ["assister_name", "assister_steamid", "round"]]
        .drop_duplicates()
        .rename(columns={"assister_name": "name", "assister_steamid": "steamid"})
    )
    assists_ct = (
        kills_with_trades.loc[
            kills_with_trades["assister_side"] == "CT",
            ["assister_name", "assister_steamid", "round"],
        ]
        .drop_duplicates()
        .rename(columns={"assister_name": "name", "assister_steamid": "steamid"})
    )
    assists_t = (
        kills_with_trades.loc[
            kills_with_trades["assister_side"] == "TERRORIST",
            ["assister_name", "assister_steamid", "round"],
        ]
        .drop_duplicates()
        .rename(columns={"assister_name": "name", "assister_steamid": "steamid"})
    )

    # Get rounds where a player was traded
    trades_total = (
        kills_with_trades.loc[
            kills_with_trades["was_traded"],
            ["victim_name", "victim_steamid", "round"],
        ]
        .drop_duplicates()
        .rename(columns={"victim_name": "name", "victim_steamid": "steamid"})
    )
    trades_ct = (
        kills_with_trades.loc[
            (kills_with_trades["victim_side"] == "CT")
            & (kills_with_trades["was_traded"]),
            ["victim_name", "victim_steamid", "round"],
        ]
        .drop_duplicates()
        .rename(columns={"victim_name": "name", "victim_steamid": "steamid"})
    )
    trades_t = (
        kills_with_trades.loc[
            (kills_with_trades["victim_side"] == "TERRORIST")
            & (kills_with_trades["was_traded"]),
            ["victim_name", "victim_steamid", "round"],
        ]
        .drop_duplicates()
        .rename(columns={"victim_name": "name", "victim_steamid": "steamid"})
    )

    # Find survivals
    survivals = (
        demo.ticks.sort_values("tick")
        .groupby(["name", "steamid", "round"])
        .tail(1)
        .loc[demo.ticks["health"] > 0]
    )
    survivals_total = survivals[["name", "steamid", "round"]]
    survivals_ct = survivals.loc[survivals["side"] == "ct"]
    survivals_t = survivals.loc[survivals["side"] == "t"]

    # Get total rounds by player
    player_sides_by_round = demo.ticks.groupby(
        ["name", "steamid", "side", "round"]
    ).head(1)[["name", "steamid", "side", "round"]]
    player_side_rounds = (
        player_sides_by_round.groupby(["name", "steamid", "side"]).size().reset_index()
    )
    player_side_rounds.columns = ["name", "steamid", "side", "n_rounds"]
    player_total_rounds = (
        player_sides_by_round.groupby(["name", "steamid"]).size().reset_index()
    )

    # Tabulate total rounds
    total_kast = (
        pd.concat([kills_total, assists_total, trades_total, survivals_total])
        .drop_duplicates()
        .reset_index(drop=True)
        .groupby(["name", "steamid"])
        .size()
        .reset_index()
        .rename(columns={0: "kast_rounds"})
        .merge(player_total_rounds, on=["name", "steamid"])
        .rename(columns={0: "n_rounds"})
    )
    total_kast["side"] = "all"
    total_kast["kast"] = total_kast["kast_rounds"] * 100 / total_kast["n_rounds"]

    # CT
    ct_kast = (
        pd.concat([kills_ct, assists_ct, trades_ct, survivals_ct])
        .drop_duplicates()
        .reset_index(drop=True)
        .groupby(["name", "steamid"])
        .size()
        .reset_index()
        .rename(columns={0: "kast_rounds"})
        .merge(
            player_side_rounds[player_side_rounds["side"] == "CT"],
            on=["name", "steamid"],
        )
        .rename(columns={0: "n_rounds"})
    )
    ct_kast["kast"] = ct_kast["kast_rounds"] * 100 / ct_kast["n_rounds"]

    # T
    t_kast = (
        pd.concat([kills_t, assists_t, trades_t, survivals_t])
        .drop_duplicates()
        .reset_index(drop=True)
        .groupby(["name", "steamid"])
        .size()
        .reset_index()
        .rename(columns={0: "kast_rounds"})
        .merge(
            player_side_rounds[player_side_rounds["side"] == "TERRORIST"],
            on=["name", "steamid"],
        )
        .rename(columns={0: "n_rounds"})
    )
    t_kast["kast"] = t_kast["kast_rounds"] * 100 / t_kast["n_rounds"]

    kast_df = pd.concat([total_kast, ct_kast, t_kast])
    return kast_df[["name", "steamid", "side", "kast_rounds", "n_rounds", "kast"]]
