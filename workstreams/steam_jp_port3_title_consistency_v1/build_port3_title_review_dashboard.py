#!/usr/bin/env python3
"""Build a three-way review dashboard for all PORT3 title slots."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path


TITLE_COUNT = 110
RENDER_SCHEMA = "nobu16.kr.port3-title-consistency-dimibang-preview.v1"
CANDIDATE_SCHEMA = "nobu16.kr.port3-title-consistency-candidate.v1"
REVIEW_SCHEMA = "nobu16.kr.port3-title-consistency-review.v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def copy_asset(source: Path, destination: Path) -> dict[str, int | str]:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {
        "file": destination.as_posix(),
        "size": destination.stat().st_size,
        "sha256": sha256(destination),
    }


def build(render_root: Path, candidate_report_path: Path, output_root: Path) -> Path:
    render_root = render_root.resolve()
    candidate_report_path = candidate_report_path.resolve()
    output_root = output_root.resolve()
    render = json.loads((render_root / "report.json").read_text(encoding="utf-8"))
    candidate = json.loads(candidate_report_path.read_text(encoding="utf-8"))
    if render.get("schema") != RENDER_SCHEMA:
        raise ValueError("render report schema differs")
    if candidate.get("schema") != CANDIDATE_SCHEMA:
        raise ValueError("candidate report schema differs")
    if len(render.get("entries", [])) != TITLE_COUNT or len(candidate.get("entries", [])) != TITLE_COUNT:
        raise ValueError("reports must each cover all 110 title slots")

    render_entries = {int(row["slot"]): row for row in render["entries"]}
    candidate_entries = {int(row["slot"]): row for row in candidate["entries"]}
    if sorted(render_entries) != list(range(TITLE_COUNT)) or sorted(candidate_entries) != list(range(TITLE_COUNT)):
        raise ValueError("report slot set differs")

    rows = []
    cards = []
    for slot in range(TITLE_COUNT):
        rendered = render_entries[slot]
        packed = candidate_entries[slot]
        if rendered["text"] != packed["text"]:
            raise ValueError(f"title text differs at slot {slot}")
        name = f"{slot:03d}.png"
        current_source = render_root / rendered["current"]["file"]
        approved_source = render_root / rendered["variants"]["dimibang"]["file"]
        bc3_source = Path(packed["bc3_roundtrip_png"]["path"])
        current_asset = copy_asset(current_source, output_root / "current" / name)
        approved_asset = copy_asset(approved_source, output_root / "approved" / name)
        bc3_asset = copy_asset(bc3_source, output_root / "bc3" / name)
        text_value = str(rendered["text"])
        rows.append(
            {
                "slot": slot,
                "text": text_value,
                "note": rendered.get("note", ""),
                "current": current_asset,
                "approved": approved_asset,
                "bc3_roundtrip": bc3_asset,
            }
        )
        safe_text = html.escape(text_value)
        search_value = html.escape(f"{slot:03d} {text_value}", quote=True)
        cards.append(
            f"""
      <section class="title-card" data-search="{search_value}">
        <header><span class="slot">{slot:03d}</span><h2>{safe_text}</h2></header>
        <div class="compare">
          <figure><figcaption>현재 기준본</figcaption><img src="current/{name}" alt="현재 {slot:03d} {safe_text}" loading="lazy"></figure>
          <figure><figcaption>승인 렌더</figcaption><img src="approved/{name}" alt="승인 렌더 {slot:03d} {safe_text}" loading="lazy"></figure>
          <figure class="candidate"><figcaption>실제 후보 BC3 역변환</figcaption><img src="bc3/{name}" alt="BC3 후보 {slot:03d} {safe_text}" loading="lazy"></figure>
        </div>
      </section>"""
        )

    manifest = {
        "schema": REVIEW_SCHEMA,
        "private_review_output": True,
        "installed_game_files_modified": False,
        "title_count": TITLE_COUNT,
        "candidate": candidate["candidate"],
        "scope": candidate["scope"],
        "rows": rows,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "review_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    candidate_sha = html.escape(str(candidate["candidate"]["sha256"]))
    page = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PORT3 화면 제목 전체 QA</title>
  <style>
    :root {{ color-scheme: dark; font-family: "Malgun Gothic", sans-serif; background: #111315; color: #ecece8; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    .toolbar {{ position: sticky; top: 0; z-index: 5; padding: 14px 18px; background: rgba(17,19,21,.96); border-bottom: 1px solid #383b3e; backdrop-filter: blur(10px); }}
    .toolbar h1 {{ margin: 0 0 5px; font-size: 20px; }}
    .summary {{ margin: 0 0 10px; color: #bfc2bd; font-size: 13px; overflow-wrap: anywhere; }}
    input {{ width: min(560px, 100%); padding: 9px 12px; border: 1px solid #555a5d; border-radius: 7px; color: #fff; background: #202326; font-size: 15px; }}
    main {{ max-width: 1660px; margin: 0 auto; padding: 16px; }}
    .title-card {{ margin: 0 0 15px; padding: 13px; background: #1a1d1f; border: 1px solid #34383b; border-radius: 9px; }}
    .title-card header {{ display: flex; align-items: baseline; gap: 9px; margin-bottom: 9px; }}
    .slot {{ min-width: 42px; padding: 3px 6px; border-radius: 4px; background: #34383b; color: #d9dbd6; font: 700 13px Consolas, monospace; text-align: center; }}
    h2 {{ margin: 0; font-size: 17px; }}
    .compare {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
    figure {{ margin: 0; padding: 8px; background: #0b0c0d; border: 1px solid #2f3335; border-radius: 6px; }}
    figure.candidate {{ border-color: #74776e; }}
    figcaption {{ margin: 0 0 6px; color: #b6b9b4; font-size: 12px; }}
    figure.candidate figcaption {{ color: #e5e2cd; font-weight: 700; }}
    img {{ display: block; width: 100%; height: auto; aspect-ratio: 4 / 1; object-fit: contain; image-rendering: auto; cursor: zoom-in; }}
    dialog {{ width: min(96vw, 1100px); padding: 12px; border: 1px solid #74776e; border-radius: 8px; background: #08090a; color: #fff; }}
    dialog::backdrop {{ background: rgba(0,0,0,.78); }}
    dialog img {{ width: 1024px; max-width: 100%; cursor: zoom-out; }}
    .hidden {{ display: none; }}
    @media (max-width: 900px) {{ .compare {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="toolbar">
    <h1>PORT3 화면 제목 전체 QA — 음식디미방체</h1>
    <p class="summary">110개 · 현재 / 승인 렌더 / 실제 BC3 역변환 · 후보 SHA-256 {candidate_sha} · Steam 미적용</p>
    <input id="filter" type="search" placeholder="슬롯 번호 또는 문구 검색" autocomplete="off">
  </div>
  <main>{''.join(cards)}
  </main>
  <dialog id="zoom"><img alt="확대 이미지"></dialog>
  <script>
    const filter = document.querySelector('#filter');
    const cards = [...document.querySelectorAll('.title-card')];
    filter.addEventListener('input', () => {{
      const q = filter.value.trim().toLowerCase();
      for (const card of cards) card.classList.toggle('hidden', q && !card.dataset.search.toLowerCase().includes(q));
    }});
    const zoom = document.querySelector('#zoom');
    const zoomImage = zoom.querySelector('img');
    document.addEventListener('click', event => {{
      if (event.target.matches('.title-card img')) {{ zoomImage.src = event.target.src; zoomImage.alt = event.target.alt; zoom.showModal(); }}
    }});
    zoom.addEventListener('click', () => zoom.close());
  </script>
</body>
</html>
"""
    index_path = output_root / "index.html"
    index_path.write_text(page, encoding="utf-8")
    return index_path


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
