# Event 5777 가네가사키 복원 — Static Patch 007 3줄

이 workstream은 PK MSG_PK/JP/msgev.bin의 event ID 5777 한 행만 새 private 후보로 만든다.
유일한 한국어 전임 입력은 tmp/pc_event_toyotomi_kanpaku_quality_wave97_v1/candidate-final/이며,
packed C5451B9BA726C8D06743E86D8F6ED320E052F6B6065A37D550DE4ACCE3CF4810,
raw E1810DEA757C5179A8C5631251656CDA83C36425C0699BE95650A6CCFBE4C11F가 아니면 실패한다.

PC JP/EN/SC/TC는 읽기 전용 의미 근거다. JP 姿勢, EN determined, SC 姿态, TC 誓言 때문에
방침보다 의지가 더 정확하다. 기존 ESC wrapper, 제어 순서, UTF-16LE terminator 구조는 보존하고
태그 내부에 줄바꿈을 넣지 않는다.

parent AGENTS.md의 Static Patch 007 기준이 authoritative다. raw G1N은 전각 48px, 반각 24px,
hard limit 1440px이고 effective width는 ceil(raw * 30 / 48), hard limit 912px이다.
이 후보의 세 줄은 raw/effective가 1056/660, 816/510, 912/570이며 최대 네 줄 이하이다.
audit에는 각 줄의 표시 문자열, raw/effective, 전각/반각 수, raw 1440 및 effective 912 초과 여부를 기록한다.

후보는 tmp/pc_event_5777_kanegasaki_static007_3line_v1/candidate-final/에만 작성한다.
Steam 설치본, Git, release, network에는 쓰지 않는다.

    python -B workstreams/pc_event_5777_kanegasaki_static007_3line_v1/build_pc_event_5777_kanegasaki_static007_3line_v1.py authoring-check
    python -B workstreams/pc_event_5777_kanegasaki_static007_3line_v1/build_pc_event_5777_kanegasaki_static007_3line_v1.py build
    python -B -m unittest workstreams/pc_event_5777_kanegasaki_static007_3line_v1/test_pc_event_5777_kanegasaki_static007_3line_v1.py -v
    python -B workstreams/pc_event_5777_kanegasaki_static007_3line_v1/build_pc_event_5777_kanegasaki_static007_3line_v1.py verify-private
