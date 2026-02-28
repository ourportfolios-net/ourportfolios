"""
Heatmap state — squarified nested treemap.

Layout:
  - Top MAX_TREEMAP_INDUSTRIES by market cap → industry tiles (3 per row).
  - All remaining industries → HeatmapChip pills shown below the treemap.
  - Row height ∝ cap^0.40.  Within-row tile width ∝ sqrt(cap).
  - _CTR_W / _CTR_H must match the pixel constants in market_overview.py.

Ticker subtiles:
  - Each tile reserves LABEL_H_PX at the top for the industry name pill.
  - Subtiles fill the space below; y-coordinates are offset accordingly.
  - Best-N: largest N ≤ _MAX_N where every subtile min(w,h) ≥ _MIN_PX.

Colours (all pre-computed; UI layer has zero conditionals):
  - Dark muted green / dark maroon / near-transparent gray.
  - Opacity encodes magnitude (0.14 → 0.60).
  - HeatmapTile stores `bg` so the UI can set the industry tile background
    to match its direction/magnitude (no black canvas).
"""

import re
import reflex as rx
from pydantic import BaseModel
from sqlalchemy import text

from ..utils.database.database import get_company_session
from ..styles import white, green, red

# ── Constants ───────────────────────────────────────────────────────────────────

_PERIOD_TABLE = {
    "1D": "daily_changes",
    "1W": "weekly_changes",
    "1M": "monthly_changes",
    "1Y": "yearly_changes",
}

MAX_TREEMAP_INDUSTRIES = 9  # top N → tiles; rest → chips
ITEMS_PER_ROW = 3  # tiles per row
_CTR_W = 760.0  # must match market_overview._TREEMAP_W_PX
_CTR_H = 540.0  # must match market_overview._TREEMAP_H
LABEL_H_PX = 26.0  # px reserved at tile top for the industry pill
_MIN_PX = 46.0  # minimum subtile dimension
_MAX_N = 5  # hard cap on tickers per industry tile
_MIN_TILE_H_PX = 80.0  # rows shorter than this overflow to chips

# ── Colour ─────────────────────────────────────────────────────────────────────

_GREEN_BASE = "rgba(22, 52, 38, 1)"  # dark forest green
_RED_BASE = "rgba(52, 19, 22, 1)"  # dark maroon
_DARK_BG = "rgba(10, 10, 14, 1)"  # base for color-mix blending


def _direction(pct: float) -> str:
    if pct > 0.30:
        return "up"
    if pct < -0.30:
        return "down"
    return "neutral"


def _opacity(pct: float) -> float:
    a = abs(pct)
    if a >= 5.0:
        return 0.60
    if a >= 3.0:
        return 0.48
    if a >= 1.5:
        return 0.36
    if a >= 0.5:
        return 0.24
    return 0.14


def _bg(direction: str, opacity: float) -> str:
    pct = round(opacity * 100)
    if direction == "up":
        return f"color-mix(in srgb, {_GREEN_BASE} {pct}%, {_DARK_BG})"
    if direction == "down":
        return f"color-mix(in srgb, {_RED_BASE} {pct}%, {_DARK_BG})"
    return white(0.03)


# Industry-level bg uses a fixed, lighter opacity so the tile background
# is subtler than the individual ticker subtiles placed on top.
_IND_OPACITY = 0.18


def _ind_bg(direction: str) -> str:
    """Muted background for the whole industry tile (behind ticker subtiles)."""
    return _bg(direction, _IND_OPACITY)


def _border_color(direction: str) -> str:
    if direction == "up":
        return green(0.22)
    if direction == "down":
        return red(0.22)
    return white(0.06)


def _pct_color(direction: str) -> str:
    if direction == "up":
        return green(0.80)
    if direction == "down":
        return red(0.80)
    return white(0.28)


def _slugify(name: str) -> str:
    s = re.sub(r"[&/]", " ", name.lower())
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", s.strip()))


# ── Squarify ───────────────────────────────────────────────────────────────────


def _worst(row: list, s: float) -> float:
    if not row or s == 0:
        return float("inf")
    rs = sum(row)
    return max(
        max(s * s * r / (rs * rs) for r in row),
        max(rs * rs / (s * s * r) for r in row),
    )


