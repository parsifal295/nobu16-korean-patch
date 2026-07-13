# NOBU16PK generic executable language backend

Date: 2026-07-13 (Asia/Seoul)

## Result (corrected by stock-runtime probe)

The generic executable does **not** obtain its JP/SC/TC selection from a
language command-line switch or from `SteamData/configPK.n16`.  Its normal
path reads a four-byte registry value:

```text
HKEY_CURRENT_USER\Software\KoeiTecmo\NOBU16\Configs
    LANGUAGE    REG_DWORD
```

The host already contained this active product key with `LANGUAGE=3`.  That
value predicts Japanese through the `3 -> 1` mask remap below, and direct stock
generic launch did boot Japanese.  A journaled stock-runtime probe against a
second candidate path, `KoeiTecmo\Nobunaga??\Configs\LANGUAGE=1`, was ignored:
the same stock executable still booted Japanese.  This dynamically disproves
the earlier claim that `Nobunaga??` was the active product root.

A sequence of journaled stock-runtime probes established the two Chinese
values.  Active `NOBU16\Configs\LANGUAGE=1` produced the Traditional-Chinese
window/title/dialog path.  Active `LANGUAGE=2` produced Simplified Chinese,
including the on-screen `请点击鼠标`.  The latter log session began at
`2026/07/13 18:05:17` and records both the generic executable and the
Simplified-Chinese system-file selection:

```text
boot_path:F:\Games\NOBU16\NOBU16PK.exe
System file is not found, create new one.
"configPKSC.n16"
```

That `LANGUAGE=2` session reached `All initialization is complete..`.  It
contains no literal `9001`, so the visible 9001 shutdown is later than language
selection and is not evidence that the registry mapping failed.  The probe
owner restores the pre-test registry value separately; this analysis did not
modify HKCU.

`Nobunaga??` does exist as a literal in the analysis image:

```text
ASCII / UTF-8:  Nobunaga??
hex:            4e 6f 62 75 6e 61 67 61 3f 3f 00
```

It belongs to an inactive/base-class virtual route.  The initial "absent"
observation was made from a restricted tool registry view and must not be used
as evidence about the host user's HKCU hive.

## Active concrete `NOBU16` registry route

The diagnostic image also contains a concrete, non-placeholder product-root
helper that matches the stock-runtime result:

- `FUN_1407E0470` opens `HKEY_CURRENT_USER\software` with access mask
  `0x2001f`, then opens/creates `KoeiTecmo`, followed by `NOBU16`.
  - `"KoeiTecmo"` is at `0x1413BF830`; its code reference is
    `0x1407E0504`.
  - `"NOBU16"` is at `0x1413BF83C`; its product-root code reference is
    `0x1407E053F`.
  - A second reference to the same `NOBU16` literal, `0x140E8C51B`, belongs
    to log-path construction and is not the registry opener.
- `FUN_1407DB4A0`, the concrete configuration loader, calls
  `FUN_1407E0470`, opens/creates the `Configs` subkey, and reads its DWORD
  values through `FUN_140918710` (`RegQueryValueExA` with a four-byte data
  buffer).
- `FUN_1407DF480`, the corresponding configuration writer, calls
  `FUN_1407E0470`, opens `Configs`, and writes DWORD values through
  `FUN_140918930` (`RegSetValueExA`-style wrapper).

This gives the exact active configuration route as:

```text
HKCU\Software\KoeiTecmo\NOBU16\Configs
```

The virtual `Nobunaga??` route described below is a base-class artifact in the
diagnostic dump.  Its earlier promotion to the active language path was a
static hypothesis, and the stock-runtime probe disproved it.  The concrete
`NOBU16` route plus the observed `LANGUAGE=3 -> Japanese` behavior is the
authoritative result.  Resolving which final override connects the language
accessor to that concrete route is not required for the file-only release and
must not be guessed from the dump's base vtable.

## Static language accessor and base virtual route

Static addresses below refer to the analysis-only diagnostic image
`KR_PATCH_WORK/data/raw/NOBU16PK.unpacked.exe`.  The stock executable itself is
not modified or distributed.

1. `FUN_1408E07A0` is a base constructor for the global application/config
   object.
   - base vtable written there: `DAT_1413EE200`
   - `[object + 0x10] = 1`, selecting the registry backend
   - initial `[object + 0x22c] = 1`
   - stores the object in `DAT_141F368A8`
2. `FUN_140E8B600`, call site `0x140E8B661`, calls
   `FUN_1408E8040(DAT_141F368A8)` during initialization.
3. `FUN_1408E8040` calls
   `FUN_1408F4A90(object, "Configs", "LANGUAGE", 0)`.
   - `"Configs"` at `0x1413BF888`
   - `"LANGUAGE"` at `0x1413EE6F8`
