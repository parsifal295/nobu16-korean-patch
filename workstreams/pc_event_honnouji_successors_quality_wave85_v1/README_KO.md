# W85 혼노지 후계자 이벤트 전수 검수

이 작업스트림은 PK 이벤트 ID 7793~7815의 23행을 W84 후보 뒤에서 전수 검수한다. 변경 행은 14개이며 나머지 9행은 직접 PC JP 원문과 PC EN/SC/TC 문맥을 대조한 뒤 유지한다.

변경 행:

7794, 7796, 7797, 7800, 7801, 7802, 7803, 7806, 7808, 7810, 7811, 7812, 7813, 7814

일본어 원문의 개행은 이식하지 않는다. 한국어 수동 개행은 문맥 단위로만 넣고, 문장 축약·정보 삭제·인명 변경은 하지 않는다. 색상 태그·제어 코드·종료 구조를 보존하며 태그 내부에 개행을 두지 않는다.

PK 이벤트 레이아웃은 원본 G1N 전각 48px·반각 24px, 한 줄 raw 960px 이하, 최대 4줄을 통과 조건으로 사용한다. ceil(raw_g1n_width_px * 30 / 48)은 보고용 실효 폭일 뿐 통과 기준이 아니다. 이 장면에는 런타임 인명 토큰과 예약값이 없다.

입력은 tmp/pc_event_koshu_campaign_quality_wave84_v1/candidate-final/MSG_PK/JP/msgev.bin 하나로 엄격하게 고정한다. 후보 산출물은 tmp/pc_event_honnouji_successors_quality_wave85_v1/candidate-final/에만 쓴다. Steam 적용·Git 커밋·푸시·릴리스는 이 작업 범위에 없다.

실행 순서:

    py -B workstreams\pc_event_honnouji_successors_quality_wave85_v1\build_pc_event_honnouji_successors_quality_wave85_v1.py profile
    py -B workstreams\pc_event_honnouji_successors_quality_wave85_v1\build_pc_event_honnouji_successors_quality_wave85_v1.py build
    py -B workstreams\pc_event_honnouji_successors_quality_wave85_v1\build_pc_event_honnouji_successors_quality_wave85_v1.py verify-private
    py -B -m unittest workstreams\pc_event_honnouji_successors_quality_wave85_v1\test_pc_event_honnouji_successors_quality_wave85_v1.py -v
