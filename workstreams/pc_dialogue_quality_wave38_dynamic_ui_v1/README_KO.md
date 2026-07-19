# Wave 38 — PC 동적 UI 문장 보정

현재 Steam PC `msggame.bin`에서 런타임 토큰 주위의 고정 한국어 UI 셸 21개만
private 후보로 고친다. 대상은 Base 11개, PK 10개다.

- 지행 지급량 불만, 지침/방침 지속 불가, 성하 시설 건설 가능 UI의 어순과
  고정 조사를 바로잡는다.
- 동적 제목 UI의 완료·실패·중지·기간 만료·남은 일수 표현을 조사 없는 상태문으로
  정리한다.
- PC JP 및 가능한 PC EN/SC/TC만 근거로 사용한다. Switch 파일·Switch 한국어·과거
  한국어 산출물은 읽지 않는다.
- 모든 변경은 literal 경계만 바꾸며 opaque 런타임 토큰·marker·종료 코드를
  byte-identical로 보존한다. 각 목표는 수동 1줄이고 현재보다 정적 셸 폭이 넓어지지
  않아 동적 값 폭을 더 악화시키지 않는다.
- 출력은 `tmp/pc_dialogue_quality_wave38_dynamic_ui_v1/candidate/` 아래 private
  후보뿐이다. Steam 적용·Git stage/commit/push·GitHub·릴리즈 기능은 없다.

이 후보는 런타임 문장 전체가 전수 완료되었다는 선언이 아니다. 실제 값·문맥이
불명확한 다른 동적 대사군은 별도 보류한다.
