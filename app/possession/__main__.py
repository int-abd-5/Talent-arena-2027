"""Generate a submission CSV from the local tactical assets with no network access."""

import argparse
import os
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from .data import ATD_METADATA, ATD_TRACKING, SMART_TAGGING, read_tags, read_tracking
from .features import opening_frame
from .model import predict_half


@dataclass(frozen=True)
class MatchLayout:
    """Video length and half slices on the zero-based tactical frame clock."""

    n_frames: int
    halves: tuple[slice, slice]
    fps: float = 25.0
    pitch: tuple[float, float] = (105.3, 68.0)


# Inclusive end frames in Metrica's DATA.md become exclusive slice stops.
TACTICAL = MatchLayout(199_319, (slice(11_185, 90_652), slice(110_808, 190_198)))


def write_submission(target: Path, labels: NDArray[np.str_]) -> None:
    """Write the full zero-based CSV, replacing the destination only after a complete write."""
    if target.suffix.lower() != ".csv":
        raise ValueError("Output must be a CSV path")
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=target.parent, mode="w", encoding="utf-8", newline="\n", delete=False
        ) as stream:
            temp = Path(stream.name)
            stream.write("frame,label\n")
            stream.writelines(f"{frame},{label}\n" for frame, label in enumerate(labels))
        temp.replace(target)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def generate(data_dir: Path, output: Path, layout: MatchLayout = TACTICAL) -> None:
    """Load the local tactical bundle, infer both halves, and write the submission."""
    tactical = data_dir / "tactical"
    tracking = read_tracking(tactical / ATD_METADATA, tactical / ATD_TRACKING, layout.n_frames)
    tags = read_tags(tactical / SMART_TAGGING, layout.n_frames, layout.fps)
    labels = np.full(layout.n_frames, "X")
    for graded in layout.halves:
        start = opening_frame(
            tracking.ball_xy,
            tags.opening_windows,
            graded.start,
            graded.stop,
            layout.pitch,
            layout.fps,
        )
        labels[graded.start : start] = "D"
        half = slice(start, graded.stop)
        labels[half] = predict_half(
            tracking.player_xy[half],
            tracking.ball_xy[half],
            tracking.slot_team,
            layout.pitch,
            fps=layout.fps,
            phase_bias=tags.phase_bias[half],
            restart_hint=tags.restart_hint[half],
            restart_bias=tags.restart_bias[half],
        )
    write_submission(output, labels)


def main() -> None:
    """Run the offline CLI with explicit inputs and fail on a malformed bundle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("MTAH_DATA_DIR", "data")),
        help="local dataset root containing tactical/ (default MTAH_DATA_DIR or data/)",
    )
    parser.add_argument("--output", type=Path, required=True, help="destination frame,label CSV")
    args = parser.parse_args()
    try:
        generate(args.data_dir, args.output)
    except (OSError, ValueError, ET.ParseError) as error:
        parser.exit(2, f"Cannot generate submission: {error}\n")
    print(f"Wrote {TACTICAL.n_frames:,} submission rows to {args.output}")


if __name__ == "__main__":
    main()
