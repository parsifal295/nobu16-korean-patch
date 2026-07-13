# NOBU16 raw LZ4 / LINK format note (2026-07-13)

## Confirmed wrapper

`MSG_PK/*/msg*.bin` and selected `res_lang.bin` entries use a 24-byte wrapper:

| Offset | Type | Meaning |
|---:|---|---|
| `0x00` | 8 bytes | Opaque build/resource prefix; preserve verbatim |
| `0x08` | `u64le` | Uncompressed size |
| `0x10` | `u64le` | Compressed payload size; equals file size minus 24 |
| `0x18` | bytes | Standard raw LZ4 block, without an LZ4 frame header |

The algorithm was confirmed by decoding all seven `MSG_PK/EN/msg*.bin` files to the exact declared output size. Six common files (`msgbre`, `msgdata`, `msgev`, `msgire`, `msgstf`, and `msgui`) use relative offset tables leading to UTF-16LE strings. `msggame` is different: its 18 sections contain bytecode/record streams with embedded UTF-16LE literals, not a simple UTF-16 string table. A valid literal-only raw LZ4 encoder is sufficient for deterministic repacking, although it produces larger files than the game's optimized encoder.

## Confirmed LINK table

`RES_EN/res_lang.bin` starts with:

| Offset | Type | Meaning |
|---:|---|---|
| `0x00` | 4 bytes | `LINK` |
| `0x04` | `u32le` | Entry count (`42` for `res_lang.bin`) |
| `0x08` | `u32le` | Version (`1`) |
| `0x0C` | `u32le` | Reserved (`0`) |
| `0x10` | repeated pair | `u32le offset`, `u32le stored_size` |

The table does **not** store an unpacked size or explicit type. `stored_size` excludes the four-byte entry trailer. Non-empty entries normally end in `EF CD AB 89`; physical empty entries use four zero bytes. Type and unpacked size are derived from the entry payload (for example, the raw-LZ4 wrapper has its unpacked size at entry `+0x08`). Repacking must update every following 32-bit offset.

There is one table-only sentinel case: `RES_EN/res_lang.bin` entries 39/40/41 are zero-sized and point to EOF, EOF+4, and EOF+8, respectively. No physical trailer bytes exist for these trailing slots. The tool preserves these virtual offsets relative to the rebuilt EOF.

## Font entry point

Top-level entries 6 and 7 of each localized `res_lang.bin` are raw-LZ4-wrapped Koei Tecmo G1N bitmap fonts (`_N1G0000` after decompression). Examples:

| Language | Entry 6 compressed | Entry 6 uncompressed | G1N glyph tables | Hangul mappings |
|---|---:|---:|---:|---:|
| EN | 94,251 | 816,756 | 3 | 0 |
| JP | 8,466,389 | 17,217,348 | 3 | 0 |
| SC | 12,092,320 | 25,817,936 | 2 | 0 |
| TC | 7,747,825 | 16,572,884 | 2 | 0 |

The same is true for entry 7. This makes the practical route: extract/decompress entry 6 and 7, add Korean glyphs to the G1N character map/atlas, recompress, and rebuild the LINK offsets. The open-source [G1N Font Editor](https://github.com/lehieugch68/G1N-Font-Editor) can create and edit this format.

## Tool commands

```text
python KR_PATCH_WORK/tools/nobu16_lz4.py verify MSG_PK/EN/msggame.bin
python KR_PATCH_WORK/tools/nobu16_lz4.py list RES_EN/res_lang.bin
python KR_PATCH_WORK/tools/nobu16_lz4.py extract-entry RES_EN/res_lang.bin 6 KR_PATCH_WORK/tmp/font6.g1n --decompress
python KR_PATCH_WORK/tools/nobu16_lz4.py repack-entry RES_EN/res_lang.bin 6 KR_PATCH_WORK/tmp/font6.edited.g1n KR_PATCH_WORK/tmp/res_lang.edited.bin --compress
python KR_PATCH_WORK/tools/nobu16_lz4.py verify-link RES_EN/res_lang.bin
```

All output commands refuse to overwrite an input path. The original game files are not modified.

## Round-trip evidence

An independent decoder plus the same literal-only encoder produced exact decoded-byte round trips for all seven EN PK message files. Original compressed → decoded → literal-only compressed sizes were:

- `msgbre`: 295,577 → 836,320 → 839,601
- `msgdata`: 267,526 → 744,236 → 747,156
- `msgev`: 758,136 → 1,868,232 → 1,875,560
- `msggame`: 714,013 → 2,169,852 → 2,178,363
- `msgire`: 25,310 → 46,920 → 47,105
- `msgstf`: 9,647 → 20,052 → 20,132
- `msgui`: 84,803 → 219,108 → 219,969

Generated verification artifacts are under `KR_PATCH_WORK/tmp/lz4_roundtrip/`; no original file was overwritten.
