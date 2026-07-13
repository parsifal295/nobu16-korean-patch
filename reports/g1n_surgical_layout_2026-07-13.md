# SC/TC G1N raw layout and surgical-validation rules

This note is based on read-only parsing of the four decompressed stock files in
`KR_PATCH_WORK/tmp/lang_fonts`.  No installed game file, process, or emulator
configuration was accessed.  The public G1N editor's `Build()` method was not
run, because it cannot preserve these files' large palette headers.

## Fixed header and palette layout

All integer fields are little-endian.

| Offset | Size | Meaning |
|---:|---:|---|
| `0x00` | 8 | ASCII signature `_N1G0000` |
| `0x08` | 4 | complete file size |
| `0x0C` | 4 | header size / first-table offset |
| `0x10` | 4 | unknown value; `0x0A` in all four files |
| `0x14` | 4 | atlas offset |
| `0x18` | 4 | palette count |
| `0x1C` | 4 | table count; 2 in all four files |
| `0x20` | `4 * table_count` | table offsets |
| next | `0x40 * palette_count` | raw palette blob; 16 ARGB uint32 values per palette |

The exact header-end equation is:

```text
header_size = 0x20 + 4 * table_count + 0x40 * palette_count
```

For SC, `palette_count=129`, so the palette blob is `0x2040` bytes and
`header_size=0x2068`.  For TC, `palette_count=93`, so the palette blob is
`0x1740` bytes and `header_size=0x1768`.  There is no disposable gap between
the palette blob and table 0.

| File | SHA-256 | File size | Header | Table 0 | Table 1 | Atlas | Atlas size | Palette SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `SC_6.g1n` | `414A8E98DCF0F52633CD039A74E97AE61A97D98A96684D450EBADD4C3C85CAEB` | `0x189F350` | `0x2068` | `0x2068` | `0x622E0` | `0x82790` | `0x181CBC0` | `C34A45CC084F695F42ED0459BBB9E93A2C36429EADD54800674F2C57B699728E` |
| `SC_7.g1n` | `DADBE4EEA223FD48CEFA9A93A08EF1F2458B3BD543ADFCEBD6D888B9EE2AFBB0` | `0xB39E90` | `0x2068` | `0x2068` | `0x622E0` | `0x82790` | `0xAB7700` | `5A3E76A88013126B659E1331A1B664EAE511D38931C8CD80BF4956CA58257B1B` |
| `TC_6.g1n` | `6C3856FA977099C90F74152E57E2D7A34F178FC141DB1CA361E8ECE8252B0E1E` | `0xFCE1D4` | `0x1768` | `0x1768` | `0x4A5A4` | `0x6AA54` | `0xF63780` | `AB21C9B90C8E198CCBDCE579EF51BD2BEADCC6DA8CE1A6B2F551E5271192F657` |
| `TC_7.g1n` | `F6F30FB95C991A0F4A1B894B3E1F9C0A82EDCA2CCDDD59B017AC77BF80ACC521` | `0x741854` | `0x1768` | `0x1768` | `0x4A5A4` | `0x6AA54` | `0x6D6E00` | `B9A7BF86E2F3414AACC9C662AE0B949EBD9FC4547A5D955084D4C8EB43F2D1D2` |

The editor's full rebuild path must not be used on these files.  Its reader
reduces the 129/93 raw palettes to the few palette arrays attached to two
in-memory `GlyphTable` objects, and `Build()` writes only those attached
arrays.  It therefore cannot reproduce the stock palette blob or its declared
header boundary.

## Table layout

Each table is independent metadata followed by no pixel data:

```text
table_offset + 0x00000: 65536 little-endian uint16 map entries
table_offset + 0x20000: 12-byte glyph record 0
                         12-byte glyph record 1
                         ...
next_table_or_atlas:     end of records
```

There is no explicit per-table glyph count.  It is derived without interpreting
the map:

