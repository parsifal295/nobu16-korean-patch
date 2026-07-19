# PC 이벤트 품질 Wave 31 — 고신뢰 정적 문장 보정

현재 Steam PC 이벤트 테이블에서 문맥상 명확한 정적 문장 네 쌍만 보정한다.
대상은 Base `MSG/JP/ev_strdata.bin`과 PK `MSG_PK/JP/msgev.bin`의 ID
`3898`, `4507`, `5528`, `6379`으로, 총 8개 셀이다.

- PC JP와 가능한 PC EN/SC/TC 테이블의 파일·셀 해시를 모두 고정한다.
- Switch 경로나 Switch 한국어는 읽지 않는다.
- ESC 색상 태그, 런타임 토큰, printf 토큰, 가장자리 공백은 원문과 동일하게
  유지한다. 줄바꿈은 각 교정안의 행 폭과 줄 수에 결속해 명시적으로 검증하며,
  ID `3898`은 문맥과 3줄 제한에 맞춘 의도적 재배치다.
- 선언된 수동 줄 수는 3줄 이하로 검증한다. PK `MSGEV`는 실제 활성 이벤트 글꼴의
  한 줄 912px 이하도 검증한다. Base는 `Text_message` 448×100 logical px 슬롯만
  확인됐고 renderer scale·자동 줄바꿈·최대 줄 수가 미해석이므로 PK의 912px 또는
  과거 1104px 임계값을 적용하지 않는다. Base 폭은 기록만 하며 실제 화면 QA가
  필요하다.
- 빌더는 `tmp/pc_event_quality_wave31_static_v1/` 아래 private 후보만 쓰며,
  Steam 적용·트랜잭션·Git·네트워크·릴리즈 기능은 없다.

이 후보는 전체 이벤트 전수 완료를 주장하지 않는다. 남은 의미·런타임·Base UI
레이아웃 보류는 별도 원장에서 계속 재판정한다.