def _sq(sizes, x, y, w, h, out):
    if not sizes:
        return
    if len(sizes) == 1:
        out.append((x, y, w, h))
        return
    s = min(w, h)
    row, best, bi = [], float("inf"), 0
    for v in sizes:
        row.append(v)
        sc = _worst(row, s)
        if sc <= best:
            best, bi = sc, len(row) - 1
        else:
            break
    comm = sizes[: bi + 1]
    rest = sizes[bi + 1 :]
    rs = sum(comm)
    if w >= h:
        rh, rx0 = rs / w, x
        for v in comm:
            out.append((rx0, y, v / rs * w, rh))
            rx0 += v / rs * w
        _sq(rest, x, y + rh, w, h - rh, out)
    else:
        cw, ry = rs / h, y
        for v in comm:
            out.append((x, ry, cw, v / rs * h))
            ry += v / rs * h
        _sq(rest, x + cw, y, w - cw, h, out)


def _squarify(weights: list, W: float, H: float) -> list:
    if not weights:
        return []
    total = sum(weights)
    if total == 0:
        return []
    out: list = []
    _sq([v / total * W * H for v in weights], 0.0, 0.0, W, H, out)
    return out


def _best_n(caps: list, W: float, H: float) -> int:
    """Largest N ≤ _MAX_N where every subtile has min(w,h) ≥ _MIN_PX."""
    avail_H = max(H - LABEL_H_PX, 1.0)
    weights = [max(c, 1.0) ** 0.5 for c in caps]
    for n in range(min(len(caps), _MAX_N), 0, -1):
        rects = _squarify(weights[:n], W, avail_H)
        if rects and all(min(rw, rh) >= _MIN_PX for _, _, rw, rh in rects):
            return n
    return 1


def _size_hint(min_dim: float) -> str:
    if min_dim > 100:
        return "xl"
    if min_dim > 70:
        return "large"
    if min_dim > 50:
        return "medium"
    return "small"


# ── Data models ────────────────────────────────────────────────────────────────


class TickerSubtile(BaseModel):
    symbol: str = ""
    pct_label: str = ""
    bg: str = _DARK_BG
    pct_color: str = "rgba(255,255,255,0.28)"
    url: str = ""
    x: float = 0.0
    y: float = 0.0  # % from tile top — already offset below the label
    w: float = 100.0
    h: float = 100.0
    size: str = "small"


class HeatmapTile(BaseModel):
    name: str = ""
    pct_label: str = ""
    bg: str = "rgba(255,255,255,0.03)"  # industry tile bg
    border: str = "rgba(255,255,255,0.06)"
    pct_color: str = "rgba(255,255,255,0.28)"
    url: str = ""
    tickers: list[TickerSubtile] = []
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0


class HeatmapChip(BaseModel):
    name: str = ""
    pct_label: str = ""
    bg: str = "rgba(255,255,255,0.03)"
    border: str = "rgba(255,255,255,0.06)"
    pct_color: str = "rgba(255,255,255,0.28)"
    url: str = ""


# ── Build ───────────────────────────────────────────────────────────────────────


