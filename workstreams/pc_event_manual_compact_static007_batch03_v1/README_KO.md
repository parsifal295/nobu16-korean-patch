# PC 이벤트 manual_compact Static Patch 007 복원 배치 03

이 배치는 미카타가하라 전투 전후 장면 `3261–3276`의 manual_compact 행 `3262`, `3274`만 변경한다.

- 한국어 입력은 batch02 private candidate 하나로 고정한다.
- 장면의 16행은 direct PC JP/EN/SC/TC 문맥·감사 범위이며, manual_compact가 아닌 행은 변경하지 않는다.
- Static Patch 007 기준은 raw 1,440px 이하, `ceil(raw * 30 / 48)` 912px 이하, 최대 네 줄이다.
- 문장을 축약·삭제하지 않으며, 일본어 원문 개행을 한국어에 기계적으로 이식하지 않는다.
- 예전 manual_compact 오버레이는 legacy/current 비교 증거일 뿐 빌드 입력으로 쓰지 않는다.
- 산출물은 `tmp/pc_event_manual_compact_static007_batch03_v1/candidate-final/`에만 만든다. Steam, Git, 릴리스, 네트워크를 변경하지 않는다.

```powershell
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch03_v1\build_pc_event_manual_compact_static007_batch03_v1.py authoring-check
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch03_v1\build_pc_event_manual_compact_static007_batch03_v1.py profile
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch03_v1\build_pc_event_manual_compact_static007_batch03_v1.py build
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch03_v1\build_pc_event_manual_compact_static007_batch03_v1.py verify-private
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch03_v1\test_pc_event_manual_compact_static007_batch03_v1.py
```
