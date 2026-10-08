"""Numeric visibility regressions; runtime/browser evidence checks actual layouts separately."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


def luminance(rgb):
    channels = [v / 255 for v in rgb]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(a * b for a, b in zip(linear, (.2126, .7152, .0722)))


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + .05) / (lo + .05)


def tokens(theme):
    css = (ROOT / 'apps/web/src/app/globals.css').read_text()
    blocks = re.findall(r':root(?:\[data-theme="light"\])?\s*\{([^}]+)', css)
    values = dict(re.findall(r'(--cw-[\w-]+):\s*([^;]+);', blocks[0]))
    if theme == 'light':
        values.update(re.findall(r'(--cw-[\w-]+):\s*([^;]+);', blocks[1]))
    def resolve(name):
        assert name in values, f"Missing semantic colour role {name}"
        value = values[name]
        if value.startswith('var('):
            return resolve(value[4:-1])
        return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))
    return resolve


class ThemeVisibilityTests(unittest.TestCase):
    def test_normal_text_roles_meet_aa_on_all_theme_surfaces(self):
        for theme in ('dark', 'light'):
            color = tokens(theme)
            for foreground in ('--cw-text', '--cw-muted', '--cw-accent-text', '--cw-link'):
                for background in ('--cw-bg', '--cw-surface', '--cw-surface-2'):
                    with self.subTest(theme=theme, foreground=foreground, background=background):
                        self.assertGreaterEqual(contrast(color(foreground), color(background)), 4.5)

    def test_filled_action_text_meets_aa_at_rest_and_hover(self):
        for theme in ('dark', 'light'):
            color = tokens(theme)
            for fill in ('--cw-accent-fill', '--cw-aqua-strong'):
                self.assertGreaterEqual(contrast(color('--cw-on-accent'), color(fill)), 4.5)

    def test_focus_and_control_boundaries_are_visible(self):
        for theme in ('dark', 'light'):
            color = tokens(theme)
            for mark in ('--cw-focus', '--cw-control-border'):
                for surface in ('--cw-bg', '--cw-surface', '--cw-surface-2'):
                    self.assertGreaterEqual(contrast(color(mark), color(surface)), 3)

    def test_hero_panel_remains_readable_over_black_and_white_images(self):
        # The rendered 97%-surface panel bounds any photograph; shadow is not counted.
        for theme in ('dark', 'light'):
            color = tokens(theme)
            for image in ((0, 0, 0), (255, 255, 255)):
                panel = tuple(.97 * a + .03 * b for a, b in zip(color('--cw-surface'), image))
                for text in ('--cw-text', '--cw-muted', '--cw-accent-text'):
                    self.assertGreaterEqual(contrast(color(text), panel), 4.5)

    def test_logo_mattes_follow_original_pixels_not_page_theme(self):
        module = ROOT / 'apps/web/src/lib/presentation/logo-matte.ts'
        self.assertTrue(module.is_file(), 'Original black/white logo contrast requires asset-specific mattes')
        script = '''
import { getLogoMatte } from './apps/web/src/lib/presentation/logo-matte.ts';
const samples = [
 'https://image.tmdb.org/t/p/w185/oRR9EXVoKP9szDkVKlze5HVJS7g.png',
 'https://image.tmdb.org/t/p/w185/ybTppkzqb3XOWKNcco144BFlosB.png',
 'https://image.tmdb.org/t/p/original/ybTppkzqb3XOWKNcco144BFlosB.png',
 'https://image.tmdb.org/t/p/w185/hUzeosd33nzE5MCNsZxCGEKTXaQ.png',
 'https://image.tmdb.org/t/p/w185/8PeKdSO13vYTod2HAJsV2m7mRr0.png',
 'https://image.tmdb.org/t/p/w185/g5oRCNCi8kNVb8gEoSoIcqkhjmR.png',
 'https://image.tmdb.org/t/p/w185/ePTA7uHqE4k0exCefnacgljxjD.png',
 'https://image.tmdb.org/t/p/w185/ygMQtjsKX7BZkCQhQZY82lgnCUO.png',
 null,
 'https://other.example/ybTppkzqb3XOWKNcco144BFlosB.png'
];
console.log(JSON.stringify(samples.map(getLogoMatte)));
'''
        result = subprocess.run(['node', '--input-type=module', '-e', script], cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), ['light', 'dark', 'dark', 'light', 'dark', 'dark', 'dark', 'dark', 'light', 'light'])


if __name__ == '__main__':
    unittest.main()
