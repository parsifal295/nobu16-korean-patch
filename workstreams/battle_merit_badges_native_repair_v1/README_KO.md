# 전공 배지 native 좌표 복원 실행 결과

## 결과

`PASS`

[PLAN_KO.md](PLAN_KO.md)의 사전 검수를 통과한 뒤 전용 빌더를 실행했다.
현재 고해상도 아틀라스의 한글 전공 배지 세 개를 순정 고해상도 native
좌표에 복원하고, 복원된 배지를 각각 정확히 1/2 축소해 저해상도 고유
좌표에 배치했다.

고해상도 전체 아틀라스 반축소는 사용하지 않았다. Steam 설치본, 릴리스
파일, Git 커밋·푸시는 변경하지 않았다.

## 후보

산출물은 Git에서 제외되는 다음 디렉터리에만 있다.

`tmp/battle_merit_badges_native_repair_v1/build_002`

| 후보 | 크기 | SHA-256 |
| --- | ---: | --- |
| `candidate/RES_JP_PK_PORT/res_lang_pk_port1.bin` | `82,910,041` | `BC4C87DD1D93BF944929E6341517828365C59203913E98302DF1A843571623D2` |
| `candidate/RES_JP/res_lang.bin` | `154,752,890` | `3AA3EFCC2E265222DA52CC7AE95A34BF97194F7D5364790DAE1E8AE011E1A394` |

기계 판정 근거는 `build_002/build_report.json`, 시각 판정 근거는
`build_002/private/merit_badges_contact_sheet.png`다.

## 좌표 결과

알파 임계값 32에서 후보 bbox는 목표 native bbox와 일치했다.

| 배지 | 고해상도 후보 bbox | 저해상도 후보 bbox |
| --- | --- | --- |
| 전공 1위 | `[2960,400,3344,480]` | `[1082,254,1274,294]` |
| 전공 2위 | `[2982,500,3322,572]` | `[1297,256,1467,292]` |
| 전공 3위 | `[3686,644,4026,716]` | `[1501,256,1671,292]` |

Contact sheet의 패널 순서는 다음과 같다.

1. 빨강: 현재 고해상도를 native UV로 자른 파손 crop
2. 초록: native 좌표에 복원한 고해상도 배지
3. 노랑: 전체 반축소 적용 직전 저해상도 일본어 배지
4. 청록: 복원 고해상도 배지를 개별 1/2 축소한 저해상도 한글 배지

세 행 모두 초록·청록 패널에서 테두리와 글자가 잘리지 않는 것을 확인했다.
후보 전체 아틀라스 렌더에서도 배지끼리 또는 인접 작은 버튼 sprite와 겹치지
않는다.

## 구조·보존 검증

### 고해상도

- 변경 outer: `/17`만
- 허용 BC3 block: `6,550`
- 실제 변경 BC3 block: `6,327`
- 허용 영역 밖 block: 현재 고해상도 통합본과 byte-identical
- G1T payload 밖 바이트, resource id `58`, texture 수·형식·크기 유지
- 후보 LINK/LZ4/G1T 재파싱 및 round-trip: `PASS`

### 저해상도

- 변경 outer: `/12`만
- 배지 허용 BC3 block: `1,313`
- 저해상도 배치 기준 대비 실제 변경 block: `1,300`
- 배지 영역 밖 block: 전체 반축소 적용 직전 배치 기준과 byte-identical
- `/12` 밖 outer: 현재 저해상도 통합본과 byte-identical
- 복원된 고해상도 배지를 배지별로 정확히 1/2 축소
- 후보 LINK/LZ4/G1T 재파싱 및 round-trip: `PASS`

단위 테스트 7개와 독립 `verify` 명령이 모두 통과했다.

## 범위 제한

전체 반축소 적용 직전 저해상도 `/12`에는 버튼 안내 오른쪽의 일본어 잔여
픽셀이 이미 존재한다. 이번 후보는 전공 배지 범위만 다루므로 이 선행 문제를
변경하지 않았고 저해상도 화면 전체가 합격했다고 판정하지 않는다.

## 실게임 QA 기록

- 사용자 제보 해상도: `1920×1080`
- 이번 후보 실게임 적용: 하지 않음
- `NOBU16PK.exe` 완전 종료·재실행: 수행하지 않음
- Steam 설치본 변경: 없음

정식 실게임 판정은 릴리스 승인을 받은 뒤 Steam 적용 직전에만 수행한다.
적용 후 게임을 완전히 종료·재실행하고 선택 해상도와 재시작 여부를 함께
기록해야 한다.

## 재현 명령

```powershell
python workstreams\battle_merit_badges_native_repair_v1\build_battle_merit_badges_native_repair_v1.py verify `
  --output-root tmp\battle_merit_badges_native_repair_v1\build_002
```
