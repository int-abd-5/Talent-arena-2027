"""Extract spatial and motion evidence with explicit confidence for missing observations."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.floating]


@dataclass(frozen=True)
class Evidence:
    """Per-frame evidence in [0, 1] for the three-state decoder."""

    control: FloatArray
    ball_reliability: FloatArray
    moving_ball: FloatArray
    still_ball: FloatArray
    outside: FloatArray
    near_line: FloatArray
    missing: FloatArray
    slow_players: FloatArray
    active_players: FloatArray


def _distance(vector: FloatArray) -> FloatArray:
    return np.sqrt(np.sum(vector * vector, axis=-1))


def opening_frame(
    ball_xy: FloatArray,
    windows: tuple[tuple[int, int], ...],
    start: int,
    stop: int,
    pitch: tuple[float, float],
    fps: float,
) -> int:
    """Estimate the start of play when an automatic opening tag follows the graded start."""
    lookahead = max(1, round(0.24 * fps))
    # Match only an opening tag near the beginning of this half. Post-goal kickoffs are excluded
    # by the tag reader. The public graded clock can start before the ball has been kicked.
    latest_opening = min(stop, start + round(180 * fps))
    for tag_start, tag_stop in windows:
        if tag_stop <= start or tag_start >= latest_opening:
            continue
        if tag_start <= start:
            return start

        frames = np.arange(tag_start, min(tag_stop, stop - lookahead))
        size = np.asarray(pitch, dtype=np.float32)
        points = ball_xy[frames] * size
        center_distance = _distance(points - size / 2)
        step_speed = _distance(points - ball_xy[frames - 1] * size) * fps
        forward_speed = _distance(ball_xy[frames + lookahead] * size - points) * fps / lookahead
        candidates = frames[
            (center_distance <= 3)
            & (step_speed >= 1)
            & (step_speed <= 40)
            & (forward_speed >= 2)
            & (forward_speed <= 32)
        ]
        # If the kickoff is occluded, the leading edge of its tag conservatively ends the prefix.
        return int(candidates[0]) if len(candidates) else tag_start
    return start


def _motion(
    points: FloatArray, fps: float, cap: float
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Short baselines suppress coordinate jitter without trusting long tracking gaps."""
    stride = max(1, round(fps * 0.12))
    left = np.maximum(np.arange(len(points)) - stride, 0)
    right = np.minimum(np.arange(len(points)) + stride, len(points) - 1)
    scale = (fps / np.maximum(1, right - left)).reshape((len(points),) + (1,) * (points.ndim - 1))
    scale = scale.astype(np.float32)
    velocity = (points[right] - points[left]) * scale
    speed = _distance(velocity)
    invalid = ~np.isfinite(points).all(axis=-1) | (speed > cap)
    velocity[invalid] = np.nan
    speed[invalid] = np.nan

    # The difference between incoming and outgoing velocity can show a touch or reception.
    left_scale = (fps / np.maximum(1, np.arange(len(points)) - left)).astype(np.float32)
    right_scale = (fps / np.maximum(1, right - np.arange(len(points)))).astype(np.float32)
    if points.ndim == 2:
        incoming = (points - points[left]) * left_scale[:, None]
        outgoing = (points[right] - points) * right_scale[:, None]
        impulse = _distance(outgoing - incoming)
        invalid_impulse = invalid | (_distance(incoming) > cap) | (_distance(outgoing) > cap)
        impulse[invalid_impulse | (left == right) | (left == np.arange(len(points)))] = 0
        impulse[right == np.arange(len(points))] = 0
    else:
        impulse = np.zeros(len(points), dtype=np.float32)
    return velocity, speed, impulse


