# PC 이벤트 manual_compact Static Patch 007 복원 배치 05

이 배치는 `3287–3500` 연속 범위의 독립 장면 7개를 함께 감사한다. historical manual_compact 대상 중 런타임 이름 토큰 보류행을 제외한 33행만 변경한다.

- 한국어 입력은 batch04 기반 bulk successor인 `pc_event_manual_compact_4000_5000_restore_v1` private candidate 하나로 고정한다.
- `3297, 3307, 3311, 3316, 3327, 3336, 3346, 3358, 3360, 3386, 3394, 3396, 3398, 3402, 3411, 3421, 3429, 3438, 3439, 3445, 3452, 3468, 3469, 3475, 3482, 3483, 3484, 3485, 3486, 3489, 3495, 3496, 3498`만 exact multi-row diff 대상이다.
- `3442, 3443, 3444, 3448, 3455, 3456, 3459, 3499`는 런타임 이름 토큰의 행별 렌더링 경로·예약 폭 근거가 없으므로 자동 재배치하지 않는다.
- direct PC JP/EN/SC/TC는 문맥과 의미 검증 전용이며, 예전 manual_compact 오버레이도 legacy/current 비교 증거일 뿐 빌드 입력으로 쓰지 않는다.
- Static Patch 007 기준은 raw 1,440px 이하, `ceil(raw * 30 / 48)` 912px 이하, 최대 네 줄이다.
- 문장을 축약·삭제하지 않으며, 일본어 원문 개행을 한국어에 기계적으로 이식하지 않는다.
- 산출물은 `tmp/pc_event_manual_compact_static007_batch05_v1/candidate-final/`에만 만든다. Steam, Git, 릴리스, 네트워크를 변경하지 않는다.

```powershell
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch05_v1\build_pc_event_manual_compact_static007_batch05_v1.py authoring-check
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch05_v1\build_pc_event_manual_compact_static007_batch05_v1.py profile
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch05_v1\build_pc_event_manual_compact_static007_batch05_v1.py build
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch05_v1\build_pc_event_manual_compact_static007_batch05_v1.py verify-private
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch05_v1\test_pc_event_manual_compact_static007_batch05_v1.py
```
