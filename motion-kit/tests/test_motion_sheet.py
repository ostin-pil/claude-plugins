"""The contact sheet and onion skin, from a folder of frames (no video decoder needed)."""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "motion-craft" / "scripts" / "motion_sheet.py"
spec = importlib.util.spec_from_file_location("motion_sheet", SCRIPT)
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)


def test_sheet_and_onion_from_a_folder_of_frames(tmp_path, capsys):
    Image = pytest.importorskip("PIL.Image")
    pytest.importorskip("numpy")
    frames = tmp_path / "frames"
    frames.mkdir()
    for i in range(20):
        im = Image.new("RGB", (64, 48), (0, 0, 0))
        im.putpixel((3 * i, 24), (255, 255, 255))
        im.save(frames / ("f%03d.png" % i))
    out, onion = tmp_path / "sheet.jpg", tmp_path / "onion.png"
    code = ms.main([str(frames), "--out", str(out), "--start", "2", "--every", "3", "--count", "6",
                    "--columns", "3", "--width", "64", "--onion", str(onion)])
    assert code == 0
    sheet = Image.open(out)
    assert sheet.size == (3 * 64 + 2 * 6, 2 * (48 + 18))
    layered = Image.open(onion).convert("RGB")
    lit = [x for x in range(64) if layered.getpixel((x, 24))[0] > 20]
    assert lit == [3 * i for i in (2, 5, 8, 11, 14, 17)]
    assert "6 frames from 2 to 17" in capsys.readouterr().out
