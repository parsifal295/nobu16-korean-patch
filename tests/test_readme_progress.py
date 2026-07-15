import json
import pathlib
import subprocess
import sys
import unittest

from tools import update_readme_progress as readme_progress


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "data" / "public" / "translation_progress.v0.1.json"

EXPECTED_PK_STRING_TARGETS = {
    "MSG_PK/SC/msgui.bin": (5100, 4037),
    "MSG_PK/SC/msgev.bin": (17910, 12906),
    "MSG_PK/SC/msgdata.bin": (29210, 25534),
    "MSG_PK/SC/msgbre.bin": (3000, 2217),
    "MSG_PK/SC/msgire.bin": (122, 122),
    "MSG_PK/SC/msgstf.bin": (20, 8),
    "MSG_PK/SC/msggame.bin": (25598, 16482),
}
EXPECTED_SHARED_STRING_TARGETS = {
    "MSG/SC/strdata.bin": (32311, 26690),
}

EXPECTED_NON_TARGET_COVERAGE = {
    "MSG_PK/SC/msgui.bin": 0,
    "MSG_PK/SC/msgev.bin": 1598,
    "MSG_PK/SC/msgdata.bin": 784,
    "MSG_PK/SC/msgbre.bin": 0,
    "MSG_PK/SC/msgire.bin": 0,
    "MSG_PK/SC/msgstf.bin": 0,
    "MSG_PK/SC/msggame.bin": 0,
    "MSG/SC/strdata.bin": 0,
}


