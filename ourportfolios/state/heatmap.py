"""Heatmap state — squarified nested treemap."""

from collections.abc import Sequence
from urllib.parse import quote

import reflex as rx
from pydantic import BaseModel
from sqlalchemy import Column, Float, MetaData, String, Table, func, select
from sqlalchemy.exc import SQLAlchemyError

from ourportfolios.utils.database.database import get_company_session
from ourportfolios.utils.database.models import OverviewORM, PriceORM

MAX_TREEMAP_INDUSTRIES = 9
ITEMS_PER_ROW = 3
_CTR_W = 760.0
_CTR_H = 620.0
LABEL_H_PX = 36.0
_MIN_PX = 52.0
_MAX_N = 4
_MIN_TILE_H_PX = 80.0
_MAX_WEIGHT_RATIO = 3.0

_STRONG_MOVE_PCT = 5.0
_MEDIUM_MOVE_PCT = 3.0
_LIGHT_MOVE_PCT = 1.5
_WEAK_MOVE_PCT = 0.5

_SIZE_XL_MIN = 110.0
_SIZE_LARGE_MIN = 75.0
_SIZE_MEDIUM_MIN = 52.0

_change_meta = MetaData(schema="market")


def _change_table(name: str) -> Table:
    return Table(
        name,
        _change_meta,
        Column("industry", String),
        Column("symbol", String),
        Column("pct_change", Float),
        Column("market_cap", Float),
    )


_PERIOD_CHANGE_TABLE = {
    "1W": _change_table("weekly_changes"),
    "1M": _change_table("monthly_changes"),
    "1Q": _change_table("quarterly_changes"),
    "1Y": _change_table("yearly_changes"),
}

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
    if a >= _STRONG_MOVE_PCT:
        return 0.18
    if a >= _MEDIUM_MOVE_PCT:
        return 0.13
    if a >= _LIGHT_MOVE_PCT:
        return 0.09
    if a >= _WEAK_MOVE_PCT:
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


Rect = tuple[float, float, float, float]


class _RectFrame(BaseModel):
    x: float
    y: float
    w: float
    h: float


def _worst(row: list[float], s: float) -> float:
    if not row or s == 0:
        return float("inf")
    rs = sum(row)
    ratios = [s * s * r / (rs * rs) for r in row]
    inverses = [rs * rs / (s * s * r) for r in row]
    return max(*ratios, *inverses)


def _sq(sizes: list[float], frame: _RectFrame, out: list[Rect]) -> None:
    if not sizes:
        return
    x, y, w, h = frame.x, frame.y, frame.w, frame.h
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
        _sq(rest, _RectFrame(x=x, y=y + rh, w=w, h=h - rh), out)
    else:
        cw, ry = rs / h, y
        for v in comm:
            out.append((x, ry, cw, v / rs * h))
            ry += v / rs * h
        _sq(rest, _RectFrame(x=x + cw, y=y, w=w - cw, h=h), out)


def _squarify(weights: list[float], width: float, height: float) -> list[Rect]:
    if not weights:
        return []
    total = sum(weights)
    if total == 0:
        return []
    out: list[Rect] = []
    _sq(
        [v / total * width * height for v in weights],
        _RectFrame(x=0.0, y=0.0, w=width, h=height),
        out,
    )
    return out


def _capped_weights(caps: list[float]) -> list[float]:
    raw = [max(c, 1.0) ** 0.5 for c in caps]
    mn = min(raw)
    ceiling = mn * _MAX_WEIGHT_RATIO
    return [min(w, ceiling) for w in raw]


def _best_n(caps: list[float], width: float, height: float) -> int:
    avail_h = max(height - LABEL_H_PX, 1.0)
    for n in range(min(len(caps), _MAX_N), 0, -1):
        weights = _capped_weights(caps[:n])
        rects = _squarify(weights, width, avail_h)
        if rects and all(min(rw, rh) >= _MIN_PX for _, _, rw, rh in rects):
            return n
    return 1


def _size_hint(min_dim: float) -> str:
    if min_dim > _SIZE_XL_MIN:
        return "xl"
    if min_dim > _SIZE_LARGE_MIN:
        return "large"
    if min_dim > _SIZE_MEDIUM_MIN:
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
    tickers: list[TickerSubtile] = rx.Field(default_factory=list)
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


IndustryRow = tuple[str, float, int]
TickerRow = tuple[str, str, float, float]


def _chip_from_industry(name: str, avg_pct: float) -> HeatmapChip:
    d = _direction(avg_pct)
    sign = "+" if avg_pct >= 0 else ""
    return HeatmapChip(
        name=name,
        pct_label=f"{sign}{avg_pct:.2f}%",
        bg=_bg(d, _tint_opacity(avg_pct)),
        pct_color_scheme=_pct_color_scheme(d),
        url=_url_industry(name),
    )


