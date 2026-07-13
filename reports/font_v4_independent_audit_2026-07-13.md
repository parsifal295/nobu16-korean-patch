# Font-v4 독립 감사 보고서 — 2026-07-13

## 결론

최신 동결된 `font_v4/build`과 `font_v4/build_determinism_2`를 읽기 전용으로 독립 감사했다. 요청된 파일 구조, G1N append-tail 계약, 요구 글자 커버리지, P3 회귀, 공개 경계, stock recipe replay, 결정성 및 금지 기능 검사를 모두 통과했다. 차단 사항은 발견되지 않았다.

이 결과는 오프라인 산출물의 구조·결정성·배포 경계를 승인하는 것이며 런타임 화면 검증을 대신하지 않는다. 현재 manifest와 공개 recipe의 `runtime_verified`/`runtime_direct_lookup_verified` 및 `release_eligible`은 의도대로 `false`다.

## 감사 범위와 방법

- 기준 트리
  - `KR_PATCH_WORK/workstreams/msgui_full/font_v4/build`
  - `KR_PATCH_WORK/workstreams/msgui_full/font_v4/build_determinism_2`
- 구현
  - `build_font_v4.py`
  - `rasterize_font_v4.ps1`
  - `compare_font_v4_builds.ps1`
  - 공용 file-only rebuilder `KR_PATCH_WORK/tools/build_file_only_font_recipe.py`
- 입력
  - `KR_PATCH_WORK/workstreams/msgui_full/build_p4_0401_1100/glyph_demand.json`
  - 순정 `RES_SC/res_lang.bin`
  - P3 Font-v3 공개 픽셀/metrics 기준물
- 독립 검사
  - 두 빌드의 전체 상대 경로, 크기, SHA-256 비교
  - G1N header/table/map/record/atlas를 직접 파싱해 stock과 target 비교
  - 요구 글자 387개를 entry 6/7, table 0/1에서 직접 조회
  - 모든 target record의 ordinal·record·pixel pointer 범위 검사
  - P3 공통 한글 226자의 픽셀 블록과 metrics JSONL 원시 바이트 비교
  - 공개 v2 recipe를 순정 archive에서 메모리 안에서 재생성하고 전체 LINK 바이트 비교
  - 공개 트리 allowlist, 완성 리소스 signature/크기 및 금지 API 정적 검색

감사 도중 게임을 실행하거나 설치 파일을 쓰지 않았다. 독립 구조 검사와 recipe replay는 Python `-B` 인메모리 방식으로 수행했다.

## 최신 동결 핀

| 산출물 | 크기 | SHA-256 |
|---|---:|---|
| `font_v4/build_font_v4.py` | 64,368 | `4CBE67E2DBBE27FC2A06E68002C7C411CB643D14FF73F257194011BDAFBD76F1` |
| `font_v4/rasterize_font_v4.ps1` | 14,483 | `5429B72D95023DC1096F52773DF0F0F56CC0468B212E6674FC4BFC7AC93D7157` |
| `font_v4/compare_font_v4_builds.ps1` | 3,668 | `A076D023E436FC1508E185E65F2F75F35AC3B228B9B0BF4BEBF7649BBE51C72E` |
| `tools/build_file_only_font_recipe.py` | 39,539 | `84471EBCCE14C2BD6C56C62B8758CA16BD604D6106FFC7C449D237774424EE33` |
| P4 `glyph_demand.json` | 18,505 | `7EE63999E2512659ED1504989964713F0D33078CAAB5E5A2350CE3B712FABC3A` |
| `build/public/recipe.json` | 311,007 | `EC4B9C68A1FF62DD06F53C55A30F45A3F12F62D1D1C7654196C780021288EA07` |
| entry 6 공개 pixel payload | 801,792 | `7131812389A78D10296BF7B5786E1CA387960C6F4A6875E0E793BAAFB1A13082` |
| entry 7 공개 pixel payload | 356,352 | `FD320B8D1ED831559B3F7C2E1F236D1D38376EDDC5EF59F345D99D7F93864EEC` |
| `build/public/metrics/glyphs.jsonl` | 443,134 | `514E46EDE2C7CB8027989EBE1B292664674226E3F555CD0B1BEE2C48A22E0EBE` |
| `build/manifest.json` | 5,271 | `51535F436ED54FF0888AE4FCFD7BC62F24B87B90208356E81BEEDDA15C1733F7` |
| `build/validation.json` | 65,223 | `CE42F2AB74633A2FC82A22C4F15BEF7B0F8ECED5B34B5E907E6574715462411C` |
| 비공개 entry 6 target G1N | 26,628,080 | `951906C6870F60F9342E9A90DF8DBF920D555092D3E06B1B822A41448740DD61` |
| 비공개 entry 7 target G1N | 12,136,240 | `C96704BF3A7FE1B29E3CB29361D1E56FCA8062CA73210CBCFCD73BE2E7C7CC66` |
| 비공개 target LINK archive | 180,350,761 | `3BC57379D9AF95E83A77C96C1EE2D104AAF4A8BEA1733EA33FC3D1BCF056D1A9` |

