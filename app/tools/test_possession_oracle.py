"""Synthetic acceptance cases for the public half prediction interface."""

import numpy as np
from numpy.typing import NDArray

from app.possession.model import predict_half

FPS = 25.0
PITCH = (105.3, 68.0)
PITCH_SIZE_M = np.array(PITCH, dtype=np.float32)
TEAMS = np.repeat(np.array([0, 1], dtype=np.int8), 11)
HOME = 0
AWAY = 11


def _background(n_frames: int) -> NDArray[np.float32]:
    """Give each team a formation with small, continuous movement."""
    time = np.arange(n_frames, dtype=np.float32) / FPS
    lateral = np.tile(np.array([10.0, 17.0, 27.0, 39.0, 50.0, 58.0]), 4)[:22]
    longitudinal = np.linspace(16.0, 96.0, 22)
    offsets = np.arange(22) * 0.7
    oscillation = time[:, None] + offsets[None, :]
    x = longitudinal[None, :] + 1.4 * np.sin(oscillation)
    y = lateral[None, :] + 1.4 * np.cos(oscillation)
    return np.stack((x, y), axis=-1).astype(np.float32)


def _xy(x: NDArray[np.float64], y: NDArray[np.float64]) -> NDArray[np.float32]:
    """Place successive positions in metres before normalization at the API boundary."""
    return np.column_stack((x, y)).astype(np.float32)


def _predict(
    players: NDArray[np.float32], ball: NDArray[np.float32], teams: NDArray[np.int8] = TEAMS
) -> NDArray[np.str_]:
    """Pass only geometry, team mapping and sampling rate to the production predictor."""
    prediction = predict_half(players / PITCH_SIZE_M, ball / PITCH_SIZE_M, teams, PITCH, fps=FPS)
    assert isinstance(prediction, np.ndarray)
    assert prediction.shape == (len(ball),)
    assert set(prediction) <= {"H", "A", "D"}
    return prediction


def _runs(labels: NDArray[np.str_]) -> list[str]:
    """List the label of each contiguous spell in chronological order."""
    starts = np.r_[True, labels[1:] != labels[:-1]]
    return labels[starts].tolist()


def test_brief_rival_proximity_and_missing_ball_do_not_split_home_control() -> None:
    """A crossing defender and a short occlusion occur during continuous home dribbling."""
    time = np.arange(210) / FPS
    ball = _xy(23.0 + 2.6 * time, np.full_like(time, 31.0))
    players = _background(len(ball))
    players[:, HOME] = ball + np.array([-0.8, 0.25])
    players[:, AWAY] = _xy(
        23.0 + 2.6 * time + 0.10,
        31.0 + np.clip(5.5 * (time - 3.25), -11.0, 12.0),
    )
    ball[123:129] = np.nan

    assert _runs(_predict(players, ball)) == ["H"]


def test_sustained_away_reception_makes_one_change_after_flight() -> None:
    """A pass travels through open space before an opponent receives and carries it."""
    frame = np.arange(245)
    ball_x = np.interp(frame, [0, 87, 118, 244], [24.0, 33.0, 55.0, 66.0])
    ball = _xy(ball_x, np.full_like(ball_x, 33.0))
    players = _background(len(ball))
    home_x = np.interp(frame, [0, 87, 244], [23.35, 32.35, 42.0])
    away_x = np.interp(frame, [0, 118, 244], [47.5, 55.65, 66.65])
    players[:, HOME] = _xy(home_x, np.full_like(home_x, 33.1))
    players[:, AWAY] = _xy(away_x, np.full_like(away_x, 32.9))

    labels = _predict(players, ball)
    assert _runs(labels) == ["H", "A"]
    assert np.all(labels[10:80] == "H")
    assert np.all(labels[138:230] == "A")


def test_observed_ball_out_separates_live_spells_until_restart() -> None:
    """The ball leaves a touchline, stays outside and is returned to a new possessor."""
    frame = np.arange(270)
    ball_x = np.interp(frame, [0, 75, 150, 184, 269], [42.0, 44.0, 44.1, 44.7, 47.0])
    ball_y = np.interp(frame, [0, 75, 103, 150, 184, 269], [10.0, 5.0, -3.0, -3.0, 3.0, 10.0])
    ball = _xy(ball_x, ball_y)
    players = _background(len(ball))
    home_x = np.interp(frame, [0, 75, 269], [41.35, 43.35, 40.5])
    home_y = np.interp(frame, [0, 75, 106, 269], [10.2, 5.2, 3.2, 5.2])
    away_x = np.interp(frame, [0, 184, 269], [48.0, 45.35, 47.65])
    away_y = np.interp(frame, [0, 155, 184, 269], [5.5, 2.2, 3.1, 10.1])
    players[:, HOME] = _xy(home_x, home_y)
    players[:, AWAY] = _xy(away_x, away_y)

    labels = _predict(players, ball)
    assert np.all(labels[15:66] == "H")
    assert np.all(labels[112:147] == "D")
    assert np.all(labels[204:255] == "A")
    assert _runs(labels[30:228]) == ["H", "D", "A"]


def test_stationary_ball_beside_player_at_midfield_can_be_live() -> None:
    """The field location and nearby controller are consistent with holding the ball."""
    ball = np.broadcast_to(np.array([49.8, 30.5], dtype=np.float32), (100, 2)).copy()
    players = _background(len(ball))
    players[:, HOME] = [49.35, 30.65]
    players[:, AWAY] = [52.40, 32.5]

    assert np.all(_predict(players, ball)[10:90] == "H")


def test_swapping_team_mapping_swaps_unambiguous_live_possession() -> None:
    """The same visible dribble is credited to the new side when team codes swap."""
    time = np.arange(105) / FPS
    ball = _xy(31.0 + 1.8 * time, np.full_like(time, 30.0))
    players = _background(len(ball))
    players[:, HOME] = ball + np.array([-0.45, 0.4])
    players[:, AWAY] = ball + np.array([4.0, -3.0])

    assert np.all(_predict(players, ball) == "H")
    assert np.all(_predict(players, ball, 1 - TEAMS) == "A")


def test_no_ball_observations_preserves_output_contract() -> None:
    """The estimator must emit one supported label for every frame without ball readings."""
    ball = np.full((65, 2), np.nan, dtype=np.float32)
    _predict(_background(len(ball)), ball)
