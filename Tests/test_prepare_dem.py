import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
from prepare_dem import convert

class SurveyConversion(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'survey.asc'
        self.source.write_text('ncols 3\nnrows 2\nxllcorner 100\nyllcorner 200\ncellsize 10\nNODATA_value -9999\n30 40 50\n0 10 20\n')
    def run_conversion(self, resolution=33):
        return convert(self.source, self.root / 'out', resolution, 'TEST projected metres', 'TEST datum', 'Synthetic QA fixture, not Machu Picchu')
    def samples(self):
        return struct.unpack('<' + 'H' * (33 * 33), (self.root / 'out/heightmap.r16').read_bytes())
    def test_orientation_dimensions_and_bilinear_height(self):
        m = self.run_conversion()
        self.assertEqual((m['widthMeters'], m['lengthMeters']), (20, 10))
        self.assertEqual((m['originEastingMeters'], m['originNorthingMeters']), (105, 205))
        values = self.samples()
        for index, expected in [(0, 0), (32, 20), (32 * 33, 30), (-1, 50), (16 * 33 + 16, 25)]:
            actual = values[index] / 65535 * m['heightMeters'] + m['baseElevationMeters']
            self.assertLessEqual(abs(actual - expected), m['maxQuantizationErrorMeters'] + 1e-10)
    def test_nodata_is_rejected(self):
        self.source.write_text(self.source.read_text().replace('0 10 20', '0 -9999 20'))
        with self.assertRaises(ValueError): self.run_conversion()
        self.assertFalse((self.root / 'out').exists())
    def test_invalid_resolution(self):
        with self.assertRaises(ValueError): self.run_conversion(1000)
    def test_output_never_overwritten(self):
        self.run_conversion()
        before = (self.root / 'out/heightmap.r16').read_bytes()
        with self.assertRaises(FileExistsError): self.run_conversion()
        self.assertEqual(before, (self.root / 'out/heightmap.r16').read_bytes())
    def test_flat_negative_elevation_preserves_datum(self):
        self.source.write_text(self.source.read_text().replace('30 40 50\n0 10 20', '-20 -20 -20\n-20 -20 -20'))
        m = self.run_conversion()
        self.assertEqual(m['baseElevationMeters'], -20)
        self.assertTrue(all(x == 0 for x in self.samples()))
    def test_center_origin(self):
        self.source.write_text(self.source.read_text().replace('xllcorner', 'xllcenter').replace('yllcorner', 'yllcenter'))
        m = self.run_conversion()
        self.assertEqual((m['originEastingMeters'], m['originNorthingMeters']), (100, 200))
    def test_incomplete_grid(self):
        self.source.write_text(self.source.read_text().replace('0 10 20', '0 10'))
        with self.assertRaises(ValueError): self.run_conversion()
    def test_nonfinite_rejected(self):
        self.source.write_text(self.source.read_text().replace('0 10 20', '0 nan 20'))
        with self.assertRaises(ValueError): self.run_conversion()

if __name__ == '__main__': unittest.main()
