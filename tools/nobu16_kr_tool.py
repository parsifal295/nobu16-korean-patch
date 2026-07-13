#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import date
from pathlib import Path


def run_cmd(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def root_from_here() -> Path:
    # this file: <root>/KR_PATCH_WORK/tools/nobu16_kr_tool.py
    return Path(__file__).resolve().parents[2]


def cmd_make_review(args: argparse.Namespace) -> int:
    root = root_from_here()
    tools = root / "KR_PATCH_WORK" / "tools"
    data = root / "KR_PATCH_WORK" / "data" / "work_templates"
    reports = root / "KR_PATCH_WORK" / "reports"

    context_csv = data / f"msggame_context_template.{args.suffix}.csv"
    context_summary = data / f"msggame_context_template.{args.suffix}.summary.json"
    review_csv = data / f"msggame_review_pack.{args.runs_suffix}.{args.suffix}.csv"
    review_md = reports / f"msggame_review_pack_{args.runs_suffix}_{args.suffix}_{args.date}.md"

    run_cmd(
        [
            "python3",
            str(tools / "msggame_context_extract.py"),
            "--input",
            str(root / "MSG_PK" / "EN" / "msggame.bin"),
            "--out-csv",
            str(context_csv),
            "--out-summary",
            str(context_summary),
            "--ctx-max-scan",
            str(args.ctx_max_scan),
            "--ctx-stop-bad",
            str(args.ctx_stop_bad),
            "--ctx-max-chars",
            str(args.ctx_max_chars),
        ]
    )
    run_cmd(
        [
            "python3",
            str(tools / "build_msggame_review_pack.py"),
            "--runs-csv",
            str(root / args.runs_csv),
            "--context-csv",
            str(context_csv),
            "--out-csv",
            str(review_csv),
            "--out-md",
            str(review_md),
            "--suggest-map",
            str(root / args.suggest_map),
        ]
    )
    print(f"context_csv={context_csv}")
    print(f"review_csv={review_csv}")
    print(f"review_md={review_md}")
    return 0


def cmd_make_draft(args: argparse.Namespace) -> int:
    root = root_from_here()
    tools = root / "KR_PATCH_WORK" / "tools"

    input_runs = root / args.input_runs_csv
    if args.apply_known_terms:
        stage1 = root / args.stage1_runs_csv
        run_cmd(
            [
                "python3",
                str(tools / "fill_msggame_known_terms.py"),
                "--input-csv",
                str(input_runs),
                "--output-csv",
                str(stage1),
            ]
        )
        base_runs = stage1
    else:
        base_runs = input_runs

    out_runs = root / args.out_runs_csv
    run_cmd(
        [
            "python3",
            str(tools / "apply_review_suggestions.py"),
            "--runs-csv",
            str(base_runs),
            "--review-csv",
            str(root / args.review_csv),
            "--out-csv",
            str(out_runs),
            "--suggest-reason",
            args.suggest_reason,
        ]
    )
    run_cmd(
        [
            "python3",
            str(tools / "msgpk_ascii_u16_run_patch.py"),
            "validate",
            "--input-csv",
            str(out_runs),
            "--allow-shorter",
        ]
    )
    print(f"draft_runs={out_runs}")
    return 0


def cmd_run_round(args: argparse.Namespace) -> int:
    root = root_from_here()
    tools = root / "KR_PATCH_WORK" / "tools"
    cmd = [
        "python3",
        str(tools / "run_translation_round.py"),
        "--tag",
        args.tag,
        "--runs-csv",
        args.runs_csv,
    ]
    if args.strict_original:
        cmd.append("--strict-original")
    run_cmd(cmd)
    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    root = root_from_here()
    tools = root / "KR_PATCH_WORK" / "tools"
    data = root / "KR_PATCH_WORK" / "data" / "work_templates"
    reports = root / "KR_PATCH_WORK" / "reports"

    stage_runs = root / args.input_runs_csv
    if args.apply_known_terms:
        known_runs = data / f"msggame_ascii_u16_runs_template.{args.round_tag}.known.csv"
        run_cmd(
            [
                "python3",
                str(tools / "fill_msggame_known_terms.py"),
                "--input-csv",
                str(stage_runs),
                "--output-csv",
                str(known_runs),
            ]
        )
        stage_runs = known_runs

    context_csv = data / f"msggame_context_template.{args.round_tag}.csv"
    context_summary = data / f"msggame_context_template.{args.round_tag}.summary.json"
    review_csv = data / f"msggame_review_pack.{args.round_tag}.csv"
    review_md = reports / f"msggame_review_pack_{args.round_tag}_{args.date}.md"
    draft_runs = data / f"msggame_ascii_u16_runs_template.{args.round_tag}.draft.csv"

    run_cmd(
        [
            "python3",
            str(tools / "msggame_context_extract.py"),
            "--input",
            str(root / "MSG_PK" / "EN" / "msggame.bin"),
            "--out-csv",
            str(context_csv),
            "--out-summary",
            str(context_summary),
            "--ctx-max-scan",
            str(args.ctx_max_scan),
            "--ctx-stop-bad",
            str(args.ctx_stop_bad),
            "--ctx-max-chars",
            str(args.ctx_max_chars),
        ]
    )
    run_cmd(
        [
            "python3",
            str(tools / "build_msggame_review_pack.py"),
            "--runs-csv",
            str(stage_runs),
            "--context-csv",
            str(context_csv),
            "--out-csv",
            str(review_csv),
            "--out-md",
            str(review_md),
            "--suggest-map",
            str(root / args.suggest_map),
        ]
    )
    run_cmd(
        [
            "python3",
            str(tools / "apply_review_suggestions.py"),
            "--runs-csv",
            str(stage_runs),
            "--review-csv",
            str(review_csv),
            "--out-csv",
            str(draft_runs),
            "--suggest-reason",
            args.suggest_reason,
        ]
    )
    run_cmd(
        [
            "python3",
            str(tools / "msgpk_ascii_u16_run_patch.py"),
            "validate",
            "--input-csv",
            str(draft_runs),
            "--allow-shorter",
        ]
    )

    round_cmd = [
        "python3",
        str(tools / "run_translation_round.py"),
        "--tag",
        args.round_tag,
        "--runs-csv",
        str(draft_runs.relative_to(root)),
    ]
    if args.strict_original:
        round_cmd.append("--strict-original")
    run_cmd(round_cmd)

    print(f"round_tag={args.round_tag}")
    print(f"context_csv={context_csv}")
    print(f"review_csv={review_csv}")
    print(f"draft_runs={draft_runs}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Nobu16 KR translation toolkit (msggame review + master round automation)"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_review = sub.add_parser("make-review", help="Build long-context + review pack")
    p_review.add_argument(
        "--runs-csv",
        default="KR_PATCH_WORK/data/work_templates/msggame_ascii_u16_runs_template.ko_v4_draft.csv",
    )
    p_review.add_argument("--runs-suffix", default="ko_v4_draft")
    p_review.add_argument("--suffix", default="long_v3")
    p_review.add_argument("--date", default=date.today().isoformat())
    p_review.add_argument("--ctx-max-scan", type=int, default=2048)
    p_review.add_argument("--ctx-stop-bad", type=int, default=64)
    p_review.add_argument("--ctx-max-chars", type=int, default=800)
    p_review.add_argument(
        "--suggest-map",
        default="KR_PATCH_WORK/data/work_templates/msggame_suggestion_map.json",
    )
    p_review.set_defaults(func=cmd_make_review)

    p_draft = sub.add_parser("make-draft", help="Apply known terms + review suggestions to build draft runs")
    p_draft.add_argument(
        "--input-runs-csv",
        default="KR_PATCH_WORK/data/work_templates/msggame_ascii_u16_runs_template.ko_v3.csv",
    )
    p_draft.add_argument("--apply-known-terms", action="store_true", default=False)
    p_draft.add_argument(
        "--stage1-runs-csv",
        default="KR_PATCH_WORK/data/work_templates/msggame_ascii_u16_runs_template.ko_stage1.csv",
    )
    p_draft.add_argument(
        "--review-csv",
        default="KR_PATCH_WORK/data/work_templates/msggame_review_pack.ko_v3.long_v2.csv",
    )
    p_draft.add_argument(
        "--out-runs-csv",
        default="KR_PATCH_WORK/data/work_templates/msggame_ascii_u16_runs_template.ko_v4_draft.csv",
    )
    p_draft.add_argument("--suggest-reason", default="safe_ui_token")
    p_draft.set_defaults(func=cmd_make_draft)

    p_round = sub.add_parser("run-round", help="Run one master translation round")
    p_round.add_argument("--tag", required=True)
    p_round.add_argument("--runs-csv", required=True)
    p_round.add_argument("--strict-original", action="store_true", default=False)
    p_round.set_defaults(func=cmd_run_round)

    p_pipe = sub.add_parser("pipeline", help="Known terms + review + suggestions + round in one command")
    p_pipe.add_argument(
        "--input-runs-csv",
        default="KR_PATCH_WORK/data/work_templates/msggame_ascii_u16_runs_template.ko_v3.csv",
    )
    p_pipe.add_argument("--round-tag", required=True)
    p_pipe.add_argument("--apply-known-terms", dest="apply_known_terms", action="store_true")
    p_pipe.add_argument("--no-apply-known-terms", dest="apply_known_terms", action="store_false")
    p_pipe.set_defaults(apply_known_terms=True)
    p_pipe.add_argument("--suggest-reason", default="safe_ui_token")
    p_pipe.add_argument(
        "--suggest-map",
        default="KR_PATCH_WORK/data/work_templates/msggame_suggestion_map.json",
    )
    p_pipe.add_argument("--ctx-max-scan", type=int, default=2048)
    p_pipe.add_argument("--ctx-stop-bad", type=int, default=64)
    p_pipe.add_argument("--ctx-max-chars", type=int, default=800)
    p_pipe.add_argument("--date", default=date.today().isoformat())
    p_pipe.add_argument("--strict-original", action="store_true", default=False)
    p_pipe.set_defaults(func=cmd_pipeline)
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
