# PC 전용 `strdata`·`msgdata` 잔존 언어 감사 v1

이 보고서는 순정 PC 일본어, 현재 Steam PC 한국어(일본어 경로에 적용된 패치), 그리고 Steam PC EN/SC/TC만 직접 대조한 결과다. Switch 한글, Switch 레포, 과거 한글 산출물, generic overlay는 읽거나 사용하지 않았다. 특히 `F:\Games\NOBU16\MSG_PK\SC`는 조사 범위에서 제외했다.

## 범위와 결과

- `strdata`: 32,311 좌표를 구조 파서로 전수 재구성 검증했다. 일본어 문자/한자 잔존은 45좌표다. 그중 6좌표는 block 4의 긴 크레딧이고, 나머지 39좌표는 UI·효과·입력 관련 잔존이다.
- `msgdata`: 29,218 좌표를 구조 파서로 전수 검증했다. 일본어 한자 잔존은 68좌표다. 추가로 303좌표는 현재 KO가 Steam PC SC와 동일한 라틴 읽기값이면서 EN과 달라, SC 병음/라틴 읽기키 잔존으로 분류했다. 이 303좌표에는 `%s`를 보존한 템플릿 4개가 포함된다. 별도로 다국어 공통 `dummy` 값 17좌표는 용도 불명 예약값으로 HOLD했다.
- U+FFFD 대체문자, 잘린 UTF-16, 파서 불일치는 없었다.
- 같은 리소스 안에서 JP 원문이 완전히 일치하고, PC EN/SC/TC 의미도 독립 대조한 현재 KO 한글 canonical anchor 25건을 확인했다. `strdata` 7건, `msgdata` 18건이며, 줄바꿈·런타임/printf 토큰·ESC 태그·앞뒤 공백·전각 퍼센트 수가 모두 보존된다.

## 처리 원칙

정확 앵커 25건은 private generic-builder 입력으로 구체화했다. private 후보는 아래 경로에만 있으며, `resource`, `block`/`id`, `current_ko`, `proposed_ko`, 각 UTF-16LE SHA-256, 빈 `allowed_format_delta`, anchor 해시, PC EN/SC/TC 대조값을 포함한다.

`tmp/pc_translation_residuals_pc_only_v1/pc_exact_anchor_candidates.v1.jsonl`

generic builder는 해당 파일을 `msgdata`와 `strdata` proposal path에 각각 추가하면 바로 읽을 수 있다. 후보 25건의 좌표 집합 해시는 `A7ABBB7BE7AB5D1C01BDFAD3ACE06041EBAFE21217425B2B41B91EA017B7C412`이다.

정확 앵커가 없는 일본어 script/CJK 88건은 아직 자동 적용하지 않는다. 고유명·크레딧·IME/런타임 항목 및 용어 선택이 갈리는 항목은 HOLD다. 303개의 가나 원문 읽기키와 17개의 공통 `dummy` 예약값도 같은 원칙으로 HOLD다.

좌표 집합·해시·검사 규칙은 `validation.v1.json`에 source-free로 기록했다. private 후보 생성/검증기는 `build_pc_exact_anchor_candidates_v1.py`이며, `--write` 뒤 인자 없이 한 번 더 실행하면 입력 재검증만 한다.
