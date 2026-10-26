"""Deterministic interpretive terrain. Not measured topography or surveyed architecture."""
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Assets/Resources/MachuPicchu'
N = 513
WIDTH, LENGTH, RELIEF = 200., 530., 100.
SEED = 2430


def generate():
    rng = random.Random(SEED)
    xx, zz = np.meshgrid(np.linspace(0, WIDTH, N), np.linspace(0, LENGTH, N))
    centre = 100 + 5 * np.sin(zz / 125)
    distance = np.abs(xx - centre)
    # A gently inclined central spine with agricultural terraces on either flank.
    spine = 42 + 0.055 * (zz - 265) + 2 * np.sin(zz / 85)
    terrace_drop = np.maximum(0, np.floor((distance - 38) / 7)) * 2.15
    edge_drop = np.maximum(0, distance - 87) * .65
    heights = spine - terrace_drop - edge_drop
    heights += .13 * np.sin(xx * .6) * np.sin(zz * .38) * (distance > 40)
    # Recess the five transverse staircase corridors before flattening building pads.
    for crossing in (88, 180, 265, 350, 440):
        for side in (-1, 1):
            inner = 100 + 5 * math.sin(crossing / 125) + side * 39
            outer = 100 + 5 * math.sin(crossing / 125) + side * 88
            j = round(crossing / LENGTH * (N - 1))
            y0 = heights[j, round(inner / WIDTH * (N - 1))]
            y1 = heights[j, round(outer / WIDTH * (N - 1))]
            progress = (xx - inner) / (outer - inner)
            mask = (np.abs(zz - crossing) < 1.7) & (progress >= 0) & (progress <= 1)
            heights[mask] = (y0 + (y1-y0) * progress - .2)[mask]
    buildings = []
    # Four interpretive clusters. The quantity is a user target, NOT a surveyed catalogue.
    for column, count in enumerate((43, 43, 43, 43)):
        base_x = (57, 77, 127, 148)[column]
        for row in range(count):
            z = 26 + row * 11.25 + rng.uniform(-.55, .55)
            x = base_x + 2 * math.sin(z / 67) + rng.uniform(-.7, .7)
            w, d = rng.uniform(8.5, 11), rng.uniform(6.2, 8.2)
            # Interior clusters leave a broad central plaza without reducing the count.
            if 220 < z < 292 and column in (1, 2):
                x += -7 if column == 1 else 7
            ix, iz = round(x / WIDTH * (N-1)), round(z / LENGTH * (N-1))
            base = float(heights[iz, ix])
            dx = np.maximum(np.abs(xx-x)-w/2-.65, 0)
            dz = np.maximum(np.abs(zz-z)-d/2-.65, 0)
            blend = np.clip(1-np.maximum(dx, dz)/1.15, 0, 1)
            heights = heights * (1-blend) + base * blend
            buildings.append(dict(id=f'Recinto_interpretativo_{len(buildings)+1:03}', x=x, z=z,
                                  y=base, width=w, depth=d, wallHeight=rng.uniform(2.3, 3.7),
                                  wallThickness=.55, doorWidth=1.45, column=column))
    # Align mean terrain elevation with the user's 2430 m reference, not a vertical survey.
    adjustment = 40 - float(heights.mean())
    heights += adjustment
    for b in buildings: b['y'] += adjustment
    assert heights.min() >= 0 and heights.max() <= RELIEF
    quantized = np.rint(heights/RELIEF*65535).astype('<u2')
    raw = quantized.tobytes()
    def sample(x,z):
        return float(heights[round(z/LENGTH*(N-1)), round(x/WIDTH*(N-1))])
    manifest = dict(schemaVersion=1, kind='INTERPRETIVE_PROTOTYPE_NOT_SURVEYED', seed=SEED,
                    widthMeters=WIDTH, lengthMeters=LENGTH, heightMeters=RELIEF, resolution=N,
                    referenceMeanElevationMeters=2430, baseElevationMeters=2390,
                    rawSha256=hashlib.sha256(raw).hexdigest(),
                    source='User-provided approximate 530 x 200 m extent and 2430 m mean altitude; no DEM',
                    horizontalOrientation='local X/Z; geographic azimuth unknown',
                    buildings=buildings, spawn=dict(x=102., y=sample(102,265)+.2, z=265.),
                    meanElevationMeters=float(heights.mean()+2390),
                    minimumElevationMeters=float(heights.min()+2390), maximumElevationMeters=float(heights.max()+2390),
                    tower=dict(x=103., z=356., y=sample(103,356), radius=5.8),
                    referencePeaks=[dict(name='Machu Picchu', elevationMeters=3082),
                                    dict(name='Huayna Picchu', elevationMeters=2693),
                                    dict(name='Huchuy Picchu', elevationMeters=2497)],
                    limitations=['Building footprints, positions, heights, terraces and terrain are invented approximations.',
                                 'Peak elevations are metadata only; no unverified mountain positions are generated.',
                                 'The 172 objects are an interpretive count, not documented identities or surveyed footprints.'])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'prototype-heightmap.bytes').write_bytes(raw)
    (OUT/'prototype-layout.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('widthMeters','lengthMeters','meanElevationMeters','minimumElevationMeters','maximumElevationMeters','rawSha256')},indent=2))
    return manifest, heights

if __name__ == '__main__': generate()
