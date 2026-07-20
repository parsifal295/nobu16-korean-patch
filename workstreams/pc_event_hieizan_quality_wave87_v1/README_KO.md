# W87 비예이산 소각 이벤트 전수 검수

이 작업스트림은 PK 이벤트 ID 3245~3260의 비예이산 소각 장면 16행을 W86 후보 뒤에서 전수 검수한다. 변경 행은 12개이고, 나머지 4행은 원문 정보·문맥·레이아웃을 확인한 뒤 유지한다.

변경 행:

3246, 3247, 3248, 3249, 3251, 3252, 3253, 3256, 3257, 3258, 3259, 3260

3257은 주군에게 귀신이라는 오명을 씌우게 하기보다 자신이 귀신이 되겠다는 결의를 복원한다. 한국어 수동 개행은 의미 단위만 사용하며, 문장 축약·정보 삭제·인명 변경을 하지 않는다. 태그·제어 코드·종료 구조를 보존하고 태그 내부에 개행을 두지 않는다.

PK 이벤트 통과 기준은 원본 G1N 전각 48px·반각 24px, 한 줄 raw 960px 이하, 최대 4줄이다. ceil(raw_g1n_width_px * 30 / 48)은 보고용 실효 폭이며 통과 기준이 아니다. 이 장면에는 런타임 인명 토큰 및 예약값이 없다.

입력은 tmp/pc_event_kanegasaki_quality_wave86_v1/candidate-final/MSG_PK/JP/msgev.bin 하나로 엄격하게 고정한다. 후보 산출물은 tmp/pc_event_hieizan_quality_wave87_v1/candidate-final/에만 쓴다. Steam 적용·Git 커밋·푸시·릴리스는 이 작업 범위에 없다.

실행 순서:

    py -B workstreams\pc_event_hieizan_quality_wave87_v1\build_pc_event_hieizan_quality_wave87_v1.py profile
    py -B workstreams\pc_event_hieizan_quality_wave87_v1\build_pc_event_hieizan_quality_wave87_v1.py build
    py -B workstreams\pc_event_hieizan_quality_wave87_v1\build_pc_event_hieizan_quality_wave87_v1.py verify-private
    py -B -m unittest workstreams\pc_event_hieizan_quality_wave87_v1\test_pc_event_hieizan_quality_wave87_v1.py -v
