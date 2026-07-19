# Wave 36 — PC Base/PK 정적 인물 대사 교차 보정

현재 Steam PC의 정적 인물 대사 3좌표를 private 후보로만 보정한다.

- Base `9:3795`: 문장 사이에 빠진 공백 1개를 복원한다. PC Base 일본어 원문과 동일 원문의 현재 한국어 선례 `17:26`으로 확인한다.
- PK `17:714`, `17:821`: 발각당한 상황을 ‘눈치챘는가’로 뒤집은 의미 오류를 바로잡는다. 두 레코드는 원문·현문·대상문이 모두 같다.
- 근거는 PC Base/PK 일본어와 PC PK EN/SC/TC만 사용한다. Base EN은 설치본에 없고, 해당 Base SC/TC 좌표는 빈 리터럴임을 별도로 고정 검증한다. Switch 자료는 읽지 않는다.
- 모든 변경은 단일 static literal이다. 제어 코드, marker, 종료 코드, 수동 개행 수를 보존하고 활성 글꼴 기준 최대 2줄·912px 이하를 검증한다.
- 산출물은 `tmp/pc_dialogue_quality_wave36_static_crossfile_v1/candidate/` 아래에만 생성한다. Steam 적용, Git stage/commit/push, GitHub, 릴리즈 기능은 없다.

이 3좌표 후보는 인물 대사 전수 감사를 완료했다는 선언이 아니다. 런타임 토큰과 실게임 QA 보류 항목은 별도로 남는다.
