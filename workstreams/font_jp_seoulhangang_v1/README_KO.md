# 일본판 기반 서울한강체 G1N 파이프라인 v1

일본어 경로로 실행하는 PC PK용 글꼴 후보를 파일만으로 재구성한다. 현재 로컬 기준 설치 경로는 `F:/SteamLibrary/steamapps/common/NOBU16`이며, 안전 후보에는 다음 두 파일을 모두 포함한다.

- `RES_JP/res_lang.bin`: LINK 42개, G1N outer entry 6/7
- `RES_JP_PK/res_lang_pk.bin`: LINK 27개, G1N outer entry 16/17

검토한 로컬 **비Steam** `NOBU16PK.exe`에는 `/res_lang.bin`(0x13BDFC0), `/res_lang_pk.bin`(0x13BE050), `RES_JP`(0x13BE1F0), `_PK`(0x13BE214)가 각각 존재한다. 이는 base와 PK 정적 경로가 별개임을 보여 주지만 현재 Steam 런타임이 둘 중 어떤 조합을 실제로 여는지는 증명하지 않는다. file-open trace 전까지 “둘 다 필수” 또는 “PK가 base를 대체하지 않는다”고 확정하지 않는다. 누락 위험을 피하기 위한 안전 후보에만 두 파일을 함께 포함한다.

## 실제 글꼴 위계

각 G1N에는 65,536칸 맵이 3개 있다. 12바이트 레코드의 byte 1/3/7이 셀 높이를 가리키고 atlas pointer stride도 이에 맞는다.

| G1N | table 0 | table 1 | table 2 | 배정 |
|---|---:|---:|---:|---|
| base 6 / PK 16 | 48 | 48 | 48 | EB / EB / EB |
| base 7 / PK 17 | 32 | 48 | 32 | B / EB / B |

table 2는 소형 티어가 아니다. 6/16 table 2 stride는 1,152바이트(48×48/2), 7/17 table 2 stride는 512바이트(32×32/2)다. 모든 48셀은 공식 `SeoulHangangEB.ttf`, 모든 32셀은 공식 `SeoulHangangB.ttf`로 렌더한다. 공식 `SeoulHangangM.ttf`는 같은 공식 ZIP의 개별 해시를 고정했지만 32보다 작은 대상 셀이 없어 사용하지 않는다.

## cmap fallback 차단과 stock 재사용

빌드 전에 EB/B TTF의 Unicode cmap을 직접 파싱한다. append union 1,308개 중 두 TTF 모두 정확히 `U+32A4`, `U+FF65`만 cmap에 없다. 그 밖의 문자가 하나라도 없거나 이 두 문자의 상태가 바뀌면 즉시 실패한다. 따라서 GDI가 다른 시스템 글꼴로 fallback해 환경마다 다른 픽셀을 만드는 경로가 없다.

두 문자는 각 G1N의 같은 셀인 table 0에 이미 있다. table 0의 8바이트 metric과 width-packed pixel을 읽어 table 2의 **새 atlas tail**에 복사하고 table 2의 새 record가 그 새 위치를 가리키게 한다. 기존 table 0 pointer를 alias하지 않는다.

- TTF raster: 1,306개, `E056B7630AE5055647421C5F53ABADC7BD49B9FE44E5BA8DF4421503D32888C6`
- stock reuse: 2개, `56FA9232EA268ED0FE5B776534B5B7A1A09DBCEAAC8D1E8C27A5EE5E68F13BE4`

## 최신 수요와 입력 잠금

- 공개 overlay 118개, 항목 83,658개
- 전체 코드포인트 1,419개, 한글 음절 1,247개
- B12/B13/B14/B15 및 msggame B07의 중앙 진행표 등록 전·후에 같은 정규화 catalog와 같은 후보 바이트 생성
- JP stock base/PK 크기와 SHA-256 fail-closed
- 서울시 공식 `seoul_font3.zip` 및 EB/B 개별 TTF SHA-256 고정

Switch 완성 archive나 glyph payload를 복사하지 않는다.

## 재현 명령

출력은 repository `tmp` 아래의 새 빈 경로이며 설치된 게임 파일을 덮어쓰지 않는다.

```powershell
python workstreams/font_jp_seoulhangang_v1/build_jp_seoulhangang_v1.py build `
  --font-eb F:\private\SeoulHangangEB.ttf `
  --font-b F:\private\SeoulHangangB.ttf `
  --output-root F:\repo\tmp\jp_font_candidate
```

TTF 없이 기존 후보의 구조·보존·고정 출력 해시를 다시 검사할 수 있다.

```powershell
python workstreams/font_jp_seoulhangang_v1/build_jp_seoulhangang_v1.py verify `
  --candidate-root F:\repo\tmp\jp_font_candidate
```

독립 A/B 빌드는 모든 후보·raster·manifest에서 바이트 단위로 일치했다.

- base 후보: 175,097,407 bytes, `4395B84C5F678E37D8F39BCEEFF1986F62B07A54FF7936FC1402412AF07536F2`
- PK 후보: 162,625,225 bytes, `697F5034140A35A676CC0D0006CCECE4753D823109C5792500C46DE6499C9C12`

## 보존 계약

대상 4개 G1N에서는 demand에 필요한 새 map ordinal·record·atlas tail만 append한다. 기존 map(append 좌표 제외), 기존 record, palette, stock atlas 전체 prefix는 동일하다. 비대상 LINK entry와 gap도 동일하므로 그 안의 G1T/이미지도 바뀌지 않는다.

공개 workstream에는 source-free recipe·해시·구조 증거·테스트만 둔다. TTF, raster pixel, stock/candidate G1N, 완성 `res_lang*.bin`은 포함하지 않는다.
