# manual_compact 전체 커버리지 원장

이 작업선은 historical `manual_compact_korean_layout` 1,553행의 처리 상태를 한곳에 모으는 read-only 감사 원장이다. 이벤트 바이너리를 만들거나 Steam 설치본·Git·릴리스·네트워크를 건드리지 않는다.

원장은 각 행을 다음 중 하나로 분류한다.

- `private_candidate_built_text_change`: private 후보 audit에 실제 텍스트 변경으로 기록됨
- `private_candidate_built_reviewed_preserve`: 검토 완료 후 후보에서는 의도적으로 유지됨
- `reviewed_layout_retained`: 문맥 검토 후 기존 수동 개행 유지
- `runtime_token_hold_context_reviewed`: 런타임 인명 토큰 예약 폭 근거가 없어 후보에서 제외됨
- `translation_quality_hold`: 레이아웃만으로 처리할 수 없어 별도 번역 의미 검토가 필요함
- `review_complete_private_candidate_pending`: review artifact는 완료됐지만 아직 후속 private 후보에 묶이지 않음
- `unreviewed_pending`: 완료 review/candidate/명시 hold가 아직 없음

별도로 `resolution_status`를 기록한다. 최종 완료 판정은 단순히 hold가 배정됐는지가 아니라 모든 1,553행이 반드시 `resolved_restore`, `resolved_preserve`, `resolved_semantic_reflow` 중 하나인지로 판단한다. 런타임 토큰 hold와 번역 품질 hold, review는 끝났지만 후보가 아직 없는 행은 모두 미완료다.

Static Patch 007 기준은 전각 48px/반각 24px 원본 G1N 폭을 `ceil(raw * 30 / 48)`로 환산해 912px 이하인지 보는 방식이며, raw 상한은 1,440px, 최대 줄 수는 4줄이다. 기존 960px raw gate는 사용하지 않는다.

실행:

```powershell
python -B -X utf8 workstreams\manual_compact_full_coverage_ledger_v1\build_manual_compact_full_coverage_ledger_v1.py build
python -B -X utf8 workstreams\manual_compact_full_coverage_ledger_v1\build_manual_compact_full_coverage_ledger_v1.py validate
python -B -X utf8 workstreams\manual_compact_full_coverage_ledger_v1\build_manual_compact_full_coverage_ledger_v1.py gate
python -B -X utf8 workstreams\manual_compact_full_coverage_ledger_v1\test_manual_compact_full_coverage_ledger_v1.py
```

`gate`은 완료 review artifact와 candidate script/audit의 일치뿐 아니라 1,553행 전체가 위 세 `resolved_*` 상태인지까지 요구한다. 현재 `pc_event_manual_compact_static007_3xxx_runtime_restore_v1` 후보가 남아 있던 43행을 보수적인 strict 한국어 동일 ID 인명 예약 폭으로 반영했다. `runtime_proven=false`는 실제 접두사 렌더링을 주장하지 않는다는 뜻일 뿐 hold가 아니며, 1,553행 모두 `resolved_*` 상태라 `gate`이 PASS한다. 이 결과는 private 후보 검증이며 Steam 설치·Git·릴리스 수행을 뜻하지 않는다.

공개 결과는 [manual_compact_full_coverage_ledger.v1.json](public/manual_compact_full_coverage_ledger.v1.json)에 생성된다.
