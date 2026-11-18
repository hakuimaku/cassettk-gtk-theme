"""Check semantic contrast and reproducible release output for Cassettk."""
from pathlib import Path
import re
import io
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from materialize import ROOT, SOURCE, VARIANTS, materialize


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return sum(weight * (c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4)
               for weight, c in zip((.2126, .7152, .0722), channels))


def contrast(a, b):
    low, high = sorted((luminance(a), luminance(b)))
    return (high + .05) / (low + .05)


class PaletteTests(unittest.TestCase):
    def test_semantic_contrast(self):
        colors = dict(re.findall(r'@define-color (\w+) (#[0-9a-fA-F]{6});',
                                 (SOURCE / "palettes/dark.css").read_text()))
        self.assertGreaterEqual(contrast(colors["cass_text"], colors["cass_window_bg"]), 4.5)
        self.assertGreaterEqual(contrast(colors["cass_text"], colors["cass_inset_bg"]), 4.5)
        self.assertGreaterEqual(contrast(colors["cass_text"], colors["cass_button_bg"]), 4.5)
        self.assertGreaterEqual(contrast(colors["cass_select_fg"], colors["cass_select_bg"]), 4.5)
        self.assertGreaterEqual(contrast(colors["cass_title_fg"], colors["cass_title_bg"]), 4.5)
        self.assertGreaterEqual(contrast(colors["cass_tooltip_fg"], colors["cass_tooltip_bg"]), 4.5)
        self.assertGreaterEqual(contrast(colors["cass_urgent_fg"], colors["cass_urgent_bg"]), 4.5)

    @unittest.skipUnless(shutil.which("rsvg-convert"), "indicator renders require librsvg and Pillow")
    def test_indicator_renders(self):
        from PIL import Image
        expected = (230, 230, 230)
        for asset in ("check", "minus", "dot"):
            path = ROOT / "themes/Cassettk/assets" / f"{asset}.svg"
            png = subprocess.run(["rsvg-convert", str(path)], check=True, capture_output=True).stdout
            image = Image.open(io.BytesIO(png)).convert("RGBA")
            pixels = image.load()
            opaque = [pixels[x, y][:3] for y in range(16) for x in range(16) if pixels[x, y][3] == 255]
            self.assertGreater(len(opaque), 5, asset)
            self.assertEqual(set(opaque), {expected}, asset)

    def test_release_matches_canonical_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            materialize(temporary)
            for name in VARIANTS.values():
                output = Path(temporary) / name
                for file in output.rglob("*"):
                    if file.is_file():
                        self.assertEqual(file.read_bytes(), (ROOT / "themes" / name / file.relative_to(output)).read_bytes())
                        self.assertNotIn(b"@INDICATOR@", file.read_bytes())
