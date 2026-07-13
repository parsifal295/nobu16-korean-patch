# MSGUI 출시 차단 번역 QA (2026-07-14)

## 범위와 안전 조건

- 기준 리소스: 공식 `MSG_PK/SC/msgui.bin` 60,829바이트,
  SHA-256 `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 검증 입력: 설치본을 변경하지 않고 배포 설치기가 만든 stock backup을 별도 staging
  game-root에 복사해 사용했다.
- 개발용 다국어 원문 catalog와 번역 batch는 Git 제외 상태를 유지했다. 추적하는 공개
  산출물은 numeric ID, SC 원문 해시, 프로젝트 소유 한국어만 담은 overlay다.
- 메모리 패치, DLL 주입·후킹, 실행 파일·레지스트리 변경은 사용하지 않았다.

## 차단 항목 교정

- SC가 공백인 실제 UI 11개(ID 2498-2500, 3688, 3691, 3784, 3855,
  3942, 3988-3990)를 EN/JP 근거로 복원했다.
- 내부 키 6개(ID 3715, 3769-3772, 3781)를 사용자용 한국어 문구로 교체했다.
- `外様`/`外様家宰` 8개를 `도자마`/`도자마 가재`로 교정했다.
- 직책 해임·강등 8개에서 `영주직`, `성주직`, `대관직`을 명시했다.
- `와(과)의` 3개(ID 3919, 3954, 4023)를 `와(과) 맺은` 문형으로 교정했다.
- 외교·종속 문맥의 `当家`/`本家` 12개를 `본가`로 통일하고 데이터 분류 용어
  `自勢力=자세력`과 구분했다.
- 실제 시나리오 선택 화면에서 연도 뒤에 붙는 ID 591을 `%2d개월`에서 `%2d월`로
  교정해 `1543년9개월` 같은 날짜 오역을 제거했다.

SC에 printf/개행 정보가 없는 비대칭 슬롯은 검사를 끄지 않았다. `printf:JP` 및
`line_breaks:JP` override가 해당 불변식을 JP stock 문자열과 다시 비교하도록 validator를
확장했다. 적용 ID는 3715, 3769-3772, 3784, 3855, 3942이며 모두 `reviewed`다.

## 공백 no-op 정규화

기존 공개 overlay에는 비어 있지 않지만 `strip()` 결과가 빈 한국어 122개가 있었다.
그중 실제 문구를 복원한 11개를 제외한 111개는 다음 규칙으로 공개 대상에서 제외했다.

- 네 언어 source가 모두 whitespace-only이면 catalog `empty`, `ko=""`
- 어느 언어든 실제 문구가 있으면 catalog `untranslated`, `ko=""`
- `translated`/`reviewed`는 non-whitespace 한국어를 반드시 포함

따라서 공백 한 칸을 번역 완료로 위장하거나 stock 공백을 불필요하게 덮어쓰는 operation은
더 이상 생성되지 않는다.

## 결정성 검증 결과

- 공개 overlay: 3,951개, SHA-256
  `65994E73624B90951D64369D20097CE46ACAFCDBD0C2EFA18B40975126F3F8C6`
- 전체 catalog 상태: `empty=1038`, `untranslated=111`, `translated=3934`,
  `reviewed=17`; 오류·경고 0개
- 독립 메시지 빌드 2회: 세 파일(`msgui.bin`, manifest, glyph demand) byte-exact
- 메시지 operation: 3,836개, ID 배열 SHA-256
  `AFA976644E825BE78093E5FBCBA7D378F86AC461E3500A610B61E9CB3BD15B5C`
- 대상 `msgui.bin`: 114,766바이트, SHA-256
  `690C2C479EA987ED66128CECF11F177CB1C8CBEC864FA5FB94D9D6945838CB58`
- 대상 raw: 114,292바이트, SHA-256
  `CB32EED60CB079174801D2D0A15E7347D3A1330F151294B357C8CC22C47155EE`
- 공개 message recipe: 691,845바이트, SHA-256
  `F41172E247DF024D1170E289D9A0AE4B03387037FDE713B75DEB67623526654F`

## 폰트 수요 및 재빌드

교정 후 비공백 원문자 집합은 645개이며, UI 제어·ESC 명령 구성문자·PUA 아이콘
20개를 제외한 실제 G1N 수요는 625개(완성형 한글 524개)다. 이전 corpus와 비교하면
`볼(U+BCFC)`이 추가되고 사용자 문구에서 제거된 내부 키 전용 `F`, ESC 명령 전용 `R`은
실제 글리프 수요에서 빠졌다.

- glyph demand SHA-256:
  `7DBF97C2AC889F2FB33856A1A8096A1DB091C4D25DB411E73E95E5D0FB7E0D16`
- 독립 Font-v4 빌드 2회: 23개 파일 전부 byte-exact
- raster union 563개, table 0 append 525개, table 1 append 563개
- font recipe: 482,506바이트, SHA-256
  `6E88317D4A48EF38EDE015E8D61FE48625D8CC2B758B2B2760374021511BC7DE`
- 후보 archive SHA-256:
  `9E0FFEAFCF3C50060E1E223988FD01BA2470987FB97A3B6DA75E0B7E3591AE9A`
- 625개 요구 글리프의 entry 6/7, table 0/1 nonzero/nonblank 검사 및 P3 226자
  회귀 검사를 모두 통과했다.

완성 상용 `msgui.bin`, `res_lang.bin`, G1N은 무시된 `tmp/translation_qa` 아래에만 있으며
Git 추적 대상이 아니다.
