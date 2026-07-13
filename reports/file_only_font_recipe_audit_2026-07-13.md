# 파일 전용 Noto 한글 폰트 recipe 감사 보고서

작성일: 2026-07-13

대상: `RES_SC/res_lang.bin`, `RES_TC/res_lang.bin`의 LINK entry 6/7

판정: **구조·재현성 검증 통과 / 게임 내 렌더링 미검증 / `release_eligible=false`**

## 결론

`KR_PATCH_WORK/tools/build_file_only_font_recipe.py`는 stock `res_lang.bin`을
SHA-256으로 확인한 뒤 entry 6/7을 메모리상에서 해제하고, 다음 세 종류의
후보 전용 데이터만 적용한다.

1. 각 G1N table의 한글 28자 map write
2. 각 G1N table에 추가되는 12-byte record 28개
3. OFL Noto 글꼴에서 생성한 새 glyph pixel tail

stock 헤더·팔레트·기존 map·기존 record·기존 atlas·LINK entry·실행 파일
바이트는 recipe payload에 포함하지 않는다. 적용 시 사용자 소유 stock
archive에서만 읽고, 결과는 별도의 tmp 파일로 만든다. 설치 파일, 실행 중인
프로세스, 메모리, 레지스트리는 건드리지 않는다.

## 배포 payload 경계

배포 대상으로 간주한 경계는
`KR_PATCH_WORK/tmp/file_only_font_recipe/release_payload` 아래의 여덟 개 파일뿐이다.
적용 도구와 LINK/LZ4 모듈을 소스 형태로 함께 넣어 이 디렉터리만으로 재적용할
수 있게 했다. 실제 적용 뒤에도 `*.pyc`나 `__pycache__`가 생기지 않음을 확인했다.

| 파일 | 크기 | SHA-256 | 출처 |
|---|---:|---|---|
| `recipe.json` | 57,121 | `8EF8E3E43EF6431232E427E60E576A0D1E7AE7EFC9C1797F1A9D6BD66CA2AF9B` | 구조 명령·원본/결과 hash gate |
| `AUDIT.json` | 2,509 | `2067F91247A5FDCA784BFA2FDD45E4EF0FFB2D4E4EB3019A89430B337D40AC09` | 기계 판독 감사 결과 |
| `payload/glyph_pixels_entry_6.bin` | 64,512 | `7CA9A076F3E44AE2861B1FDEC05D43729313E12BB5C81F945A8E4E049242DABF` | 후보의 stock-atlas 이후 Noto pixel tail만 |
| `payload/glyph_pixels_entry_7.bin` | 28,672 | `B647A7B729DA2E1BA92229C5B29E1F104DE134BFF3461126D4A0F0957F32F378` | 후보의 stock-atlas 이후 Noto pixel tail만 |
| `licenses/OFL-NotoSansKR.txt` | 4,388 | `1C05C68C34F9708415AADA51F17E1B0092D2CEA709BF4A94CD38114F9E73D7D9` | SIL OFL 1.1 |
| `licenses/OFL-NotoSerifKR.txt` | 4,350 | `5E0DA210FB04058A8C0087985D2D456B931C2579811A49655721D3CF0C36B6D6` | SIL OFL 1.1 |
| `tools/build_file_only_font_recipe.py` | 37,551 | `AC1CAA3C3F0E7BDDDE9FC5571875F02C89617A47A904D217B15AB57F28EC7E1D` | 파일 전용 표준 라이브러리 applier 소스 |
| `tools/nobu16_lz4.py` | 23,537 | `ABCE481B4424308DAB83A2301A6293443239E69AB1712B0D809D5DA284D64E08` | LINK/LZ4 표준 라이브러리 소스 |

binary glyph payload 합계는 **93,184 bytes**다. `recipe.json`에 들어가는 record는
모두 새 glyph용 record이며 기존 상업 리소스 record는 없다. 원본 파일의 hash,
크기, offset, record count 같은 수치형 구조 정보만 포함한다.
여덟 파일 전체 크기는 **222,640 bytes**다.

`KR_PATCH_WORK/tmp/file_only_font_recipe/verification` 아래에 생성된 G1N 및
`res_lang.*.recipe.bin`은 재현성 확인을 위한 상업 원본 파생 tmp 산출물이다.
**배포 payload에 포함하면 안 된다.**

## 원본 byte 미포함 감사

recipe 생성 코드는 후보 G1N에서 다음 경계만 binary payload로 쓴다.

```text
candidate[new_atlas_offset + complete_stock_atlas_length : EOF]
```

그 앞의 complete stock atlas가 stock과 byte-identical인지 먼저 검사하며, header는
file size·atlas offset·table-1 offset 외의 변경을 거부한다. 두 table의 map은 지정된
28개 codepoint 외의 변경을 거부하고, 기존 record 배열은 byte-identical이어야 한다.
따라서 payload 생성 경로에는 stock byte range를 복사하는 코드가 없다.

폰트 provenance는 다음과 같이 고정했다.

