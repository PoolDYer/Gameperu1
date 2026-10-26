import hashlib
import json
from pathlib import Path
import struct
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'Assets/Resources/MachuPicchu'

class PrototypeGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((DATA/'prototype-layout.json').read_text())
        cls.raw=(DATA/'prototype-heightmap.bytes').read_bytes()
        cls.heights=struct.unpack('<'+'H'*(cls.m['resolution']**2),cls.raw)
    def test_extent_and_count(self):
        self.assertEqual((self.m['widthMeters'],self.m['lengthMeters']),(200,530))
        self.assertEqual(len(self.m['buildings']),172)
        self.assertEqual(len(set(b['id'] for b in self.m['buildings'])),172)
    def test_integrity_and_altitude(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.m['rawSha256'])
        average=sum(self.heights)/len(self.heights)/65535*self.m['heightMeters']+self.m['baseElevationMeters']
        self.assertAlmostEqual(average,2430,places=3)
    def test_buildings_within_footprint(self):
        for b in self.m['buildings']:
            self.assertGreater(b['x']-b['width']/2,0)
            self.assertLess(b['x']+b['width']/2,200)
            self.assertGreater(b['z']-b['depth']/2,0)
            self.assertLess(b['z']+b['depth']/2,530)
    def test_spawn_ground_clearance(self):
        p=self.m['spawn']; n=self.m['resolution']
        ground=self.heights[round(p['z']/530*(n-1))*n+round(p['x']/200*(n-1))]/65535*self.m['heightMeters']
        self.assertGreater(p['y']-ground,.15)
        self.assertLess(p['y']-ground,.25)
        for b in self.m['buildings']:
            self.assertFalse(abs(p['x']-b['x'])<b['width']/2+1 and abs(p['z']-b['z'])<b['depth']/2+1)
    def test_provenance_and_artifacts(self):
        self.assertEqual(self.m['kind'],'INTERPRETIVE_PROTOTYPE_NOT_SURVEYED')
        self.assertTrue((DATA/'Architecture_Interpretive.fbx').stat().st_size>1000)
        report=json.loads((ROOT/'Artifacts/geometry-validation.json').read_text())
        self.assertEqual(report['buildingCount'],172)
        self.assertEqual((report['terrainWidth'],report['terrainLength']),(200,530))
    def test_building_footprints_do_not_overlap(self):
        for i,a in enumerate(self.m['buildings']):
            for b in self.m['buildings'][i+1:]:
                overlap=(abs(a['x']-b['x']) < (a['width']+b['width'])/2+.55 and
                         abs(a['z']-b['z']) < (a['depth']+b['depth'])/2+.55)
                self.assertFalse(overlap,(a['id'],b['id']))

if __name__=='__main__': unittest.main()
