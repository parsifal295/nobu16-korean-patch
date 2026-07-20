# 최종 런타임 인명 토큰 43행 복원 후보

이 작업물은 Static Patch 007 기준에서 보류됐던 PK 이벤트 런타임 인명 토큰 43행을 마지막으로 결합한 private 후보다. 바이너리 입력은 오직 607행 결합 후보 `pc_event_manual_compact_static007_3900_11008_restore_v1/candidate-final/MSG_PK/JP/msgev.bin`이며, batch07은 각 artifact의 기준 행이 최신 입력과 같은지 확인하는 읽기 전용 근거로만 사용한다.

- 적용 근거: `manual_compact_runtime_3442_3611_review_v1` 17행과 `pc_event_3xxx_runtime_review_v1` 26행.
- 각 행은 batch07 artifact 기준 텍스트와 최신 strict 입력 텍스트가 완전히 같은지 먼저 확인한 뒤에만 적용한다.
- 제어 코드·색상 태그·런타임 토큰을 JP 기준으로 보존하고, 토큰 숫자 ID의 현재 엄격 한국어 인명 전체를 치환해 폭을 보수적으로 예약한다. 접두사 의미나 실제 런타임 동작은 추정하지 않으므로 `runtime_proven`은 모든 행에서 `false`로 유지한다.
- 모든 표시 줄은 원본 G1N 폭 `1440px` 이하, `ceil(raw × 30 / 48)` 실효 폭 `912px` 이하, 최대 4줄로 검사한다.
- 미해결 runtime hold는 남기지 않는다. 이는 폭 예약과 문맥 개행 검토를 끝냈다는 뜻이며, 런타임 접두사별 동작을 증명했다는 뜻은 아니다.
- 문장을 축약하거나 삭제하지 않는다. 3442·3443의 `또한`을 유지했고, 품질 보정 5건(3524 단수 주어, 3579 국중/지방 호족, 3713 사역문, 3767 주어 결속, 3789 신망·중재 의미)을 별도 ID로 기록한다.

후보는 `tmp/pc_event_manual_compact_static007_3xxx_runtime_restore_v1/candidate-final/` 아래에만 작성된다. Steam 적용, Git, 푸시, 릴리스, 네트워크 작업은 이 workstream 범위에 없다.

```powershell
python -B -X utf8 workstreams\pc_event_manual_compact_static007_3xxx_runtime_restore_v1\build_pc_event_manual_compact_static007_3xxx_runtime_restore_v1.py profile
python -B -X utf8 workstreams\pc_event_manual_compact_static007_3xxx_runtime_restore_v1\build_pc_event_manual_compact_static007_3xxx_runtime_restore_v1.py build
python -B -X utf8 workstreams\pc_event_manual_compact_static007_3xxx_runtime_restore_v1\build_pc_event_manual_compact_static007_3xxx_runtime_restore_v1.py verify-private
python -B -X utf8 workstreams\pc_event_manual_compact_static007_3xxx_runtime_restore_v1\test_pc_event_manual_compact_static007_3xxx_runtime_restore_v1.py
```
