# PC 전용 이벤트 텍스트 잔재 감사 v1

범위는 `ev_strdata` 17,868좌표와 `msgev` 17,916좌표다. 순정 PC 일본어와 현재 Steam PC 한글, Steam PC EN/SC/TC만 직접 대조했다. `ev_strdata`는 PC EN 리소스가 없어 JP/SC/TC만 비교했다.

스위치 레포·스위치 한글·과거 한글 작업물·generic overlay는 열거나 사용하지 않았다. 알려진 오염 경로 `F:\Games\NOBU16\MSG_PK\SC`도 읽지 않았다.

결과는 다음과 같다.

- `ev_strdata`: 일본어/한자 잔재 0건, 신규 안전 후보 0건. ASCII 25건은 모든 PC 언어에서 동일한 내부 키였다.
- `msgev`: 일본어가 그대로 남은 4건(`3118`, `10837`, `10840`, `10905`)을 별도 private 후보로 만들었다. 각 후보는 현재 텍스트 SHA 고정, JP/EN/SC/TC 대조, 제어 토큰 순서 보존, 줄바꿈 수 보존을 통과한다.
- `msgev` 병음 제목 62건은 canonical PC 한글 제목과 1:1로 다시 대조했다. 각 canonical 제목을 PC JP/EN/SC/TC와 의미 검토한 결과 모두 타당했고, 앵커 자체의 수정 후보는 없다. 병음 62건의 실제 복원 후보는 이 감사에서 중복 생성하지 않는다.

공개 `validation.v1.json`에는 좌표·해시·포맷 증명만 두며 현재/제안 한글 원문은 넣지 않는다. private 후보는 `tmp/translation_quality_event_semantic_residuals_pc_only_v1/` 아래에만 생성된다.