```text
record_count = (next_table_offset - table_offset - 0x20000) / 12
```

For the final table, `next_table_offset` is `atlas_offset`.

| Language | Table 0 records | Table 0 nonzero one-to-one mappings | Table 1 records | Table 1 nonzero one-to-one mappings |
|---|---:|---:|---:|---:|
| SC | 21,898 | 21,897 | 100 | 99 |
| TC | 13,957 | 13,956 | 100 | 99 |

Ordinal 0 is also the value for an unmapped codepoint, so the stock map has one
fewer unambiguous nonzero mapping than records.  Every stock nonzero ordinal is
in range, reachable, and unique.  Aliasing a new codepoint to an old glyph is
valid as a diagnostic and intentionally introduces a duplicate ordinal.

The 12-byte record is:

| Record offset | Size | Meaning |
|---:|---:|---|
| `+0` | 1 | bitmap/layout width |
| `+1` | 1 | height |
| `+2` | 1 | signed x offset |
| `+3` | 1 | signed baseline |
| `+4` | 1 | advance width |
| `+5` | 1 | signed atlas row stride; negative in these files |
| `+6` | 1 | mirrored signed x offset |
| `+7` | 1 | mirrored height |
| `+8` | 4 | atlas-relative pixel offset |

For all stock records, bytes `+6/+7` equal `+2/+1`.  Pixel-block size is:

```text
pixel_size = abs(int8(record[5])) * record[1]
physical_pixel_offset = atlas_offset + uint32(record[8:12])
```

The original atlas-relative pointer bias is zero in every table of all four
files.  Sorted pixel intervals cover the complete atlas exactly once, with no
gap or overlap.

The source contains both full-width and narrow slots, so multiplying every
record by one global cell size is incorrect:

| File/table | Pixel-block distribution |
|---|---|
| SC entry 6, table 0 | `0x480` x 21,797; `0x240` x 101 |
| SC entry 6, table 1 | `0x480` x 100 |
| SC entry 7, table 0 | `0x200` x 21,797; `0x100` x 101 |
| SC entry 7, table 1 | `0x200` x 100 |
| TC entry 6, table 0 | `0x480` x 13,857; `0x240` x 100 |
| TC entry 6, table 1 | `0x480` x 100 |
| TC entry 7, table 0 | `0x200` x 13,857; `0x100` x 100 |
| TC entry 7, table 1 | `0x200` x 100 |

## Safest append equations: preserve the complete stock atlas as a prefix

The runtime lookup uses the mapped ordinal to select its 12-byte record and
uses that record's `+8` atlas-relative pointer directly.  It does not require
the pixel blocks to follow table-record order.  Therefore the least invasive
append keeps every old record and the complete old atlas byte-identical, then
places only new pixels at the atlas tail.

Let:

- `T0`, `T1`, `A`, and `F` be the original table 0, table 1, atlas, and EOF
  offsets;
- `n0` and `n1` be appended record counts;
- `P0` and `P1` be the sums of the appended record pixel sizes in each table.

Then:

```text
T0' = T0
T1' = T1 + 12*n0
A'  = A  + 12*(n0+n1)
F'  = F  + 12*(n0+n1) + P0 + P1
```

Required byte preservation and insertion order:

```text
candidate[A' : A' + (F-A)] == stock[A : F]
candidate atlas tail == new table-0 pixels in ordinal order
                        + new table-1 pixels in ordinal order
```

All old 12-byte records, including their `+8` pointers, remain byte-identical.
For new record `j` in table `i`:

```text
new_ordinal(i,j) = old_record_count(i) + j
map_cell(i,U)     = new_ordinal(i,j)
map_file_offset   = Ti' + 2*U
record_file_offset= Ti' + 0x20000 + 12*new_ordinal(i,j)

new_pointer(i,j)  = (F-A)
                    + sum(Pk for k < i)
                    + sum(pixel_size(i,m) for m < j)
```

