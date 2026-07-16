# Steam JP 시나리오 날짜 월 단위 보정

시나리오 선택 화면의 `1559년 3개월` 표기를 `1559년 3월`로 고치는 단일 항목
후단 보정이다. 대상은 Steam PK 1.1.7 일본어 경로의
`MSG_PK/JP/msgui.bin` ID 1051뿐이다.

- 순정 JP 원문 `%d月` → 한국어 `%d월`
- 기간용 별도 원문 `%dカ月` → 기존 한국어 `%d개월` 유지
- v0.7 `msgui` 후보를 기준으로 한 항목만 수정하며, 다른 5,099개 문자열은 불변
- SC 바이너리·SC 런타임 경로는 읽거나 사용하지 않음

공개 overlay에는 상용 원문이 아닌 Steam JP 원문 해시, v0.7 기준 한국어 해시,
대상 한국어와 해시만 저장한다. 생성·검증은 순정 Steam 1.1.7 JP 백업과 v0.7
후보 핀이 모두 일치할 때만 통과한다.

```powershell
python workstreams/steam_jp_scenario_date_hotfix_v1/build_steam_jp_scenario_date_hotfix_v1.py verify
python workstreams/steam_jp_scenario_date_hotfix_v1/test_steam_jp_scenario_date_hotfix_v1.py
```

검증 항목은 다음과 같다.

- ID 1051 한 항목만 변경
- `1559년 3월` 날짜 단위 조합
- ID 1678의 기간 단위 `%d개월` 보존
- 메시지 테이블·LZ4 wrapper 왕복 및 비대상 문자열 불변
- 결정론적 A/B 재빌드와 공개 workstream 무바이너리 정책
