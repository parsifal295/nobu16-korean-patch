# Steam JP `msgdata` P1 잔여 170건

이 workstream은 Steam 1.1.7의 활성 `MSG_PK/JP/msgdata.bin` v6 기준에서 남은
고신뢰 일본어 표기 170건을 대상으로 한다. 좌표 계약 해시는
`00EC1CA72A9015A88CA7D0673C1C79B42AAF38144ADE32FD1CE11C61ED4F94F5`다.

- 기존 공개 카탈로그와 활성 JP 원문 UTF-16LE 해시가 정확히 일치한 22건은 재사용한다.
- 기존 값이 한글 번역으로 적합하지 않은 항목은 재사용하지 않고 직접 번역한다.
- 나머지 148건은 직접 번역이며, 독음 필드는 일본어 독음을 한글로 적고 표시 필드는 한국어로 번역한다.
- 공개 JSON에는 원문 문자열이나 완전 게임 리소스를 넣지 않는다.
- 완성 바이너리 후보는 `KR_PATCH_WORK/tmp/steam_jp_msgdata_p1_residual_170_v1/` 아래에서만 생성된다.

검증은 활성 v6 해시 게이트, 항목별 원문 해시, 제어·서식 토큰, 비선택
UTF-16LE payload 보존, 파서 왕복, raw/packed 결정성, source-free 공용 산출물을 포함한다.
이 workstream은 게임 설치, GitHub, 릴리즈를 변경하지 않는다.