Only these header values change: the complete file size at `0x08`, the atlas
offset at `0x14`, and later table pointers at `0x20 + 4*i`.  Header size,
unknown field, palette count/blob, old map cells, old records, and old atlas are
immutable.

This tail layout is intentionally **not** round-trippable through the public
editor.  That editor estimates a glyph's pixel length from the next record's
pointer and assumes table-record order, whereas the runtime path and this
validator use each record's own row stride, height, and atlas-relative pointer.
Do not open and save a surgical candidate in that editor.  A game boot/render
test remains a separate release gate after structural validation.

## Independent validator

`KR_PATCH_WORK/tools/validate_g1n_surgical.py` is standard-library-only and has
no write path.  It supports:

```powershell
# Structural inspection
python validate_g1n_surgical.py STOCK.g1n

# Map-only diagnostic: every non-map byte must remain identical
python validate_g1n_surgical.py STOCK.g1n ALIAS.g1n --mode alias

# Tail-only appended glyphs, including all equations above
python validate_g1n_surgical.py STOCK.g1n APPENDED.g1n --mode append-tail
```

`--expect-codepoints` can pin the exact BMP character set.  The validator also
checks declared size, raw header/palette layout, table arithmetic, ordinal
ranges/reachability, mirrored metrics, row-stride capacity, exact atlas pointer
coverage, old-region byte preservation, and nonblank appended pixel blocks.

All four stock files passed structural validation.  The SC mapping-only probe
also passed with exactly 28 changed codepoints in both tables of both entries:

| Candidate | SHA-256 | Allowed change | Alias targets |
|---|---|---|---|
| `SC_6.hangul_to_N.g1n` | `B4A0070757C26D0445C43A3CDD960F356C7F4A3C87BAE3C8CA452F0DEEA52181` | 28 uint16 map cells per table only | table 0 ordinal 115; table 1 ordinal 51 |
| `SC_7.hangul_to_N.g1n` | `662F15A8D8A38C0EDD5E9B82369737944390FAEBAA9241BBCDD586C358B16AE7` | 28 uint16 map cells per table only | table 0 ordinal 115; table 1 ordinal 51 |

Their header, palette blob, record arrays, atlas, offsets, and file sizes are
byte-identical to stock.

The pinned-Noto SC/TC tail-append candidates also passed all append rules:

| Candidate | SHA-256 | Size | New table 1 | New atlas | Additions |
|---|---|---:|---:|---:|---|
| `SC_6.pinned_noto.g1n` | `E4F151238D3B331D73A09785D0B2736709B2B235DD1B308C06F082A83C15ADCA` | `0x18AF1F0` | `0x62430` | `0x82A30` | 28 records and the exact 28-codepoint set in each table |
| `SC_7.pinned_noto.g1n` | `CE976A729FBCA8F3B18A7DF5137B78CF08A76E073A25635607500B8BD026CFAD` | `0xB41130` | `0x62430` | `0x82A30` | 28 records and the exact 28-codepoint set in each table |
| `TC_6.pinned_noto.g1n` | `0E63992235BB1E198BC78DC9A8F7BC97C1DDFC2CDF902832D11D709D340C06AE` | `0xFDE074` | `0x4A6F4` | `0x6ACF4` | 28 records and the exact 28-codepoint set in each table |
| `TC_7.pinned_noto.g1n` | `C1D7B8B02EBCA1A02134DD176A7CFDFCCB6953E3A7CCE552B1800F28BA894E9F` | `0x748AF4` | `0x4A6F4` | `0x6ACF4` | 28 records and the exact 28-codepoint set in each table |

For all four candidates, table 0 remains at its stock offset; table 1 moves by
`28*12 = 0x150`, and the atlas moves by `56*12 = 0x2A0`.  Entry 6 adds
`56*0x480 = 0xFC00` pixel bytes and entry 7 adds `56*0x200 = 0x7000` pixel
bytes.  The validator confirmed that every new block is nonblank, the complete
stock atlas is an exact prefix, and the combined old/new pointer intervals
cover the candidate atlas with neither a gap nor an overlap.

