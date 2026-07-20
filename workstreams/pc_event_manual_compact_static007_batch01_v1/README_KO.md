# PC 이벤트 manual_compact Static Patch 007 복원 배치 01

이 작업선은 `3210`, `3231`, `3232`, `3233`, `3234`, `3239` 여섯 행만 변경한다.

- 한국어 입력은 `pc_event_5777_kanegasaki_static007_3line_v1`의 private candidate 하나로 고정한다.
- `3210–3214`, `3230–3244`는 문맥·direct PC JP/EN/SC/TC 대조 범위다. manual_compact가 아닌 행은 감사 기록만 남기고 변경하지 않는다.
- Static Patch 007 기준은 전각 48px, 반각 24px, raw 1,440px 이하, `ceil(raw * 30 / 48)` 912px 이하, 최대 네 줄이다.
- 일본어 원문 개행은 근거로 이식하지 않는다. 모든 대상은 축약하거나 문장을 삭제하지 않고 한국어 문맥 단위로 다시 배치한다.
- 이전 `manual_compact_korean_layout` 오버레이는 historical/current 비교 증거일 뿐 한국어 빌드 입력으로 쓰지 않는다.
- 산출물은 `tmp/pc_event_manual_compact_static007_batch01_v1/candidate-final/` 아래에만 생성한다. Steam 설치본, Git, 릴리스, 네트워크는 변경하지 않는다.

실행 순서:

```powershell
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch01_v1\build_pc_event_manual_compact_static007_batch01_v1.py authoring-check
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch01_v1\build_pc_event_manual_compact_static007_batch01_v1.py profile
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch01_v1\build_pc_event_manual_compact_static007_batch01_v1.py build
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch01_v1\build_pc_event_manual_compact_static007_batch01_v1.py verify-private
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch01_v1\test_pc_event_manual_compact_static007_batch01_v1.py
```
