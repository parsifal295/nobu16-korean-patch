# Steam JP 한글 글리프 폭 최적화 감사·후보 v1

Switch 한글 패치 v2.2→v2.3의 긴 대사 줄바꿈 개선을 Steam PK 1.1.7 일본어 경로에 **파일만으로** 옮기기 위한 작업이다. 이 workstream은 아직 게임 파일을 적용하거나 릴리즈하지 않는다.

## 확정된 Switch 근거

Switch `RES_JP/res_lang.bin`의 `/6`, `/7`만 v2.2→v2.3에서 변경됐다. 최적화 집합은 정확히 다음 2,405 codepoint다.

- 공백 `U+0020`: 1개
- 호환 자모 `U+3131–U+3163`: 51개
- 한글 음절: 2,353개
- 전체 SHA-256: `FD1338F53F1AB1B634496C65CA5AED5F5D182C2731B6A32E4AE1366A6030848D`

12-byte G1N record에서 바뀐 것은 서로 묶인 세 필드다.

| byte | 의미 | v2.3 규칙 |
|---:|---|---|
| 0 | visible width | 짝수 새 폭 |
| 4 | advance | byte 0과 동일 |
| 5 | signed 4bpp row stride | `-(width / 2)` |

맵과 record pointer(8–11)는 그대로지만 atlas 바이트는 실제로 바뀐다. 각 glyph의 기존 allocation 안에서 실제 잉크를 포함하는 행 구간을 glyph별 x-offset에서 잘라 새 stride로 연속 pack하고, 남은 allocation tail을 0으로 채운다. 따라서 record만 고치면 줄 단위 stride가 달라져 글자가 깨질 수 있으며 금지한다.

## PC 대응 범위

현재 Steam JP v0.9 폰트는 각 table에 최적화 집합 중 1,253개만 있어 1,152개(음절 1,102 + 자모 50)를 추가해야 전체 Switch 범위를 만족한다. 7개 실제 PK font G1N 모두에 적용한다.

| Steam PK 경로 | G1N outer | PC profile | Switch metric 근거 |
|---|---:|---|---|
| `RES_JP/res_lang.bin` | `/6`, `/7` | EB48 / B32·EB48·B32 | `/6` 48px, `/7` table0 24px |
| `RES_JP_PK/res_lang_pk.bin` | `/16`, `/17` | 위 regular 계층과 동일 | 위와 동일 |
| `RES_JP_PK_PORT/res_lang_pk_port1.bin` | `/1` | B64·EB96·B32 | 24→64, 48→96, 24→32 |
| `RES_JP_PK_PORT/res_lang_pk_port2.bin` | `/0`, `/1` | EB96 / B64·EB96·B64 | 48→96, 24→64 |

`/6` PC table 2의 EB fallback은 현 JP builder가 table 0과 같은 SeoulHangang EB raster를 쓰므로 Switch `/6` table 0 metric을 사용한다. B32/B64는 Switch `/7` table 0을 사용한다. Switch 이미지·crop x-offset은 복사하지 않는다.

## PC metric과 pixel 정책

- 32/48/64/96px target cell마다 `source_width * target_cell / source_cell`을 계산한다.
- 4bpp 제약 때문에 가장 가까운 **짝수** 폭을 고르고, 동률이면 넓은 값을 선택한다.
- 각 SeoulHangang PC glyph의 실제 nonzero ink bbox가 새 폭에 완전히 들어가는 crop window를 계산한다. 맞지 않으면 넓히지 않고 fail-closed한다.
- window는 Switch x-offset이 아니라 **PC raster ink bbox 중심**에서 정한다.
- 기존 glyph은 같은 PC allocation에서 crop+row-pack하므로 보이는 잉크를 잃지 않는다. 추가 1,152 glyph만 SHA-pinned 공식 SeoulHangang EB/B TTF로 새로 raster한다.
- `U+0020`은 유일한 허용 blank glyph이다. Switch-derived triplet을 쓰고 packed payload/tail을 0으로 만든다. 다른 blank glyph은 실패다.

## 후보 빌더

`build_steam_jp_font_advance_candidate_v1.py`는 다음을 모두 gate한다.

- Steam JP 1.1.7 v0.9 preimage SHA/size
- Switch v2.2/v2.3 ZIP 및 G1N crop+row-pack 근거
- 공식 SeoulHangang TTF SHA/cmap
- 2,405개 전 table coverage와 record capacity
- 기존 record pointer, 맵, 보호 metric bytes, non-target LINK entry 보존
- atlas 변경이 최적화 glyph allocation 내부로만 한정됨
- candidate output SHA/size 및 LINK 재추출

출력은 반드시 빈 `KR_PATCH_WORK/tmp/...` 아래의 private candidate여야 한다. 아래 예시는 게임에 쓰지 않는다.

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\steam_jp_font_advance_audit_v1\build_steam_jp_font_advance_candidate_v1.py `
  --input-root F:\SteamLibrary\steamapps\common\NOBU16 `
  --switch-v22-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.2.zip `
  --switch-v23-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.3.zip `
  --font-eb tmp\third_party_fonts\SeoulHangangEB.ttf `
  --font-b tmp\third_party_fonts\SeoulHangangB.ttf `
  --powershell C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe `
  --output-root tmp\steam_jp_font_advance_candidate_v1
```

공개 workstream에는 코드·검증 메타데이터만 둔다. Switch/Steam resource, raster payload, candidate `.bin/.g1n`, TTF는 포함하지 않는다.