## 결정성

- 두 빌드는 각각 23개 파일이다.
- 공개 6개, 비공개 검증 파일 15개, `manifest.json`, `validation.json`의 상대 경로 집합이 같다.
- 23개 전부 크기와 SHA-256이 동일하다. tree diff는 0이다.
- 제공된 `compare_font_v4_builds.ps1`도 `exact=true`, 공개 6/6, 비공개 15/15 exact를 반환했다.
- 두 빌드의 manifest, validation, 공개 recipe, metrics, pixel payload 및 비공개 target archive가 모두 byte-exact다.

## corpus와 per-table append 계약

- 전체 demand: 387자
- 한글 완성형: 342자
- 비한글: 45자
- 네 map 모두에서 기존 stock으로 충족되는 비한글: 33자
- table 1에서만 신규 래스터가 필요한 문장부호: 12자

12자는 다음과 같다.

`U+00D7`, `U+2026`, `U+2192`, `U+2500`, `U+25CB`, `U+3010`, `U+3011`, `U+FF05`, `U+FF0B`, `U+FF0D`, `U+FF1D`, `U+FF5E`

| entry | table | append | 내용 |
|---:|---:|---:|---|
| 6 | 0 | 342 | 한글 342자만 |
| 6 | 1 | 354 | 한글 342자 + 문장부호 12자 |
| 7 | 0 | 342 | 한글 342자만 |
| 7 | 1 | 354 | 한글 342자 + 문장부호 12자 |

검사 결과:

- 한글 342자는 stock의 네 map에서 모두 ordinal 0이며 target에서만 신규 ordinal로 추가된다.
- 위 문장부호 12자는 entry 6/7 table 0에서 기존 stock ordinal, 12-byte record 및 pixel 바이트가 모두 동일하다.
- 같은 12자는 entry 6/7 table 1에서 stock ordinal 0이고 target에만 신규 추가된다.
- 나머지 비한글 33자는 네 map에서 기존 stock ordinal·record·pixel이 그대로 유지된다.
- 각 map의 실제 변경 codepoint 집합은 해당 table의 append 목록과 정확히 같다.

## G1N 구조, pointer 및 coverage

두 entry 모두 stock record count는 table 0/1에서 `21,898 / 100`, target은 `22,240 / 454`다.

- table 0 offset은 유지된다.
- table 1 offset은 table 0의 신규 record 342개, 즉 `342 × 12`바이트만큼 이동한다.
- atlas offset은 두 table의 신규 record `696 × 12`바이트만큼 이동한다.
- header는 선언 크기, atlas offset, table 1 offset만 달라지고 palette와 나머지 header 바이트는 같다.
- 기존 map은 append 대상 외에 동일하고 기존 record 영역도 byte-exact다.
- 완전한 stock atlas는 target atlas의 정확한 prefix다.
- 공개 generated pixel payload가 target의 정확한 tail이다.
- 모든 map ordinal은 각 table의 record count보다 작다.
- target의 ordinal 1 이상 record 45,384개를 전부 검사했고 height, stride, pointer 및 pixel end가 모두 target atlas 범위 안에 있었다.
- 387자 × 4개 map, 총 1,548개 직접 조회에서 모두 nonzero ordinal과 nonblank pixel을 확인했다.

## P3 Font-v3 회귀

P3 기준물은 다음 해시로 고정해 비교했다.

| 기준물 | SHA-256 |
|---|---|
| P3 demand | `43C23F44A9794A1461BA84AEB919FDC661B97D285BA96AE3102F8A3842C5D8DA` |
| P3 metrics | `9AB29BC75F3A14FC40A240BCDE40C3076A759B7B8A255E04A9630F5D71176D7D` |
| P3 entry 6 pixels | `BBBEE931A8F856C220BFC1489BC8DF5B026C687E78C64A926A750DAC3B68F96B` |
| P3 entry 7 pixels | `A3319739970E41A39FBDCE1FE6DB4AF7EE91A8F165C8F741DBC524653442B3B1` |

- 공통 한글 226자 × entry 2개 × table 2개의 904개 pixel block이 byte-exact다.
- 같은 904개 metrics JSONL line을 원시 바이트 단위로 비교해 모두 일치했다.
- 최신 Font-v4 공개 metrics는 실제 table별 append만 포함하며 정확히 1,392행이다: `2 × (342 + 354)`.

## 공개 recipe의 순정 stock replay

