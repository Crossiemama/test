from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd


@dataclass
class ProcessingConfig:
    timezone: str = "Europe/Moscow"
    freq: str = "H"
    workday_only: bool = True


def _build_time_grid(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    if df.empty:
        return df

    start = df["datetime"].min()
    end = df["datetime"].max()
    grid = pd.DataFrame({"datetime": pd.date_range(start, end, freq=freq)})
    return grid


def _mark_workday(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["is_workday"] = out["datetime"].dt.dayofweek < 5
    return out


def normalize_timeseries(df: pd.DataFrame, cfg: ProcessingConfig) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    out["datetime"] = pd.to_datetime(out["datetime"]) 
    out = out.sort_values("datetime")

    grid = _build_time_grid(out, cfg.freq)
    out = grid.merge(out, on="datetime", how="left")

    value_cols: List[str] = [c for c in out.columns if c != "datetime"]
    for col in value_cols:
        out[col] = out[col].ffill().bfill()

    out = _mark_workday(out)
    if cfg.workday_only:
        out = out[out["is_workday"]]

    return out.reset_index(drop=True)


def validate_required_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
