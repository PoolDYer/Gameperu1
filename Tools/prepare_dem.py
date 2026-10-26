"""Convert a projected, metre-based ESRI ASCII grid to a Unity heightfield.
No third-party dependencies. Does not fill gaps or invent elevations.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def read_grid(path):
    header = {}
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    keys = {"ncols", "nrows", "xllcorner", "yllcorner", "xllcenter", "yllcenter", "cellsize", "nodata_value"}
    first_data = 0
    for index, line in enumerate(lines):
        parts = line.split()
        if not parts:
            continue
        if parts[0].lower() not in keys:
            first_data = index
            break
        if len(parts) != 2 or parts[0].lower() in header:
            raise ValueError("Invalid or duplicate ASCII grid header")
        header[parts[0].lower()] = float(parts[1])
    else:
        raise ValueError("Grid has no samples")
    for key in ("ncols", "nrows", "cellsize"):
        if key not in header or not math.isfinite(header[key]):
            raise ValueError("Missing/invalid " + key)
    nx, ny = int(header["ncols"]), int(header["nrows"])
    if nx != header["ncols"] or ny != header["nrows"] or min(nx, ny) < 2 or header["cellsize"] <= 0:
        raise ValueError("Grid dimensions or cell size invalid")
    for axis in ("x", "y"):
        if sum(axis + "ll" + suffix in header for suffix in ("corner", "center")) != 1:
            raise ValueError("Specify one origin convention per axis")
    values = [float(v) for line in lines[first_data:] for v in line.split()]
    if len(values) != nx * ny:
        raise ValueError("Grid sample count mismatch")
    nodata = header.get("nodata_value")
    if any(not math.isfinite(v) or v == nodata for v in values):
        raise ValueError("NoData/non-finite elevations: obtain valid data; gaps are not filled")
    # ASCII rows run north to south; Unity Z increases northward.
    rows = [values[i * nx:(i + 1) * nx] for i in range(ny)][::-1]
    return header, rows


def convert(source, output, resolution, crs, vertical_datum, attribution):
    if resolution < 33 or resolution > 4097 or (resolution - 1) & (resolution - 2):
        raise ValueError("Unity resolution must be 2^n + 1, from 33 to 4097")
    if not crs.strip() or not vertical_datum.strip() or not attribution.strip():
        raise ValueError("CRS, vertical datum and source attribution are required")
    header, rows = read_grid(source)
    nx, ny = len(rows[0]), len(rows)
    cell = header["cellsize"]
    low, high = min(map(min, rows)), max(map(max, rows))
    height = max(high - low, 1.0)
    # Terrain covers sample centres; the outer half-cell margins are not invented.
    origin = [header.get(axis + "llcenter", header.get(axis + "llcorner", 0) + cell / 2) for axis in ("x", "y")]
    if any(not math.isfinite(v) for v in origin):
        raise ValueError("Invalid georeference")
    raw = bytearray()
    for z in range(resolution):
        y = z * (ny - 1) / (resolution - 1)
        j = min(int(y), ny - 2)
        fy = y - j
        for x in range(resolution):
            u = x * (nx - 1) / (resolution - 1)
            i = min(int(u), nx - 2)
            fx = u - i
            v = (1 - fy) * ((1 - fx) * rows[j][i] + fx * rows[j][i + 1]) + fy * ((1 - fx) * rows[j + 1][i] + fx * rows[j + 1][i + 1])
            raw.extend(struct.pack('<H', round((v - low) / height * 65535)))
    destination = Path(output)
    if destination.exists():
        raise FileExistsError("Choose a new output directory; existing data is preserved")
    destination.mkdir(parents=True)
    metadata = dict(schemaVersion=1, resolution=resolution, widthMeters=(nx - 1) * cell,
                    lengthMeters=(ny - 1) * cell, heightMeters=height, baseElevationMeters=low,
                    originEastingMeters=origin[0], originNorthingMeters=origin[1], crs=crs,
                    verticalDatum=vertical_datum, source=attribution, sourceCellSizeMeters=cell,
                    sourceSha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                    rawSha256=hashlib.sha256(raw).hexdigest(), rawFile="heightmap.r16",
                    sampleOrder="south-to-north, west-to-east", byteOrder="little-endian",
                    coverage="outer sample centres; excludes half-cell outer margins",
                    maxQuantizationErrorMeters=height / 65535 / 2)
    (destination / 'heightmap.r16').write_bytes(raw)
    (destination / 'terrain.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    return metadata


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('output')
    p.add_argument('--resolution', type=int, default=1025)
    p.add_argument('--crs', required=True, help='Projected CRS in metres, verified from source metadata')
    p.add_argument('--vertical-datum', required=True)
    p.add_argument('--source-credit', required=True)
    p.add_argument('--confirm-meters', action='store_true', required=True,
                   help='Confirm horizontal coordinates and elevations are in metres, not lat/lon degrees')
    a = p.parse_args()
    print(json.dumps(convert(a.source, a.output, a.resolution, a.crs, a.vertical_datum, a.source_credit), indent=2))
