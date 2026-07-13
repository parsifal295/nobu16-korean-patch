#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[diuoxXfsc]")
SUPPORTED_ENCODINGS = {"utf16le", "utf16be", "utf16le_run"}


@dataclass
class Entry:
    id: int
    file: str
    encoding: str
    offset: int
    allocated_bytes: int
    original_en: str
    translated_ko: str = ""
    status: str = "todo"
    notes: str = ""
    align: int | None = None


@dataclass
class Catalog:
    path: Path
    headers: list[str]
    entries: list[Entry]

    @property
    def by_id(self) -> dict[int, Entry]:
        return {e.id: e for e in self.entries}


def _bool_has(col: str, headers: list[str]) -> bool:
    return any(h.strip().lower() == col for h in headers)


def _detect_encoding(headers: list[str], row: dict[str, str]) -> str:
    enc = (row.get("encoding") or "").strip().lower()
    if enc:
        return enc
    # run template has no encoding column
    if _bool_has("align", headers):
        return "utf16le_run"
    # fallback for unknown templates
    return "utf16le"


def _normalize_status(e: Entry) -> None:
    if e.translated_ko.strip():
        if e.status.strip().lower() in {"", "todo", "pending"}:
            e.status = "translated"
    else:
        if e.status.strip() == "":
            e.status = "todo"


def load_catalog(path: Path) -> Catalog:
    entries: list[Entry] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        headers = [h for h in (r.fieldnames or []) if h is not None]
        for row in r:
            enc = _detect_encoding(headers, row)
            if enc not in SUPPORTED_ENCODINGS:
                raise ValueError(f"unsupported encoding in csv: {enc}")

            align: int | None = None
            align_raw = (row.get("align") or "").strip()
            if align_raw:
                align = int(align_raw)

            e = Entry(
                id=int(row["id"]),
                file=(row.get("file") or "").strip(),
                encoding=enc,
                offset=int(row["offset"]),
                allocated_bytes=int(row["allocated_bytes"]),
                original_en=row.get("original_en", ""),
                translated_ko=row.get("translated_ko", ""),
                status=row.get("status", "todo"),
                notes=row.get("notes", ""),
                align=align,
            )
            _normalize_status(e)
            entries.append(e)

    return Catalog(path=path, headers=headers, entries=entries)


def save_catalog(path: Path, cat: Catalog) -> None:
    # Preserve original column order where possible.
    headers = list(cat.headers) if cat.headers else []
    if not headers:
        headers = [
            "id",
            "file",
            "encoding",
            "offset_hex",
            "offset",
            "align",
            "allocated_bytes",
            "max_chars_est",
            "original_en",
            "translated_ko",
            "status",
            "notes",
        ]

    if "encoding" not in headers:
        headers.insert(2, "encoding")
    if "offset_hex" not in headers:
        try:
            pos = headers.index("offset")
        except ValueError:
            pos = 3
        headers.insert(pos, "offset_hex")
    if "max_chars_est" not in headers:
        try:
            pos = headers.index("allocated_bytes") + 1
        except ValueError:
            pos = len(headers)
        headers.insert(pos, "max_chars_est")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        w.writeheader()
        for e in cat.entries:
            row = {
                "id": e.id,
                "file": e.file,
                "encoding": e.encoding,
                "offset_hex": f"0x{e.offset:X}",
                "offset": e.offset,
                "align": "" if e.align is None else e.align,
                "allocated_bytes": e.allocated_bytes,
                "max_chars_est": e.allocated_bytes // 2,
                "original_en": e.original_en,
                "translated_ko": e.translated_ko,
                "status": e.status,
                "notes": e.notes,
            }
            w.writerow(row)


def encode_text(text: str, enc: str, ascii_only_run: bool = False) -> bytes:
    if enc == "utf16le":
        return text.encode("utf-16-le") + b"\x00\x00"
    if enc == "utf16be":
        return text.encode("utf-16-be") + b"\x00\x00"
    if enc == "utf16le_run":
        if ascii_only_run:
            out = bytearray()
            for ch in text:
                code = ord(ch)
                if not (0x20 <= code <= 0x7E):
                    raise ValueError(f"non-ascii char in utf16le_run text: {ch!r}")
                out.extend((code, 0x00))
            return bytes(out)
        return text.encode("utf-16-le")
    raise ValueError(f"unknown encoding: {enc}")


def _decode_terminated(data: bytes, offset: int, alloc: int, enc: str) -> tuple[str, bool]:
    end = min(len(data), offset + alloc)
    pos = offset
    chars: list[str] = []
    while pos + 1 < end:
        if enc == "utf16le":
            code = data[pos] | (data[pos + 1] << 8)
        elif enc == "utf16be":
            code = (data[pos] << 8) | data[pos + 1]
        else:
            raise ValueError(f"terminated decode only for utf16le/utf16be, got {enc}")
        if code == 0:
            return ("".join(chars), True)
        chars.append(chr(code))
        pos += 2
    return ("".join(chars), False)


