#!/usr/bin/env python3
"""Assemble the public file-only NOBU16 Korean main-menu release.

This is a build-time tool.  Python and other build helpers are deliberately
not copied into the public output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from pathlib import Path, PurePosixPath

from audit_file_only_release import audit as audit_public_release


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return value


def safe_relative(value: str) -> Path:
    pure = PurePosixPath(value.replace("\\", "/"))
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"unsafe relative path: {value!r}")
    devices = {"CON", "PRN", "AUX", "NUL"}
    devices.update(f"COM{index}" for index in range(1, 10))
    devices.update(f"LPT{index}" for index in range(1, 10))
    for part in pure.parts:
        if ":" in part or part.endswith((" ", ".")):
            raise ValueError(f"unsafe Windows path segment: {value!r}")
        if part.split(".", 1)[0].upper() in devices:
            raise ValueError(f"Windows device path is forbidden: {value!r}")
    return Path(*pure.parts)


def assert_contained_ordinary(root: Path, source: Path) -> None:
    resolved_root = root.resolve(strict=True)
    resolved_source = source.resolve(strict=True)
    if not resolved_source.is_relative_to(resolved_root):
        raise ValueError(f"source escapes its component root: {source}")
    current = root
    candidates = [current]
    for part in source.relative_to(root).parts:
        current = current / part
        candidates.append(current)
    for candidate in candidates:
        is_junction = getattr(candidate, "is_junction", lambda: False)()
        if candidate.is_symlink() or is_junction:
            raise ValueError(f"component path contains a link or junction: {candidate}")


def checked_copy(
    source: Path,
    destination: Path,
    expected: dict | None = None,
    containment_root: Path | None = None,
) -> None:
    if containment_root is not None:
        assert_contained_ordinary(containment_root, source)
    if not source.is_file() or source.is_symlink():
        raise ValueError(f"required ordinary file is missing: {source}")
    pinned_size = source.stat().st_size
    pinned_hash = sha256(source)
    if expected is not None:
        expected_size = int(expected["size"])
        expected_hash = str(expected["sha256"]).upper()
        if pinned_size != expected_size or pinned_hash != expected_hash:
            raise ValueError(f"source payload verification failed: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    if destination.stat().st_size != pinned_size or sha256(destination) != pinned_hash:
        raise ValueError(f"copied snapshot does not match its verified source: {destination}")


def require_bool(recipe: dict, key: str, expected: bool) -> None:
    if recipe.get(key) is not expected:
        raise ValueError(f"font recipe {key} must be {expected}")


def assemble(args: argparse.Namespace) -> Path:
    font_root = args.font_component.resolve()
    message_recipe = args.message_recipe.resolve()
    validation_path = args.validation_evidence.resolve()
    final_output = args.output_root.resolve()
    project_root = Path(__file__).resolve().parents[1]
    if final_output.exists():
        raise ValueError(f"final output must not exist: {final_output}")
    final_output.parent.mkdir(parents=True, exist_ok=True)
    output = final_output.parent / f".{final_output.name}.staging-{uuid.uuid4().hex}"
    output.mkdir()

    font_recipe_source = font_root / "recipe.json"
    font_recipe_path = output / "components" / "font" / "recipe.json"
    checked_copy(
        font_recipe_source,
        font_recipe_path,
        containment_root=font_root,
    )
    font_recipe = read_json(font_recipe_path)
    require_bool(font_recipe, "release_eligible", True)
    require_bool(font_recipe, "runtime_direct_lookup_verified", True)
    require_bool(font_recipe, "file_only", True)
    if font_recipe.get("runtime_patch_features") != []:
        raise ValueError("font recipe runtime_patch_features must be empty")
    provenance = font_recipe.get("font_provenance")
    if not isinstance(provenance, dict):
        raise ValueError("font recipe has no provenance object")
    if not provenance.get("repository") or not provenance.get("google_fonts_commit"):
        raise ValueError("font recipe has no pinned upstream repository/commit")
    sources = provenance.get("source_fonts")
    if not isinstance(sources, dict) or set(sources) != {
        "NotoSansKR-wght.ttf", "NotoSerifKR-wght.ttf"
    }:
        raise ValueError("font recipe source-font provenance is incomplete")
    for source_name, source_spec in sources.items():
        if not isinstance(source_spec, dict):
            raise ValueError(f"font source provenance is not an object: {source_name}")
        if not source_spec.get("sha256") or not source_spec.get("version") or not source_spec.get("upstream_url"):
            raise ValueError(f"font source provenance is incomplete: {source_name}")
    language = font_recipe.get("languages", {}).get("SC")
    if not isinstance(language, dict):
        raise ValueError("font recipe does not contain the SC language")
    entries = language.get("entries")
    if not isinstance(entries, dict) or set(entries) != {"6", "7"}:
        raise ValueError("font recipe must contain exactly SC entries 6 and 7")

    copied_payloads: set[Path] = set()
    for key in ("6", "7"):
        entry = entries[key]
        payload = entry.get("pixel_payload")
        if not isinstance(payload, dict):
            raise ValueError(f"SC font entry {key} has no pixel payload")
        relative = safe_relative(str(payload["file"]))
        if relative.suffix.lower() in {".py", ".pyc", ".pyo"}:
            raise ValueError(f"script payload is forbidden: {relative}")
        if relative not in copied_payloads:
            checked_copy(
                font_root / relative,
                output / "components" / "font" / relative,
                payload,
                containment_root=font_root,
            )
            copied_payloads.add(relative)

    license_root = font_root / "licenses"
    licenses = sorted(license_root.glob("*.txt"))
    license_specs = {
        "OFL-NotoSansKR.txt": {
            "size": 4388,
            "sha256": "1C05C68C34F9708415AADA51F17E1B0092D2CEA709BF4A94CD38114F9E73D7D9",
        },
        "OFL-NotoSerifKR.txt": {
            "size": 4350,
            "sha256": "5E0DA210FB04058A8C0087985D2D456B931C2579811A49655721D3CF0C36B6D6",
        },
    }
    if {path.name for path in licenses} != set(license_specs):
        raise ValueError("font component license set is incomplete or unexpected")
    for license_path in licenses:
        checked_copy(
            license_path,
            output / "components" / "font" / "licenses" / license_path.name,
            license_specs[license_path.name],
            containment_root=font_root,
        )

    staged_message_recipe = output / "components" / "message" / "main_menu_sc.recipe.json"
    checked_copy(
        message_recipe,
        staged_message_recipe,
        containment_root=message_recipe.parent,
    )
    message = read_json(staged_message_recipe)
    if message.get("schema") != "nobu16.file-only-msg-recipe.v1":
        raise ValueError("unexpected message recipe schema")
    if (
        message.get("file_only") is not True
        or message.get("scope") != "main_menu"
        or message.get("version") != "0.1"
        or message.get("language") != "SC"
        or message.get("source", {}).get("relative_path") != "MSG_PK/SC/msgui.bin"
        or len(message.get("operations", [])) != 9
    ):
        raise ValueError("message recipe release contract is invalid")
    copies = {
        project_root / "tools" / "FileRecipeCore.cs": output / "tools" / "FileRecipeCore.cs",
        project_root / "tools" / "Invoke-FileOnlyPatch.ps1": output / "tools" / "Invoke-FileOnlyPatch.ps1",
        project_root / "release_templates" / "APPLY_KOREAN_PATCH.bat": output / "APPLY_KOREAN_PATCH.bat",
        project_root / "release_templates" / "RESTORE_ORIGINALS.bat": output / "RESTORE_ORIGINALS.bat",
        project_root / "release_templates" / "VERIFY_PACKAGE.bat": output / "VERIFY_PACKAGE.bat",
        project_root / "release_templates" / "README_KO.md": output / "README_KO.md",
        project_root / "release_templates" / "FILE_ONLY_POLICY_KO.md": output / "FILE_ONLY_POLICY_KO.md",
    }
    for source, destination in copies.items():
        checked_copy(source, destination, containment_root=project_root)

    staged_validation = output / "VALIDATION_EVIDENCE.json"
    checked_copy(
        validation_path,
        staged_validation,
        containment_root=validation_path.parent,
    )
    validation = read_json(staged_validation)
    if validation.get("schema") != "nobu16.file-only-validation-evidence.v1":
        raise ValueError("unexpected validation-evidence schema")
    required_checks = {
        "runtime_screen_verified",
        "file_only_apply_verified",
        "restore_verified",
        "bad_stock_rejected",
        "mixed_state_recovered",
        "process_running_refused",
    }
    checks = validation.get("checks")
    if not isinstance(checks, dict) or set(checks) != required_checks:
        raise ValueError("validation evidence has an unexpected check set")
    failed_checks = sorted(name for name in required_checks if checks.get(name) is not True)
    if failed_checks:
        raise ValueError("validation evidence contains failed checks: " + ", ".join(failed_checks))
    expected_artifacts = {
        "font_recipe_sha256": sha256(font_recipe_path),
        "message_recipe_sha256": sha256(staged_message_recipe),
        "installer_sha256": sha256(output / "tools" / "Invoke-FileOnlyPatch.ps1"),
        "recipe_core_sha256": sha256(output / "tools" / "FileRecipeCore.cs"),
        "apply_wrapper_sha256": sha256(output / "APPLY_KOREAN_PATCH.bat"),
        "restore_wrapper_sha256": sha256(output / "RESTORE_ORIGINALS.bat"),
        "verify_wrapper_sha256": sha256(output / "VERIFY_PACKAGE.bat"),
    }
    artifacts = validation.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("validation evidence has no artifact hashes")
    for key, expected_hash in expected_artifacts.items():
        if str(artifacts.get(key, "")).upper() != expected_hash:
            raise ValueError(f"validation evidence does not match {key}")
    forbidden_suffixes = {".py", ".pyc", ".pyo", ".exe", ".dll"}
    for path in output.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"public output contains a symlink: {path}")
        if path.is_file() and path.suffix.lower() in forbidden_suffixes:
            raise ValueError(f"public output contains a forbidden file type: {path}")

    files = []
    for path in sorted(candidate for candidate in output.rglob("*") if candidate.is_file()):
        relative = path.relative_to(output).as_posix()
        files.append({
            "path": relative,
            "size": path.stat().st_size,
            "sha256": sha256(path),
        })

    manifest = {
        "schema": "nobu16.korean-file-only-release.v1",
        "release_name": "NOBU16 Korean main-menu file-only v0.1",
        "architecture": "file-only-offline",
        "process_memory_access": False,
        "executable_modified": False,
        "registry_modified": False,
        "launches_game": False,
        "resident_component": False,
        "commercial_full_files_included": False,
        "requires_process_running": False,
        "runtime_validation": "passed",
        "install_restore_tested": True,
        "release_eligible": True,
        "target_files": ["MSG_PK/SC/msgui.bin", "RES_SC/res_lang.bin"],
        "payload_format": "recipes-and-deltas-only",
        "python_required_by_end_user": False,
        "registry_write": False,
        "official_launcher_language": "Simplified Chinese",
        "official_launcher_language_value": 2,
        "transaction_journal": True,
        "read_only_policy": ["game executables", "official launcher", "registry"],
        "font_provenance": provenance,
        "files": files,
    }
    (output / "release_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    try:
        audit_result = audit_public_release(output)
        if audit_result.get("status") != "PASS":
            rendered = json.dumps(audit_result.get("issues", []), ensure_ascii=False)
            raise ValueError("assembled public output failed the strict audit: " + rendered)
        output.rename(final_output)
    except Exception:
        manifest_path = output / "release_manifest.json"
        if manifest_path.is_file():
            manifest_path.unlink()
        raise
    return final_output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--font-component", type=Path, required=True)
    parser.add_argument("--message-recipe", type=Path, required=True)
    parser.add_argument("--validation-evidence", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    output = assemble(args)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
