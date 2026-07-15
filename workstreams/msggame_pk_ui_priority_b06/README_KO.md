# msggame PK UI 우선 번역 B06

`MSG_PK/SC/msggame.bin`에서 아직 미번역된 전투 상태·명령, 군단 출진,
외교·평정, 조언 UI 300좌표를 한국어로 번역한 배치입니다.

- 블록별 수량: 6번 130개, 7번 37개, 9번 116개, 15번 17개
- B04 250좌표와 B05 300좌표를 해시로 고정하고 모두 선행 예약
- 등록된 모든 기존 오버레이와 좌표 중복 없음
- 서사 전용 17번 블록 제외
- 스위치 v1.3 한국어와 JP 원문 해시가 유일하게 연결되는 74좌표는 의미·용어 참고에 활용
- 선행·후행 공백, 개행, 포맷·제어코드·PUA 구조 보존
- 동일 원문은 동일 번역으로 고정
- 공식 SC·JP·EN·TC 최대 행 폭 기준 `+12` 이내
- 단독 재구성과 전체 선행 오버레이 합성 후보 모두 파싱 및 좌표 보존 검증

빌드와 테스트:

```powershell
python -X utf8 workstreams/msggame_pk_ui_priority_b06/build_msggame_pk_ui_priority_b06.py
python -X utf8 -m unittest workstreams/msggame_pk_ui_priority_b06/test_msggame_pk_ui_priority_b06.py -v
```

공개 산출물에는 번역문과 원문 해시만 포함되며 상용 원문은 포함하지 않습니다.
공유 진행률, 루트 README, 실제 게임 파일은 수정하지 않습니다.
