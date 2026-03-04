"""
Heatmap state — squarified nested treemap.

Subtile layout:
- Squarify with market-cap-proportional weights (cap^0.5).
- Weights are clamped so max/min ratio ≤ 3.0 — prevents extreme strips
  while keeping clear visual hierarchy between large and small caps.
- _MAX_N = 4 — show at most 4 tickers per industry tile to keep tiles readable.
- _best_n: tries N=4 down to N=1, picks the largest N where all rects
  have min(w,h) >= _MIN_PX.
"""

from urllib.parse import quote
import reflex as rx
from pydantic import BaseModel
from sqlalchemy import text

from ..utils.database.database import get_company_session

_PERIOD_TABLE = {
    "1D": "daily_changes",
    "1W": "weekly_changes",
    "1M": "monthly_changes",
    "1Y": "yearly_changes",
}

MAX_TREEMAP_INDUSTRIES = 9
ITEMS_PER_ROW = 3
_CTR_W = 760.0
_CTR_H = 620.0
LABEL_H_PX = 30.0
_MIN_PX = 52.0  # min(w,h) for a subtile — keeps tiles readable
_MAX_N = 4  # max tickers shown per industry tile
_MIN_TILE_H_PX = 80.0
_MAX_WEIGHT_RATIO = 3.0  # largest weight can be at most 3× the smallest

_DARK_BG = "rgba(10, 10, 12, 1)"
_GREEN_TINT = "rgba(16, 185, 129, 1)"
_RED_TINT = "rgba(239, 68, 68, 1)"


def _direction(pct: float) -> str:
    if pct > 0:
        return "up"
    if pct < 0:
        return "down"
    return "neutral"


def _tint_opacity(pct: float) -> float:
    a = abs(pct)
    if a >= 5.0:
        return 0.18
    if a >= 3.0:
        return 0.13
    if a >= 1.5:
        return 0.09
    if a >= 0.5:
        return 0.06
    return 0.04


def _bg(direction: str, tint_op: float) -> str:
    pct = min(round(tint_op * 100 * 3), 40)
    if direction == "up":
        return f"color-mix(in srgb, {_GREEN_TINT} {pct}%, {_DARK_BG})"
    if direction == "down":
        return f"color-mix(in srgb, {_RED_TINT} {pct}%, {_DARK_BG})"
    return _DARK_BG


def _ind_bg(direction: str) -> str:
    if direction == "up":
        return f"color-mix(in srgb, {_GREEN_TINT} 8%, {_DARK_BG})"
    if direction == "down":
        return f"color-mix(in srgb, {_RED_TINT} 8%, {_DARK_BG})"
    return _DARK_BG


def _pct_color_scheme(direction: str) -> str:
    if direction == "up":
        return "green"
    if direction == "down":
        return "red"
    return "gray"


def _url_industry(name: str) -> str:
    return f"/industries/{quote(name, safe='')}"


def _url_ticker(symbol: str) -> str:
    return f"/tickers/{symbol.upper()}"


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


def _capped_weights(caps: list) -> list:
    """
    cap^0.5 weights, then clamp so max/min <= _MAX_WEIGHT_RATIO.
    Preserves ordering and relative size signal while preventing extreme strips.
    """
    raw = [max(c, 1.0) ** 0.5 for c in caps]
    mn = min(raw)
    ceiling = mn * _MAX_WEIGHT_RATIO
    return [min(w, ceiling) for w in raw]


def _best_n(caps: list, W: float, H: float) -> int:
    avail_H = max(H - LABEL_H_PX, 1.0)
    for n in range(min(len(caps), _MAX_N), 0, -1):
        weights = _capped_weights(caps[:n])
        rects = _squarify(weights, W, avail_H)
        if rects and all(min(rw, rh) >= _MIN_PX for _, _, rw, rh in rects):
            return n
    return 1


def _size_hint(min_dim: float) -> str:
    if min_dim > 110:
        return "xl"
    if min_dim > 75:
        return "large"
    if min_dim > 52:
        return "medium"
    return "small"


# ── Data models ────────────────────────────────────────────────────────────────


class TickerSubtile(BaseModel):
    symbol: str = ""
    pct_label: str = ""
    pct_color_scheme: str = "gray"
    bg: str = _DARK_BG
    url: str = ""
    x: float = 0.0
    y: float = 0.0
    w: float = 100.0
    h: float = 100.0
    size: str = "small"


class HeatmapTile(BaseModel):
    name: str = ""
    pct_label: str = ""
    bg: str = _DARK_BG
    pct_color_scheme: str = "gray"
    url: str = ""
    tickers: list[TickerSubtile] = []
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0


class HeatmapChip(BaseModel):
    name: str = ""
    pct_label: str = ""
    bg: str = _DARK_BG
    pct_color_scheme: str = "gray"
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
        d = _direction(avg_pct)
        sign = "+" if avg_pct >= 0 else ""
        chips.append(
            HeatmapChip(
                name=name,
                pct_label=f"{sign}{avg_pct:.2f}%",
                bg=_bg(d, _tint_opacity(avg_pct)),
                pct_color_scheme=_pct_color_scheme(d),
                url=_url_industry(name),
            )
        )

    rows_layout = [
        treemap_inds[i : i + ITEMS_PER_ROW]
        for i in range(0, len(treemap_inds), ITEMS_PER_ROW)
    ]
    row_ws = [
        sum(max(ind_cap.get(str(r[0]), 1.0), 1.0) ** 0.40 for r in row)
        for row in rows_layout
    ]
    grand = max(sum(row_ws), 1.0)

    tiles: list[HeatmapTile] = []
    y_pct_accum = 0.0

    for row, rw in zip(rows_layout, row_ws):
        h_pct = rw / grand * 100.0
        tile_h_px = h_pct / 100.0 * _CTR_H

        if tile_h_px < _MIN_TILE_H_PX:
            for ind_row in row:
                name = str(ind_row[0])
                avg_pct = float(ind_row[1] or 0.0)
                d = _direction(avg_pct)
                sign = "+" if avg_pct >= 0 else ""
                chips.insert(
                    0,
                    HeatmapChip(
                        name=name,
                        pct_label=f"{sign}{avg_pct:.2f}%",
                        bg=_bg(d, _tint_opacity(avg_pct)),
                        pct_color_scheme=_pct_color_scheme(d),
                        url=_url_industry(name),
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
                rects = _squarify(_capped_weights(caps[:n]), tile_w_px, avail_H)
                label_pct = LABEL_H_PX / tile_h_px * 100.0
                ticker_zone = 100.0 - label_pct

                for (sym, t_pct, _), (ix, iy, iw, ih) in zip(top, rects):
                    t_d = _direction(t_pct)
                    t_sign = "+" if t_pct >= 0 else ""
                    y_in_tile = label_pct + (iy / avail_H * ticker_zone)
                    h_in_tile = ih / avail_H * ticker_zone
                    subtiles.append(
                        TickerSubtile(
                            symbol=sym,
                            pct_label=f"{t_sign}{t_pct:.2f}%",
                            pct_color_scheme=_pct_color_scheme(t_d),
                            bg=_bg(t_d, _tint_opacity(t_pct)),
                            url=_url_ticker(sym),
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
                    bg=_ind_bg(d),
                    pct_color_scheme=_pct_color_scheme(d),
                    url=_url_industry(name),
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
