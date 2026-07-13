#!/usr/bin/env python3
"""Exercise vNext directory and ZIP leak/path defenses with hostile fixtures.

Development-only: all mutated copies are written below KR_PATCH_WORK/tmp and
the canonical release directory/ZIP are opened read-only.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import stat
import subprocess
import warnings
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RELEASE = (
    PROJECT_ROOT / "KR_PATCH_WORK" / "releases" / "msgui_p3_file_only_v0.2_2026-07-13"
)
DEFAULT_AUDITOR = (
    PROJECT_ROOT
    / "KR_PATCH_WORK"
    / "workstreams"
    / "msgui_full"
    / "release_vnext"
    / "Audit-ReleaseVNext.ps1"
)
COMPLETE_TARGET = (
    PROJECT_ROOT
    / "KR_PATCH_WORK"
    / "workstreams"
    / "msgui_full"
    / "build_p3_core_terms"
    / "recipe_rebuilt.msgui.bin"
)
POWERSHELL = Path(r"C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe")


def reset_copy(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def run_audit(auditor: Path, package: Path, archive: Path | None = None) -> dict[str, object]:
    command = [
        str(POWERSHELL),
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(auditor),
        "-PackageRoot",
        str(package),
    ]
    if archive is not None:
        command += ["-ZipPath", str(archive)]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "return_code": completed.returncode,
        "rejected": completed.returncode != 0,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def run_verify(package: Path) -> dict[str, object]:
    installer = package / "tools" / "Invoke-FileOnlyPatch.ps1"
    command = [
        str(POWERSHELL),
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(installer),
        "-Action",
        "Verify",
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "return_code": completed.returncode,
        "rejected": completed.returncode != 0,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def directory_probe(label: str, auditor: Path, package: Path) -> dict[str, object]:
    verifier = run_verify(package)
    standalone = run_audit(auditor, package)
    return {
        "probe": label,
        "verifier": verifier,
        "standalone_auditor": standalone,
        "rejected": bool(verifier["rejected"] and standalone["rejected"]),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def update_manifest_file_spec(package: Path, relative: str) -> None:
    manifest_path = package / "release_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = package / Path(relative)
    matches = [item for item in manifest["files"] if item["path"] == relative.replace("\\", "/")]
    if len(matches) != 1:
        raise RuntimeError(f"manifest file entry is not unique: {relative}")
    matches[0]["size"] = target.stat().st_size
    matches[0]["sha256"] = sha256_file(target)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def inject_duplicate_property(
    path: Path,
    key: str,
    occurrence: int,
    variant: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf'^(?P<indent>\s*)"{re.escape(key)}"(?P<rest>\s*:\s*.*)$', re.MULTILINE)
    matches = list(pattern.finditer(text))
    if occurrence < 1 or occurrence > len(matches):
        raise RuntimeError(f"cannot find occurrence {occurrence} of {key!r} in {path}")
    match = matches[occurrence - 1]
    if variant in {"direct", "nested"}:
        duplicate_key = key
    elif variant == "escaped-equivalent":
        duplicate_key = f"\\u{ord(key[0]):04X}{key[1:]}"
    elif variant == "case-only":
        swapped = key[0].upper() if key[0].islower() else key[0].lower()
        duplicate_key = swapped + key[1:]
    else:
        raise ValueError(f"unknown duplicate-key variant: {variant}")
    duplicate = f'{match.group("indent")}"{duplicate_key}"{match.group("rest")}'
    text = text[: match.end()] + "\n" + duplicate + text[match.end() :]
    path.write_text(text, encoding="utf-8", newline="\n")


def append_zip_member(path: Path, info_or_name: zipfile.ZipInfo | str, data: bytes) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(info_or_name, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    parser.add_argument("--auditor", type=Path, default=DEFAULT_AUDITOR)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "KR_PATCH_WORK" / "tmp" / "release_safety_audit" / "vnext_defenses",
    )
    args = parser.parse_args()

    release = args.release.resolve(strict=True)
    source_zip = Path(str(release) + ".zip").resolve(strict=True)
    auditor = args.auditor.resolve(strict=True)
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    target_bytes = COMPLETE_TARGET.read_bytes()
    prefix = release.name + "/"
    results: list[dict[str, object]] = []

    # Directory leak probes.
    renamed = output / "dir_renamed_complete_target"
    reset_copy(release, renamed)
    shutil.copyfile(COMPLETE_TARGET, renamed / "components" / "message" / "recipe_rebuilt.msgui.bin")
    results.append(directory_probe("directory renamed complete target", auditor, renamed))

    embedded = output / "dir_base64_complete_target"
    reset_copy(release, embedded)
    recipe_path = embedded / "components" / "message" / "msgui_sc.recipe.json"
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    recipe["unexpected_complete_target_b64"] = base64.b64encode(target_bytes).decode("ascii")
    recipe_path.write_text(
        json.dumps(recipe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    results.append(directory_probe("directory recipe base64 extra field", auditor, embedded))

    nested = output / "dir_nested_zip_complete_target"
    reset_copy(release, nested)
    with zipfile.ZipFile(
        nested / "components" / "message" / "diagnostic.zip",
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.writestr("msgui.bin", target_bytes)
    results.append(directory_probe("directory nested archive", auditor, nested))

    json_targets = [
        ("manifest", Path("release_manifest.json"), "release_eligible", "size"),
        ("evidence", Path("VALIDATION_EVIDENCE.json"), "release_eligible", "passed"),
        ("message_recipe", Path("components/message/msgui_sc.recipe.json"), "file_only", "sha256"),
        ("font_recipe", Path("components/font/recipe.json"), "file_only", "sha256"),
    ]
    for json_label, relative, direct_key, nested_key in json_targets:
        variants = [
            ("direct", direct_key, 1),
            ("nested", nested_key, 1),
            ("escaped-equivalent", direct_key, 1),
            ("case-only", direct_key, 1),
        ]
        for variant, key, occurrence in variants:
            fixture = output / f"json_{json_label}_{variant}"
            reset_copy(release, fixture)
            inject_duplicate_property(fixture / relative, key, occurrence, variant)
            results.append(
                directory_probe(
                    f"{json_label} {variant} duplicate JSON key",
                    auditor,
                    fixture,
                )
            )

    # The standalone auditor must pin executable source/wrappers before it
    # invokes packaged Verify.  The installer fixture contains benign marker
    # creation code; a passing defense means the marker is never created.
    marker = output / "UNTRUSTED_INSTALLER_EXECUTED.txt"
    marker.unlink(missing_ok=True)
    code_tamper = output / "code_tamper_installer_marker"
    reset_copy(release, code_tamper)
    installer_path = code_tamper / "tools" / "Invoke-FileOnlyPatch.ps1"
    installer_text = installer_path.read_text(encoding="utf-8")
    anchor = "$ErrorActionPreference = 'Stop'"
    marker_literal = str(marker).replace("'", "''")
    injected = anchor + f"\n[IO.File]::WriteAllText('{marker_literal}', 'executed')"
    if installer_text.count(anchor) != 1:
        raise RuntimeError("installer marker injection anchor is not unique")
    installer_path.write_text(
        installer_text.replace(anchor, injected, 1),
        encoding="utf-8",
        newline="\n",
    )
    update_manifest_file_spec(code_tamper, "tools/Invoke-FileOnlyPatch.ps1")
    marker_audit = run_audit(auditor, code_tamper)
    results.append(
        {
            "probe": "installer+manifest tamper rejected before packaged code execution",
            "standalone_auditor": marker_audit,
            "marker_absent": not marker.exists(),
            "rejected": bool(marker_audit["rejected"] and not marker.exists()),
        }
    )

    source_tampers = [
        ("apply wrapper", Path("APPLY_KOREAN_PATCH.bat"), b"\r\nREM benign tamper\r\n"),
        ("recipe core", Path("tools/FileRecipeCore.cs"), b"\n// benign tamper\n"),
        ("JSON key guard", Path("tools/JsonKeyGuard.cs"), b"\n// benign tamper\n"),
    ]
    for label, relative, suffix in source_tampers:
        fixture = output / ("code_tamper_" + label.lower().replace(" ", "_"))
        reset_copy(release, fixture)
        target = fixture / relative
        target.write_bytes(target.read_bytes() + suffix)
        update_manifest_file_spec(fixture, relative.as_posix())
        standalone = run_audit(auditor, fixture)
        results.append(
            {
                "probe": f"{label}+manifest tamper pre-execution rejection",
                "standalone_auditor": standalone,
                "rejected": bool(standalone["rejected"]),
            }
        )

    # ZIP central-directory/member probes.  The audited folder remains canonical.
    zip_cases: list[tuple[str, str | zipfile.ZipInfo, bytes]] = [
        ("zip duplicate member", prefix + "README_KO.md", b"duplicate"),
        ("zip case collision", prefix + "readme_ko.md", b"case collision"),
        ("zip traversal", prefix + "../escape.txt", b"escape"),
        ("zip nested archive", prefix + "diagnostic.zip", b"PK\x03\x04nested"),
    ]
    symlink = zipfile.ZipInfo(prefix + "components/message/symlink")
    symlink.create_system = 3
    symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
    zip_cases.append(("zip symlink", symlink, b"msgui_sc.recipe.json"))

    for index, (label, member, data) in enumerate(zip_cases, start=1):
        candidate = output / f"zip_attack_{index}.zip"
        shutil.copyfile(source_zip, candidate)
        append_zip_member(candidate, member, data)
        standalone = run_audit(auditor, release, candidate)
        results.append(
            {
                "probe": label,
                "standalone_auditor": standalone,
                "rejected": bool(standalone["rejected"]),
            }
        )

    report = {
        "schema": "nobu16.vnext-release-defense-probe.v1",
        "development_only": True,
        "release": str(release),
        "zip": str(source_zip),
        "canonical_audit": run_audit(auditor, release, source_zip),
        "results": results,
        "all_hostile_fixtures_rejected": all(item["rejected"] for item in results),
    }
    report_path = output / "probe_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["canonical_audit"]["return_code"] == 0 and report["all_hostile_fixtures_rejected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
