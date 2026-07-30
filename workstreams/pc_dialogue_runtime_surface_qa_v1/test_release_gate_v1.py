#!/usr/bin/env python3
"""Release-blocker tests for the final-candidate runtime surface gate."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
GATE_PATH = WORKSTREAM / "gate_final_candidate_v1.py"
VERIFIER_PATH = WORKSTREAM / "verify_release_gate_v1.ps1"
RESOURCE_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "rust_patcher_v1"
    / "rust"
    / "tools"
    / "New-V090ResourceTarget.ps1"
)


def load_gate() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_runtime_surface_final_candidate_gate_v1",
        GATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {GATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GATE = load_gate()
AUDIT = GATE.AUDIT


def resource_audit(
    resource: str,
    blob: bytes,
    *,
    issues: tuple[Any, ...] = (),
) -> Any:
    return AUDIT.ResourceAudit(
        resource=resource,
        path="<test>",
        sha256=GATE.sha256_bytes(blob),
        record_count=1,
        literal_count=0,
        decoded_record_count=1,
        issues=issues,
    )


def terminal_resource(
    resource: str,
    blob: bytes,
    *,
    issues: tuple[Any, ...] = (),
) -> Any:
    return GATE.TERMINAL.TerminalBoundaryResource(
        resource=resource,
        path="<test>",
        sha256=GATE.sha256_bytes(blob),
        record_count=1,
        decoded_record_count=1,
        call_site_count=0,
        terminal_suffix_variant_count=0,
        issues=issues,
    )


def call_assembly_resource(
    resource: str,
    blob: bytes,
    *,
    issues: tuple[Any, ...] = (),
) -> Any:
    return GATE.CALL_ASSEMBLY.CallAssemblyResource(
        resource=resource,
        path="<test>",
        sha256=GATE.sha256_bytes(blob),
        record_count=1,
        decoded_record_count=1,
        call_record_count=0,
        call_site_count=0,
        unique_call_target_count=0,
        rendered_call_variant_count=0,
        assembled_record_variant_count=1,
        synthetic_selector_call_record_count=0,
        issues=issues,
    )


def call_assembly_resources(
    base: bytes,
    pk: bytes,
) -> tuple[Any, Any]:
    return (
        call_assembly_resource("base_msggame", base),
        call_assembly_resource("pk_msggame", pk),
    )


def candidate_guardrails(
    base: bytes,
    pk: bytes,
) -> dict[str, Any]:
    hashes = {
        "MSG/JP/msggame.bin": GATE.sha256_bytes(base),
        "MSG_PK/JP/msggame.bin": GATE.sha256_bytes(pk),
    }
    structure_resources = {
        path: {
            "candidate": {"sha256": sha256},
            "issue_count": 0,
            "category_counts": {},
            "literal_changed_count": 0,
            "allowed_mutation_count": (
                GATE.STRUCTURE.EXPECTED_PK_REVIEWED_MUTATION_COUNT
                if path == "MSG_PK/JP/msggame.bin"
                else GATE.STRUCTURE.EXPECTED_BASE_CALL_ALLOWLIST_COUNT
            ),
            "issues": [],
        }
        for path, sha256 in hashes.items()
    }
    width_resources = {
        path: {
            "candidate": {"sha256": sha256},
            "issue_count": 0,
            "issue_coordinate_count": 0,
            "category_counts": {},
            "issues": [],
        }
        for path, sha256 in hashes.items()
    }
    return {
        "structure_report": {
            "schema": GATE.STRUCTURE.SCHEMA,
            "status": "PASS",
            "issue_count": 0,
            "resources": structure_resources,
            "pk_reviewed_retarget_contract": {
                "source_sha256":
                    GATE.STRUCTURE.EXPECTED_PK_SOURCE_SHA256,
                "candidate_sha256": hashes["MSG_PK/JP/msggame.bin"],
                "operation_count":
                    GATE.STRUCTURE.EXPECTED_PK_REVIEWED_OPERATION_COUNT,
                "operation_sha256":
                    GATE.STRUCTURE.EXPECTED_PK_REVIEWED_OPERATION_SHA256,
                "component_mutation_count":
                    GATE.STRUCTURE.EXPECTED_PK_REVIEWED_MUTATION_COUNT,
                "component_contract_sha256":
                    GATE.STRUCTURE.EXPECTED_PK_REVIEWED_COMPONENT_SHA256,
                "exact_coordinate_component_before_after_hash_bound":
                    True,
                "literal_bodies_omitted": True,
            },
        },
        "relative_width_report": {
            "schema": GATE.WIDTH.SCHEMA,
            "status": "PASS",
            "issue_count": 0,
            "resources": width_resources,
        },
        "stage_width_report": {
            "schema":
                "nobu16.kr.base-remediation-stage-relative-width.v1",
            "status": "PASS",
            "issue_count": 0,
            "stages": {},
            "call_semantic_rebuild_excluded_from_plus_24_gate": True,
        },
        "call_semantic_report": {
            "schema": "nobu16.kr.base-call-assembly-remediation.v1",
            "status": "PASS",
            "final_issue_count": 0,
            "source_sha256": "A" * 64,
            "candidate_sha256": "B" * 64,
            "literal_replacement_count": 0,
            "literal_before_after_hash_contract": {
                "entry_count": 0,
                "entry_sha256": GATE.sha256_bytes(b""),
                "entries": [],
                "source_or_translation_bodies_omitted": True,
            },
        },
    }


class FinalCandidateGateTests(unittest.TestCase):
    def test_real_final_candidates_build_pass(self) -> None:
        base = GATE.STRUCTURE.DEFAULT_BASE_CANDIDATE
        pk = GATE.STRUCTURE.DEFAULT_PK_CANDIDATE
        payload = GATE.build_gate(base, pk)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["runtime_completion"], "PASS")
        self.assertEqual(payload["issue_count"], 0)
        self.assertEqual(
            payload["resources"]["MSG/JP/msggame.bin"]["sha256"],
            "51D5B250F03F084A49B165D1C23DB6771363DBB2A22CB298A23E4A3CF313B5DC",
        )
        self.assertEqual(
            payload["resources"]["MSG_PK/JP/msggame.bin"]["sha256"],
            GATE.STRUCTURE.EXPECTED_PK_CANDIDATE_SHA256,
        )
        structure = payload["audit_contract"]["candidate_structure"]
        self.assertEqual(
            structure["pk_reviewed_operation_count"],
            GATE.STRUCTURE.EXPECTED_PK_REVIEWED_OPERATION_COUNT,
        )
        self.assertEqual(
            structure["pk_reviewed_component_mutation_count"],
            GATE.STRUCTURE.EXPECTED_PK_REVIEWED_MUTATION_COUNT,
        )
        self.assertTrue(
            structure[
                "pk_exact_coordinate_component_before_after_hash_bound"
            ]
        )

    def test_zero_issues_is_the_only_runtime_completion_pass(self) -> None:
        base = b"base-candidate"
        pk = b"pk-candidate"
        passed = GATE.build_gate_from_audits(
            (
                resource_audit("base_msggame", base),
                resource_audit("pk_msggame", pk),
            ),
            (
                terminal_resource("base_msggame", base),
                terminal_resource("pk_msggame", pk),
            ),
            call_assembly_resources(base, pk),
            sizes={
                "base_msggame": len(base),
                "pk_msggame": len(pk),
            },
            **candidate_guardrails(base, pk),
        )
        self.assertEqual(passed["status"], "PASS")
        self.assertEqual(passed["runtime_completion"], "PASS")
        self.assertTrue(passed["runtime_completion_allowed"])
        self.assertEqual(passed["issue_count"], 0)

        defect = AUDIT.Issue(
            resource="pk_msggame",
            category="unresolved_dual_particle",
            block_id=1,
            record_id=2,
            literal_id=0,
            text_sha256="0" * 64,
            details={"tokens": ("이(가)",)},
        )
        failed = GATE.build_gate_from_audits(
            (
                resource_audit("base_msggame", base),
                resource_audit("pk_msggame", pk, issues=(defect,)),
            ),
            (
                terminal_resource("base_msggame", base),
                terminal_resource("pk_msggame", pk),
            ),
            call_assembly_resources(base, pk),
            sizes={
                "base_msggame": len(base),
                "pk_msggame": len(pk),
            },
            **candidate_guardrails(base, pk),
        )
        self.assertEqual(failed["status"], "FAIL")
        self.assertEqual(failed["runtime_completion"], "FAIL")
        self.assertFalse(failed["runtime_completion_allowed"])
        self.assertEqual(failed["issue_count"], 1)
        self.assertNotIn("text", failed["issues"][0])

    def test_terminal_boundary_issue_blocks_runtime_completion(self) -> None:
        base = b"base-candidate"
        pk = b"pk-candidate"
        defect = GATE.TERMINAL.TerminalBoundaryIssue(
            resource="base_msggame",
            category="completed_prefix_terminal_suffix",
            block_id=1,
            record_id=2,
            literal_id=0,
            component_index=2,
            call_target="0:1",
            prefix_family="formal_declarative",
            suffix_family="bare_terminal",
            prefix_sha256="0" * 64,
            suffix_sha256="1" * 64,
            combined_sha256="2" * 64,
        )
        failed = GATE.build_gate_from_audits(
            (
                resource_audit("base_msggame", base),
                resource_audit("pk_msggame", pk),
            ),
            (
                terminal_resource(
                    "base_msggame",
                    base,
                    issues=(defect,),
                ),
                terminal_resource("pk_msggame", pk),
            ),
            call_assembly_resources(base, pk),
            sizes={
                "base_msggame": len(base),
                "pk_msggame": len(pk),
            },
            **candidate_guardrails(base, pk),
        )
        self.assertFalse(failed["runtime_completion_allowed"])
        self.assertEqual(failed["issue_count"], 1)
        self.assertEqual(
            failed["category_counts"],
            {"completed_prefix_terminal_suffix": 1},
        )

    def run_verifier(
        self,
        evidence: Path,
        base: Path,
        pk: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(VERIFIER_PATH),
                "-Evidence",
                str(evidence),
                "-BaseDialogueMsggame",
                str(base),
                "-PkDialogueMsggame",
                str(pk),
            ],
            check=False,
            capture_output=True,
            encoding="utf-8",
        )

    def test_powershell_verifier_binds_both_candidate_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base_bytes = b"base-candidate"
            pk_bytes = b"pk-candidate"
            base = root / "base.bin"
            pk = root / "pk.bin"
            evidence = root / "gate.json"
            base.write_bytes(base_bytes)
            pk.write_bytes(pk_bytes)
            payload = GATE.build_gate_from_audits(
                (
                    resource_audit("base_msggame", base_bytes),
                    resource_audit("pk_msggame", pk_bytes),
                ),
                (
                    terminal_resource("base_msggame", base_bytes),
                    terminal_resource("pk_msggame", pk_bytes),
                ),
                call_assembly_resources(base_bytes, pk_bytes),
                sizes={
                    "base_msggame": len(base_bytes),
                    "pk_msggame": len(pk_bytes),
                },
                **candidate_guardrails(base_bytes, pk_bytes),
            )
            evidence.write_text(
                GATE.canonical_json(payload),
                encoding="utf-8",
            )

            accepted = self.run_verifier(evidence, base, pk)
            self.assertEqual(
                accepted.returncode,
                0,
                msg=accepted.stdout + accepted.stderr,
            )

            pk.write_bytes(pk_bytes + b"-drift")
            rejected = self.run_verifier(evidence, base, pk)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("binding mismatch", rejected.stderr)

    def test_powershell_verifier_rejects_forged_pass_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base_bytes = b"base-candidate"
            pk_bytes = b"pk-candidate"
            base = root / "base.bin"
            pk = root / "pk.bin"
            evidence = root / "gate.json"
            base.write_bytes(base_bytes)
            pk.write_bytes(pk_bytes)
            payload = GATE.build_gate_from_audits(
                (
                    resource_audit("base_msggame", base_bytes),
                    resource_audit("pk_msggame", pk_bytes),
                ),
                (
                    terminal_resource("base_msggame", base_bytes),
                    terminal_resource("pk_msggame", pk_bytes),
                ),
                call_assembly_resources(base_bytes, pk_bytes),
                sizes={
                    "base_msggame": len(base_bytes),
                    "pk_msggame": len(pk_bytes),
                },
                **candidate_guardrails(base_bytes, pk_bytes),
            )
            payload["issue_count"] = 1
            evidence.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            rejected = self.run_verifier(evidence, base, pk)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("issue count is not zero", rejected.stderr)

    def test_powershell_verifier_rejects_stale_audit_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base_bytes = b"base-candidate"
            pk_bytes = b"pk-candidate"
            base = root / "base.bin"
            pk = root / "pk.bin"
            evidence = root / "gate.json"
            base.write_bytes(base_bytes)
            pk.write_bytes(pk_bytes)
            payload = GATE.build_gate_from_audits(
                (
                    resource_audit("base_msggame", base_bytes),
                    resource_audit("pk_msggame", pk_bytes),
                ),
                (
                    terminal_resource("base_msggame", base_bytes),
                    terminal_resource("pk_msggame", pk_bytes),
                ),
                call_assembly_resources(base_bytes, pk_bytes),
                sizes={
                    "base_msggame": len(base_bytes),
                    "pk_msggame": len(pk_bytes),
                },
                **candidate_guardrails(base_bytes, pk_bytes),
            )
            payload["audit_contract"]["engine_sha256"] = "0" * 64
            evidence.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            rejected = self.run_verifier(evidence, base, pk)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("audit engine binding mismatch", rejected.stderr)

    def test_powershell_verifier_rejects_stale_selector_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base_bytes = b"base-candidate"
            pk_bytes = b"pk-candidate"
            base = root / "base.bin"
            pk = root / "pk.bin"
            evidence = root / "gate.json"
            base.write_bytes(base_bytes)
            pk.write_bytes(pk_bytes)
            payload = GATE.build_gate_from_audits(
                (
                    resource_audit("base_msggame", base_bytes),
                    resource_audit("pk_msggame", pk_bytes),
                ),
                (
                    terminal_resource("base_msggame", base_bytes),
                    terminal_resource("pk_msggame", pk_bytes),
                ),
                call_assembly_resources(base_bytes, pk_bytes),
                sizes={
                    "base_msggame": len(base_bytes),
                    "pk_msggame": len(pk_bytes),
                },
                **candidate_guardrails(base_bytes, pk_bytes),
            )
            payload["audit_contract"]["selector_domain_contract"][
                "sha256"
            ] = "0" * 64
            evidence.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            rejected = self.run_verifier(evidence, base, pk)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn(
                "selector-domain hash binding mismatch",
                rejected.stderr,
            )

    def test_powershell_verifier_rejects_stale_terminal_detector(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base_bytes = b"base-candidate"
            pk_bytes = b"pk-candidate"
            base = root / "base.bin"
            pk = root / "pk.bin"
            evidence = root / "gate.json"
            base.write_bytes(base_bytes)
            pk.write_bytes(pk_bytes)
            payload = GATE.build_gate_from_audits(
                (
                    resource_audit("base_msggame", base_bytes),
                    resource_audit("pk_msggame", pk_bytes),
                ),
                (
                    terminal_resource("base_msggame", base_bytes),
                    terminal_resource("pk_msggame", pk_bytes),
                ),
                call_assembly_resources(base_bytes, pk_bytes),
                sizes={
                    "base_msggame": len(base_bytes),
                    "pk_msggame": len(pk_bytes),
                },
                **candidate_guardrails(base_bytes, pk_bytes),
            )
            payload["audit_contract"]["terminal_boundary_detector"][
                "engine_sha256"
            ] = "0" * 64
            evidence.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            rejected = self.run_verifier(evidence, base, pk)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn(
                "terminal-boundary detector binding mismatch",
                rejected.stderr,
            )

    def test_v090_target_builder_requires_gate_before_output(self) -> None:
        script = RESOURCE_BUILDER_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "[string]$DialogueRuntimeSurfaceEvidence",
            script,
        )
        self.assertIn(
            "dialogue_runtime_surface_gate = [ordered]@{",
            script,
        )
        verifier_call = script.index("& $runtimeSurfaceVerifier")
        output_creation = script.index(
            "New-Item -ItemType Directory -Path $outputRoot"
        )
        self.assertLess(verifier_call, output_creation)


if __name__ == "__main__":
    unittest.main()
