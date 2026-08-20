#!/usr/bin/env python3
"""Render deterministic, text-only navigation-wheel typography candidates.

This builder deliberately does not create, repaint, or inpaint wheel artwork.
It emits only transparent Korean label layers and comparison sheets.  The
layers are intended to be composited later over body/icon plates separated
from the stock Japanese atlases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont, __version__ as pillow_version


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
WORKSPACE = REPO.parent.parent
DEFAULT_THIRD_PARTY = WORKSPACE / "repository" / "KR_PATCH_WORK" / "tmp" / "third_party_fonts"

SCHEMA = "nobu16.kr.navigation-wheel-text-candidates.v1"
OVERSAMPLE = 8
CELL_SIZE = (100, 95)
SAFE_WIDTH = 96
TARGET_INK_HEIGHT = 23
INK_BOTTOM = 91
LABELS = ("입성", "군평정", "국인정보", "보급거점", "공략목표")


class CandidateError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    short_name: str
    description: str
    font_path: Path
    expected_sha256: str
    weight: int | None
    tracking_em: float


@dataclass(frozen=True)
class StateStyle:
    state_id: str
    label: str
    fill: tuple[int, int, int, int]
    stroke: tuple[int, int, int, int]
    shadow: tuple[int, int, int, int]
    stroke_px: float
    shadow_offset: tuple[float, float]


STYLES = (
    StateStyle(
        "normal",
        "정상",
        (48, 38, 25, 255),
        (255, 247, 214, 255),
        (73, 51, 25, 190),
        1.20,
        (0.0, 1.0),
    ),
    StateStyle(
        "selected",
        "선택",
        (250, 252, 255, 255),
        (82, 105, 166, 255),
        (20, 48, 112, 210),
        1.15,
        (0.0, 1.0),
    ),
)


def candidates(args: argparse.Namespace) -> tuple[Candidate, ...]:
    return (
        Candidate(
            "a_noto_serif_900",
            "A 정통 명조",
            "Noto Serif KR 900 · 원본 명조 계열에 가장 가까운 정석형",
            args.noto_serif,
            "11F8D5DE6F1B79195EFBA3828AAA2EC95C1178F5AE976FB23C8D53250A9938F3",
            900,
            -0.025,
        ),
        Candidate(
            "b_seoul_hangang_eb",
            "B 서울한강 EB",
            "서울한강 ExtraBold · 붓맛과 시대감을 강조한 명조형",
            args.seoul_hangang,
            "60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1",
            None,
            -0.035,
        ),
        Candidate(
            "c_yydimibang_bold",
            "C 음식디미방",
            "영양군 음식디미방 Bold · 고서·목판 인상이 강한 개성형",
            args.yydimibang,
            "647D7710ED205C005892D96A468996C1F8FCBA135F41BF975A5EBA2C86DE7326",
            None,
            -0.010,
        ),
        Candidate(
            "d_noto_sans_850",
            "D 선명 고딕",
            "Noto Sans KR 850 · 작은 화면 판독성을 우선한 대비형",
            args.noto_sans,
            "194018E6B2B293A7964F037B25C0249CE1418BC9AB3C971060A03AA57861E252",
            850,
            -0.035,
        ),
    )


def load_font(candidate: Candidate, size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(candidate.font_path), size=size)
    if candidate.weight is not None:
        axes = font.get_variation_axes()
        require(len(axes) == 1, f"unexpected variation axes: {candidate.font_path}")
        minimum = int(axes[0]["minimum"])
        maximum = int(axes[0]["maximum"])
        require(minimum <= candidate.weight <= maximum, f"weight outside font axis: {candidate.weight}")
        font.set_variation_by_axes([candidate.weight])
    return font


def render_chars(text: str, font: ImageFont.FreeTypeFont, tracking_px: float) -> Image.Image:
    probe = Image.new("L", (4096, 1024), 0)
    draw = ImageDraw.Draw(probe)
    boxes = [draw.textbbox((0, 0), char, font=font, stroke_width=0) for char in text]
    advances = [float(draw.textlength(char, font=font)) for char in text]
    min_top = min(box[1] for box in boxes)
    max_bottom = max(box[3] for box in boxes)
    width = int(math.ceil(sum(advances) + tracking_px * max(0, len(text) - 1))) + 8
    height = int(max_bottom - min_top) + 8
    result = Image.new("L", (max(1, width), max(1, height)), 0)
    canvas = ImageDraw.Draw(result)
    cursor = 4.0
    for char, advance, box in zip(text, advances, boxes):
        canvas.text((round(cursor), 4 - min_top), char, font=font, fill=255, stroke_width=0)
        cursor += advance + tracking_px
    bbox = result.getbbox()
    require(bbox is not None, f"font produced an empty label: {text}")
    return result.crop(bbox)


def make_fill_mask(candidate: Candidate, text: str) -> tuple[Image.Image, dict[str, Any]]:
    target_height = TARGET_INK_HEIGHT * OVERSAMPLE
    low, high = 4 * OVERSAMPLE, 64 * OVERSAMPLE
    best: tuple[int, Image.Image, int] | None = None
    while low <= high:
        size = (low + high) // 2
        font = load_font(candidate, size)
        tracking = candidate.tracking_em * size
        mask = render_chars(text, font, tracking)
        delta = abs(mask.height - target_height)
        if best is None or delta < best[0]:
            best = (delta, mask, size)
        if mask.height < target_height:
            low = size + 1
        elif mask.height > target_height:
            high = size - 1
        else:
            break
    require(best is not None, "font-size search failed")
    _, mask, font_size = best
    if mask.height != target_height:
        target_width = max(1, round(mask.width * target_height / mask.height))
        mask = mask.resize((target_width, target_height), Image.Resampling.LANCZOS)
    max_width = SAFE_WIDTH * OVERSAMPLE
    horizontal_scale = min(1.0, max_width / mask.width)
    if horizontal_scale < 1.0:
        mask = mask.resize((max_width, mask.height), Image.Resampling.LANCZOS)
    require(horizontal_scale >= 0.86, f"label requires excessive condensation: {candidate.candidate_id} {text}")
    return mask, {
        "font_size_oversampled_px": font_size,
        "fill_size_oversampled_px": [mask.width, mask.height],
        "natural_horizontal_scale": round(horizontal_scale, 6),
    }


def colored(mask: Image.Image, rgba: tuple[int, int, int, int]) -> Image.Image:
    result = Image.new("RGBA", mask.size, rgba)
    if rgba[3] == 255:
        result.putalpha(mask)
    else:
        result.putalpha(mask.point(lambda value: round(value * rgba[3] / 255)))
    return result


def composite_layer(candidate: Candidate, text: str, style: StateStyle) -> tuple[Image.Image, dict[str, Any]]:
    mask, metrics = make_fill_mask(candidate, text)
    radius = max(1, round(style.stroke_px * OVERSAMPLE))
    stroke_mask = mask.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    margin = radius + max(abs(round(value * OVERSAMPLE)) for value in style.shadow_offset) + 4
    work_size = (mask.width + margin * 2, mask.height + margin * 2)
    work = Image.new("RGBA", work_size, (0, 0, 0, 0))
    base_xy = (margin, margin)
    shadow_xy = (
        margin + round(style.shadow_offset[0] * OVERSAMPLE),
        margin + round(style.shadow_offset[1] * OVERSAMPLE),
    )
    work.alpha_composite(colored(stroke_mask, style.shadow), shadow_xy)
    work.alpha_composite(colored(stroke_mask, style.stroke), base_xy)
    work.alpha_composite(colored(mask, style.fill), base_xy)

    cell = Image.new("RGBA", (CELL_SIZE[0] * OVERSAMPLE, CELL_SIZE[1] * OVERSAMPLE), (0, 0, 0, 0))
    x = (cell.width - work.width) // 2
    fill_bottom = INK_BOTTOM * OVERSAMPLE
    y = fill_bottom - (margin + mask.height)
    cell.alpha_composite(work, (x, y))
    native = cell.resize(CELL_SIZE, Image.Resampling.LANCZOS)
    bbox = native.getbbox()
    require(bbox is not None, "composited layer is empty")
    metrics.update(
        {
            "state": style.state_id,
            "cell_size_px": list(CELL_SIZE),
            "layer_bbox_px": list(bbox),
            "layer_size_px": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
            "target_ink_height_px": TARGET_INK_HEIGHT,
            "ink_bottom_px": INK_BOTTOM,
            "stroke_px": style.stroke_px,
            "shadow_offset_px": list(style.shadow_offset),
        }
    )
    return native, metrics


def checker(size: tuple[int, int], block: int = 8) -> Image.Image:
    result = Image.new("RGB", size, (54, 58, 64))
    draw = ImageDraw.Draw(result)
    for y in range(0, size[1], block):
        for x in range(0, size[0], block):
            if (x // block + y // block) % 2:
                draw.rectangle((x, y, x + block - 1, y + block - 1), fill=(42, 46, 52))
    return result


def preview_cell(layer: Image.Image, zoom: int) -> Image.Image:
    background = checker(layer.size, 5)
    background.paste(layer, (0, 0), layer)
    return background.resize((layer.width * zoom, layer.height * zoom), Image.Resampling.NEAREST)


def render_contact_sheet(
    all_layers: dict[tuple[str, str, str], Image.Image],
    specs: Iterable[Candidate],
) -> Image.Image:
    specs = tuple(specs)
    zoom = 3
    cell_w, cell_h = CELL_SIZE[0] * zoom, CELL_SIZE[1] * zoom
    gap = 14
    column_w = cell_w * 2 + gap * 3
    header_h = 132
    row_h = cell_h + 48
    footer_h = 70
    width = column_w * len(specs)
    height = header_h + row_h * len(LABELS) + footer_h
    sheet = Image.new("RGB", (width, height), (25, 27, 31))
    draw = ImageDraw.Draw(sheet)
    ui_font_path = REPO / "vendor" / "noto" / "NotoSansKR-wght.ttf"
    ui = ImageFont.truetype(str(ui_font_path), 25)
    ui.set_variation_by_axes([800])
    small = ImageFont.truetype(str(ui_font_path), 17)
    small.set_variation_by_axes([650])
    tiny = ImageFont.truetype(str(ui_font_path), 14)
    tiny.set_variation_by_axes([550])

    for column, spec in enumerate(specs):
        x0 = column * column_w
        draw.rectangle((x0, 0, x0 + column_w - 1, height - 1), outline=(63, 68, 77), width=1)
        draw.text((x0 + 18, 14), spec.short_name, font=ui, fill=(247, 247, 244))
        draw.multiline_text((x0 + 18, 52), spec.description, font=small, fill=(190, 197, 207), spacing=3)
        draw.text((x0 + gap, 105), "정상", font=small, fill=(230, 230, 226))
        draw.text((x0 + gap * 2 + cell_w, 105), "선택", font=small, fill=(230, 230, 226))
        for row, text in enumerate(LABELS):
            y0 = header_h + row * row_h
            draw.text((x0 + gap, y0 + 3), text, font=small, fill=(210, 214, 220))
            for state_index, style in enumerate(STYLES):
                layer = all_layers[(spec.candidate_id, text, style.state_id)]
                preview = preview_cell(layer, zoom)
                px = x0 + gap + state_index * (cell_w + gap)
                py = y0 + 34
                sheet.paste(preview, (px, py))
                draw.rectangle((px, py, px + cell_w - 1, py + cell_h - 1), outline=(92, 98, 109), width=1)
    draw.text(
        (18, height - 49),
        "텍스트 레이어만 표시 · 바디/아이콘은 일본어 원본에서 분리 후 합성 · 생성형 이미지 처리 없음 · 1px을 3배 정수 확대",
        font=tiny,
        fill=(171, 179, 190),
    )
    return sheet


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    tmp = (REPO / "tmp").resolve()
    try:
        output.relative_to(tmp)
    except ValueError as exc:
        raise CandidateError(f"output must stay below repo tmp: {output}") from exc
    require(not output.exists(), f"output already exists: {output}")
    output.mkdir(parents=True)

    specs = candidates(args)
    for spec in specs:
        require(spec.font_path.is_file(), f"font missing: {spec.font_path}")
        actual = sha256_file(spec.font_path)
        require(actual == spec.expected_sha256, f"font hash differs: {spec.font_path} {actual}")

    layers: dict[tuple[str, str, str], Image.Image] = {}
    rows: list[dict[str, Any]] = []
    for spec in specs:
        candidate_dir = output / spec.candidate_id
        candidate_dir.mkdir()
        for text in LABELS:
            for style in STYLES:
                layer, metrics = composite_layer(spec, text, style)
                name = f"{text}_{style.state_id}_100x95.png"
                layer.save(candidate_dir / name, optimize=False, compress_level=9)
                layers[(spec.candidate_id, text, style.state_id)] = layer
                rows.append(
                    {
                        "candidate_id": spec.candidate_id,
                        "text": text,
                        "file": f"{spec.candidate_id}/{name}",
                        **metrics,
                    }
                )

    sheet = render_contact_sheet(layers, specs)
    sheet_path = output / "navigation_wheel_text_candidates_v1.png"
    sheet.save(sheet_path, optimize=False, compress_level=9)
    manifest = {
        "schema": SCHEMA,
        "image_generation": "forbidden-and-not-used",
        "artifact_scope": "transparent-text-layers-only",
        "pillow_version": pillow_version,
        "oversample": OVERSAMPLE,
        "cell_size_px": list(CELL_SIZE),
        "safe_width_px": SAFE_WIDTH,
        "target_ink_height_px": TARGET_INK_HEIGHT,
        "ink_bottom_px": INK_BOTTOM,
        "labels": list(LABELS),
        "candidates": [
            {
                "candidate_id": spec.candidate_id,
                "short_name": spec.short_name,
                "description": spec.description,
                "font_path": str(spec.font_path.resolve()),
                "font_sha256": spec.expected_sha256,
                "weight": spec.weight,
                "tracking_em": spec.tracking_em,
            }
            for spec in specs
        ],
        "layers": rows,
        "contact_sheet": sheet_path.name,
    }
    manifest_path = output / "manifest.v1.json"
    write_json(manifest_path, manifest)
    return {
        "output": str(output),
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": sha256_file(sheet_path),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "layers": len(rows),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--noto-serif", type=Path, default=REPO / "vendor" / "noto" / "NotoSerifKR-wght.ttf")
    result.add_argument("--noto-sans", type=Path, default=REPO / "vendor" / "noto" / "NotoSansKR-wght.ttf")
    result.add_argument("--seoul-hangang", type=Path, default=DEFAULT_THIRD_PARTY / "SeoulHangangEB.ttf")
    result.add_argument(
        "--yydimibang",
        type=Path,
        default=DEFAULT_THIRD_PARTY / "yeongyang_eumsikdimibang" / "Yydimibang.ttf",
    )
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