- Google Fonts commit: `ec0464b978de222073645d6d3366f3fdf03376d8`
- `NotoSansKR-wght.ttf`: `194018E6B2B293A7964F037B25C0249CE1418BC9AB3C971060A03AA57861E252`
- `NotoSerifKR-wght.ttf`: `11F8D5DE6F1B79195EFBA3828AAA2EC95C1178F5AE976FB23C8D53250A9938F3`

## 재적용 및 roundtrip 결과

재현 명령은 다음과 같다. 두 apply 명령은 설치 경로의 stock archive를 읽기만 하고
결과를 `KR_PATCH_WORK/tmp` 아래에 새로 쓴다.

```powershell
python KR_PATCH_WORK/tools/build_file_only_font_recipe.py export
python KR_PATCH_WORK/tmp/file_only_font_recipe/release_payload/tools/build_file_only_font_recipe.py apply `
  --recipe KR_PATCH_WORK/tmp/file_only_font_recipe/release_payload/recipe.json `
  --language SC --stock-archive RES_SC/res_lang.bin `
  --output-dir KR_PATCH_WORK/tmp/file_only_font_recipe/verification/SC
python KR_PATCH_WORK/tmp/file_only_font_recipe/release_payload/tools/build_file_only_font_recipe.py apply `
  --recipe KR_PATCH_WORK/tmp/file_only_font_recipe/release_payload/recipe.json `
  --language TC --stock-archive RES_TC/res_lang.bin `
  --output-dir KR_PATCH_WORK/tmp/file_only_font_recipe/verification/TC
```

### SC

- stock archive gate: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- entry 6 결과: `E4F151238D3B331D73A09785D0B2736709B2B235DD1B308C06F082A83C15ADCA`
- entry 7 결과: `CE976A729FBCA8F3B18A7DF5137B78CF08A76E073A25635607500B8BD026CFAD`
- 최종 archive 결과: `7FB2E6E7ABE2ADC7C359170ECB92952054C2F7F412933B8F1B339B6ADE661B7E`
- 기존 pinned-Noto SC 후보와 standalone G1N 및 최종 LINK archive가 모두 byte-identical
- LINK parse/rebuild, entry 재추출, 입력 archive 불변 검증 통과

### TC

- stock archive gate: `A286388AC4A8F6E03E3BD5AC5B91069E858805EBBE81F670991B162A813B0B2F`
- entry 6 결과: `0E63992235BB1E198BC78DC9A8F7BC97C1DDFC2CDF902832D11D709D340C06AE`
- entry 7 결과: `C1D7B8B02EBCA1A02134DD176A7CFDFCCB6953E3A7CCE552B1800F28BA894E9F`
- 최종 archive 결과: `5228871705DBF0CDB61B95A704E74B51B8B2CE59539CBA78CF94ACB096B199AF`
- 기존 pinned-Noto TC 후보와 standalone G1N 및 최종 LINK archive가 모두 byte-identical
- LINK parse/rebuild, entry 재추출, 입력 archive 불변 검증 통과

SC와 TC의 Noto pixel payload는 entry별로 완전히 같으므로 하나씩만 저장한다.
언어별 map ordinal과 atlas pointer 차이는 `recipe.json`의 새 record/map 명령으로
분리했다.

추가로 `validate_g1n_surgical.py --mode append-tail`을 재구성된 SC/TC entry 6/7
네 개에 독립 실행했다. 네 경우 모두 `[PASS]`, `appended_records=[28, 28]`, 각
table의 변경 codepoint가 지정된 28자와 정확히 일치했다.

## 파일 안전성과 금지 기능

- 원본 archive와 출력 경로가 같으면 즉시 중단한다.
- 모든 stock entry/archive에 exact SHA-256 gate를 적용한다.
- 출력은 임시 파일을 완전히 쓴 뒤 `os.replace`로 확정한다.
- export 대상 디렉터리에 감사 inventory 밖의 파일이 있으면 dirty package로 보고
  덮어쓰지 않고 중단한다.
- 적용 전후 stock archive SHA-256을 비교해 불변을 확인한다.
- 다른 LINK entry payload가 한 byte라도 바뀌면 실패한다.
- `WriteProcessMemory`, process handle, DLL injection, hook, resident launcher,
  registry write 기능은 구현하지 않았다.

부정 테스트로 SC recipe에 TC stock archive를 입력했으며, 출력 디렉터리를 만들기
전에 stock SHA-256 mismatch로 종료 코드 1을 반환했다. 테스트 뒤 실제 SC/TC stock
archive hash도 각각 원래 값과 동일했다.

도구 hash:

- `build_file_only_font_recipe.py`: `AC1CAA3C3F0E7BDDDE9FC5571875F02C89617A47A904D217B15AB57F28EC7E1D`
- `nobu16_lz4.py`: `ABCE481B4424308DAB83A2301A6293443239E69AB1712B0D809D5DA284D64E08`

## 남은 release gate

이 검증은 파일 구조와 결정론적 재현성만 증명한다. 실제 게임의 SC/TC 경로에서
28개 한글 codepoint가 새 record를 직접 조회하고 화면에 정상 렌더링되는지는 아직
검증하지 못했다. 따라서 recipe와 모든 apply report는 의도적으로
`runtime_direct_lookup_verified=false`, `release_eligible=false`를 유지한다.
