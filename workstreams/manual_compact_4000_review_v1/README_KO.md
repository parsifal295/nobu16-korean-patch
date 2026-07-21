# 4,000번대 이벤트 수동 압축 복원 검토

이 작업물은 `manual_compact_korean_layout` 이력이 있는 4,000–4,999번 이벤트 행을 대상으로 한 읽기 전용 검토표다. 후보 바이너리, Steam 게임 파일, Git, 릴리스, 네트워크 작업은 만들거나 수행하지 않는다.

현재 기준은 `pc_event_manual_compact_static007_batch03_v1`의 엄격한 후보이며, 과거 전체 한국어는 복원 재료로만 쓴다. 현재 문장이 과거 압축본과 달라진 경우에는 나중의 품질 수정 또는 런타임 인명 토큰 수정을 보존하고, 구판 문장으로 덮어쓰지 않는다.

각 행에는 다음을 기록한다.

- 현재·구판 전체·제안 한국어와 현재 품질 수정 보존 여부
- 압축본에서 복원되는 표면 요소와 보존 때문에 재도입하지 않는 구판 요소
- JP/EN/SC/TC 직접 PC 원문, 제어 코드·색상 태그·런타임 토큰 서명
- 표시 문자열별 원본 G1N 폭, `ceil(raw * 30 / 48)` 실효 폭, 전각/반각 수, 동적 인명 예약 폭, 912px 통과 여부 및 4줄 한도

줄바꿈은 한국어 의미 단위만 유지한다. 일본어 원문 개행을 규칙으로 복사하지 않으며, 문장 축약·삭제와 전역 개행 제거는 금지한다.

실행:

```powershell
python workstreams/manual_compact_4000_review_v1/build_manual_compact_4000_review_v1.py build
python workstreams/manual_compact_4000_review_v1/build_manual_compact_4000_review_v1.py verify
```

결과물은 `public/manual_compact_4000_review.v1.json`이다.
