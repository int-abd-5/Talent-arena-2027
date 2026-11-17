"""Decode one team possession sequence per half from soft observations and transition costs."""

import math

import numpy as np
from numpy.typing import NDArray

from .features import FloatArray, build_evidence

LABELS = np.array(["H", "A", "D"])
# Chosen on the predeclared DFL development games. See ADR-0002 for the comparisons.
DEFAULT_TURNOVER_PENALTY = 2.5
DEFAULT_STOPPAGE_PENALTY = 4.0
DEFAULT_STOPPAGE_BIAS = 0.05
SCORE_SCALE = 1024


def _cue(values: FloatArray | None, n_frames: int, lower: float) -> FloatArray:
    if values is None:
        return np.zeros(n_frames, dtype=np.float32)
    if values.shape != (n_frames,) or not np.isfinite(values).all():
        raise ValueError("Each tag signal must have one finite value per frame")
    return np.clip(values, lower, 1.0)


def _ticks(values: FloatArray) -> list[list[int]]:
    return np.rint(values * SCORE_SCALE).astype(np.int64).tolist()


def _best(
    stay: tuple[int, int], first: tuple[int, int], second: tuple[int, int]
) -> tuple[int, int]:
    return max((stay, first, second), key=lambda choice: choice[0])


def _decode(
    emission: FloatArray,
    switch_team: FloatArray,
    enter_live: FloatArray,
    enter_dead: FloatArray,
) -> NDArray[np.str_]:
    """Viterbi recursion with a stable stay-first tie break and no cross-half state."""
    observations = _ticks(emission)
    turnovers = _ticks(switch_team)
    restarts = _ticks(enter_live)
    stoppages = np.rint(enter_dead * SCORE_SCALE).astype(np.int64).tolist()
    back = np.empty((len(emission), 3), dtype=np.int8)
    home, away, dead = observations[0]
    for frame in range(1, len(emission)):
        to_home, to_away = turnovers[frame]
        restart_home, restart_away = restarts[frame]
        to_dead = stoppages[frame]
        best_home, from_home = _best((home, 0), (away - to_home, 1), (dead - restart_home, 2))
        best_away, from_away = _best((away, 1), (home - to_away, 0), (dead - restart_away, 2))
        best_dead, from_dead = _best((dead, 2), (home - to_dead, 0), (away - to_dead, 1))
        evidence_h, evidence_a, evidence_d = observations[frame]
        home = best_home + evidence_h
        away = best_away + evidence_a
        dead = best_dead + evidence_d
        back[frame] = (from_home, from_away, from_dead)

    final_scores = (home, away, dead)
    state = max(range(3), key=final_scores.__getitem__)
    path = np.empty(len(emission), dtype=np.int8)
    for frame in range(len(emission) - 1, 0, -1):
        path[frame] = state
        state = int(back[frame, state])
    path[0] = state
    return LABELS[path]


def predict_half(
    player_xy: FloatArray,
    ball_xy: FloatArray,
    slot_team: NDArray[np.integer],
    pitch: tuple[float, float],
    *,
    fps: float = 25.0,
    phase_bias: FloatArray | None = None,
    restart_hint: FloatArray | None = None,
    restart_bias: FloatArray | None = None,
    turnover_penalty: float = DEFAULT_TURNOVER_PENALTY,
    stoppage_penalty: float = DEFAULT_STOPPAGE_PENALTY,
    stoppage_bias: float = DEFAULT_STOPPAGE_BIAS,
) -> NDArray[np.str_]:
    """Label a complete nonempty half H, A, or D on its input frame grid.

    Coordinates are normalized to the pitch and slot teams are 0 (home) or 1 (away).
    Optional tag hints are soft evidence. The penalty parameters are expressed at 25 fps.
    """
    if player_xy.ndim != 3 or player_xy.shape[-1] != 2 or len(player_xy) == 0:
        raise ValueError("Player tracking needs a nonempty (frames, slots, 2) array")
    n_frames, n_slots, _ = player_xy.shape
    if ball_xy.shape != (n_frames, 2) or slot_team.shape != (n_slots,):
        raise ValueError("Player, ball and team arrays must agree in shape")
    if set(slot_team.tolist()) != {0, 1}:
        raise ValueError("Tracking must include slots for both teams coded as 0 and 1")
    if len(pitch) != 2 or not all(math.isfinite(value) and value > 0 for value in (*pitch, fps)):
        raise ValueError("Pitch size and frame rate must be finite and positive")
    if not (
        math.isfinite(turnover_penalty)
        and turnover_penalty > 0
        and math.isfinite(stoppage_penalty)
        and stoppage_penalty > 0
        and math.isfinite(stoppage_bias)
    ):
        raise ValueError("Transition penalties must be positive and the stoppage bias finite")

    phase = _cue(phase_bias, n_frames, -1)
    restart = _cue(restart_hint, n_frames, 0)
    restart_team = _cue(restart_bias, n_frames, -1)
    evidence = build_evidence(player_xy, ball_xy, slot_team, pitch, fps)
    control = evidence.control
    strongest = control.max(axis=1)
    margin = control[:, 0] - control[:, 1]
    moving_inside = evidence.moving_ball * (1 - evidence.outside)
    still_near_line = evidence.still_ball * evidence.near_line

    # A long gap in isolation cannot raise the stoppage emission. Use player slowdown as
    # secondary evidence that play stopped, or geometry when a ball exit was observed.
    slowing = evidence.slow_players * np.maximum(evidence.still_ball, evidence.missing)
    restart_pause = restart * np.maximum(still_near_line, slowing)
    stop_support = np.maximum(evidence.outside, np.maximum(still_near_line, slowing))
    live = (
        0.04 * evidence.ball_reliability
        + 0.37 * moving_inside
        + 0.19 * strongest
        + 0.15 * evidence.active_players
    )
    dead = (
        1.50 * evidence.outside
        + 0.58 * still_near_line
        + 0.50 * slowing
        + 0.35 * restart_pause
        + stoppage_bias * stop_support
    )
    # An approximate phase can break an evidence tie but carries much less weight than control.
    team_prior = 0.13 * phase * (1 - np.abs(margin))
    team_prior += 0.13 * restart_team * moving_inside * (1 - np.abs(margin))
    ownership = 0.60 * margin + team_prior
    emissions = np.column_stack((live + ownership, live - ownership, dead))

    timescale = fps / 25
    switch_team = turnover_penalty * timescale * (1.65 - 0.72 * control)
    restart_support = np.maximum(control, (0.70 * moving_inside)[:, None])
    enter_live = stoppage_penalty * timescale * (1.50 - 0.80 * restart_support)
    enter_live *= (1 - 0.30 * restart * moving_inside)[:, None]
    enter_dead = stoppage_penalty * timescale * (1.55 - 0.75 * stop_support)
    return _decode(emissions, switch_team, enter_live, enter_dead)
