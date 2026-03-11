from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
import requests


@dataclass
class SourceConfig:
    name: str
    source_type: str
    url: Optional[str] = None
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
    datetime_col: str = "datetime"
    value_col: str = "value"


class BaseCollector:
    def __init__(self, cfg: SourceConfig) -> None:
        self.cfg = cfg

    def fetch(self) -> pd.DataFrame:
        raise NotImplementedError


class HttpJsonCollector(BaseCollector):
    def fetch(self) -> pd.DataFrame:
        if not self.cfg.url:
            raise ValueError(f"Source '{self.cfg.name}' has no url")

        response = requests.request(
            method=self.cfg.method,
            url=self.cfg.url,
            headers=self.cfg.headers,
            params=self.cfg.params,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        if isinstance(payload, dict):
            records = payload.get("data", payload.get("results", []))
        else:
            records = payload

        df = pd.DataFrame(records)
        if df.empty:
            return df

        return df.rename(columns={
            self.cfg.datetime_col: "datetime",
            self.cfg.value_col: self.cfg.name,
        })[["datetime", self.cfg.name]]


class HttpCsvCollector(BaseCollector):
    def fetch(self) -> pd.DataFrame:
        if not self.cfg.url:
            raise ValueError(f"Source '{self.cfg.name}' has no url")
        df = pd.read_csv(self.cfg.url)
        return df.rename(columns={
            self.cfg.datetime_col: "datetime",
            self.cfg.value_col: self.cfg.name,
        })[["datetime", self.cfg.name]]


class FileCsvCollector(BaseCollector):
    def fetch(self) -> pd.DataFrame:
        if not self.cfg.path:
            raise ValueError(f"Source '{self.cfg.name}' has no path")
        df = pd.read_csv(self.cfg.path)
        return df.rename(columns={
            self.cfg.datetime_col: "datetime",
            self.cfg.value_col: self.cfg.name,
        })[["datetime", self.cfg.name]]


COLLECTOR_MAP = {
    "http_json": HttpJsonCollector,
    "http_csv": HttpCsvCollector,
    "file_csv": FileCsvCollector,
}


def build_source_configs(raw_sources: Iterable[Dict[str, Any]]) -> List[SourceConfig]:
    return [SourceConfig(**raw) for raw in raw_sources]


def run_collectors(configs: List[SourceConfig]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []

    for cfg in configs:
        collector_cls = COLLECTOR_MAP.get(cfg.source_type)
        if collector_cls is None:
            raise ValueError(f"Unknown source type: {cfg.source_type}")

        df = collector_cls(cfg).fetch()
        if df.empty:
            continue

        df["datetime"] = pd.to_datetime(df["datetime"], utc=False)
        frames.append(df)

    if not frames:
        return pd.DataFrame(columns=["datetime"])

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="datetime", how="outer")

    return merged.sort_values("datetime").reset_index(drop=True)


def save_dataframe(df: pd.DataFrame, output_path: str) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.suffix.lower() == ".parquet":
        df.to_parquet(output, index=False)
    else:
        df.to_csv(output, index=False)

    return output
