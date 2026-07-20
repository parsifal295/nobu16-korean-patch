# 3xxx 이벤트 런타임 인명 토큰 전수 재검토

이 작업물은 `MSG_PK/JP/msgev.bin`의 3xxx 구간 중, 런타임 인명 토큰 때문에 이전 수동 개행 작업에서 보류했던 26개 행을 **후속 후보로 만들기 전에** 전수 검토한 읽기 전용 보고서다. 문장을 축약하거나 삭제하지 않는다.

- 검토 대상: `3692, 3694, 3703, 3713, 3715, 3734, 3736, 3765, 3766, 3767, 3783, 3789, 3795, 3798, 3806, 3810, 3815, 3818, 3859, 3860, 3861, 3862, 3865, 3875, 3876, 3877` (26행)
- 각 행은 완전한 한국어 원문을 복원하고, 일본어 원문의 개행은 사용하지 않으며, 문맥 단위의 한국어 개행만 새로 배치한다.
- 직접 PC JP/EN/SC/TC 문맥과 현재 한국어 행의 제어 코드·색상 태그·런타임 토큰 순서를 비교한다. 태그 내부에는 개행을 넣지 않는다.
- 런타임 토큰은 접두사 의미를 추정하지 않는다. 숫자 ID가 가리키는 현재 엄격 한국어 인명 전체를 매 행에 치환해 보수적으로 폭을 예약한다.
- `Static Patch 007` 기준으로 원본 G1N 폭 `1440px` 이하, `ceil(raw × 30 / 48)` 실효 폭 `912px` 이하, 최대 4줄을 모든 표시 줄마다 검사한다.

보고서의 비교 기준은 batch07 private 후보이다. 이 보고서가 제안하는 26개 대상 텍스트가 그 기준과 어떤 차이가 있는지 계속 명시적으로 검증한다. 실제 메시지 바이너리 후보를 만들 때는 그 뒤에 결합된 다음 엄격 입력인 `pc_event_manual_compact_static007_3900_11008_restore_v1/candidate-final/MSG_PK/JP/msgev.bin`을 사용해야 하며, 이 작업물은 바이너리를 만들거나 Steam·Git·릴리스를 건드리지 않는다.

```powershell
python -B -X utf8 workstreams\pc_event_3xxx_runtime_review_v1\build_pc_event_3xxx_runtime_review_v1.py check
python -B -X utf8 workstreams\pc_event_3xxx_runtime_review_v1\build_pc_event_3xxx_runtime_review_v1.py write-report
python -B -X utf8 workstreams\pc_event_3xxx_runtime_review_v1\test_pc_event_3xxx_runtime_review_v1.py
```

생성 보고서: `public/pc_event_3xxx_runtime_review.v1.json`
