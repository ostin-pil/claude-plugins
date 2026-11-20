"""The motion-path probe on synthetic motion whose answers are known."""
import importlib.util
import json
import math
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "motion-craft" / "scripts" / "motion_path.py"
spec = importlib.util.spec_from_file_location("motion_path", SCRIPT)
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

FPS = 60
CYCLE = 30  # samples per cycle
N = 120     # four cycles


def sine_line(n=N, cycle=CYCLE, amplitude=10.0, phase=0):
    return [(amplitude * math.sin(2 * math.pi * (i - phase) / cycle), 0.0) for i in range(n)]


def triangle_line(n=N, cycle=CYCLE, amplitude=10.0):
    out = []
    for i in range(n):
        t = (i % cycle) / cycle
        v = 4 * t - 1 if t < 0.5 else 3 - 4 * t
        out.append((amplitude * v, 0.0))
    return out


def ellipse(n=N, cycle=CYCLE, a=10.0, b=3.0):
    return [(a * math.cos(2 * math.pi * i / cycle), b * math.sin(2 * math.pi * i / cycle)) for i in range(n)]


def on_twos(points):
    return [points[i - i % 2] for i in range(len(points))]


def test_cycle_and_reversals_of_a_swing():
    m = mp.measure(sine_line(), FPS)
    assert m["cycle_samples"] == CYCLE
    assert m["reversals_per_cycle"] == pytest.approx(2.0, abs=0.3)
    assert m["cycle_seconds"] == pytest.approx(CYCLE / FPS)


def test_a_straight_back_and_forth_has_no_bulge_or_loop():
    m = mp.measure(sine_line(), FPS)
    assert m["bulge"] < 0.01
    assert m["loop"] < 0.01


def test_an_open_loop_reads_as_one():
    m = mp.measure(ellipse(), FPS)
    assert m["loop"] > 0.5
    # 3 deep over a 20-long chord.
    assert m["bulge"] == pytest.approx(0.15, abs=0.01)


def test_a_sine_eases_into_its_extremes_and_a_triangle_does_not():
    eased = mp.measure(sine_line(), FPS)["ease"]
    even = mp.measure(triangle_line(), FPS)["ease"]
    assert eased < 0.75
    assert even == pytest.approx(1.0, abs=0.1)


def test_on_twos_halves_the_distinct_poses_and_keeps_the_cycle():
    m = mp.measure(on_twos(sine_line()), FPS)
    assert m["distinct_poses"] == N // 2
    assert m["cycle_samples"] == CYCLE
    assert m["poses_per_cycle"] == CYCLE // 2


def test_lag_finds_how_far_one_part_trails_another():
    leader = mp.along(sine_line(), (0.0, 0.0), (1.0, 0.0))
    trailer = mp.along(sine_line(phase=3), (0.0, 0.0), (1.0, 0.0))
    assert mp.lag(leader, trailer, CYCLE // 2) == 3
    assert mp.lag(trailer, leader, CYCLE // 2) == -3


def test_a_corner_in_mid_path_is_found_and_a_reversal_is_not():
    square_corner = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (2.0, 1.0), (2.0, 2.0)]
    centre, direction = mp.main_direction(square_corner)
    assert mp.sharpest_corner(square_corner, centre, direction) == pytest.approx(90.0, abs=1.0)
    back_and_forth = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (1.0, 0.0), (0.0, 0.0)]
    centre, direction = mp.main_direction(back_and_forth)
    assert mp.sharpest_corner(back_and_forth, centre, direction) == pytest.approx(0.0, abs=1e-6)


def test_the_command_line_reports_and_draws(tmp_path, capsys):
    pytest.importorskip("PIL")
    data = {"fps": FPS, "space": "screen", "points": {
        "Shoulder": [list(p) for p in sine_line()],
        "Hand": [list(p) for p in sine_line(phase=2)],
    }}
    source = tmp_path / "paths.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    out = tmp_path / "paths.png"
    report = tmp_path / "report.json"
    assert mp.main([str(source), "--out", str(out), "--lag", "Shoulder:Hand", "--json", str(report)]) == 0
    assert out.stat().st_size > 1000
    written = json.loads(report.read_text(encoding="utf-8"))
    assert written["lags"]["Shoulder:Hand"] == 2
    assert "Hand trails Shoulder by 2 samples" in capsys.readouterr().out


def test_relative_to_takes_out_the_body_s_bob(tmp_path, capsys):
    bob = [(0.0, 3.0 * math.sin(2 * math.pi * i / 15)) for i in range(N)]
    hand = [(s[0] + b[0], s[1] + b[1]) for s, b in zip(sine_line(), bob)]
    data = {"fps": FPS, "space": "world", "points": {"Chest": [list(p) for p in bob], "Hand": [list(p) for p in hand]}}
    source = tmp_path / "paths.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    raw, relative = tmp_path / "raw.json", tmp_path / "relative.json"
    assert mp.main([str(source), "--json", str(raw)]) == 0
    assert mp.main([str(source), "--relative-to", "Chest", "--json", str(relative)]) == 0
    assert json.loads(raw.read_text(encoding="utf-8"))["points"]["Hand"]["bulge"] > 0.1
    assert json.loads(relative.read_text(encoding="utf-8"))["points"]["Hand"]["bulge"] < 0.01

