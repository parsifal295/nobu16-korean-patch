# Wave 35 — PC PK 정적 인물 대사 명료성 보정

현재 Steam PC `MSG_PK/JP/msggame.bin`의 정적 인물 대사 1건을 private 후보로만 더 명료하게 다듬는다.

- 대상: `17:938` — `제3진, 앞으로`를 문장으로 완결된 전진 명령으로 다듬고, 원문의 임박한 결판 의미를 더 분명하게 드러낸다.
- 근거: PC PK 일본어 원본과 PC EN/SC/TC만 사용한다. Switch 파일·번역문·레퍼런스는 읽지 않는다.
- 안전성: 단일 literal과 종료 코드만 있는 정적 레코드다. 제어 코드·literal marker·수동 개행 수를 보존하고, 실제 활성 글꼴 기준 2줄 `384px / 528px`로 검증한다.
- 산출물: `tmp/pc_dialogue_quality_wave35_static_command_v1/candidate/` 아래에만 생성한다.
- 제한: Steam 게임 파일 적용, Git stage/commit/push, GitHub 작업, 릴리즈 기능은 구현하지 않았다.

이 후보는 명백한 문법 파손이 아니라 품질·명료성 개선이다. 인물 대사 전수 감사를 완료했다는 뜻도 아니며, 다른 정적·런타임 대사는 별도 근거와 검증이 필요하다.
