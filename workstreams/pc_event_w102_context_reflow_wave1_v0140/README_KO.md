# W102 이벤트 문맥 개행 보정 1차

현재 Steam W102 `MSG_PK/JP/msgev.bin`을 직접 기준으로, 아네가와 전투 14건과 전역 6건의 수동 줄바꿈을 문맥 단위로 재배치한다. 줄 길이를 맞추려고 문장을 축약하지 않으며, 색상 태그·동적 인명 토큰·표시 문구는 바꾸지 않는다.

각 줄은 현재 런타임 규칙인 30px, 유효 폭 912px, 최대 4줄로 측정한다. 이전 `manual_compact` 인벤토리는 현재 W102와 대량 drift가 있어 입력으로 재사용하지 않는다.

생성되는 `private/pc_event_w102_context_reflow_wave1.review.v1.json`에는 각 표시 줄의 문자열, 원본 G1N 폭, 30/48 환산 실효 폭, 전각/반각 문자 수, 줄 수, 912px 초과 여부와 동적 인명 토큰 예약 폭을 기록한다.

```powershell
python -X utf8 workstreams/pc_event_w102_context_reflow_wave1_v0140/build_pc_event_w102_context_reflow_wave1_v0140.py build
python -X utf8 workstreams/pc_event_w102_context_reflow_wave1_v0140/build_pc_event_w102_context_reflow_wave1_v0140.py verify
python -X utf8 -m unittest -v workstreams/pc_event_w102_context_reflow_wave1_v0140/test_pc_event_w102_context_reflow_wave1_v0140.py
```

후보는 `private/candidate`에만 생성한다. Steam 설치 파일은 수정하지 않는다.
