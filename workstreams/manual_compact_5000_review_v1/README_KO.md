# 5,000번대 manual compact 복원 검토

이 작업물은 `manual_compact_korean_layout` 이력이 있는 이벤트 ID 5,000–5,999의 복원안과 근거만 담는다. 게임 바이너리 후보를 만들지 않으며 Steam·Git·릴리스 작업을 하지 않는다.

`build_manual_compact_5000_review_v1.py`는 다음을 읽는다.

- 현재 static007 3줄 5777 후속본 `tmp/pc_event_5777_kanegasaki_static007_3line_v1/candidate-final/MSG_PK/JP/msgev.bin`
- pristine PC 일본어 및 직접 PC EN/SC/TC 이벤트 텍스트
- 수동 3줄 압축 전 한국어 백업
- historical compact manifest와 런타임 인명 토큰 예약표

각 행은 현재 품질 수정이 historical compact 기록과 다르면 그 수정본을 보존한다. 그렇지 않은 행은 압축 전의 완전한 한국어 문장을 복구하고, 원본의 한국어 의미 단위 개행만 유지하며 들여쓰기만 제거한다.

레이아웃 판정은 static patch 007 기준이다. 원본 G1N 폭은 전각 48px/반각 24px로 측정하고 `ceil(raw * 30 / 48) <= 912` 및 최대 4줄을 사용한다. 이 조건의 원본 폭 상한은 1,440px이다.

생성 결과는 [manual_compact_5000_review.v1.json](public/manual_compact_5000_review.v1.json)이며, 각 행에는 JP/EN/SC/TC 근거·historical/current/legacy 한국어·복원안·제어 코드 검증·각 표시 줄의 폭/문자 수/토큰 예약을 기록한다.
