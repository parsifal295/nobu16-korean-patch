# 7,000번대 manual compact 복원 검토

이 작업물은 manual_compact_korean_layout 이력이 있는 PK 이벤트 7,000–7,999번 201행의 복원안과 근거만 담는다. 게임 바이너리 후보, Steam 적용, Git, 릴리스 작업은 만들거나 수행하지 않는다.

기준 입력은 batch06 strict 후보이며, 압축 전 한국어는 문장 복원 근거로만 사용한다. 직접 PC JP/EN/SC/TC를 각 행에 함께 기록하고, 사후 품질 수정으로 historical compact와 달라진 61행은 각각 원문 완결성을 판정했다. 완결된 현재문은 유지하고, 빠진 절·관계·용어가 확인된 행만 현재 용어를 살려 보완했다.

레이아웃은 Static Patch 007 기준이다. 표시 줄마다 원본 G1N 폭, ceil(raw * 30 / 48) 실효 폭, 전각/반각 문자 수, 런타임 토큰 예약 폭, 912px 초과 여부를 기록한다. 최대 네 줄이며, 일본어 원문의 개행은 한국어 줄바꿈 규칙으로 사용하지 않는다.

실행 명령:

    python workstreams/manual_compact_7000_review_v1/build_manual_compact_7000_review_v1.py build
    python workstreams/manual_compact_7000_review_v1/build_manual_compact_7000_review_v1.py verify

결과물은 public/manual_compact_7000_review.v1.json이다.