def _missing_context(
    points: FloatArray, confidence: FloatArray, fps: float, pitch: FloatArray
) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray, FloatArray]:
    """Bridge short plausible gaps and carry observed exit evidence into nearby gaps."""
    observed = confidence > 0
    indices = np.arange(len(points))
    previous = np.maximum.accumulate(np.where(observed, indices, -1))
    following = np.minimum.accumulate(np.where(observed, indices, len(points))[::-1])[::-1]
    left = np.maximum(previous, 0)
    right = np.minimum(following, len(points) - 1)
    gap_size = np.maximum(1, following - previous - 1)
    gap_distance = _distance(points[right] - points[left])
    can_fill = (
        ~observed
        & (previous >= 0)
        & (following < len(points))
        & (gap_size <= max(1, round(0.28 * fps)))
        & (gap_distance <= 30 * (gap_size + 1) / fps)
    )
    interp = points.copy()
    weight = ((indices[can_fill] - previous[can_fill]) / (gap_size[can_fill] + 1))[:, None]
    interp[can_fill] = (1 - weight) * points[left[can_fill]] + weight * points[right[can_fill]]
    certainty = confidence.copy()
    certainty[can_fill] = 0.35

    signed = np.max(np.maximum(-interp, interp - pitch), axis=1)
    outside_observed = np.nan_to_num(np.clip((signed - 0.15) / 0.85, 0, 1)) * confidence
    past = outside_observed[left] * np.exp(-(indices - previous) / (2.4 * fps))
    future = outside_observed[right] * np.exp(-(following - indices) / (1.0 * fps))
    outside = np.where(observed, outside_observed, np.maximum(past, future))
    near_line = np.nan_to_num(np.clip((signed + 1.5) / 1.5, 0, 1)) * certainty
    missing = ~observed * np.clip((gap_size / fps - 0.45) / 2.5, 0, 1)
    return interp, certainty, outside.astype(np.float32), near_line, missing.astype(np.float32)


def _ball_observations(points: FloatArray, fps: float) -> FloatArray:
    """Remove isolated jumps that return too quickly to a plausible trajectory."""
    seen = np.isfinite(points).all(axis=1)
    step = _distance(np.diff(points, axis=0))
    back_to_path = _distance(points[2:] - points[:-2]) < (3 + 30 / fps)
    jump = (step[:-1] > (2 + 65 / fps)) & (step[1:] > (2 + 65 / fps)) & back_to_path
    seen[1:-1] &= ~jump
    return seen.astype(np.float32)


def build_evidence(
    player_xy: FloatArray,
    ball_xy: FloatArray,
    slot_team: NDArray[np.integer],
    pitch: tuple[float, float],
    fps: float,
) -> Evidence:
    """Compute team control, ball location and motion, and collective activity."""
    size = np.asarray(pitch, dtype=np.float32)
    players = np.asarray(player_xy, dtype=np.float32) * size
    ball = np.asarray(ball_xy, dtype=np.float32) * size
    confidence = _ball_observations(ball, fps)
    ball[confidence == 0] = np.nan
    ball, reliability, outside, near_line, missing = _missing_context(ball, confidence, fps, size)
    ball_velocity, ball_speed, impulse = _motion(ball, fps, cap=52.0)
    player_velocity, player_speed, _ = _motion(players, fps, cap=12.0)

    distance = _distance(players - ball[:, None, :])
    relative_speed = _distance(player_velocity - ball_velocity[:, None, :])
    close = np.exp(-np.square(distance / 2.25))
    co_moving = np.nan_to_num(np.exp(-np.square(relative_speed / 5.0)), nan=0.35)
    flight = np.nan_to_num(1 / (1 + np.square(ball_speed / 8.0)), nan=0.65)
    touch = np.nan_to_num(np.clip((impulse - 2.5) / 7.5, 0, 1))
    motion_support = 0.20 + 0.50 * co_moving + 0.30 * flight[:, None]
    contact = close * np.maximum(motion_support, 0.62 * touch[:, None])
    contact *= (reliability * (1 - outside * 0.85))[:, None]
    contact = np.nan_to_num(contact)
    control = np.column_stack([contact[:, slot_team == team].max(axis=1) for team in (0, 1)])

    has_speed = np.isfinite(player_speed)
    n_speed = has_speed.sum(axis=1)
    movement_coverage = np.minimum(n_speed / 8, 1)
    denominator = np.maximum(n_speed, 1)
    slow_fraction = (player_speed < 1.25).sum(axis=1) / denominator
    fast_fraction = (player_speed > 2.4).sum(axis=1) / denominator
    slow_players = np.clip((slow_fraction - 0.45) / 0.45, 0, 1) * movement_coverage
    active_players = np.clip((fast_fraction - 0.10) / 0.36, 0, 1) * movement_coverage
    moving_ball = np.nan_to_num(np.clip((ball_speed - 0.9) / 3.4, 0, 1)) * reliability
    still_ball = np.nan_to_num(np.clip((1.0 - ball_speed) / 0.8, 0, 1)) * reliability
    return Evidence(
        control,
        reliability,
        moving_ball,
        still_ball,
        outside,
        near_line,
        missing,
        slow_players,
        active_players,
    )
