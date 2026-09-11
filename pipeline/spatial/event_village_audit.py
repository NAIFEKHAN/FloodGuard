"""Exact-code, WGS84 point-in-polygon feasibility audit; never a modelling join."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
from shapely.geometry import MultiPolygon, Point, Polygon


NILGIRIS = {"the nilgiris", "nilgiris"}
AUDIT_COLUMNS = ("inventory_serial", "slide_no", "latitude", "longitude", "reported_history_date", "spatial_match_status", "matched_village_lgd_code", "source_pdf_page")


@dataclass(frozen=True)
class SpatialRecord:
    attributes: dict[str, str]
    geometry: MultiPolygon | Polygon | None
    polygon_parts: int


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _coordinates(text: str | None) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for item in (text or "").split():
        values = item.split(",")
        if len(values) < 2:
            continue
        points.append((float(values[0]), float(values[1])))
    return points


def _placemark(element: ET.Element) -> SpatialRecord:
    attributes: dict[str, str] = {}
    for node in element.iter():
        if _local(node.tag) == "Data" and node.get("name"):
            value = next((child.text for child in node if _local(child.tag) == "value"), "")
            attributes[node.get("name", "").strip()] = (value or "").strip()
    polygons: list[Polygon] = []
    for polygon_node in (node for node in element.iter() if _local(node.tag) == "Polygon"):
        outer = next((child for child in polygon_node.iter() if _local(child.tag) == "outerBoundaryIs"), None)
        shell_node = next((child for child in outer.iter() if _local(child.tag) == "coordinates"), None) if outer is not None else None
        shell = _coordinates(shell_node.text if shell_node is not None else None)
        holes: list[list[tuple[float, float]]] = []
        for inner in (child for child in polygon_node if _local(child.tag) == "innerBoundaryIs"):
            coordinate_node = next((child for child in inner.iter() if _local(child.tag) == "coordinates"), None)
            ring = _coordinates(coordinate_node.text if coordinate_node is not None else None)
            if len(ring) >= 4:
                holes.append(ring)
        if len(shell) >= 4:
            polygons.append(Polygon(shell, holes))
    if not polygons:
        geometry = None
    elif len(polygons) == 1:
        geometry = polygons[0]
    else:
        geometry = MultiPolygon(polygons)
    return SpatialRecord(attributes=attributes, geometry=geometry, polygon_parts=len(polygons))


def read_nilgiris_kmz(path: Path) -> list[SpatialRecord]:
    """Read only Nilgiris KML features, retaining exact raw attribute values."""
    records: list[SpatialRecord] = []
    with zipfile.ZipFile(path) as archive:
        member = next(name for name in archive.namelist() if name.casefold().endswith(".kml"))
        with archive.open(member) as stream:
            for _, element in ET.iterparse(stream, events=("end",)):
                if _local(element.tag) != "Placemark":
                    continue
                record = _placemark(element)
                if record.attributes.get("district", "").strip().casefold() in NILGIRIS:
                    records.append(record)
                element.clear()
    return records


def exact_code_records(records: list[SpatialRecord], villages: pd.DataFrame) -> list[SpatialRecord]:
    """Retain only unambiguous exact VL-code / LGD-code and district/taluk matches."""
    village_codes = villages.set_index("village_lgd_code")
    matched: list[SpatialRecord] = []
    for record in records:
        code = record.attributes.get("vlcode", "")
        if code not in village_codes.index:
            continue
        village = village_codes.loc[code]
        if record.attributes.get("dtcode", "") == str(village["district_lgd_code"]) and record.attributes.get("sdcode", "") == str(village["taluk_lgd_code"]):
            matched.append(record)
    return matched


def link_events(events: pd.DataFrame, exact_records: list[SpatialRecord]) -> pd.DataFrame:
    """Classify every input event strictly by exact-code polygon containment.

    A boundary touch or more than one containing polygon is explicitly ambiguous.
    No nearest feature, buffer, or non-exact feature participates.
    """
    usable = [(record.attributes["vlcode"], record.geometry) for record in exact_records if record.geometry is not None and record.geometry.is_valid]
    output: list[dict[str, object]] = []
    for _, event in events.iterrows():
        point = Point(float(event["longitude"]), float(event["latitude"]))
        contains = [code for code, geometry in usable if geometry.contains(point)]
        touches = [code for code, geometry in usable if geometry.touches(point)]
        if len(contains) == 1 and not touches:
            match_status, code = "EXACT_POLYGON_MATCH", contains[0]
        elif len(contains) > 1 or touches:
            match_status, code = "AMBIGUOUS_GEOMETRY", ""
        else:
            match_status, code = "NO_EXACT_POLYGON_MATCH", ""
        row = {column: event[column] for column in AUDIT_COLUMNS if column in event.index}
        row.update(spatial_match_status=match_status, matched_village_lgd_code=code)
        output.append(row)
    return pd.DataFrame(output, columns=AUDIT_COLUMNS)


def geometry_summary(records: list[SpatialRecord]) -> dict[str, int]:
    geometries = [record.geometry for record in records]
    return {
        "records": len(records), "valid": sum(geometry is not None and geometry.is_valid for geometry in geometries),
        "invalid": sum(geometry is None or not geometry.is_valid for geometry in geometries),
        "multipart": sum(record.polygon_parts > 1 for record in records),
        "polygon_parts": sum(record.polygon_parts for record in records),
    }


def overlap_pairs(records: list[SpatialRecord]) -> list[tuple[str, str]]:
    """Report only positive-area overlaps; shared borders are not overlaps."""
    pairs: list[tuple[str, str]] = []
    valid = [record for record in records if record.geometry is not None and record.geometry.is_valid]
    for index, left in enumerate(valid):
        for right in valid[index + 1:]:
            if left.geometry.intersects(right.geometry) and left.geometry.intersection(right.geometry).area > 0:
                pairs.append((left.attributes.get("vlcode", ""), right.attributes.get("vlcode", "")))
    return pairs
