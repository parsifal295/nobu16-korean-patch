#!/usr/bin/env python3
"""Build a three-way BASE LOW title review dashboard."""

from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path


TITLE_COUNT = 110


def build(render_root: Path, candidate_report_path: Path, output_root: Path) -> Path:
    render_root = render_root.resolve()
    candidate = json.loads(candidate_report_path.resolve().read_text(encoding="utf-8"))
    render = json.loads((render_root / "report.json").read_text(encoding="utf-8"))
    if candidate.get("schema") != "nobu16.kr.base-low-title-consistency-candidate.v1":
        raise ValueError("candidate report schema differs")
    if render.get("schema") != "nobu16.kr.base-low-title-dimibang-render.v1":
        raise ValueError("render report schema differs")
    entries = {int(row["slot"]): row for row in candidate["entries"]}
    if sorted(entries) != list(range(TITLE_COUNT)):
        raise ValueError("candidate slot set differs")

    output_root = output_root.resolve()
    for folder in ("current", "approved", "bc3"):
        (output_root / folder).mkdir(parents=True, exist_ok=True)
    cards = []
    manifest_rows = []
    for slot in range(TITLE_COUNT):
        row = entries[slot]
        name = f"{slot:03d}.png"
        sources = {
            "current": Path(row["current_low_png"]["path"]),
            "approved": Path(row["source_low_png"]["path"]),
            "bc3": Path(row["bc3_roundtrip_png"]["path"]),
        }
        for folder, source in sources.items():
            shutil.copy2(source, output_root / folder / name)
        text_value = str(row["text"])
        safe_text = html.escape(text_value)
        search = html.escape(f"{slot:03d} {text_value}", quote=True)
        manifest_rows.append({"slot": slot, "text": text_value, "files": {key: f"{key}/{name}" for key in sources}})
        cards.append(f"""
      <section class="card" data-search="{search}">
        <header><span>{slot:03d}</span><h2>{safe_text}</h2></header>
        <div class="compare">
          <figure><figcaption>현재 BASE LOW</figcaption><img src="current/{name}" alt="현재 {slot:03d} {safe_text}" loading="lazy"></figure>
          <figure><figcaption>PORT3 승인본 50% 축소</figcaption><img src="approved/{name}" alt="축소 {slot:03d} {safe_text}" loading="lazy"></figure>
          <figure class="candidate"><figcaption>실제 LOW 후보 BC3 역변환</figcaption><img src="bc3/{name}" alt="BC3 {slot:03d} {safe_text}" loading="lazy"></figure>
        </div>
      </section>""")

    manifest = {
        "schema": "nobu16.kr.base-low-title-review.v1",
        "installed_game_files_modified": False,
        "title_count": TITLE_COUNT,
        "candidate": candidate["candidate"],
        "scope": candidate["scope"],
        "rows": manifest_rows,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "review_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    candidate_sha = html.escape(str(candidate["candidate"]["sha256"]))
    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BASE LOW 화면 제목 전체 QA</title>
<style>
:root{{color-scheme:dark;font-family:"Malgun Gothic",sans-serif;background:#111315;color:#ecece8}}*{{box-sizing:border-box}}body{{margin:0}}
.toolbar{{position:sticky;top:0;z-index:5;padding:14px 18px;background:rgba(17,19,21,.96);border-bottom:1px solid #383b3e}}h1{{margin:0 0 5px;font-size:20px}}.summary{{margin:0 0 10px;color:#bfc2bd;font-size:13px;overflow-wrap:anywhere}}input{{width:min(560px,100%);padding:9px 12px;border:1px solid #555a5d;border-radius:7px;color:#fff;background:#202326;font-size:15px}}
main{{max-width:1500px;margin:auto;padding:16px}}.card{{margin:0 0 15px;padding:13px;background:#1a1d1f;border:1px solid #34383b;border-radius:9px}}header{{display:flex;align-items:baseline;gap:9px;margin-bottom:9px}}header span{{min-width:42px;padding:3px 6px;border-radius:4px;background:#34383b;font:700 13px Consolas,monospace;text-align:center}}h2{{margin:0;font-size:17px}}.compare{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}}figure{{margin:0;padding:8px;background:#0b0c0d;border:1px solid #2f3335;border-radius:6px}}figure.candidate{{border-color:#74776e}}figcaption{{margin-bottom:6px;color:#b6b9b4;font-size:12px}}.candidate figcaption{{color:#e5e2cd;font-weight:700}}img{{display:block;width:100%;height:auto;aspect-ratio:4/1;object-fit:contain;image-rendering:auto;cursor:zoom-in}}dialog{{width:min(96vw,650px);padding:12px;border:1px solid #74776e;border-radius:8px;background:#08090a}}dialog::backdrop{{background:rgba(0,0,0,.78)}}dialog img{{width:512px;max-width:100%;cursor:zoom-out}}.hidden{{display:none}}@media(max-width:900px){{.compare{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="toolbar"><h1>BASE LOW 화면 제목 전체 QA — 음식디미방체</h1><p class="summary">110개 · 512×128 · 현재 / 축소 PNG / 실제 BC3 · 후보 SHA-256 {candidate_sha} · Steam 미적용</p><input id="filter" type="search" placeholder="슬롯 번호 또는 문구 검색"></div>
<main>{''.join(cards)}</main><dialog id="zoom"><img alt="확대 이미지"></dialog>
<script>const f=document.querySelector('#filter'),cs=[...document.querySelectorAll('.card')];f.addEventListener('input',()=>{{const q=f.value.trim().toLowerCase();for(const c of cs)c.classList.toggle('hidden',q&&!c.dataset.search.toLowerCase().includes(q))}});const z=document.querySelector('#zoom'),zi=z.querySelector('img');document.addEventListener('click',e=>{{if(e.target.matches('.card img')){{zi.src=e.target.src;zi.alt=e.target.alt;z.showModal()}}}});z.addEventListener('click',()=>z.close());</script>
</body></html>"""
    index = output_root / "index.html"
    index.write_text(page, encoding="utf-8")
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-root", type=Path, required=True)
    parser.add_argument("--candidate-report", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    index = build(args.render_root, args.candidate_report, args.output_root)
    print(json.dumps({"dashboard": str(index), "title_count": TITLE_COUNT}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