def _build(industry_rows, ticker_rows):
    raw: dict[str, list] = {}
    for row in ticker_rows:
        raw.setdefault(str(row[0]), []).append(
            (str(row[1]), float(row[2] or 0.0), float(row[3] or 0.0))
        )

    ind_cap = {ind: sum(max(c, 1.0) for _, _, c in ticks) for ind, ticks in raw.items()}

    sorted_inds = sorted(
        industry_rows,
        key=lambda r: ind_cap.get(str(r[0]), 0.0),
        reverse=True,
    )

    treemap_inds = sorted_inds[:MAX_TREEMAP_INDUSTRIES]
    chip_inds = sorted_inds[MAX_TREEMAP_INDUSTRIES:]

    chips: list[HeatmapChip] = []
    for ind_row in chip_inds:
        name = str(ind_row[0])
        avg_pct = float(ind_row[1] or 0.0)
        d, op = _direction(avg_pct), _opacity(avg_pct)
        sign = "+" if avg_pct >= 0 else ""
        chips.append(
            HeatmapChip(
                name=name,
                pct_label=f"{sign}{avg_pct:.2f}%",
                bg=_bg(d, op),
                border=_border_color(d),
                pct_color=_pct_color(d),
                url=f"/industries/{_slugify(name)}",
            )
        )

    rows = [
        treemap_inds[i : i + ITEMS_PER_ROW]
        for i in range(0, len(treemap_inds), ITEMS_PER_ROW)
    ]
    row_ws = [
        sum(max(ind_cap.get(str(r[0]), 1.0), 1.0) ** 0.40 for r in row) for row in rows
    ]
    grand = max(sum(row_ws), 1.0)

    tiles: list[HeatmapTile] = []
    y_pct_accum = 0.0

    for row, rw in zip(rows, row_ws):
        h_pct = rw / grand * 100.0
        tile_h_px = h_pct / 100.0 * _CTR_H

        if tile_h_px < _MIN_TILE_H_PX:
            for ind_row in row:
                name = str(ind_row[0])
                avg_pct = float(ind_row[1] or 0.0)
                d, op = _direction(avg_pct), _opacity(avg_pct)
                sign = "+" if avg_pct >= 0 else ""
                chips.insert(
                    0,
                    HeatmapChip(
                        name=name,
                        pct_label=f"{sign}{avg_pct:.2f}%",
                        bg=_bg(d, op),
                        border=_border_color(d),
                        pct_color=_pct_color(d),
                        url=f"/industries/{_slugify(name)}",
                    ),
                )
            continue

        row_sqrt = sum(max(ind_cap.get(str(r[0]), 1.0), 1.0) ** 0.5 for r in row)
        x_pct = 0.0

        for ind_row in row:
            name = str(ind_row[0])
            avg_pct = float(ind_row[1] or 0.0)
            cap_total = max(ind_cap.get(name, 1.0), 1.0)
            w_pct = cap_total**0.5 / row_sqrt * 100.0
            tile_w_px = w_pct / 100.0 * _CTR_W
            d = _direction(avg_pct)
            sign = "+" if avg_pct >= 0 else ""

            items = raw.get(name, [])
            subtiles: list[TickerSubtile] = []

            if items:
                caps = [max(c, 1.0) for _, _, c in items]
                n = _best_n(caps, tile_w_px, tile_h_px)
                top = items[:n]
                avail_H = tile_h_px - LABEL_H_PX

                rects = _squarify([c**0.5 for _, _, c in top], tile_w_px, avail_H)

                label_pct = LABEL_H_PX / tile_h_px * 100.0
                ticker_zone = 100.0 - label_pct

                for (sym, t_pct, _), (ix, iy, iw, ih) in zip(top, rects):
                    t_d, t_op = _direction(t_pct), _opacity(t_pct)
                    t_sign = "+" if t_pct >= 0 else ""
                    y_in_tile = label_pct + (iy / avail_H * ticker_zone)
                    h_in_tile = ih / avail_H * ticker_zone
                    subtiles.append(
                        TickerSubtile(
                            symbol=sym,
                            pct_label=f"{t_sign}{t_pct:.2f}%",
                            bg=_bg(t_d, t_op),
                            pct_color=_pct_color(t_d),
                            url=f"/tickers/{sym.lower()}",
                            x=round(ix / tile_w_px * 100.0, 5),
                            y=round(y_in_tile, 5),
                            w=round(iw / tile_w_px * 100.0, 5),
                            h=round(h_in_tile, 5),
                            size=_size_hint(min(iw, ih)),
                        )
                    )

            tiles.append(
                HeatmapTile(
                    name=name,
                    pct_label=f"{sign}{avg_pct:.2f}%",
                    bg=_ind_bg(d),  # muted industry background colour
                    border=_border_color(d),
                    pct_color=_pct_color(d),
                    url=f"/industries/{_slugify(name)}",
                    tickers=subtiles,
                    x=round(x_pct, 5),
                    y=round(y_pct_accum, 5),
                    w=round(w_pct, 5),
                    h=round(h_pct, 5),
                )
            )
            x_pct += w_pct

        y_pct_accum += h_pct

    return tiles, chips


# ── State ──────────────────────────────────────────────────────────────────────


class HeatmapState(rx.State):
    selected_period: str = "1D"
    tiles: list[HeatmapTile] = []
    chips: list[HeatmapChip] = []
    loading: bool = False

    @rx.event(background=True)
    async def load_heatmap_data(self):
        async with self:
            self.loading = True
        await self._fetch(self.selected_period)
        async with self:
            self.loading = False

    @rx.event(background=True)
    async def set_period(self, period: str):
        async with self:
            self.selected_period = period
            self.loading = True
        await self._fetch(period)
        async with self:
            self.loading = False

    async def _fetch(self, period: str):
        table = _PERIOD_TABLE.get(period, "daily_changes")
        try:
            async with get_company_session() as session:
                ind_res = await session.execute(
                    text(f"""
                    SELECT industry, AVG(pct_change), COUNT(*)
                    FROM market.{table}
                    WHERE industry IS NOT NULL AND industry != ''
                    GROUP BY industry
                """)
                )
                tick_res = await session.execute(
                    text(f"""
                    SELECT industry, symbol, pct_change, market_cap
                    FROM market.{table}
                    WHERE industry IS NOT NULL AND industry != ''
                          AND market_cap IS NOT NULL AND market_cap > 0
                    ORDER BY industry, market_cap DESC
                """)
                )
            tiles, chips = _build(ind_res.fetchall(), tick_res.fetchall())
            async with self:
                self.tiles = tiles
                self.chips = chips
        except BaseException as exc:
            print(f"[HeatmapState] {exc}")
            async with self:
                self.tiles = []
                self.chips = []
