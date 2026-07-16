# Steam JP 공통 메시지 wave08 통합

v0.7.0의 공통 메시지 미해결 96건을 Steam PK 1.1.7 일본어 순정 테이블의
현행 좌표까지 다시 추적했다. 여기서 96은 **전체 현재 미번역 분모가 아니라**
기존 JP 후보에서 Steam 1.1.7로 자동 정렬되지 않은 legacy gap이다. 96건 모두
이전 일본어 원문 해시가 현행 순정 테이블에 그대로 존재하지 않아 자동 이식에서
보류됐다. SC 게임 바이너리는 읽거나 사용하지 않았다.

## 전체 좌표 차집합

추적된 완성 좌표 집합과 v0.7 JP-native overlay의 차이를 equal-hash block으로
Steam 1.1.7에 투영한 뒤 wave08과 성씨 복구를 반영하면, 5종 43,169건은 다음처럼
정확히 분해된다.

| 분류 | 건수 | 번역 진행률 반영 |
|---|---:|---|
| v0.8 실제 한국어 변경 | 40,581 | wave08 94건과 성씨 복구 980건 포함 |
| source-equal 구조 계약 | 1,796 | 반영하지 않음 |
| 형식 계약 불일치 | 730 | 별도 검토 대상 |
| 정렬 gap | 62 | 내부 더미 2건 포함 |

source-equal 1,796건은 `msgev` 83건과 `msgdata` 1,713건이다. 내부 키, `dummy`,
기호, 형식 토큰처럼 한국어 overlay 값과 현행 JP 값이 이미 같은 좌표이므로
후보 바이너리 바이트는 한 바이트도 바뀌지 않는다. 이 수는 **적용 번역 수나
게임 내 한국어 증가로 계상하지 않는다.** 7개 source-free shard는 좌표 커버리지
감사와 병렬 작업 충돌 방지용 구조 카탈로그일 뿐이다.

## 원인 분류

| 원인 | 건수 | 처리 |
|---|---:|---|
| 의미가 같은 일본어 표기·오탈자 교정 | 5 | 기존 한국어 재사용 검증 완료 |
| 더미 슬롯이 실제 제목·검색키·설명으로 전환 | 82 | 신규 번역 |
| 인명·효과·수치·용어의 의미 변경 | 6 | 현행 원문 기준 신규 번역 |
| 제작진 명단 갱신 | 1 | 기존 번역에 새 명단 반영 |
| 내부 테스트용 더미 식별자 변경 | 2 | 비의미 문자열로 보류 |

실제 번역 가능한 의미 문자열은 94건이고, 내부 더미 2건은 화면 번역 진척도와
분리한다. 정확한 구좌표·현행좌표·원인·병렬 배치는 `triage.v1.json`에 고정했다.

## 충돌 없는 병렬 배치

- `j01`: `msgev` 의미 동일 표기 교정 5건 — 구현 완료
- `j02`: `msgev` 변경 인명 2건 — 구현 완료
- `j03`: `msgev` 이벤트·시대 개요 제목 31건 — 구현 완료
- `j04`: `msgev` 제목 검색·정렬용 읽기 31건 — 구현 완료
- `j05`: `msgdata` 현행 효과·수치·용어 변경 6건 — 구현 완료
- `j06`: `msgdata` 신규 전승 이름 6건 — 구현 완료
- `j07`: `msgdata` 신규 전승 검색·정렬용 읽기 6건 — 구현 완료
- `j08`: `msgdata` 신규 전승 설명 6건 — 구현 완료
- `j09`: `msgstf` 제작진 명단 1건 — 구현 완료
- `hold`: `msgev` 내부 테스트 더미 2건

각 의미 배치는 `(resource, current_id)`가 겹치지 않으며 현행 일본어 UTF-16LE 해시
벡터를 별도로 고정했다. 따라서 서로 다른 에이전트가 동시에 번역해도 좌표
충돌 없이 마지막에 합칠 수 있다. `msgbre`와 `msgire`에는 이번 96건에 속하는
미해결 항목이 없다.

## j01 재현

`j01`은 오탈자 한 건과 표기 정규화 네 건이다. 의미·제어문자·줄바꿈·printf
토큰이 유지되므로 검증된 기존 한국어 5건을 현행 좌표에 다시 연결했다.

```powershell
python workstreams/steam_jp_common_messages_wave08/build_wave08_j01.py verify
python workstreams/steam_jp_common_messages_wave08/test_wave08_j01.py
```

개별 검증은 기존 v1의 39,507건을 모두 보존한 뒤 해당 배치만 추가한다. wave08
통합기는 9개 배치의 의미 문자열 94건을 함께 적용해 총 39,601건 후보를 만든다.
여기에 후속 성씨 복구 980건을 더한 v0.8 공용 메시지 후보의 실제 한국어 변경은
40,581건이다. `의미 미해결 0건`은 이 문서에서 분류한 wave08 의미 항목 94건에만
한정되며, 전체 게임의 미번역 문장·문맥 검수·화면 품질이 0건이라는 뜻은 아니다.
내부 테스트 더미 2건은 별도 보류 상태다.
완성 바이너리는 추적하지 않으며 `build` 출력도 저장소 `tmp` 아래에서만 허용한다.

구조 계약 1,796건은 다음 명령으로 별도 검증한다. 이 복구 계약 자체는 v0.7
기준 후보를 바꾸지 않으므로 해당 독립 검증의 실제 한국어 변경 수는 계속
39,507이며 두 후보 바이너리 해시도 v0.7과 동일해야 한다. 이는 wave08·성씨
복구까지 합친 v0.8의 40,581건과 다른, 구조 계약 전용 기준이다.

```powershell
python workstreams/steam_jp_common_messages_wave08/build_exact_contract_recovery.py verify
python workstreams/steam_jp_common_messages_wave08/build_exact_contract_recovery.py audit-source-union
python workstreams/steam_jp_common_messages_wave08/test_exact_contract_recovery.py
```

## 최종 통합 재현

통합 결과의 리소스별 신규 변경은 `msgev` 69건, `msgdata` 24건, `msgstf` 1건이다.
`msgbre`와 `msgire`는 기존 v1 후보 바이트를 그대로 유지한다. 구조 계약 1,796건은
후보 바이트를 바꾸지 않으므로 적용 번역 수에서 제외하며, 내부 더미 2건도 후보에
넣지 않는다. 5종 순정 Steam PK 1.1.7 JP 해시, 비대상 좌표, 메시지 테이블 구조,
래퍼 접두부 및 결정론적 A/B 결과를 다음 명령으로 한 번에 검증한다.

```powershell
python workstreams/steam_jp_common_messages_wave08/build_wave08_integration.py verify
python workstreams/steam_jp_common_messages_wave08/test_wave08_integration.py
```