4. Because `[object + 0x10] == 1`, `FUN_1408F4A90` takes the registry path and
   calls `FUN_1408F4F00` to open/create the `Configs` subkey.  The alternate
   `[object + 0x10] == 0` branch calls `GetPrivateProfileIntA`; the observed
   stock configuration uses the registry backend instead.
5. `FUN_1408F4F00` calls `FUN_1408F3A50` for a virtual product root, then
   `FUN_140916500` (`RegCreateKeyExA`) for `Configs`.
6. `FUN_1408F3A50` opens `HKCU\software`, then obtains publisher and product
   components through virtual methods.  The base-vtable implementations visible
   in the diagnostic image are:
   - opens `HKCU\software` with `RegOpenKeyExA`;
   - obtains `KoeiTecmo` from vtable slot `+0xA0`, implemented by
     `FUN_1408F4EE0`;
   - obtains literal `Nobunaga??` from vtable slot `+0xB0`, implemented by
     `FUN_1408F3DD0`;
   - opens/creates both components with `RegCreateKeyExA`.

   That base product method is not the active stock-runtime method.  Runtime
   evidence proves the effective product component is `NOBU16`: the host's
   existing `HKCU\Software\KoeiTecmo\NOBU16\Configs\LANGUAGE=3` controls the
   observed JP selection, while the parallel `Nobunaga??` value does not.
7. `FUN_1408F4A90` calls `FUN_140918710`, a `RegQueryValueExA` wrapper with a
   four-byte destination.  Therefore `LANGUAGE` is a `REG_DWORD`.  Missing or
   unreadable data leaves the supplied default (`0`) in effect.

Direct-reference audit:

- `FUN_1408E8040` has one direct code caller: `0x140E8B661` in
  `FUN_140E8B600` (plus a data-table reference).
- `FUN_1408F4A90` is called by `FUN_1408E8040` for language selection.
- The `LANGUAGE` configuration string at `0x1413EE6F8` has one code reference,
  `0x1408E8049` in `FUN_1408E8040`.

## Value mapping

`FUN_1408E8040` accepts values `0..3`, computes `1 << value`, and remaps the
computed value `8` to `1`:

The bit masks alone do not name the resource languages.  Stock-runtime probes
are authoritative for assigning the `2` and `4` masks; the earlier static-only
SC/TC labels were reversed.

| Registry DWORD | Stored language mask (`object + 0x22c`) | Result |
|---:|---:|---|
| 0 | 1 | Japanese |
| 1 | 2 | Traditional Chinese (stock-runtime confirmed) |
| 2 | 4 | Simplified Chinese (stock-runtime and `configPKSC.n16` confirmed) |
| 3 | 1 | Japanese in the generic executable (explicit remap from 8) |
| 4 or higher | unchanged; function reports failure | invalid |

The generic executable therefore has no English state.  The official launcher
uses the separate `NOBU16PK_EN.exe` executable for English rather than passing
an English value to `NOBU16PK.exe`.

## Command-line audit

`FUN_140E8C390` copies `GetCommandLineA()` into a 4096-byte buffer and invokes
vtable slot `+0x68`.  For the constructed object that slot resolves to
`FUN_1408E1F30`.

`FUN_1408E1F30` tokenizes `-` or `/` options and recognizes these literals:

- `logoff`
- `adapter` followed by an integer
- `output` followed by an integer
- `m`

No `language`, `lang`, `-language`, or `/language` command-line option is
implemented in that parser.  Whole-image string/xref inspection likewise found
the configuration key `LANGUAGE` referenced only by `FUN_1408E8040`.  The
confirmed language transfer mechanism is consequently the registry value, not
a generic-executable command-line argument.

The on-disk official launcher is protected/packed.  Its imports include the
registry APIs, `ShellExecuteW`/`ShellExecuteExW`, and Steam API functions, but
its protected code does not provide reliable static call-site xrefs.  This
report therefore does not claim an unverified launcher command-line builder.

## Separate `configPK.n16` path

The `SteamData/configPK.n16` system file is a separate binary settings store.
The corresponding system-file routines (`FUN_1407D81A0`, `FUN_1407DCE40`,
`FUN_1407DD0D0`, and `FUN_1407DD250` in the English diagnostic image) construct,
load, create, and serialize that file.  Registry helpers independently read and
write the `Configs` values.  Changing the launcher's graphics dialog without a
`configPK.n16` timestamp/hash change is therefore consistent with the language
value not living in that binary file.

## Release and safety constraints

This finding does not authorize executable patching, runtime hooks, injection,
or process-memory access.  The Korean patch release contract remains:

```text
architecture = file-only-offline
process_memory_access = false
executable_modified = false
requires_process_running = false
payload_format = recipes-and-deltas-only
```

Do not ship a runtime patcher, unpacked executable, full `res_lang.bin`, or full
`msgui.bin`.  Distribution payloads must contain only verified recipes/deltas
and restoration metadata.  In particular, the older RuntimePatcher-based
main-menu release is excluded from all future bundles.
