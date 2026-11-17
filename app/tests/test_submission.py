"""Exercise tracking, tag conversion, and the CSV writer with synthetic inputs."""

import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from app.possession.__main__ import MatchLayout, generate, write_submission
from app.possession.data import ATD_METADATA, ATD_TRACKING, SMART_TAGGING, read_tags, read_tracking
from app.possession.model import predict_half

META = (
    '<match><Team id="home"/><Team id="away"/>'
    '<Player teamId="home"/><Player teamId="away"/></match>'
)
SLOT_VALUES = "0.30,0.50,0;0.70,0.50,0"


def _bundle(root: Path, n_frames: int = 100) -> Path:
    tactical = root / "tactical"
    tactical.mkdir()
    (tactical / ATD_METADATA).write_text(META)
    (tactical / SMART_TAGGING).write_text("<file/>")
    rows = []
    for frame in range(n_frames):
        x = "0.30" if frame < n_frames // 2 else "0.70"
        rows.append(f"{frame + 1}:{SLOT_VALUES}:{x},0.50,NaN\n")
    (tactical / ATD_TRACKING).write_text("".join(rows))
    return tactical


@pytest.mark.parametrize(
    ("line", "reason"),
    [
        ("2:0.3,0.5,0;0.7,0.5,0:NaN,NaN,NaN", "frame ID"),
        ("1:0.3,0.5,0:NaN,NaN,NaN", "slot shape"),
        ("1:0.3,0.5,0;0.7,0.5,0:NaN,NaN", "field count"),
        ("1:0.3,0.5,0;0.7,0.5,0:inf,0.50,0", "finite or NaN"),
        ("", "records, expected"),
    ],
)
def test_rejects_malformed_tracking(tmp_path: Path, line: str, reason: str) -> None:
    """Bad coordinates or a noncontiguous timeline stop the submission before writing."""
    tactical = _bundle(tmp_path, n_frames=1)
    (tactical / ATD_TRACKING).write_text(f"{line}\n" if line else "")
    with pytest.raises(ValueError, match=reason):
        read_tracking(tactical / ATD_METADATA, tactical / ATD_TRACKING, n_frames=1)


def _tag(start: float, end: float, code: str, team: str, kind: str = "") -> str:
    return (
        f"<instance><start>{start}</start><end>{end}</end><code>{code}</code>"
        f"<label><group>Team</group><text>{team}</text></label>"
        f"<label><group>Type</group><text>{kind}</text></label></instance>"
    )


def test_tag_priors_respect_team_and_clock(tmp_path: Path) -> None:
    """Seconds map to half-open intervals. Duplicate tags and N/A teams remain bounded."""
    xml = tmp_path / "tags.xml"
    buildup = _tag(0.2, 1.8, "BUILD UP", "Barcelona")
    defense = _tag(2.0, 3.0, "DEFENDING IN MIDDLE THIRD", "Barcelona")
    restart = _tag(3.0, 4.0, "SET PIECES", "Atletic Club")
    unknown = _tag(4.0, 5.0, "SET PIECES", "N/A")
    xml.write_text(f"<file>{buildup}{buildup}{defense}{restart}{unknown}</file>")
    hints = read_tags(xml, n_frames=125, fps=25.0)
    assert np.all(hints.phase_bias[:5] == 0)
    assert 0 < hints.phase_bias[5] < hints.phase_bias[25]
    assert hints.phase_bias[25] == pytest.approx(0.85)
    assert hints.phase_bias[45] == 0
    assert hints.phase_bias[62] < 0
    assert hints.restart_hint[87] > 0
    assert hints.restart_bias[87] < 0
    assert hints.restart_hint[112] > 0
    assert hints.restart_bias[112] == 0


def test_output_timeline_and_reproducibility(tmp_path: Path) -> None:
    """Run all submission stages on a synthetic match with a break between halves."""
    _bundle(tmp_path)
    layout = MatchLayout(100, (slice(5, 45), slice(55, 95)))
    target = tmp_path / "outputs" / "Team Name.csv"
    generate(tmp_path, target, layout)
    first_run = target.read_bytes()
    generate(tmp_path, target, layout)
    assert first_run == target.read_bytes()
    with target.open(newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["frame", "label"]
        rows = list(reader)
    assert [int(row["frame"]) for row in rows] == list(range(100))
    assert (
        "".join(row["label"] for row in rows) == "X" * 5 + "H" * 40 + "X" * 10 + "A" * 40 + "X" * 5
    )


def test_refuses_wrong_output_extension(tmp_path: Path) -> None:
    """A CSV output argument cannot overwrite a non-CSV file."""
    target = tmp_path / "existing.txt"
    target.write_text("keep")
    with pytest.raises(ValueError, match="must be a CSV"):
        write_submission(target, np.array(["H"]))
    assert target.read_text() == "keep"


def test_cli_missing_bundle(tmp_path: Path) -> None:
    """The command fails clearly on a missing local bundle."""
    output = tmp_path / "missing.csv"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.possession",
            "--data-dir",
            str(tmp_path),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Cannot generate submission" in result.stderr
    assert not output.exists()


def test_inference_rejects_invalid_tag_and_team_shapes() -> None:
    """Decline mismatched team mapping and tag arrays instead of broadcasting silently."""
    players = np.zeros((4, 2, 2), dtype=np.float32)
    ball = players[:, 0]
    pitch = (105.3, 68.0)
    with pytest.raises(ValueError, match="arrays must agree"):
        predict_half(players, ball, np.array([0]), pitch)
    with pytest.raises(ValueError, match="include slots for both"):
        predict_half(players, ball, np.array([0, 0]), pitch)
    with pytest.raises(ValueError, match="finite value per frame"):
        predict_half(players, ball, np.array([0, 1]), pitch, phase_bias=np.zeros(3))


def test_uninformative_long_gap_preserves_live_play() -> None:
    """A decoder bias cannot create a stoppage when every observation is missing."""
    n_frames = 2_000
    players = np.full((n_frames, 2, 2), np.nan)
    ball = np.full((n_frames, 2), np.nan)
    for block in (slice(0, 200), slice(1_800, n_frames)):
        players[block, 0] = (0.30, 0.50)
        players[block, 1] = (0.70, 0.50)
        ball[block] = (0.30, 0.50)
    labels = predict_half(players, ball, np.array([0, 1]), (105.3, 68.0))
    assert np.all(labels == "H")


def test_opening_restart_ends_the_graded_dead_prefix(tmp_path: Path) -> None:
    """Use the tracking and automatic opening tag when a half is graded before kickoff."""
    tactical = _bundle(tmp_path, n_frames=250)
    (tactical / SMART_TAGGING).write_text(
        "<file>" + _tag(6.2, 8.6, "SET PIECES", "Athletic Club", "Kick Off (Start)") + "</file>"
    )
    rows = []
    for frame in range(250):
        x = 0.50 + min(10, max(0, frame - 170)) * 0.001 if frame >= 100 else 0.30
        slots = f"0.30,0.50,0;{x},0.50,0"
        rows.append(f"{frame + 1}:{slots}:{x},0.50,NaN\n")
    (tactical / ATD_TRACKING).write_text("".join(rows))
    target = tmp_path / "submission.csv"
    generate(tmp_path, target, MatchLayout(250, (slice(0, 80), slice(100, 240))))
    with target.open(newline="") as stream:
        labels = [row["label"] for row in csv.DictReader(stream)]
    assert labels[80:100] == ["X"] * 20
    assert labels[100:170] == ["D"] * 70
    assert labels[172:240] == ["A"] * 68