def _subtiles_for_items(
    items: list[TickerRow],
    tile_w_px: float,
    tile_h_px: float,
) -> list[TickerSubtile]:
    if not items:
        return []

    caps = [max(c, 1.0) for _, _, c in items]
    n = _best_n(caps, tile_w_px, tile_h_px)
    top = items[:n]
    avail_h = tile_h_px - LABEL_H_PX
    rects = _squarify(_capped_weights(caps[:n]), tile_w_px, avail_h)
    label_pct = LABEL_H_PX / tile_h_px * 100.0
    ticker_zone = 100.0 - label_pct

    subtiles: list[TickerSubtile] = []
    for (sym, t_pct, _), (ix, iy, iw, ih) in zip(top, rects, strict=False):
        t_d = _direction(t_pct)
        t_sign = "+" if t_pct >= 0 else ""
        y_in_tile = label_pct + (iy / avail_h * ticker_zone)
        h_in_tile = ih / avail_h * ticker_zone
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
            ),
        )
    return subtiles


def _add_chip_row(chips: list[HeatmapChip], row: list[IndustryRow]) -> None:
    for ind_row in row:
        name = str(ind_row[0])
        avg_pct = float(ind_row[1] or 0.0)
        chips.insert(0, _chip_from_industry(name, avg_pct))


def _build(
    industry_rows: Sequence[IndustryRow],
    ticker_rows: Sequence[TickerRow],
) -> tuple[list[HeatmapTile], list[HeatmapChip]]:
    raw: dict[str, list[TickerRow]] = {}
    for row in ticker_rows:
        raw.setdefault(str(row[0]), []).append(
            (str(row[1]), float(row[2] or 0.0), float(row[3] or 0.0)),
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
        chips.append(_chip_from_industry(name, avg_pct))

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

    for row, rw in zip(rows_layout, row_ws, strict=False):
        h_pct = rw / grand * 100.0
        tile_h_px = h_pct / 100.0 * _CTR_H

        if tile_h_px < _MIN_TILE_H_PX:
            _add_chip_row(chips, row)
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
            subtiles = _subtiles_for_items(items, tile_w_px, tile_h_px)

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
                ),
            )
            x_pct += w_pct

        y_pct_accum += h_pct

    return tiles, chips


# ── State ──────────────────────────────────────────────────────────────────────


class HeatmapState(rx.State):
    selected_period: str = "1D"
    tiles: list[HeatmapTile] = rx.Field(default_factory=list)
    chips: list[HeatmapChip] = rx.Field(default_factory=list)
    loading: bool = False

    @rx.event(background=True)
    async def load_heatmap_data(self) -> None:
        async with self:
            self.loading = True
        await self._fetch(self.selected_period)
        async with self:
            self.loading = False

    @rx.event(background=True)
    async def set_period(self, period: str) -> None:
        async with self:
            self.selected_period = period
            self.loading = True
        await self._fetch(period)
        async with self:
            self.loading = False

    async def _fetch(self, period: str) -> None:
        try:
            async with get_company_session() as session:
                if period == "1D":
                    ind_stmt = (
                        select(
                            OverviewORM.industry,
                            func.avg(PriceORM.pct_price_change).label("pct_change"),
                            func.count().label("row_count"),
                        )
                        .join(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
                        .where(
                            OverviewORM.industry.is_not(None),
                            OverviewORM.industry != "",
                            PriceORM.pct_price_change.is_not(None),
                        )
                        .group_by(OverviewORM.industry)
                    )
                    tick_stmt = (
                        select(
                            OverviewORM.industry,
                            PriceORM.symbol,
                            PriceORM.pct_price_change.label("pct_change"),
                            OverviewORM.market_cap,
                        )
                        .join(OverviewORM, PriceORM.symbol == OverviewORM.symbol)
                        .where(
                            OverviewORM.industry.is_not(None),
                            OverviewORM.industry != "",
                            OverviewORM.market_cap.is_not(None),
                            OverviewORM.market_cap > 0,
                            PriceORM.pct_price_change.is_not(None),
                        )
                        .order_by(OverviewORM.industry, OverviewORM.market_cap.desc())
                    )
                else:
                    table = _PERIOD_CHANGE_TABLE.get(period)
                    if table is None:
                        table = _PERIOD_CHANGE_TABLE["1W"]
                    ind_stmt = (
                        select(
                            table.c.industry,
                            func.avg(table.c.pct_change).label("pct_change"),
                            func.count().label("row_count"),
                        )
                        .where(
                            table.c.industry.is_not(None),
                            table.c.industry != "",
                            table.c.pct_change.is_not(None),
                        )
                        .group_by(table.c.industry)
                    )
                    tick_stmt = (
                        select(
                            table.c.industry,
                            table.c.symbol,
                            table.c.pct_change,
                            table.c.market_cap,
                        )
                        .where(
                            table.c.industry.is_not(None),
                            table.c.industry != "",
                            table.c.market_cap.is_not(None),
                            table.c.market_cap > 0,
                            table.c.pct_change.is_not(None),
                        )
                        .order_by(table.c.industry, table.c.market_cap.desc())
                    )

                ind_res = await session.execute(ind_stmt)
                tick_res = await session.execute(tick_stmt)
            tiles, chips = _build(ind_res.fetchall(), tick_res.fetchall())
            async with self:
                self.tiles = tiles
                self.chips = chips
        except (SQLAlchemyError, KeyError, TypeError, ValueError):
            async with self:
                self.tiles = []
                self.chips = []
