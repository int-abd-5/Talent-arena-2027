"""Read local Metrica EPTS tracking and automatic SportsCode tags on the tactical clock."""

import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ATD_TRACKING = "BAR-ATH_tactical_atd.txt"
ATD_METADATA = "BAR-ATH_tactical_atd.xml"
SMART_TAGGING = "BAR-ATH_tactical_smart_tagging.xml"

# Defense describes the tagged side's activity. Its opponent receives a weaker prior.
PHASE_WEIGHT = {
    "ATTACKING TRANSITION": 0.90,
    "BUILD UP": 0.85,
    "CREATING CHANCES": 0.75,
    "PROGRESSION": 0.65,
    "BALL IN FINAL THIRD": 0.55,
    "BALL IN THE BOX": 0.55,
    "LONG BALL": 0.50,
    "DEFENSIVE TRANSITION": -0.55,
    "DEFENDING IN ATTACKING THIRD": -0.35,
    "DEFENDING IN MIDDLE THIRD": -0.35,
    "DEFENDING IN DEFENSIVE THIRD": -0.35,
}
TEAM_SIGN = {"barcelona": 1, "atletic club": -1, "athletic club": -1, "n/a": 0}


@dataclass(frozen=True)
class Tracking:
    """Ball and player X/Y in normalized pitch coordinates and team code per slot."""

    player_xy: NDArray[np.float32]
    ball_xy: NDArray[np.float32]
    slot_team: NDArray[np.int8]


@dataclass(frozen=True)
class TagEvidence:
    """Phase and restart hints. A positive team bias points to home."""

    phase_bias: NDArray[np.float32]
    restart_hint: NDArray[np.float32]
    restart_bias: NDArray[np.float32]


def read_tracking(metadata: Path, tracking: Path, n_frames: int) -> Tracking:
    """Read exactly one ATD record per frame in order, matching the XML team assignments."""
    root = ET.parse(metadata).getroot()
    team_ids = [team.get("id") for team in root.iter("Team")]
    if len(team_ids) != 2 or None in team_ids or team_ids[0] == team_ids[1]:
        raise ValueError("Tracking metadata must declare two distinct teams in home/away order")
    players = list(root.iter("Player"))
    if not players or any(player.get("teamId") not in team_ids for player in players):
        raise ValueError("Every track slot must belong to a declared team")

    # The ATD column order is the Player order in the corresponding metadata export.
    slot_team = np.array([team_ids.index(player.get("teamId")) for player in players], np.int8)
    n_slots = len(slot_team)
    player_xy = np.empty((n_frames, n_slots, 2), dtype=np.float32)
    ball_xy = np.empty((n_frames, 2), dtype=np.float32)
    count = 0
    with tracking.open(encoding="ascii") as stream:
        for count, line in enumerate(stream, start=1):
            fields = line.rstrip("\r\n").split(":")
            if len(fields) != 3 or count > n_frames or fields[0] != str(count):
                raise ValueError(f"ATD row {count} must have the matching one-based frame ID")
            _, slots, ball = fields
            if slots.count(";") != n_slots - 1 or slots.count(",") != 2 * n_slots:
                raise ValueError(f"ATD player data has the wrong slot shape at row {count}")
            if ball.count(",") != 2:
                raise ValueError(f"ATD ball data has the wrong field count at row {count}")
            values = np.fromstring(slots.replace(";", ",") + "," + ball, sep=",", dtype=np.float32)
            if values.size != 3 * (n_slots + 1):
                raise ValueError(f"ATD record has incomplete coordinates at row {count}")
            xy = values.reshape(n_slots + 1, 3)[:, :2]
            player_xy[count - 1] = xy[:-1]
            ball_xy[count - 1] = xy[-1]
    if count != n_frames:
        raise ValueError(f"ATD has {count} records, expected {n_frames}")
    if np.isinf(ball_xy).any() or np.isinf(player_xy).any():
        raise ValueError("ATD coordinates must be finite or NaN")
    return Tracking(player_xy, ball_xy, slot_team)


def _fade(width: int, fade_frames: int) -> NDArray[np.float32]:
    offsets = np.arange(width, dtype=np.float32)
    return np.minimum(np.minimum(offsets + 1, width - offsets) / fade_frames, 1.0)


def read_tags(path: Path, n_frames: int, fps: float) -> TagEvidence:
    """Rasterize supported tags into bounded, soft hints with no double count for overlaps."""
    phases = np.zeros((2, n_frames), dtype=np.float32)
    restarts = np.zeros(n_frames, dtype=np.float32)
    restart_teams = np.zeros((2, n_frames), dtype=np.float32)
    events = ET.parse(path).getroot().iter("instance")
    fade_frames = max(1, round(0.5 * fps))
    for event in events:
        code = (event.findtext("code") or "").strip().upper()
        if code not in PHASE_WEIGHT and code != "SET PIECES":
            continue
        start_s = float(event.findtext("start") or "nan")
        end_s = float(event.findtext("end") or "nan")
        if not math.isfinite(start_s) or not math.isfinite(end_s) or end_s <= start_s:
            raise ValueError("Smart Tagging contains an invalid interval")
        start = max(0, round(start_s * fps))
        end = min(n_frames, round(end_s * fps))
        if end <= start:
            continue
        team = next(
            (
                (label.findtext("text") or "").strip().casefold()
                for label in event.findall("label")
                if (label.findtext("group") or "").strip().casefold() == "team"
            ),
            "",
        )
        sign = TEAM_SIGN.get(team, 0)
        fade = _fade(end - start, fade_frames)
        if code == "SET PIECES":
            target = restarts[start:end]
            np.maximum(target, fade, out=target)
            if sign:
                target = restart_teams[int(sign < 0), start:end]
                np.maximum(target, fade, out=target)
        elif sign:
            weight = sign * PHASE_WEIGHT[code]
            target = phases[int(weight < 0), start:end]
            np.maximum(target, abs(weight) * fade, out=target)
    return TagEvidence(phases[0] - phases[1], restarts, restart_teams[0] - restart_teams[1])