class ReadmeProgressTests(unittest.TestCase):
    def test_pinned_string_inventory_is_complete(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        actual = {
            resource["path"]: (
                resource["total_slots"],
                resource["translation_target_total"],
            )
            for resource in payload["resources"]
            if resource["kind"] == "strings"
        }
        self.assertEqual(actual, EXPECTED_PK_STRING_TARGETS)
        self.assertEqual(sum(target for _, target in actual.values()), 61306)
        shared = {
            resource["path"]: (
                resource["total_slots"],
                resource["translation_target_total"],
            )
            for resource in payload["shared_strings"]
        }
        self.assertEqual(shared, EXPECTED_SHARED_STRING_TARGETS)
        self.assertEqual(sum(target for _, target in shared.values()), 26690)
        self.assertEqual(payload["completed_statuses"], ["translated", "reviewed"])

    def test_msggame_record_and_literal_counts_are_explicit_and_included(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        actual = {
            resource["path"]: (
                resource["record_total"],
                resource["total_slots"],
                resource["translation_target_total"],
            )
            for resource in payload["resources"]
            if resource["path"].endswith("msggame.bin")
        }
        self.assertEqual(actual, {"MSG_PK/SC/msggame.bin": (21581, 25598, 16482)})

    def test_msggame_coordinate_overlay_is_counted_as_completed(self):
        coverage, completed = readme_progress.overlay_stats(
            [
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b01r0003_b02r0086_0197.v0.1.json",
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b02r0198_0297.v0.2.json",
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b02r0298_0565.v0.3.json",
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b02r0566_0665.v0.4.json",
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b02r0666_b04r0075.v0.5.json",
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b04r0076_b06r0559.v0.6.json",
            ],
            {"translated", "reviewed"},
        )
        self.assertEqual(900, len(coverage))
        self.assertEqual(coverage, completed)

    def test_shared_strdata_block_slot_overlays_are_exactly_counted(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        shared = payload["shared_strings"][0]
        targets = readme_progress.load_target_keys()[shared["path"]]
        stats = readme_progress.targeted_overlay_stats(
            shared["overlay_globs"], {"translated", "reviewed"}, targets
        )
        self.assertEqual(24425, stats.overlay_coverage)
        self.assertEqual(24425, stats.overlay_completed)
        self.assertEqual(24425, stats.target_coverage)
        self.assertEqual(24425, stats.target_completed)
        self.assertEqual(0, stats.non_target_coverage)
        self.assertEqual(0, stats.non_target_completed)
        self.assertEqual(2265, len(targets) - stats.target_completed)

    def test_progress_uses_target_intersection_and_separates_non_targets(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        completed_statuses = set(payload["completed_statuses"])
        targets = readme_progress.load_target_keys()
        non_target_coverage = {}
        target_done = 0
        non_target_done = 0
        raw_union_done = 0
        string_resources = [
            resource
            for resource in payload["resources"]
            if resource["kind"] == "strings"
        ] + payload["shared_strings"]
        for resource in string_resources:
            stats = readme_progress.targeted_overlay_stats(
                resource["overlay_globs"], completed_statuses, targets[resource["path"]]
            )
            non_target_coverage[resource["path"]] = stats.non_target_coverage
            self.assertEqual(stats.overlay_coverage, stats.target_coverage + stats.non_target_coverage)
            self.assertEqual(stats.overlay_completed, stats.target_completed + stats.non_target_completed)
            target_done += stats.target_completed
            non_target_done += stats.non_target_completed
            raw_union_done += stats.overlay_completed
        self.assertEqual(EXPECTED_NON_TARGET_COVERAGE, non_target_coverage)
        self.assertEqual(2382, sum(non_target_coverage.values()))
        self.assertEqual(raw_union_done, target_done + non_target_done)

        msgev = next(
            resource
            for resource in payload["resources"]
            if resource["path"] == "MSG_PK/SC/msgev.bin"
        )
        coverage, _completed = readme_progress.overlay_stats(
            msgev["overlay_globs"], completed_statuses
        )
        non_target_ids = sorted(
            key[1] for key in coverage - targets[msgev["path"]]
        )
        self.assertEqual(list(range(14799, 16397)), non_target_ids)

    def test_render_reports_exact_target_and_non_target_totals(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        completed_statuses = set(payload["completed_statuses"])
        targets = readme_progress.load_target_keys()
        pk_stats_by_path = {
            resource["path"]: readme_progress.targeted_overlay_stats(
                resource["overlay_globs"], completed_statuses, targets[resource["path"]]
            )
            for resource in payload["resources"]
            if resource["kind"] == "strings"
        }
        shared = payload["shared_strings"][0]
        shared_stats = readme_progress.targeted_overlay_stats(
            shared["overlay_globs"], completed_statuses, targets[shared["path"]]
        )
        done = sum(stats.target_completed for stats in pk_stats_by_path.values())
        non_target = sum(
            stats.non_target_coverage for stats in pk_stats_by_path.values()
        )
        rendered = readme_progress.render()
        self.assertIn(f"번역 완료 {done:,} / 61,306 ({done / 61306 * 100:.1f}%)", rendered)
        self.assertIn(f"비대상 활성 커버리지는 **{non_target:,}개**", rendered)
        self.assertIn(
            "`MSG/SC/strdata.bin`의 1개 문자열 리소스는 "
            "**번역 완료 24,425 / 26,690 (91.5%)**",
            rendered,
        )
        self.assertIn(
            "`MSG/SC/strdata.bin` | 24,425 / 26,690 | 24,425 | "
            "32,311 슬롯 | 91.5%",
            rendered,
        )
        self.assertEqual(24425, shared_stats.target_completed)
        self.assertEqual(0, shared_stats.non_target_coverage)
        for path in ("MSG_PK/SC/msgev.bin", "MSG_PK/SC/msgdata.bin"):
            stats = pk_stats_by_path[path]
            target = len(targets[path])
            self.assertIn(
                f"`{path}` | {stats.target_completed:,} / {target:,} | "
                f"{stats.target_coverage:,} (+{stats.non_target_coverage:,} 비대상 활성)",
                rendered,
            )

    def test_readme_progress_is_current(self):
        result = subprocess.run(
            [sys.executable, "-B", "tools/update_readme_progress.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pk_runtime_summary_keeps_shared_res_sc_visible(self):
        rendered = readme_progress.render()
        self.assertIn("PK 실행 경로 `MSG_PK/SC`의 7개 메시지 리소스", rendered)
        self.assertIn("PK 실행에서 함께 로드되는 공용 경로 `MSG/SC/strdata.bin`", rendered)
        self.assertIn("PK 공용 글꼴·리소스 경로 `RES_SC`의 2개 검증 단계", rendered)
        self.assertNotIn("MSG/SC/ev_strdata.bin", rendered)

    def test_render_uses_each_current_catalog_note(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        rendered = readme_progress.render()
        for resource in payload["resources"] + payload["shared_strings"]:
            self.assertIn(resource["note"], rendered)

    def test_readme_includes_only_verified_pk_loaded_shared_base_progress(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        progress_block = readme.split(readme_progress.START, 1)[1].split(
            readme_progress.END, 1
        )[0]
        self.assertIn("MSG/SC/strdata.bin", progress_block)
        self.assertNotIn("MSG/SC/ev_strdata.bin", progress_block)


if __name__ == "__main__":
    unittest.main()
