"""Stream Now V2 policy plus real manifest/denial regression.

Browser qualification independently exercises the engine and rendered journey.
"""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'apps/web/src'


class StreamNowTests(unittest.TestCase):
    def test_real_route_and_dormant_server_boundary(self):
        page = SRC / 'app/stream-now/page.tsx'
        self.assertTrue(page.is_file(), 'V2 real Stream Now route missing')
        self.assertIn('resolveAuthorizedPlayback', page.read_text())
        self.assertIn('import "server-only"', (SRC / 'lib/playable/authority.ts').read_text())

    def test_route_does_not_nest_site_main_landmark(self):
        page = (SRC / "app/stream-now/page.tsx").read_text()
        self.assertNotIn("<main", page)
        self.assertIn('<section aria-label="Stream Now">', page)

    def test_all_navigation_uses_canonical_route(self):
        for name in ['components/site/SiteFrame.tsx', 'components/home/HomepageExperience.tsx', 'components/catalog/TitleDetails.tsx']:
            text = (SRC / name).read_text()
            self.assertNotIn('/under-development/stream-now', text, name)
            self.assertIn('/stream-now', text, name)
        legacy = (SRC / 'app/under-development/[feature]/page.tsx').read_text()
        self.assertIn('permanentRedirect("/stream-now")', legacy)
        config = (ROOT / "apps/web/next.config.ts").read_text()
        self.assertIn('source: "/under-development/stream-now"', config)
        self.assertIn('destination: "/stream-now"', config)
        self.assertIn("permanent: true", config)

    def test_no_engineering_or_lab_ui(self):
        for name in ['components/site/UnderDevelopmentPanel.tsx', 'components/home/HomepageExperience.tsx']:
            self.assertNotIn('Stream Now is under development', (SRC / name).read_text())
        component = SRC / 'components/player/CineWatchPlayer.tsx'
        self.assertTrue(component.is_file(), 'qualified player absent')
        text = component.read_text()
        for forbidden in ['Qualification diagnostics', '/api/qualification/', 'Bonanza', 'PLAYER_LAB_MEDIA_PATH', 'localStorage', 'sessionStorage']:
            self.assertNotIn(forbidden, text)
        self.assertFalse((SRC / 'app/api/qualification').exists())

    def test_silent_thirty_second_loop_and_static_reduced_motion(self):
        css = SRC / 'components/stream/StreamNowAnimation.module.css'
        self.assertTrue(css.is_file(), 'animation absent')
        text = css.read_text()
        self.assertRegex(text, r'animation:\s*flow\s+30s\s+ease-in-out\s+infinite')
        self.assertIn('prefers-reduced-motion: reduce', text)
        self.assertIn('animation: none', text)
        self.assertIn('0%, 100%', text)
        component = (SRC / 'components/stream/StreamNowAnimation.tsx').read_text()
        for forbidden in ['<video', '<audio', '<button', '<iframe', 'database', 'R2', 'available', 'ready', 'Awaiting']:
            self.assertNotIn(forbidden, component)

    def test_real_manifest_validation_and_unauthorized_denial(self):
        script = ROOT / 'scripts/check_stream_now_contract.mjs'
        self.assertTrue(script.is_file(), 'real contract test absent')
        result = subprocess.run(['node', str(script)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
