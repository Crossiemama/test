from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from tz_pipeline.collectors import build_source_configs, run_collectors, save_dataframe
from tz_pipeline.document_builder import convert_markdown_file_to_docx
from tz_pipeline.processing import ProcessingConfig, normalize_timeseries


def collect_command(config_path: str, output_path: str) -> None:
    cfg_raw = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    sources = build_source_configs(cfg_raw["sources"])
    collected = run_collectors(sources)

    process_cfg = ProcessingConfig(**cfg_raw.get("processing", {}))
    normalized = normalize_timeseries(collected, process_cfg)

    save_dataframe(normalized, output_path)


def docx_command(markdown_path: str, output_path: str) -> None:
    convert_markdown_file_to_docx(markdown_path, output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TZ data pipeline and DOCX formatter")
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser("collect", help="Collect and normalize data")
    collect.add_argument("--config", required=True, help="YAML config path")
    collect.add_argument("--output", required=True, help="Output CSV/Parquet path")

    docx = sub.add_parser("build-docx", help="Build GOST-like DOCX from markdown")
    docx.add_argument("--input-md", required=True, help="Input markdown file")
    docx.add_argument("--output-docx", required=True, help="Output DOCX file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "collect":
        collect_command(config_path=args.config, output_path=args.output)
        return

    if args.command == "build-docx":
        docx_command(markdown_path=args.input_md, output_path=args.output_docx)
        return


if __name__ == "__main__":
    main()
