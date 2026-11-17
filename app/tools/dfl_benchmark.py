"""Benchmark the possession estimator on public DFL matches from IDSSE v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from array import array
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any
from urllib.request import urlopen
from xml.etree import ElementTree
from xml.parsers import expat

import numpy as np
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parents[2]
FPS = 25
SECTIONS = ("firstHalf", "secondHalf")
LABELS = np.array(["H", "A", "D", "X"])
MASK_SEED = 20271117
MASK_FRACTION = 0.407
CACHE_SCHEMA = 1


@dataclass(frozen=True)
class FigshareFile:
    """Versioned original XML asset with the checksum published by the Figshare API."""

    file_id: int
    md5: str


@dataclass(frozen=True)
class Match:
    """Allowlisted IDSSE match with pinned assets and benchmark split."""

    code: str
    split: str
    metadata: FigshareFile
    positions: FigshareFile


MATCHES = (
    Match(
        "J03WOH",
        "development",
        FigshareFile(51643478, "b9710781d400dd812f62b0a6e3d7bce8"),
        FigshareFile(51643520, "3efff25a86a61768e7d253b4bba137a3"),
    ),
    Match(
        "J03WQQ",
        "development",
        FigshareFile(51643484, "5979209af316a914ce57347d0633df6c"),
        FigshareFile(51643529, "9105bad987191d3c3c362c1fce9a4fcd"),
    ),
    Match(
        "J03WN1",
        "holdout",
        FigshareFile(51643472, "37b0f85588c0acfb995fe633c7ac2e0d"),
        FigshareFile(51643517, "bacb2f609c1d1b0bfc906f6b9d4109f2"),
    ),
)


def _digest(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "md5").hexdigest()


def _fetch(asset: FigshareFile, target: Path) -> None:
    if target.is_file() and _digest(target) == asset.md5:
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://ndownloader.figshare.com/files/{asset.file_id}"
    with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".part", delete=False) as file:
        temporary = Path(file.name)
        try:
            with urlopen(url, timeout=60) as response:
                shutil.copyfileobj(response, file, length=2**20)
            file.close()
            if _digest(temporary) != asset.md5:
                raise ValueError(f"Figshare checksum mismatch for file {asset.file_id}")
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)


@dataclass
class Series:
    """One ball or player track on its original frame counter."""

    frames: array[int]
    x: array[float]
    y: array[float]
    truth: array[int]


def _metadata(path: Path, match: Match) -> tuple[dict[str, int], tuple[float, float]]:
    document = ElementTree.parse(path)
    general = document.find(".//General")
    environment = document.find(".//Environment")
    if general is None or environment is None or general.get("MatchId") != f"DFL-MAT-{match.code}":
        raise ValueError(f"Incorrect IDSSE metadata for {match.code}")

    teams = {general.attrib["HomeTeamId"]: 0, general.attrib["GuestTeamId"]: 1}
    pitch = (float(environment.attrib["PitchX"]), float(environment.attrib["PitchY"]))
    if len(teams) != 2 or not np.all(np.isfinite(pitch)) or min(pitch) <= 0:
        raise ValueError(f"Invalid team or pitch metadata for {match.code}")
    return teams, pitch


def _label(status: str | None, owner: str | None) -> int:
    if status == "0":
        return 2
    if status == "1":
        return {"1": 0, "2": 1}.get(owner, 3)
    return 3


def _position_sets(
    path: Path, match: Match, teams: dict[str, int]
) -> dict[tuple[str, str, str], Series]:
    # XML is grouped by entity rather than frame. Expat streams records without
    # constructing the large XML tree or retaining irrelevant event attributes.
    datasets: dict[tuple[str, str, str], Series] = {}
    active: Series | None = None
    ball = False

    def start(name: str, attributes: dict[str, str]) -> None:
        nonlocal active, ball
        if name == "FrameSet":
            if attributes["MatchId"] != f"DFL-MAT-{match.code}":
                raise ValueError(f"Incorrect IDSSE positions for {match.code}")
            section, team = attributes["GameSection"], attributes["TeamId"]
            ball = team == "BALL"
            active = None
            if section in SECTIONS and (ball or team in teams):
                key = (section, team, "BALL" if ball else attributes["PersonId"])
                if key not in datasets:
                    datasets[key] = Series(array("i"), array("f"), array("f"), array("b"))
                active = datasets[key]
        elif name == "Frame" and active is not None:
            frame = int(attributes["N"])
            if active.frames and frame <= active.frames[-1]:
                raise ValueError(f"Repeated or out-of-order IDSSE frame in {match.code}")
            active.frames.append(frame)
            active.x.append(float(attributes.get("X") or "nan"))
            active.y.append(float(attributes.get("Y") or "nan"))
            if ball:
                active.truth.append(
                    _label(attributes.get("BallStatus"), attributes.get("BallPossession"))
                )

    def end(name: str) -> None:
        nonlocal active
        if name == "FrameSet":
            active = None

    parser = expat.ParserCreate()
    parser.StartElementHandler = start
    parser.EndElementHandler = end
    with path.open("rb") as file:
        parser.ParseFile(file)
    return datasets


def _aligned_half(
    section: str,
    datasets: dict[tuple[str, str, str], Series],
    teams: dict[str, int],
    pitch: tuple[float, float],
) -> dict[str, NDArray[Any]]:
    raw_ball = datasets.get((section, "BALL", "BALL"))
    if raw_ball is None or not raw_ball.frames:
        raise ValueError(f"Missing ball track in {section}")

    slots = sorted(
        (key for key in datasets if key[0] == section and key[1] in teams),
        key=lambda key: (teams[key[1]], key[2]),
    )
    sides = np.array([teams[key[1]] for key in slots], dtype=np.int8)
    if set(sides) != {0, 1}:
        raise ValueError(f"Missing player team in {section}")

    first, last = raw_ball.frames[0], raw_ball.frames[-1]
    frames = np.arange(first, last + 1, dtype=np.int32)
    ball = np.full((frames.size, 2), np.nan, dtype=np.float32)
    players = np.full((frames.size, len(slots), 2), np.nan, dtype=np.float32)
    truth = np.full(frames.size, 3, dtype=np.int8)

    def fill(series: Series, result: NDArray[np.float32]) -> NDArray[np.int32]:
        offset = np.asarray(series.frames) - first
        within = (offset >= 0) & (offset < frames.size)
        selected = offset[within]
        result[selected, 0] = np.asarray(series.x)[within] / pitch[0] + 0.5
        result[selected, 1] = np.asarray(series.y)[within] / pitch[1] + 0.5
        return selected

    truth[fill(raw_ball, ball)] = np.asarray(raw_ball.truth)
    if np.all(truth == 3):
        raise ValueError(f"Missing DFL reference labels in {section}")
    for slot, key in enumerate(slots):
        fill(datasets[key], players[:, slot, :])

    return {"frames": frames, "players": players, "ball": ball, "sides": sides, "truth": truth}


def prepare(match: Match, data_dir: Path) -> Path:
    """Fetch the allowlisted XML and cache aligned positions and ground truth."""
    output = data_dir / f"{match.code}.v{CACHE_SCHEMA}.npz"
    if output.is_file():
        return output

    metadata = data_dir / "raw" / f"{match.code}.metadata.xml"
    positions = data_dir / "raw" / f"{match.code}.positions.xml"
    _fetch(match.metadata, metadata)
    _fetch(match.positions, positions)
    teams, pitch = _metadata(metadata, match)
    tracks = _position_sets(positions, match, teams)
    payload = {"pitch": np.asarray(pitch)}
    for half, section in enumerate(SECTIONS, start=1):
        payload.update(
            {
                f"{key}{half}": arr
                for key, arr in _aligned_half(section, tracks, teams, pitch).items()
            }
        )
    with tempfile.NamedTemporaryFile(dir=data_dir, suffix=".npz", delete=False) as file:
        temporary = Path(file.name)
        try:
            np.savez(file, **payload)
            file.close()
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    return output


def masked_ball(ball: NDArray[np.float32], match: Match, half: int) -> NDArray[np.float32]:
    """Hide 40.7% of frame positions in seeded contiguous blocks, independent of labels."""
    result = ball.copy()
    rng = np.random.default_rng([MASK_SEED, int(match.code, 36), half])
    n = len(result)
    boundaries = [0]
    while boundaries[-1] < n:
        boundaries.append(min(n, boundaries[-1] + int(rng.integers(5, 4 * FPS + 1))))

    remaining = round(n * MASK_FRACTION)
    for index in rng.permutation(len(boundaries) - 1):
        left, right = boundaries[index : index + 2]
        block = min(remaining, right - left)
        result[left : left + block] = np.nan
        remaining -= block
        if remaining == 0:
            break
    return result


def _baseline(
    players: NDArray[np.float32],
    ball: NDArray[np.float32],
    sides: NDArray[np.int8],
    pitch: tuple[float, float],
    baseline: ModuleType,
) -> NDArray[np.str_]:
    # Equivalent to passing the nearest-slot team codes to the official centered vote.
    distance_squared = np.sum(((players - ball[:, None, :]) * pitch) ** 2, axis=2)
    distance_squared[~np.isfinite(distance_squared)] = np.inf
    nearest = np.argmin(distance_squared, axis=1)
    exists = np.isfinite(distance_squared[np.arange(len(nearest)), nearest])
    codes = np.where(exists, sides[nearest], baseline.NOBODY)
    return baseline.smooth(codes, round(2 * FPS))


def _official_tools(repo: Path) -> tuple[ModuleType, ModuleType]:
    if not (
        (repo / "evaluation" / "possession_metrics.py").is_file()
        and (repo / "starter" / "baseline.py").is_file()
    ):
        raise ValueError(f"No official scorer and baseline under {repo}")
    sys.path[:0] = [str(repo / "evaluation"), str(repo)]
    import possession_metrics
    from starter import baseline

    return possession_metrics, baseline


def _separate_halves(items: list[NDArray[np.int8]]) -> NDArray[np.int8]:
    # The official scorer splits runs wherever the reference is X.
    return np.concatenate((items[0], np.array([3], dtype=np.int8), items[1]))


def score(
    match: Match,
    data_dir: Path,
    official_repo: Path,
    conditions: tuple[str, ...],
    solver_kwargs: dict[str, Any],
    baseline_only: bool,
) -> list[dict[str, Any]]:
    """Measure each method and mask condition with the official spell and frame metrics."""
    pm, baseline = _official_tools(official_repo)
    if not baseline_only:
        from app.possession.model import predict_half

    path = data_dir / f"{match.code}.v{CACHE_SCHEMA}.npz"
    if not path.is_file():
        raise ValueError(f"Cache for {match.code} is missing. Run `prepare --split {match.split}`.")

    summary = []
    with np.load(path, allow_pickle=False) as data:
        pitch = (float(data["pitch"][0]), float(data["pitch"][1]))
        truth = [data[f"truth{half}"] for half in (1, 2)]
        ref = _separate_halves(truth)
        for condition in conditions:
            predicted: dict[str, list[NDArray[np.int8]]] = {"nearest_smooth50": []}
            if not baseline_only:
                predicted["estimator"] = []
            missing = 0
            for half in (1, 2):
                players, ball, sides = (
                    data[f"{key}{half}"] for key in ("players", "ball", "sides")
                )
                if condition == "masked":
                    ball = masked_ball(ball, match, half)
                graded = truth[half - 1] != 3
                missing += np.count_nonzero(graded & ~np.isfinite(ball).all(axis=1))
                predicted["nearest_smooth50"].append(
                    pm.label_codes(_baseline(players, ball, sides, pitch, baseline))
                )
                if not baseline_only:
                    labels = predict_half(players, ball, sides, pitch, fps=FPS, **solver_kwargs)
                    predicted["estimator"].append(pm.label_codes(labels))

            for method, halves in predicted.items():
                result = pm.evaluate(ref, _separate_halves(halves), bootstrap_n=0)
                summary.append(
                    {
                        "match": match.code,
                        "split": match.split,
                        "condition": condition,
                        "method": method,
                        "graded_frames": result["n_graded"],
                        "ball_missing_fraction": missing / result["n_graded"],
                        "spell_f1": result["spell_f1_mean"],
                        "macro_f1": result["macro_f1"],
                        "dead_f1": result["per_class"]["D"]["f1"],
                        "predicted_spells": result["n_pred_spells"],
                        "reference_spells": result["n_gt_spells"],
                    }
                )
    return summary


def main() -> None:
    """Prepare IDSSE v1 caches or score an explicitly chosen split."""
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("command", choices=("prepare", "score"))
    cli.add_argument("--split", required=True, choices=("development", "holdout"))
    cli.add_argument("--cache", type=Path, default=ROOT / "data" / "external_dfl")
    cli.add_argument("--official-repo", type=Path, default=ROOT.parent / "more-than-a-hack-2027")
    cli.add_argument("--condition", default="both", choices=("original", "masked", "both"))
    cli.add_argument("--solver-kwargs", default="{}", help="Optional JSON keyword overrides")
    cli.add_argument(
        "--baseline-only", action="store_true", help="Run without importing the estimator"
    )
    args = cli.parse_args()
    matches = [match for match in MATCHES if match.split == args.split]
    if args.command == "prepare":
        for match in matches:
            print(prepare(match, args.cache), flush=True)
        return

    overrides = json.loads(args.solver_kwargs)
    if not isinstance(overrides, dict):
        cli.error("--solver-kwargs must contain a JSON object")
    conditions = ("original", "masked") if args.condition == "both" else (args.condition,)
    results = []
    for match in matches:
        results.extend(
            score(
                match,
                args.cache,
                args.official_repo.resolve(),
                conditions,
                overrides,
                args.baseline_only,
            )
        )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