- stock archive: 160,318,119바이트, SHA-256 `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- 공개 schema: `nobu16.file-only-g1n-tail-recipe.v2`
- 공개 recipe와 두 generated pixel payload만 사용해 순정 stock에서 entry 6/7을 인메모리 재구성했다.
- 재구성한 두 G1N은 비공개 target G1N과 각각 byte-exact다.
- 전체 LINK archive 재구성 결과는 180,350,761바이트, SHA-256 `3BC57379D9AF95E83A77C96C1EE2D104AAF4A8BEA1733EA33FC3D1BCF056D1A9`이며 비공개 candidate와 완전히 동일하다.
- LINK는 42개 entry다. entry 6/7 외 40개 compressed wrapper가 stock과 byte-exact다.
- 재구성 LINK에서 entry 6/7을 다시 추출한 raw G1N도 target과 byte-exact다.
- stock 및 target LINK의 parse/rebuild identity roundtrip을 통과했다.

## 공개 배포 경계

`build/public`은 다음 6개만 포함한다.

| 공개 파일 | SHA-256 |
|---|---|
| `licenses/OFL-NotoSansKR.txt` | `1C05C68C34F9708415AADA51F17E1B0092D2CEA709BF4A94CD38114F9E73D7D9` |
| `licenses/OFL-NotoSerifKR.txt` | `5E0DA210FB04058A8C0087985D2D456B931C2579811A49655721D3CF0C36B6D6` |
| `metrics/glyphs.jsonl` | `514E46EDE2C7CB8027989EBE1B292664674226E3F555CD0B1BEE2C48A22E0EBE` |
| `payload/glyph_pixels_entry_6.bin` | `7131812389A78D10296BF7B5786E1CA387960C6F4A6875E0E793BAAFB1A13082` |
| `payload/glyph_pixels_entry_7.bin` | `FD320B8D1ED831559B3F7C2E1F236D1D38376EDDC5EF59F345D99D7F93864EEC` |
| `recipe.json` | `EC4B9C68A1FF62DD06F53C55A30F45A3F12F62D1D1C7654196C780021288EA07` |

- allowlist 외 파일은 없다.
- 완성 G1N, LINK/archive, EXE, DLL 또는 상용 원문은 없다.
- 공개 파일 어느 것도 완성 stock/target 리소스 크기와 같지 않고 `_N1G0000` 또는 `LINK` signature로 시작하지 않는다.
- binary payload는 고정 Noto KR에서 생성한 glyph pixels뿐이다.
- `commercial_original_bytes_in_public_payload=false`, `stock_archive_required_at_apply_time=true`다.
- 완성 G1N과 LINK candidate는 `private`에만 있으며 `distribution_forbidden=true`다.

## 금지 기능 정적 검사

builder, rasterizer, comparer 및 공용 recipe rebuilder에서 다음 계열을 대소문자 무시 검색했다.

- `OpenProcess`, `ReadProcessMemory`, `WriteProcessMemory`
- `VirtualAllocEx`, `VirtualProtectEx`, `CreateRemoteThread`
- `NtWriteVirtualMemory`, `NtCreateThreadEx`, `SetWindowsHookEx`
- `LoadLibrary`, `GetProcAddress`, `DllImport`
- Registry API, `reg.exe`, `Start-Process`, `Process.Start`, `ShellExecute`
- NOBU 실행 파일, injection/hooking/memory-patch 표기

기능성 적중은 0건이다. 유일한 문자열 적중은 공용 recipe 도구가 기록하는 `contains_runtime_memory_patch: False` 선언이었다. builder의 `subprocess.run`은 고정된 `rasterize_font_v4.ps1`을 Windows PowerShell로 실행하는 경로 하나뿐이며 게임·런처를 실행하지 않는다. 공개 recipe도 `file_only=true`, `process_memory_access=false`, `registry_access=false`, `runtime_patch_features=[]`다.

## 기존 자산과 설치본 불변

| 항목 | 현재 SHA-256 | 판정 |
|---|---|---|
| P3 catalog | `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA` | 기존 핀 유지 |
| P3 message recipe | `49570FE246028113C19AE2DFCB12633DC9EC23401A02EDA3B95245EB611E070D` | 기존 핀 유지 |
| Font-v3 recipe | `1A2B882AF265D599974B5278C409CE76B4435DF9CE5BB0FDC751B6881F0BE691` | 기존 핀 유지 |
| v0.2 release manifest | `0ACD79C83464F6306C2910C253EE3E022965CCFF5DDE570DF31D64648003B7FC` | 기존 핀 유지 |
| v0.2 ZIP | `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8` | 기존 핀 유지 |
| v0.2 ZIP sidecar | `D977FA4223ED5C94CEE5E24103DCC24028213388C1AD784D4D80A043DFF8636C` | 기존 핀 유지 |
| 설치 `MSG_PK/SC/msgui.bin` | `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82` | 순정 |
| 설치 `RES_SC/res_lang.bin` | `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99` | 순정 |

감사 종료 시 NOBU 계열 실행 프로세스는 0개였다.

## 남은 게이트

Font-v4 자체의 오프라인·결정성·공개 경계 감사는 통과했다. 그러나 P4 메시지와 Font-v4를 결합한 격리 설치/복원, 간체중문 실행 경로의 실제 화면 렌더링, 대표 신규 116자 및 문장부호 렌더링, 정상 종료 후 stock 원복 증거가 아직 필요하다. 이 런타임 증거를 고정하기 전에는 `runtime_verified=false`와 `release_eligible=false`를 유지해야 한다.
