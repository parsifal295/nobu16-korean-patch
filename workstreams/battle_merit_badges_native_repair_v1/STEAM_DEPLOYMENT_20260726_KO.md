# Steam 적용 기록 — build_005

## 결과

`PASS`

- 적용 시각: `2026-07-26T16:18:25.7564369+09:00`
- Steam 루트: `F:\SteamLibrary\steamapps\common\NOBU16`
- 적용 후보: `tmp/battle_merit_badges_native_repair_v1/build_005`
- 적용 중 `NOBU16PK.exe` 상태: 완전 종료

## 적용 파일

| 경로 | 적용 후 SHA-256 |
| --- | --- |
| `RES_JP/res_lang.bin` | `4AA373D263B563CBFFCF97FB1AC6E572607CEFB89652FF6700B34D17FB978A62` |
| `RES_JP_PK_PORT/res_lang_pk_port1.bin` | `BC4C87DD1D93BF944929E6341517828365C59203913E98302DF1A843571623D2` |

두 Steam 대상 파일은 각각 `build_005` 후보와 byte-identical이다.

## 복구 백업

백업 루트:

`F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\battle-merit-no-japanese-build005-20260726`

| 경로 | 적용 전 SHA-256 |
| --- | --- |
| `RES_JP/res_lang.bin` | `952B97FAE48F5D077E4663EFBE7B2975ADDBC0A521E63F9EDE373D7A77D55600` |
| `RES_JP_PK_PORT/res_lang_pk_port1.bin` | `E2B22DFD399E87DF109947F0F98FC58D1BF360B1B54299A6BB4D2051CE53EEA5` |

백업 파일은 적용 전 Steam 파일과 크기 및 SHA-256이 일치한다.

## 실게임 이미지 QA

- 검사 예정 해상도: `1920×1080`
- 적용 후 게임 실행: 수행하지 않음
- 해상도 선택 후 `NOBU16PK.exe` 완전 종료·재실행: 수행하지 않음
- 따라서 이 기록은 파일 적용과 정적 무결성만 증명하며, 실게임 렌더링 합격 판정은 아직 내리지 않는다.
