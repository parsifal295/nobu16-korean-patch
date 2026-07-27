# 번체중문 PK 휠 한국어 이식 Steam 적용 기록

## 결과

`PASS`

- 적용 시각: `2026-07-27T11:33:27.8561125+09:00`
- Steam 루트: `F:\SteamLibrary\steamapps\common\NOBU16`
- 후보 빌드: `tmp/tc_pk_wheel_from_jp_korean_v1_build002`
- 적용 중 `NOBU16PK.exe`: 완전 종료 상태

## 적용 범위

- TC 저해상도 PK 휠: 활성 레코드 `0..77` 전체
- TC 고해상도 PK 휠: 활성 레코드 `0..77` 전체
- 상세 휠: 12종 × 6상태 = 72레코드
- 중앙 휠 `광역`: 1종 × 6상태 = 6레코드
- 비문자 꼬리 레코드 `78..81`: 변경하지 않음

상세 레이블은 `공투`, `증원`, `대기`, `공성전`, `성역할`, `편집`,
`해제`, `보급거점`, `해제`, `방어거점`, `해제`, `편집`이다.

## 적용 파일

| 경로 | 적용 후 SHA-256 | 후보와 일치 |
| --- | --- | --- |
| `RES_TC_PK/res_lang_pk.bin` | `72C91E02272AF96561D1F574DF734AFA0F561BD3F78FBAC66A1872EEAAE1ABFB` | 예 |
| `RES_TC_PK_PORT/res_lang_pk_port2.bin` | `6D9380CB26E7F9903ABD3516DDFFB7A67BC9BFB4ED0AD5220B45C1C6A19ED01A` | 예 |

## 복구 백업

백업 루트:

`F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\tc-pk-wheel-korean-build002-20260727`

| 경로 | 적용 전 SHA-256 |
| --- | --- |
| `RES_TC_PK/res_lang_pk.bin` | `19C0149A7B4F9A5CA2672F61D4D8F3C3674FC343E33AEF3E4E1ED04BAFDC5B7B` |
| `RES_TC_PK_PORT/res_lang_pk_port2.bin` | `42C82BEB4524FB0E4FC9ED61AFF1EDB24422F196EC7424A831EB9E687C94EB77` |

백업 파일은 적용 전 Steam 파일과 크기 및 SHA-256이 일치한다.

## 정적·이미지 QA

- JP/TC 의미 레코드 순서 일치: `PASS`
- 활성 셀 비중첩: `PASS`
- 활성 레코드 78개 전체 교체: 저·고해상도 각각 `PASS`
- 선택 셀의 모든 BC3 블록이 JP 한국어 소스에서 유래: `PASS`
- 선택 셀 밖 BC3 블록 바이트 보존: `PASS`
- TC 레이아웃 표/좌표 바이트 보존: `PASS`
- 비대상 G1T/중첩 LINK/외부 LINK 엔트리 바이트 보존: `PASS`
- 후보 재파싱·독립 12그룹 재추출: 저·고해상도 각각 `PASS`
- 단위 테스트: `5/5 PASS`

고해상도 중앙 `광역` 6상태만 JP의 204×188 셀을 TC의 200×184 셀에
premultiplied-alpha Lanczos3 방식으로 축소했다. 나머지 150개 상태
(저해상도 78개, 고해상도 상세 72개)는 같은 셀 크기로 이식했다.

## 실게임 이미지 QA

- 검증 예정 해상도: `1920×1080`
- 적용 후 게임 실행: 아직 수행하지 않음
- 해상도 선택 후 `NOBU16PK.exe` 완전 종료·재실행: 아직 수행하지 않음

따라서 파일 적용과 정적 검수는 완료됐지만, 최종 실게임 화면 판정은
1920×1080을 선택하고 프로세스를 완전히 재시작한 뒤 수행해야 한다.
