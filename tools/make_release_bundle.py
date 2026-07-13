#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from datetime import date
from pathlib import Path


FILES = ["msgui.bin", "msgev.bin", "msgdata.bin", "msgbre.bin", "msggame.bin"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_tag(raw: str) -> str:
    out = raw.strip().replace(" ", "_")
    if not out:
        raise ValueError("empty tag")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Create release bundle with manifest for a master patch tag")
    ap.add_argument("--tag", required=True, help="master tag suffix, e.g. v15_ko_full_token_fill")
    ap.add_argument("--src-root", default="/mnt/f/games/nobu16")
    ap.add_argument("--release-name", help="release folder name (default: <tag>_<YYYY-MM-DD>)")
    args = ap.parse_args()

    root = Path(args.src_root).resolve()
    tag = safe_tag(args.tag)
    today = date.today().isoformat()
    rel_name = args.release_name or f"{tag}_{today}"

    patch_dir = root / "KR_PATCH_WORK" / "patches" / f"master_{tag}" / "MSG_PK" / "EN"
    apply_script_name = f"apply_master_{tag}_patch.sh"
    restore_script_name = f"restore_master_{tag}_backup.sh"
    apply_script = root / "KR_PATCH_WORK" / "tools" / apply_script_name
    restore_script = root / "KR_PATCH_WORK" / "tools" / restore_script_name
    out_root = root / "KR_PATCH_WORK" / "releases" / rel_name
    out_msg = out_root / "MSG_PK" / "EN"

    if not patch_dir.exists():
        raise FileNotFoundError(f"missing patch dir: {patch_dir}")
    if not apply_script.exists() or not restore_script.exists():
        raise FileNotFoundError("missing apply/restore script for this tag")

    out_msg.mkdir(parents=True, exist_ok=True)
    tools_out = out_root / "tools"
    tools_out.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, str]] = []
    for name in FILES:
        patched = patch_dir / name
        original = root / "MSG_PK" / "EN" / name
        if not patched.exists():
            continue
        if not original.exists():
            raise FileNotFoundError(f"missing original file: {original}")

        p = patched.read_bytes()
        o = original.read_bytes()
        if len(p) != len(o):
            raise ValueError(f"size mismatch for {name}: orig={len(o)} patched={len(p)}")

        shutil.copy2(patched, out_msg / name)

        changed_bytes = sum(a != b for a, b in zip(o, p))
        manifest_rows.append(
            {
                "file": f"MSG_PK/EN/{name}",
                "orig_size": str(len(o)),
                "patched_size": str(len(p)),
                "changed_bytes": str(changed_bytes),
                "orig_sha256": sha256_bytes(o),
                "patched_sha256": sha256_bytes(p),
            }
        )

    # Generate self-contained apply/restore scripts that use files bundled in this release folder.
    apply_out = tools_out / apply_script_name
    restore_out = tools_out / restore_script_name
    file_list = " ".join(r["file"].split("/")[-1] for r in manifest_rows)

    apply_body = f"""#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
RELEASE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
PATCH_DIR="$RELEASE_ROOT/MSG_PK/EN"
TARGET_DIR="$ROOT_DIR/MSG_PK/EN"
BACKUP_DIR="$ROOT_DIR/KR_PATCH_WORK/backups/release_{rel_name}"
TS="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

for f in {file_list}; do
  src="$PATCH_DIR/$f"
  dst="$TARGET_DIR/$f"
  bak="$BACKUP_DIR/${{f}}.${{TS}}.bak"

  if [[ ! -f "$src" ]]; then
    echo "ERROR: missing release file: $src" >&2
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

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
TARGET_DIR="$ROOT_DIR/MSG_PK/EN"
BACKUP_DIR="$ROOT_DIR/KR_PATCH_WORK/backups/release_{rel_name}"

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

    apply_out.write_text(apply_body, encoding="utf-8")
    restore_out.write_text(restore_body, encoding="utf-8")
    apply_out.chmod(0o755)
    restore_out.chmod(0o755)

    manifest_csv = out_root / "manifest.csv"
    with manifest_csv.open("w", encoding="utf-8", newline="") as f:
        fields = ["file", "orig_size", "patched_size", "changed_bytes", "orig_sha256", "patched_sha256"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(manifest_rows)

    notes = out_root / "RELEASE_NOTES.md"
    lines: list[str] = []
    lines.append(f"# Release Bundle `{rel_name}`")
    lines.append("")
    lines.append(f"- date: {today}")
    lines.append(f"- tag: `{tag}`")
    lines.append(f"- files: {len(manifest_rows)}")
    lines.append("")
    lines.append("## Included")
    lines.append("")
    lines.append("- `MSG_PK/EN/*.bin` patched files")
    lines.append("- `tools/apply_master_<tag>_patch.sh`")
    lines.append("- `tools/restore_master_<tag>_backup.sh`")
    lines.append("- `manifest.csv` (sizes/hash/changed-bytes)")
    lines.append("")
    lines.append("## Apply")
    lines.append("")
    lines.append("```bash")
    lines.append(f"bash KR_PATCH_WORK/releases/{rel_name}/tools/{apply_script_name}")
    lines.append("```")
    lines.append("")
    lines.append("## Restore")
    lines.append("")
    lines.append("```bash")
    lines.append(f"bash KR_PATCH_WORK/releases/{rel_name}/tools/{restore_script_name}")
    lines.append("```")
    lines.append("")
    notes.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"tag={tag}")
    print(f"release={out_root}")
    print(f"manifest={manifest_csv}")
    print(f"notes={notes}")
    print(f"files={len(manifest_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
