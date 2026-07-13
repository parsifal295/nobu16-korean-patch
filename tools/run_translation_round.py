#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path


def run_cmd(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def safe_tag(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", raw.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        raise ValueError("tag became empty after sanitization")
    return cleaned.lower()


def catalog_stats(catalog_csv: Path) -> tuple[int, int, Counter[str]]:
    with catalog_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    translated = [r for r in rows if (r.get("translated_ko") or "").strip()]
    by_file = Counter(Path(r["file"]).name for r in translated)
    return len(rows), len(translated), by_file


def write_apply_restore_scripts(root_dir: Path, tag: str, files: list[str]) -> tuple[Path, Path]:
    tools_dir = root_dir / "KR_PATCH_WORK" / "tools"
    patch_dir = f"$ROOT_DIR/KR_PATCH_WORK/patches/master_{tag}/MSG_PK/EN"
    backup_dir = f"$ROOT_DIR/KR_PATCH_WORK/backups/master_{tag}"

    apply_path = tools_dir / f"apply_master_{tag}_patch.sh"
    restore_path = tools_dir / f"restore_master_{tag}_backup.sh"

    file_list = " ".join(files)
    apply_body = f"""#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/../.." && pwd)"
PATCH_DIR="{patch_dir}"
TARGET_DIR="$ROOT_DIR/MSG_PK/EN"
BACKUP_DIR="{backup_dir}"
TS="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

for f in {file_list}; do
  src="$PATCH_DIR/$f"
  dst="$TARGET_DIR/$f"
  bak="$BACKUP_DIR/${{f}}.${{TS}}.bak"

  if [[ ! -f "$src" ]]; then
    echo "ERROR: missing patch file: $src" >&2
    exit 1
  fi
  if [[ ! -f "$dst" ]]; then
    echo "ERROR: missing target file: $dst" >&2
    exit 1
  fi

  cp -f "$dst" "$bak"
  cp -f "$src" "$dst"
  echo "Patched $f (backup: $bak)"
done
"""

    restore_body = f"""#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/../.." && pwd)"
TARGET_DIR="$ROOT_DIR/MSG_PK/EN"
BACKUP_DIR="{backup_dir}"

for f in {file_list}; do
  latest="$(ls -1t "$BACKUP_DIR"/"${{f}}".*.bak 2>/dev/null | head -n 1 || true)"
  if [[ -z "$latest" ]]; then
    echo "ERROR: no backup found for $f in $BACKUP_DIR" >&2
    exit 1
  fi
  cp -f "$latest" "$TARGET_DIR/$f"
  echo "Restored $f from $latest"
done
"""

    apply_path.write_text(apply_body, encoding="utf-8")
    restore_path.write_text(restore_body, encoding="utf-8")
    apply_path.chmod(0o755)
    restore_path.chmod(0o755)
    return apply_path, restore_path


def write_report(
    report_path: Path,
    tag: str,
    base_master: Path,
    runs_csv: Path,
    out_catalog: Path,
    patch_root: Path,
    rows_total: int,
    translated_total: int,
    by_file: Counter[str],
    strict_original: bool,
    apply_script: Path,
    restore_script: Path,
) -> None:
    strict_text = "--strict-original" if strict_original else "(strict disabled)"
    lines: list[str] = []
    lines.append(f"# Translation Round `{tag}` Status ({date.today().isoformat()})")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Base master: `{base_master}`")
    lines.append(f"- Runs CSV: `{runs_csv}`")
    lines.append(f"- Output catalog: `{out_catalog}`")
    lines.append(f"- Output patch root: `{patch_root}`")
    lines.append(f"- Rows total: `{rows_total}`")
    lines.append(f"- Translated rows: `{translated_total}`")
    lines.append("")
    lines.append("## Patched Counts (catalog translated rows)")
    lines.append("")
    for name in sorted(by_file):
        lines.append(f"- `{name}`: {by_file[name]}")
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append("```bash")
    lines.append(
        "python3 KR_PATCH_WORK/tools/msgpk_ascii_u16_run_patch.py "
        f"validate --input-csv {runs_csv} --allow-shorter"
    )
    lines.append(
        "python3 KR_PATCH_WORK/tools/extend_master_with_runs.py "
        f"--master-csv {base_master} --runs-csv {runs_csv} --out-csv {out_catalog}"
    )
    lines.append(
        "python3 KR_PATCH_WORK/tools/apply_master_catalog.py "
        f"--catalog-csv {out_catalog} --src-root /mnt/f/games/nobu16 "
        f"--out-root {patch_root} {strict_text}"
    )
    lines.append("```")
    lines.append("")
    lines.append("## Operational Scripts")
    lines.append("")
    lines.append(f"- Apply: `tools/{apply_script.name}`")
    lines.append(f"- Restore: `tools/{restore_script.name}`")
    lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run one translation round: validate runs, extend master, apply strict patch."
    )
    ap.add_argument("--tag", required=True, help="e.g. v4_ko_v2")
    ap.add_argument(
        "--src-root", default="/mnt/f/games/nobu16", help="Game root containing MSG_PK/EN files"
    )
    ap.add_argument(
        "--base-master-csv",
        default="KR_PATCH_WORK/data/work_templates/master_msgpk_en_catalog.v2.csv",
    )
    ap.add_argument("--runs-csv", required=True)
    ap.add_argument(
        "--strict-original",
        action="store_true",
        default=False,
        help="Enable strict original text check in apply step",
    )
    args = ap.parse_args()

    root_dir = Path(args.src_root).resolve()
    tag = safe_tag(args.tag)
    tools_dir = root_dir / "KR_PATCH_WORK" / "tools"

    base_master = (root_dir / args.base_master_csv).resolve()
    runs_csv = (root_dir / args.runs_csv).resolve()
    out_catalog = root_dir / "KR_PATCH_WORK" / "data" / "work_templates" / f"master_msgpk_en_catalog.{tag}.csv"
    out_patch_root = root_dir / "KR_PATCH_WORK" / "patches" / f"master_{tag}"

    if not base_master.exists():
        raise FileNotFoundError(f"missing base master csv: {base_master}")
    if not runs_csv.exists():
        raise FileNotFoundError(f"missing runs csv: {runs_csv}")

    run_cmd(
        [
            "python3",
            str(tools_dir / "msgpk_ascii_u16_run_patch.py"),
            "validate",
            "--input-csv",
            str(runs_csv),
            "--allow-shorter",
        ]
    )
    run_cmd(
        [
            "python3",
            str(tools_dir / "extend_master_with_runs.py"),
            "--master-csv",
            str(base_master),
            "--runs-csv",
            str(runs_csv),
            "--out-csv",
            str(out_catalog),
        ]
    )

    apply_cmd = [
        "python3",
        str(tools_dir / "apply_master_catalog.py"),
        "--catalog-csv",
        str(out_catalog),
        "--src-root",
        str(root_dir),
        "--out-root",
        str(out_patch_root),
    ]
    if args.strict_original:
        apply_cmd.append("--strict-original")
    run_cmd(apply_cmd)

    rows_total, translated_total, by_file = catalog_stats(out_catalog)

    files = ["msgui.bin", "msgev.bin", "msgdata.bin", "msgbre.bin"]
    if by_file.get("msggame.bin", 0) > 0:
        files.append("msggame.bin")
    apply_script, restore_script = write_apply_restore_scripts(root_dir, tag, files)

    report_path = (
        root_dir
        / "KR_PATCH_WORK"
        / "reports"
        / f"master_catalog_{tag}_status_{date.today().isoformat()}.md"
    )
    write_report(
        report_path=report_path,
        tag=tag,
        base_master=base_master,
        runs_csv=runs_csv,
        out_catalog=out_catalog,
        patch_root=out_patch_root,
        rows_total=rows_total,
        translated_total=translated_total,
        by_file=by_file,
        strict_original=args.strict_original,
        apply_script=apply_script,
        restore_script=restore_script,
    )

    print(f"tag={tag}")
    print(f"catalog={out_catalog}")
    print(f"patch_root={out_patch_root}")
    print(f"rows_total={rows_total}")
    print(f"translated_total={translated_total}")
    print(f"apply_script={apply_script}")
    print(f"restore_script={restore_script}")
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
