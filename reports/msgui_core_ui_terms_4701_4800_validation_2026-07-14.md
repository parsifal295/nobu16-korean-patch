# msgui ID 4701-4800 번역 배치 검증 기록

## 결과

- 대상 범위: ID 4701-4800, 정확히 100행
- canonical `empty`: ID 4701-4799, 99개
- 실제 문구: ID 4800, 1개
- 번역: `UI 1행 더미`
- 병합 및 stock 대조 검증: `valid=true`, 오류 0개, 경고 0개
- 설치 게임 파일 변경: 없음

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_4701_4800.v0.1.json`
- 배치 SHA-256: `5AD70E54C7BA88120EF0C3130147177D29582DB5F5D08E7375C6BEEF55DF8853`
- 임시 단독 병합 catalog SHA-256:
  `3A666AA1B04B4B4F8A57FC6EF70C796C93AB0169AF237BA3282A387E2CECE9AB`
- 단독 validation JSON SHA-256:
  `9078A794BA66E83DD563C8C7D38917074553B75089D386B208486D57C65ECEC4`

ID 4800은 EN `dummy`, JP `UI1行ナレダミー`, SC `UI 1行dummy`인 단일 행
내레이션용 더미 슬롯이다. printf, 줄바꿈, ESC, PUA, 기타 제어문자는 없다.

## 단독 빌드와 결정성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 빌드했다.

- 대상 `msgui.bin` 크기: 85,945바이트
- 대상 `msgui.bin` SHA-256:
  `D5DAEE9D9BDD1E0CB8B664A35D47126B3CE0F73627473600AD7B698F21C7E517`
- 대상 raw 크기: 85,584바이트
- 대상 raw SHA-256:
  `A18272EC9031C0FDCFCB26CF60A50F8326D78E4A352D104396549883D7B34E99`
- build manifest SHA-256:
  `09E218C72305275AC6758771790EDE82DD75BE269F34F36D07E622BE6FCD3181`
- glyph demand SHA-256:
  `60341C9A3744B42F0D186B08C03ABA41AD3DA37E29D456457DD295689768572E`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다.
검증 뒤 설치본 `MSG_PK/SC/msgui.bin`은 stock SHA-256
`C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82` 그대로다.