### Per-file preserved ranges

All offsets below are half-open `[start,end)` file ranges.  The candidate
header keeps the signature, header size, unknown value, palette/table counts,
table-0 pointer, and complete palette blob exact.  Only file size (`0x08`),
atlas offset (`0x14`), and table-1 pointer (`0x24`) change.  In each map, every
stock nonzero cell and every stock zero cell other than the exact 28 requested
Hangul cells remains byte-identical.

| Stock file | Exact palette blob | Exact table-0 old records | Exact table-1 old records, stock -> candidate | Exact complete old atlas, stock -> candidate | Candidate-only pixel tail |
|---|---|---|---|---|---|
| SC entry 6 | `[0x28,0x2068)` | `[0x22068,0x622E0)` | `[0x822E0,0x82790)` -> `[0x82430,0x828E0)` | `[0x82790,0x189F350)` -> `[0x82A30,0x189F5F0)` | `[0x189F5F0,0x18AF1F0)` |
| SC entry 7 | `[0x28,0x2068)` | `[0x22068,0x622E0)` | `[0x822E0,0x82790)` -> `[0x82430,0x828E0)` | `[0x82790,0xB39E90)` -> `[0x82A30,0xB3A130)` | `[0xB3A130,0xB41130)` |
| TC entry 6 | `[0x28,0x1768)` | `[0x21768,0x4A5A4)` | `[0x6A5A4,0x6AA54)` -> `[0x6A6F4,0x6ABA4)` | `[0x6AA54,0xFCE1D4)` -> `[0x6ACF4,0xFCE474)` | `[0xFCE474,0xFDE074)` |
| TC entry 7 | `[0x28,0x1768)` | `[0x21768,0x4A5A4)` | `[0x6A5A4,0x6AA54)` -> `[0x6A6F4,0x6ABA4)` | `[0x6AA54,0x741854)` -> `[0x6ACF4,0x741AF4)` | `[0x741AF4,0x748AF4)` |

The table-0 old records stay at the same file offsets.  Table-1 metadata moves
by `0x150`, so preservation is compared at its new logical location rather
than at the same absolute offset.

### LINK repack and re-extraction gate

The generated `res_lang` archives were parsed independently with
`nobu16_lz4.py verify-link`.  Both contain 42 entries and reproduce
byte-identically through the LINK parser's no-change round trip:

| Archive | SHA-256 | LINK verification |
|---|---|---|
| `SC/res_lang.SC.pinned_noto.bin` | `7FB2E6E7ABE2ADC7C359170ECB92952054C2F7F412933B8F1B339B6ADE661B7E` | 42 entries; `byte_identical_roundtrip=OK` |
| `TC/res_lang.TC.pinned_noto.bin` | `5228871705DBF0CDB61B95A704E74B51B8B2CE59539CBA78CF94ACB096B199AF` | 42 entries; `byte_identical_roundtrip=OK` |

Entries 6 and 7 already re-extracted from each candidate LINK are byte-for-byte
identical to the standalone validated G1Ns:

| Re-extracted entry | Exact match | Size | SHA-256 |
|---|---|---:|---|
| SC 6 | yes | 25,883,120 | `E4F151238D3B331D73A09785D0B2736709B2B235DD1B308C06F082A83C15ADCA` |
| SC 7 | yes | 11,800,880 | `CE976A729FBCA8F3B18A7DF5137B78CF08A76E073A25635607500B8BD026CFAD` |
| TC 6 | yes | 16,638,068 | `0E63992235BB1E198BC78DC9A8F7BC97C1DDFC2CDF902832D11D709D340C06AE` |
| TC 7 | yes | 7,637,748 | `C1D7B8B02EBCA1A02134DD176A7CFDFCCB6953E3A7CCE552B1800F28BA894E9F` |
