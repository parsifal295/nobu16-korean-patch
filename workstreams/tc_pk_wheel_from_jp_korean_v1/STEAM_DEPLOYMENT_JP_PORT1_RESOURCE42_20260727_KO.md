# JP PORT1 보급거점 휠 한국어 교체 Steam 적용 기록

## 결과

`PASS`

- 적용 시각: `2026-07-27T12:17:05.8553605+09:00`
- Steam 루트: `F:\SteamLibrary\steamapps\common\NOBU16`
- 후보 빌드: `tmp/jp_port1_runtime_supply_base_closure_v1_build001`
- 적용 중 `NOBU16PK.exe`: 완전 종료 상태

## 적용 범위

실게임에서 `補給拠点`가 남아 있던 실제 런타임 경로만 교체했다.

- 파일: `RES_JP_PK_PORT/res_lang_pk_port1.bin`
- 저해상도: outer `36`, resource `42`, texture `0`, 레코드 `32..37`
- 고해상도: outer `37`, resource `42`, texture `0`, 레코드 `32..37`
- 상태 수: 저·고해상도 각각 6개
- 표시 문구: `補給拠点` → `보급거점`
- 비대상 outer 엔트리와 선택 셀 밖 BC3 블록: 바이트 보존

## 적용 파일과 복구 백업

| 구분 | 경로 | 크기 | SHA-256 |
| --- | --- | ---: | --- |
| 적용 후 | `RES_JP_PK_PORT/res_lang_pk_port1.bin` | 82,946,169 | `94F7602CCD41D750FFB3A5493ABE083E9F652B60374F82294FF3722EF9933AD1` |
| 적용 전 백업 | `KR_PATCH_BACKUP/file_only_transaction/jp-port1-resource42-supply-base-build001-20260727/RES_JP_PK_PORT/res_lang_pk_port1.bin` | 82,910,041 | `BC4C87DD1D93BF944929E6341517828365C59203913E98302DF1A843571623D2` |

적용 후 Steam 파일은 검수된 후보와 SHA-256이 정확히 일치한다.
백업 파일은 적용 전 Steam 파일의 SHA-256과 정확히 일치한다.

## 정적·이미지 QA

- 변경 outer 엔트리: `36`, `37`만 변경
- 저해상도 허용 BC3 블록 `3,744`개 중 `2,534`개 변경
- 고해상도 허용 BC3 블록 `13,800`개 중 `9,783`개 변경
- 선택 셀 밖 BC3 블록 바이트 보존: `PASS`
- 비대상 outer 엔트리 바이트 보존: `PASS`
- 후보 전체 JP 템플릿 재검색: 정확 일치 `2 → 0`
- 단위 테스트: `7/7 PASS`

## 실게임 이미지 QA

- 선택 해상도: `1920×1080`
- 적용 전 프로세스 종료: 완료
- 적용 후 `NOBU16PK.exe` 새 프로세스 시작: `2026-07-27T12:17:21.8092778+09:00`
- 완전 종료·재실행 여부: `예`
- 실제 군사 휠 재진입: 완료
- 오른쪽 휠 표시: `보급거점`
- 일본어 `補給拠点` 잔여 픽셀: 보이지 않음
- 최종 판정: `PASS`
