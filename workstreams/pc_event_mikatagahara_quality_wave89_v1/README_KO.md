# W89 미카타가하라 전투 이벤트 전수 검수

이 작업스트림은 PK 이벤트 ID 3261~3276의 신겐 서상과 미카타가하라 전투 장면 16행을 W88 후보 뒤에서 전수 검수한다. direct PC JP를 기준으로 PC EN/SC/TC를 교차 확인했고, 16행 모두 원문 정보·문맥·레이아웃을 재작성한다.

변경 행:

3261~3276 전체 16행

문장 축약이나 정보 삭제는 하지 않는다. 3262는 반오다 연합의 최대 난적이자 가장 성가신 인물이라는 서술과 카이의 고참 영걸을 복원한다. 3270~3276은 무언의 도발, 가신의 간언 무시, 추격전, 미카타가하라의 패전, 충신의 대리 희생, 충복의 피신, 적에게 배우고 자신을 경계한 결말을 원문 의미 단위로 복원한다.

한국어 수동 개행은 의미 단위만 사용한다. 일본어 원문의 LF는 문안 판단에 사용하지 않는다. 태그·제어 코드·종료 구조를 보존하고, 태그 내부에 개행을 두지 않는다. 이 장면에는 런타임 인명 토큰 및 예약값이 없다.

PK 이벤트 통과 기준은 원본 G1N 전각 48px·반각 24px, 한 줄 raw 960px 이하, 최대 4줄이다. `ceil(raw_g1n_width_px * 30 / 48)`은 보고용 실효 폭이며 통과 기준이 아니다. 각 변경 행은 감사 JSON에 표시 문자열, raw 폭, 환산 실효 폭, 전각/반각 수, 줄 수, 960px 초과 여부를 기록한다.

입력은 `tmp/pc_event_honganji_quality_wave88_v1/candidate-final/MSG_PK/JP/msgev.bin` 하나로 엄격하게 고정한다. 후보 산출물은 `tmp/pc_event_mikatagahara_quality_wave89_v1/candidate-final/`에만 쓴다. Steam 적용·Git 커밋·푸시·릴리스는 이 작업 범위에 없다.

실행 순서:

    py -B workstreams\pc_event_mikatagahara_quality_wave89_v1\build_pc_event_mikatagahara_quality_wave89_v1.py profile
    py -B workstreams\pc_event_mikatagahara_quality_wave89_v1\build_pc_event_mikatagahara_quality_wave89_v1.py build
    py -B workstreams\pc_event_mikatagahara_quality_wave89_v1\build_pc_event_mikatagahara_quality_wave89_v1.py verify-private
    py -B -m unittest workstreams\pc_event_mikatagahara_quality_wave89_v1\test_pc_event_mikatagahara_quality_wave89_v1.py -v
