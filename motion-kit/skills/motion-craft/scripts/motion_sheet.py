"""Lay a reel out for judging: a contact sheet of frames, and an onion skin of them.

    uv run --with av --with pillow --with numpy python motion_sheet.py reel.mp4 --out sheet.jpg
        [--start 60] [--every 2] [--count 12] [--columns 6] [--width 320]
        [--crop X,Y,W,H] [--onion onion.png] [--fps-label 60]

The contact sheet shows `count` frames, `every` frames apart from `start`, each
labelled with its frame number and time, `columns` to a row, each scaled to
`width` pixels. The onion skin lays the same frames over one another, the
earliest faintest, so a moving part's path and spacing show in one image.
`crop` cuts each frame to a region first (the figure, close).

Video decoding needs PyAV; any format FFmpeg reads works. Frames already saved
as images can be passed instead of a video by giving a folder: its PNG and JPG
files are taken in name order.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def frames_from(source: str, wanted: list[int]):
    """The wanted frames (indices into the reel), as PIL images, in order."""
    from PIL import Image

    path = Path(source)
    if path.is_dir():
        files = sorted(p for p in path.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
        return [Image.open(files[i]).convert("RGB") for i in wanted if i < len(files)]
    import av

    out = {}
    last = max(wanted)
    with av.open(source) as container:
        for i, frame in enumerate(container.decode(video=0)):
            if i in wanted:
                out[i] = frame.to_image().convert("RGB")
            if i >= last:
                break
    return [out[i] for i in wanted if i in out]


def sheet(images, labels, columns: int, width: int):
    from PIL import Image, ImageDraw

    scaled = [im.resize((width, round(im.height * width / im.width))) for im in images]
    cell_h = max(im.height for im in scaled) + 18
    rows = (len(scaled) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * width + (columns - 1) * 6, rows * cell_h), (18, 18, 22))
    pen = ImageDraw.Draw(canvas)
    for k, (im, label) in enumerate(zip(scaled, labels)):
        x, y = (k % columns) * (width + 6), (k // columns) * cell_h
        pen.text((x + 4, y + 2), label, fill=(230, 230, 230))
        canvas.paste(im, (x, y + 18))
    return canvas


def onion(images, threshold: int = 12):
    """The frames as ghosts over their still background: what each frame shows that the
    background doesn't is laid in, the earliest at 35% opacity rising to the latest at
    full. The background is the per-pixel median of the frames, so a still room stays
    clean and only what moved is ghosted. Needs NumPy."""
    import numpy as np
    from PIL import Image

    size = images[-1].size
    stack = np.stack([np.asarray(im.convert("RGB").resize(size), dtype=np.float32) for im in images])
    background = np.median(stack, axis=0)
    out = background.copy()
    n = len(images)
    for k in range(n):
        alpha = 1.0 if k == n - 1 else 0.35 + 0.45 * k / max(n - 2, 1)
        moved = np.abs(stack[k] - background).max(axis=2) > threshold
        out[moved] = out[moved] * (1.0 - alpha) + stack[k][moved] * alpha
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("reel", help="a video, or a folder of frame images")
    parser.add_argument("--out", required=True, help="the contact sheet to write")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--every", type=int, default=2)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--columns", type=int, default=6)
    parser.add_argument("--width", type=int, default=320)
    parser.add_argument("--crop", help="X,Y,W,H in the reel's pixels")
    parser.add_argument("--onion", help="also write an onion skin of the same frames here")
    parser.add_argument("--fps-label", type=float, default=60.0, help="the reel's frame rate, for the time labels")
    args = parser.parse_args(argv)

    wanted = [args.start + k * args.every for k in range(args.count)]
    images = frames_from(args.reel, wanted)
    if not images:
        print("no frames found at %s" % wanted, file=sys.stderr)
        return 1
    if args.crop:
        x, y, w, h = (int(v) for v in args.crop.split(","))
        images = [im.crop((x, y, x + w, y + h)) for im in images]
    labels = ["%d  %.2f s" % (i, i / args.fps_label) for i in wanted[: len(images)]]
    sheet(images, labels, args.columns, args.width).save(args.out, quality=90)
    if args.onion:
        onion(images).save(args.onion)
    print("%d frames from %d to %d into %s%s" % (len(images), wanted[0], wanted[len(images) - 1], args.out,
                                                 " and %s" % args.onion if args.onion else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
