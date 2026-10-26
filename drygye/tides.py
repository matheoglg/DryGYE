"""Parse the INOCAR Guayaquil tide table and interpolate its predictions."""
import csv
import math
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from drygye.config import TIDE_PEAK_MIN_M, TIMEZONE, TIDES_CSV_PATH

MONTHS = (10, 10, 11, 11, 12, 12)
HOUR_X = (77.1, 161.4, 245.6, 329.9, 414.1, 498.4)
LOCAL_TZ = ZoneInfo(TIMEZONE)


def parse_tide_pdf(pdf_path, out_csv):
    """Read the six aligned month blocks and write local-time tide events."""
    import pdfplumber

    events = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            for column, center in enumerate(HOUR_X):
                groups = {}
                left, right = center - 38, center + 38
                for word in words:
                    x, y, token = word["x0"], word["top"], word["text"]
                    if left <= x <= right:
                        groups.setdefault(round(y, 1), []).append((x, token))
                day = None
                for y in sorted(groups):
                    row = groups[y]
                    day_tokens = [int(t) for x, t in row if x < center - 10 and re.fullmatch(r"\d{1,2}", t) and 1 <= int(t) <= 31]
                    if day_tokens:
                        day = day_tokens[0]
                    times = [t for x, t in row if center - 10 <= x < center + 18 and re.fullmatch(r"\d{4}", t)]
                    heights = [t for x, t in row if x >= center + 18 and re.fullmatch(r"\d\.\d{2}", t)]
                    if day is None or not times or not heights:
                        continue
                    hour, minute = int(times[0][:2]), int(times[0][2:])
                    if hour > 23 or minute > 59:
                        continue
                    dt = datetime(2026, MONTHS[column], day, hour, minute, tzinfo=LOCAL_TZ)
                    height = float(heights[0])
                    events.append({"datetime": dt.isoformat(), "height_m": height,
                                   "kind": "high" if height >= TIDE_PEAK_MIN_M else "low"})
    unique = {event["datetime"]: event for event in events}
    events = sorted(unique.values(), key=lambda event: event["datetime"])
    if len(events) < 200:
        raise ValueError(f"Parsed only {len(events)} tide events; refusing to write an incomplete table.")
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("datetime", "height_m", "kind"))
        writer.writeheader()
        writer.writerows(events)
    return events


def load_tides(path=TIDES_CSV_PATH):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        events = list(csv.DictReader(stream))
    return [(datetime.fromisoformat(row["datetime"]), float(row["height_m"])) for row in events]


def tide_height_at(ts, path=TIDES_CSV_PATH):
    """Cosine-interpolate between neighboring predicted high/low events."""
    if not TIDES_CSV_PATH.exists() and Path(path) == TIDES_CSV_PATH:
        from drygye.config import TIDE_PDF_PATH
        parse_tide_pdf(TIDE_PDF_PATH, TIDES_CSV_PATH)
    when = datetime.fromisoformat(ts) if isinstance(ts, str) else ts
    if when.tzinfo is None:
        when = when.replace(tzinfo=LOCAL_TZ)
    events = load_tides(path)
    for (t0, h0), (t1, h1) in zip(events, events[1:]):
        if t0 <= when <= t1:
            fraction = (when - t0).total_seconds() / (t1 - t0).total_seconds()
            return h0 + (h1 - h0) * (1 - math.cos(math.pi * fraction)) / 2
    if events and when == events[-1][0]:
        return events[-1][1]
    raise ValueError("Timestamp falls outside the INOCAR tide table (October–December 2026).")


def is_high_tide(ts):
    from drygye.config import TIDE_HIGH_M
    return tide_height_at(ts) >= TIDE_HIGH_M
