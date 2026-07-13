# Font-v4 전체 MSGUI 0000–5099 검증 — 2026-07-14

## 입력 계약

- 추적 가능한 최종 corpus: `workstreams/msgui_full/font_v4/corpus/msgui_0000_5099/glyph_demand.json`
- glyph demand SHA-256: `AA12D687C85D69D2D011FCBBFAD1B54D972223C01F8A3D47ABDD7FF6FA4EEB05`
- 번역 문자열 비공백 원문자: 645개
- G1N 제외 토큰: 19개
  - `U+001B`: UI 제어문자
  - `U+0051`, `U+005A`: `ESC C?` 명령 구성문자
  - PUA 게임 아이콘: 16개
- 실제 폰트 글리프: 626개(완성형 한글 523, 비한글 103)
- 제외 코드포인트 LF SHA-256: `B88CD9A68EBB6FC6221D01FFE7F89AA014FECA46EF1A2B13CCDCC8730D36F2FF`
- 제외 사유 행 compact JSON SHA-256: `6579C55EFF39DCA50D8152BCFE3686072DB1F07B185B50BAF363840F4C772E38`

P3 226자 회귀 입력은 임시·ignore 경로가 아니라
`workstreams/msgui_full/font_v4/regression/p3_226.glyph_demand.json`에 고정했다.
그 SHA-256은 `43C23F44A9794A1461BA84AEB919FDC661B97D285BA96AE3102F8A3842C5D8DA`다.
빌더는 과거 공개 픽셀과 메트릭의 고정 SHA를 생성 결과에서 직접 검증하므로 동결
`releases/`나 이전 `build/` 디렉터리에 의존하지 않는다.

## 빌드 결과

서로 다른 빈 출력 M/N에서 같은 명령을 독립 실행했다. 양쪽 파일 인벤토리는 23개로
같고 모든 파일이 바이트 단위로 일치했다.

- raster union: 562개(한글 523, 새 비한글 39)
- stock으로 완전히 충족된 비한글: 64개
- table append: entry 6/7 공통으로 table 0은 524개, table 1은 562개
- 후보 `res_lang.bin`: 181,011,663바이트,
  `02F0D4E09F8F1B13CD90D23A92F75302F49E34059CB659C4E59C1569EE2D3A8A`
- entry 6 G1N: 27,082,040바이트,
  `F2C76E79ADE0024F237DA1061E0DCFFCC18CB7D4DCCB54B7C72BFDD0F9CAC996`
- entry 7 G1N: 12,340,600바이트,
  `769C94F7C9E8E7EA5BF47644A56328EF2B8761DC43F9E6D26E46C127C716BC1B`
- 공개 recipe: 481,533바이트,
  `561477D6312FF02DDD18C09CBF4A2802E00BFA42015B325CFE6F04BDED04C109`
- 공개 metrics: 691,550바이트,
  `1AF2EF974E0E6E3670F2FF3AAC127C28717128C86573DF759EBCFF73C01A9074`
- 공개 entry 6 pixels: 1,251,072바이트,
  `53898FD6039F8CAD63BC85D50791DD3451D9EDCB69EB6F15EE08550EF50A91ED`
- 공개 entry 7 pixels: 556,032바이트,
  `CD34058F3C85554900314394AB3C1CFD92DF6CA7007068F44F2D12968DCA168D`
- build manifest: `9088261DEEA56AC396E7712C1C520B793ACAF4E57435EE62810732E748DEE820`
- validation: `C6E2D6BBA3E1214DD70DE0491C3ADEF0120583DBBAF81CFB08B60CDB9721F266`

P3 226자 픽셀·메트릭 회귀, raster-v2 seed, append tail, 공개 recipe 재생,
네 map의 626자 nonzero/nonblank, stock 소유 비한글 보존 검사가 모두 통과했다.

## 공개 경계와 설치본 불변

공개 font 트리는 OFL 라이선스 2개, 프로젝트가 생성한 Noto 픽셀 2개, metrics 1개,
구조 recipe 1개만 허용한다. 완성 G1N과 `res_lang.bin` 후보는 private 출력이며 배포하지
않는다. 게임 프로세스·메모리·DLL 주입·후킹·실행 파일·레지스트리는 사용하지 않았다.

검증 뒤 설치본 `RES_SC/res_lang.bin`은 stock SHA-256
`916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`를 유지했다.
