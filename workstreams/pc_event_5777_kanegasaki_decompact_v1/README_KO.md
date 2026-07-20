# Event 5777 가네가사키 축약문 복원

이 private workstream은 PK MSG_PK/JP/msgev.bin의 event ID 5777 한 행만 고친다.
한국어 입력은 tmp/pc_event_toyotomi_kanpaku_quality_wave97_v1/candidate-final/ 하나뿐이며,
packed C5451B9BA726C8D06743E86D8F6ED320E052F6B6065A37D550DE4ACCE3CF4810 및 raw
E1810DEA757C5179A8C5631251656CDA83C36425C0699BE95650A6CCFBE4C11F가 아니면 즉시 실패한다.

직접 PC JP/EN/SC/TC는 읽기 전용 의미 근거다. JP의 姿勢, EN의 determined, SC의 姿态,
TC의 誓言을 근거로 요청안의 방침보다 의지가 더 정확하다고 판단했다. 모든 기존 ESC
wrapper와 UTF-16LE terminator 구조를 보존하고, 태그 내부에는 줄바꿈을 넣지 않는다.

대상은 네 의미 줄이며 raw G1N 48px/24px 기준 폭은 672, 840, 336, 912px이다.
960px 이하와 최대 네 줄이 통과 조건이며 ceil(raw * 30 / 48)는 보고 전용이다.

후보 산출물은 tmp/pc_event_5777_kanegasaki_decompact_v1/candidate-final/에만 작성된다.
Steam 설치본, Git, 네트워크, release payload에는 쓰지 않는다.

검증 명령:

    python -B workstreams/pc_event_5777_kanegasaki_decompact_v1/build_pc_event_5777_kanegasaki_decompact_v1.py authoring-check
    python -B workstreams/pc_event_5777_kanegasaki_decompact_v1/build_pc_event_5777_kanegasaki_decompact_v1.py build
    python -B -m unittest workstreams/pc_event_5777_kanegasaki_decompact_v1/test_pc_event_5777_kanegasaki_decompact_v1.py -v
    python -B workstreams/pc_event_5777_kanegasaki_decompact_v1/build_pc_event_5777_kanegasaki_decompact_v1.py verify-private