def _decode_run(data: bytes, offset: int, alloc: int) -> str:
    end = min(len(data), offset + alloc)
    chunk = bytes(data[offset:end])
    if len(chunk) % 2 != 0:
        raise ValueError(f"odd run length: {len(chunk)}")
    return chunk.decode("utf-16-le", errors="strict")


def decode_current(data: bytes, e: Entry) -> tuple[str, bool]:
    if e.encoding in {"utf16le", "utf16be"}:
        return _decode_terminated(data, e.offset, e.allocated_bytes, e.encoding)
    if e.encoding == "utf16le_run":
        return (_decode_run(data, e.offset, e.allocated_bytes), True)
    raise ValueError(f"unknown encoding: {e.encoding}")


def placeholder_list(text: str) -> list[str]:
    return PLACEHOLDER_RE.findall(text)


def validate_entries(
    entries: list[Entry],
    *,
    exact_length: bool,
    ascii_only_run: bool,
) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    targets = 0

    for e in entries:
        t = e.translated_ko
        if not t.strip():
            continue
        targets += 1
        try:
            enc = encode_text(t, e.encoding, ascii_only_run=ascii_only_run)
        except Exception as ex:
            errors.append(f"id={e.id} off=0x{e.offset:X}: {ex}")
            continue

        if exact_length and len(enc) != e.allocated_bytes:
            errors.append(
                f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} must equal allocated {e.allocated_bytes}"
            )
        elif len(enc) > e.allocated_bytes:
            errors.append(f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} > allocated {e.allocated_bytes}")

        src_ph = placeholder_list(e.original_en)
        dst_ph = placeholder_list(t)
        if src_ph != dst_ph:
            warnings.append(f"id={e.id} off=0x{e.offset:X}: placeholder mismatch src={src_ph} dst={dst_ph}")

    return errors, warnings, targets


def _apply_entry_bytes(
    data: bytearray,
    e: Entry,
    *,
    strict_original: bool,
    exact_length: bool,
    ascii_only_run: bool,
) -> bool:
    t = e.translated_ko
    if not t.strip():
        return False

    if strict_original:
        cur, ok = decode_current(data, e)
        if not ok:
            raise ValueError(f"id={e.id} off=0x{e.offset:X}: current text has no terminator in allocation")
        if cur != e.original_en:
            raise ValueError(f"id={e.id} off=0x{e.offset:X}: original mismatch current={cur!r} csv={e.original_en!r}")

    enc = encode_text(t, e.encoding, ascii_only_run=ascii_only_run)
    if exact_length and len(enc) != e.allocated_bytes:
        raise ValueError(f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} must equal allocated {e.allocated_bytes}")
    if len(enc) > e.allocated_bytes:
        raise ValueError(f"id={e.id} off=0x{e.offset:X}: encoded {len(enc)} > allocated {e.allocated_bytes}")

    if e.encoding == "utf16le_run" and len(enc) < e.allocated_bytes:
        pad_pairs = (e.allocated_bytes - len(enc)) // 2
        patch = enc + (b"\x20\x00" * pad_pairs)
    else:
        patch = enc + (b"\x00" * (e.allocated_bytes - len(enc)))
    data[e.offset : e.offset + e.allocated_bytes] = patch
    return True


def inject_single_file(
    *,
    src_bin: Path,
    out_bin: Path,
    entries: list[Entry],
    strict_original: bool,
    exact_length: bool,
    ascii_only_run: bool,
) -> tuple[int, int]:
    data = bytearray(src_bin.read_bytes())
    patched = 0
    skipped = 0

    for e in entries:
        did = _apply_entry_bytes(
            data,
            e,
            strict_original=strict_original,
            exact_length=exact_length,
            ascii_only_run=ascii_only_run,
        )
        if did:
            patched += 1
        else:
            skipped += 1

    out_bin.parent.mkdir(parents=True, exist_ok=True)
    out_bin.write_bytes(data)
    return patched, skipped


def inject_tree(
    *,
    src_root: Path,
    out_root: Path,
    entries: list[Entry],
    strict_original: bool,
    exact_length: bool,
    ascii_only_run: bool,
) -> tuple[int, int, int]:
    by_file: dict[Path, list[Entry]] = {}
    for e in entries:
        p = Path(e.file)
        by_file.setdefault(p, []).append(e)

    files_written = 0
    total_patched = 0
    total_skipped = 0

    for file_path, group in sorted(by_file.items(), key=lambda kv: str(kv[0])):
        src = file_path
        if not src.exists():
            if not src.is_absolute():
                src = src_root / src
            if not src.exists():
                raise FileNotFoundError(f"source file not found for csv row file={file_path}")
        rel = src.relative_to(src_root) if src.is_relative_to(src_root) else Path(src.name)
        out = out_root / rel
        patched, skipped = inject_single_file(
            src_bin=src,
            out_bin=out,
            entries=group,
            strict_original=strict_original,
            exact_length=exact_length,
            ascii_only_run=ascii_only_run,
        )
        files_written += 1
        total_patched += patched
        total_skipped += skipped

    return files_written, total_patched, total_skipped

