#!/usr/bin/env python3
"""Reproduce complete-resource leak cases against the current directory auditor.

This is a development-only diagnostic, not a release component.  A probe is
reported as ``bypass_reproduced=true`` when the current auditor accepts a
fixture containing a complete commercial game resource in some form.
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "KR_PATCH_WORK" / "tools"))

from audit_file_only_release import audit  # noqa: E402


def reset_from_release(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def write_report(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "KR_PATCH_WORK" / "tmp" / "release_safety_audit" / "probes",
    )
    args = parser.parse_args()

    source_release = (
        PROJECT_ROOT
        / "KR_PATCH_WORK"
        / "releases"
        / "mainmenu_file_only_v0.1_2026-07-13"
    )
    complete_target = (
        PROJECT_ROOT
        / "KR_PATCH_WORK"
        / "workstreams"
        / "msgui_full"
        / "build_p3_core_terms"
        / "recipe_rebuilt.msgui.bin"
    )
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    target_bytes = complete_target.read_bytes()

    results: list[dict[str, object]] = []

    renamed = output_root / "renamed_complete_target"
    reset_from_release(source_release, renamed)
    shutil.copyfile(
        complete_target,
        renamed / "components" / "message" / "recipe_rebuilt.msgui.bin",
    )
    renamed_audit = audit(renamed)
    results.append(
        {
            "probe": "renamed complete P3 msgui binary",
            "auditor_status": renamed_audit["status"],
            "bypass_reproduced": renamed_audit["status"] == "PASS",
        }
    )

    embedded = output_root / "base64_complete_target"
    reset_from_release(source_release, embedded)
    recipe_path = embedded / "components" / "message" / "main_menu_sc.recipe.json"
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    recipe["unexpected_complete_target_b64"] = base64.b64encode(target_bytes).decode("ascii")
    write_report(recipe_path, recipe)
    embedded_audit = audit(embedded)
    results.append(
        {
            "probe": "complete P3 msgui embedded as an ignored JSON field",
            "auditor_status": embedded_audit["status"],
            "bypass_reproduced": embedded_audit["status"] == "PASS",
        }
    )

    nested_zip = output_root / "nested_zip_complete_target"
    reset_from_release(source_release, nested_zip)
    zip_path = nested_zip / "components" / "message" / "diagnostic.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("msgui.bin", target_bytes)
    zip_audit = audit(nested_zip)
    results.append(
        {
            "probe": "complete P3 msgui nested in an unlisted ZIP",
            "auditor_status": zip_audit["status"],
            "bypass_reproduced": zip_audit["status"] == "PASS",
        }
    )

    report = {
        "schema": "nobu16.vnext-release-audit-probe.v1",
        "development_only": True,
        "complete_target": str(complete_target),
        "complete_target_size": len(target_bytes),
        "results": results,
        "all_bypasses_reproduced": all(item["bypass_reproduced"] for item in results),
    }
    report_path = output_root / "probe_report.json"
    write_report(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_bypasses_reproduced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
