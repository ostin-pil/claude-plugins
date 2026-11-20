"""Measure and draw the paths of moving parts: arcs, spacing, reversals, lag.

    uv run --with pillow python motion_path.py paths.json [--out paths.png]
        [--plane xy|zy|xz] [--lag A:B ...] [--from N] [--to N] [--json report.json]

The input is a JSON object:

    {
      "fps": 60,                      # samples per second
      "space": "screen" | "world",    # screen: pixels, y grows down; world: y up
      "plane": "xy",                  # optional default plane to measure and draw in
      "points": {                     # each a list of [x, y] or [x, y, z], one per sample
        "HandL": [[412.0, 380.5], ...],
        "UpperArmL": [[...], ...]
      }
    }

For each point it reports, in the chosen plane:
  samples and distinct poses (consecutive identical positions collapse, so a
      character stepped on twos shows half as many poses as samples)
  range along the path's main direction and across it
  cycle: the period found by autocorrelation along the main direction, if any
  reversals per cycle along the main direction (a swing has 2)
  bulge: how far the path bows off the straight line between its extremes,
      as a share of that line's length (0 is a straight back-and-forth)
  loop: the area a cycle encloses over the main range times the cross range
      (0 means the part retraces one line; overlap and lag open a loop)
  sharpest corner: the largest turn between successive moves that is not a
      reversal (a corner in mid-path reads mechanical)
  ease: speed near the extremes over speed through the middle (below 1 slows
      into the extremes, about 1 is even spacing)
With --lag A:B it reports how many samples B's motion trails A's along each
one's main direction, from the cross-correlation over one cycle.

Pure Python apart from Pillow, which only the drawing needs.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

EPS = 1e-6
PLANES = {"xy": (0, 1), "zy": (2, 1), "xz": (0, 2)}


# Loading -----------------------------------------------------------------------------

def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if "points" not in data or not data["points"]:
        raise ValueError("no points in %s" % path)
    data.setdefault("fps", 60.0)
    data.setdefault("space", "world")
    return data


def project(samples: list, plane: str) -> list[tuple[float, float]]:
    a, b = PLANES[plane]
    out = []
    for sample in samples:
        if len(sample) == 2 and plane != "xy":
            raise ValueError("2D points can only be measured in the xy plane")
        out.append((float(sample[a]), float(sample[b])))
    return out


# Measures ----------------------------------------------------------------------------

def distinct(points: list[tuple[float, float]], eps: float = EPS) -> list[tuple[float, float]]:
    """Consecutive identical positions collapsed into one pose."""
    poses: list[tuple[float, float]] = []
    for p in points:
        if not poses or math.dist(p, poses[-1]) > eps:
            poses.append(p)
    return poses


def main_direction(points: list[tuple[float, float]]) -> tuple[tuple[float, float], tuple[float, float]]:
    """The mean and the unit direction of largest variance."""
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points) / n
    syy = sum((p[1] - my) ** 2 for p in points) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points) / n
    angle = 0.5 * math.atan2(2.0 * sxy, sxx - syy)
    return (mx, my), (math.cos(angle), math.sin(angle))


def along(points, centre, direction) -> list[float]:
    return [(p[0] - centre[0]) * direction[0] + (p[1] - centre[1]) * direction[1] for p in points]


def across(points, centre, direction) -> list[float]:
    return [-(p[0] - centre[0]) * direction[1] + (p[1] - centre[1]) * direction[0] for p in points]


def period(signal: list[float], threshold: float = 0.5) -> int | None:
    """The cycle, in samples: the strongest autocorrelation peak after the signal has first
    decorrelated (gone below zero), if it's above `threshold`; else None. Waiting for the dip
    keeps the holds of a stepped signal from passing for a cycle."""
    n = len(signal)
    mean = sum(signal) / n
    centred = [s - mean for s in signal]
    energy = sum(c * c for c in centred)
    if energy < EPS:
        return None

    def r(lag):
        return sum(centred[i] * centred[i + lag] for i in range(n - lag)) / energy * n / (n - lag)

    dipped = None
    for lag in range(1, n // 2 + 1):
        if r(lag) < 0.0:
            dipped = lag
            break
    if dipped is None:
        return None
    best, best_r = None, threshold
    for lag in range(dipped, n // 2 + 1):
        value = r(lag)
        if value > best_r:
            best, best_r = lag, value
        elif best is not None and value < best_r - 0.2:
            break
    return best


def reversals(values: list[float], eps: float = EPS) -> int:
    count = 0
    sign = 0
    for a, b in zip(values, values[1:]):
        step = b - a
        if abs(step) <= eps:
            continue
        s = 1 if step > 0 else -1
        if sign and s != sign:
            count += 1
        sign = s
    return count


def bulge(points, centre, direction) -> float:
    """How far the path bows off the chord between its two extremes along the main direction."""
    a = along(points, centre, direction)
    low = points[a.index(min(a))]
    high = points[a.index(max(a))]
    chord = math.dist(low, high)
    if chord < EPS:
        return 0.0
    ux, uy = (high[0] - low[0]) / chord, (high[1] - low[1]) / chord
    furthest = max(abs(-(p[0] - low[0]) * uy + (p[1] - low[1]) * ux) for p in points)
    return furthest / chord


def loop_openness(points: list[tuple[float, float]], centre, direction) -> float:
    """Shoelace area of the closed path over (main range x cross range); 0 for a retraced line."""
    if len(points) < 3:
        return 0.0
    area = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        area += x0 * y1 - x1 * y0
    area = abs(area) / 2.0
    a = along(points, centre, direction)
    c = across(points, centre, direction)
    box = (max(a) - min(a)) * (max(c) - min(c))
    return area / box if box > EPS else 0.0


def sharpest_corner(poses: list[tuple[float, float]], centre, direction) -> float:
    """The largest turn, in degrees, between successive moves, leaving out reversals along the main direction."""
    worst = 0.0
    moves = [(b[0] - a[0], b[1] - a[1]) for a, b in zip(poses, poses[1:])]
    for m0, m1 in zip(moves, moves[1:]):
        l0, l1 = math.hypot(*m0), math.hypot(*m1)
        if l0 < EPS or l1 < EPS:
            continue
        a0 = m0[0] * direction[0] + m0[1] * direction[1]
        a1 = m1[0] * direction[0] + m1[1] * direction[1]
        if a0 * a1 < 0.0:
            continue
        cos = max(-1.0, min(1.0, (m0[0] * m1[0] + m0[1] * m1[1]) / (l0 * l1)))
        worst = max(worst, math.degrees(math.acos(cos)))
    return worst


def ease(poses: list[tuple[float, float]], centre, direction) -> float | None:
    """Mean step near the extremes (outer 20% of the range each side) over mean step through the middle 40%."""
    a = along(poses, centre, direction)
    low, high = min(a), max(a)
    span = high - low
    if span < EPS or len(poses) < 4:
        return None
    outer, middle = [], []
    for i in range(len(poses) - 1):
        step = math.dist(poses[i], poses[i + 1])
        mid = ((a[i] + a[i + 1]) * 0.5 - low) / span
        if mid < 0.2 or mid > 0.8:
            outer.append(step)
        elif 0.3 <= mid <= 0.7:
            middle.append(step)
    if not outer or not middle:
        return None
    m = sum(middle) / len(middle)
    return (sum(outer) / len(outer)) / m if m > EPS else None


def lag(signal_a: list[float], signal_b: list[float], window: int) -> int:
    """The shift k, |k| <= window, at which b(t) best matches a(t - k): positive when b trails a."""
    n = min(len(signal_a), len(signal_b))

    def norm(s):
        m = sum(s[:n]) / n
        c = [v - m for v in s[:n]]
        e = math.sqrt(sum(v * v for v in c)) or 1.0
        return [v / e for v in c]

    a, b = norm(signal_a), norm(signal_b)
    best_k, best_r = 0, -2.0
    for k in range(-window, window + 1):
        pairs = [(a[i - k], b[i]) for i in range(max(0, k), min(n, n + k))]
        if not pairs:
            continue
        r = sum(x * y for x, y in pairs) * n / len(pairs)
        if r > best_r:
            best_r, best_k = r, k
    return best_k


def measure(points: list[tuple[float, float]], fps: float) -> dict:
    centre, direction = main_direction(points)
    a = along(points, centre, direction)
    c = across(points, centre, direction)
    poses = distinct(points)
    cycle = period(a)
    one_cycle = points[:cycle] if cycle else points
    cycle_poses = distinct(one_cycle)
    rev = reversals(along(poses, centre, direction))
    cycles = len(points) / cycle if cycle else None
    return {
        "samples": len(points),
        "distinct_poses": len(poses),
        "range_main": max(a) - min(a),
        "range_across": max(c) - min(c),
        "direction": direction,
        "_centre": centre,
        "cycle_samples": cycle,
        "cycle_seconds": cycle / fps if cycle else None,
        "poses_per_cycle": len(cycle_poses) if cycle else None,
        "reversals_per_cycle": rev / cycles if cycles else rev,
        "bulge": bulge(one_cycle, centre, direction),
        "loop": loop_openness(cycle_poses if cycle else poses, centre, direction),
        "sharpest_corner_deg": sharpest_corner(poses, centre, direction),
        "ease": ease(poses, centre, direction),
        "_along": a,
    }


# Drawing -----------------------------------------------------------------------------

COLOURS = [(230, 90, 60), (60, 150, 230), (90, 190, 90), (220, 180, 40), (180, 90, 200), (60, 200, 200)]


def draw(projected: dict, measures: dict, out: str, flip_y: bool, title: str) -> None:
    from PIL import Image, ImageDraw

    width, height, pad = 1400, 760, 40
    image = Image.new("RGB", (width, height), (20, 20, 24))
    pen = ImageDraw.Draw(image)
    pen.text((pad, 10), title, fill=(230, 230, 230))
    # The paths, at one scale, in a square on the left.
    side = height - 2 * pad - 20
    xs = [p[0] for pts in projected.values() for p in pts]
    ys = [p[1] for pts in projected.values() for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys), EPS)
    ox, oy = min(xs), min(ys)

    def at(p):
        x = pad + (p[0] - ox) / span * side
        y = (p[1] - oy) / span * side
        y = pad + 20 + (side - y if flip_y else y)
        return x, y

    pen.rectangle([pad, pad + 20, pad + side, pad + 20 + side], outline=(70, 70, 80))
    for k, (name, pts) in enumerate(projected.items()):
        colour = COLOURS[k % len(COLOURS)]
        line = [at(p) for p in pts]
        if len(line) > 1:
            pen.line(line, fill=tuple(v // 2 for v in colour), width=1)
        for i, p in enumerate(distinct(pts)):
            x, y = at(p)
            pen.ellipse([x - 3, y - 3, x + 3, y + 3], fill=colour)
            if i % 4 == 0:
                pen.text((x + 4, y - 10), str(i), fill=colour)
        x, y = at(pts[0])
        pen.rectangle([x - 5, y - 5, x + 5, y + 5], outline=(255, 255, 255))
    # Each point's motion along its main direction against time, on the right.
    left = pad * 2 + side
    plot_w = width - left - pad
    rows = len(projected)
    row_h = (height - 2 * pad - 20) / max(rows, 1)
    for k, (name, pts) in enumerate(projected.items()):
        colour = COLOURS[k % len(COLOURS)]
        m = measures[name]
        a = m["_along"]
        lo, hi = min(a), max(a)
        top = pad + 20 + k * row_h
        pen.rectangle([left, top + 4, left + plot_w, top + row_h - 4], outline=(70, 70, 80))
        n = len(a)
        if hi - lo > EPS and n > 1:
            curve = [(left + i / (n - 1) * plot_w, top + row_h - 8 - (v - lo) / (hi - lo) * (row_h - 16)) for i, v in enumerate(a)]
            pen.line(curve, fill=colour, width=2)
        if m["cycle_samples"]:
            for c in range(m["cycle_samples"], n, m["cycle_samples"]):
                x = left + c / (n - 1) * plot_w
                pen.line([(x, top + 4), (x, top + row_h - 4)], fill=(90, 90, 100))
        pen.text((left + 6, top + 8), "%s  %s" % (name, summary(m)), fill=colour)
    image.save(out)


def summary(m: dict) -> str:
    parts = ["poses %d/%d" % (m["distinct_poses"], m["samples"])]
    if m["cycle_samples"]:
        parts.append("cycle %d (%.2f s, %s poses)" % (m["cycle_samples"], m["cycle_seconds"], m["poses_per_cycle"]))
    parts.append("bulge %.2f" % m["bulge"])
    parts.append("loop %.2f" % m["loop"])
    parts.append("corner %.0f deg" % m["sharpest_corner_deg"])
    if m["ease"] is not None:
        parts.append("ease %.2f" % m["ease"])
    return ", ".join(parts)


# Command line --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths")
    parser.add_argument("--out", help="PNG to draw the paths into")
    parser.add_argument("--plane", choices=sorted(PLANES), help="plane to measure in (default: the file's, else xy)")
    parser.add_argument("--lag", action="append", default=[], metavar="A:B", help="report how far B trails A")
    parser.add_argument("--from", dest="start", type=int, default=0)
    parser.add_argument("--to", dest="end", type=int)
    parser.add_argument("--json", help="write the measures here too")
    args = parser.parse_args(argv)

    data = load(args.paths)
    plane = args.plane or data.get("plane", "xy")
    fps = float(data["fps"])
    projected = {name: project(samples, plane)[args.start:args.end] for name, samples in data["points"].items()}
    measures = {name: measure(pts, fps) for name, pts in projected.items() if len(pts) >= 3}
    for name, m in measures.items():
        print("%-14s %s, range %.4g along, %.4g across, reversals %.1f per cycle" % (
            name, summary(m), m["range_main"], m["range_across"], m["reversals_per_cycle"]))
    lags = {}
    for pair in args.lag:
        first, second = pair.split(":")
        if first not in measures or second not in measures:
            print("lag %s: no such point" % pair, file=sys.stderr)
            continue
        window = (measures[first]["cycle_samples"] or len(projected[first])) // 2
        # Both along the first point's main direction, so their signs agree.
        trailing = along(projected[second], measures[second]["_centre"], measures[first]["direction"])
        k = lag(measures[first]["_along"], trailing, window)
        cycle = measures[first]["cycle_samples"]
        lags[pair] = k
        print("lag %s: %s trails %s by %d samples (%.3f s%s)" % (
            pair, second, first, k, k / fps, ", %.2f of a cycle" % (k / cycle) if cycle else ""))
    if args.out:
        draw(projected, measures, args.out, data["space"] != "screen", "%s  (%s plane, %g fps)" % (args.paths, plane, fps))
    if args.json:
        clean = {name: {k: v for k, v in m.items() if not k.startswith("_")} for name, m in measures.items()}
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump({"plane": plane, "fps": fps, "points": clean, "lags": lags}, handle, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
