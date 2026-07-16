# Steam JP 시스템 버튼 아틀라스 감사

대상은 Steam 일본어판 1.1.7의 `RES_JP/res_lang.bin` 내부 `/5/0`의
`texture1`뿐입니다. 제목·로고·실행 파일·레지스트리·런타임 후킹은 범위에
포함하지 않습니다.

현재 상태는 **audit-only**입니다. Switch v2.1→v2.2의 한글 표기는 사설
시각 참조로만 해독했고, PC 버튼 배경을 훼손하지 않는 immutable PC donor와
pixel-bound 보존 증명이 아직 성립하지 않았습니다. 그러므로 이 작업 흐름은
게임 설치 파일을 쓰거나 배포 후보를 만들면 안 됩니다. `build` 명령도 이
감사 단계에서는 의도적으로 비활성화돼 있습니다.

확인된 대응은 8개입니다.

| Switch 한글 표기 | 상태 | PC JP 버튼 대응 |
| --- | --- | --- |
| 닫기 | cyan | 닫기 |
| 중지 | cyan | 중지 |
| 결정 | white | 결정 |
| 거부 | white | 거부 |
| 뒤로 | white | 뒤로 |
| 아니오 | white | 아니오 |
| 건너뛰기 | cyan | 건너뛰기 |
| 예 | cyan | 예 |

위 표는 셀 대응 감사 결과다. 이 중 `뒤로`의 PC 대상 셀은 인접 버튼 경계와
이전 `U+5426` 조각을 가로지르는 것으로 확인돼 **invalid/deferred**다. 즉, 핵심
8개 모두가 후보 대상이라는 뜻이 아니며 `뒤로`는 화면 단위 재매핑이 검증될
때까지 어떠한 텍스처 후보에서도 제외한다.

핵심 8개와 겹치지 않는 다음 배치 카탈로그도 1:1 셀 대조까지 마쳤습니다.
이 11개 역시 donor 검증 전에는 audit-only입니다.

| Switch 한글 표기 | 상태 | PC JP 버튼 대응 | 아이콘 보존 |
| --- | --- | --- | --- |
| 전부개방 | cyan | 전부개방 | 없음 |
| 희 | cyan | 희 | 없음 |
| 지휘 | white | 지휘 | 없음 |
| 재교섭 | blue | 재교섭 | 순환/재시작 |
| 승낙 | white | 승낙 | 체크 |
| 처단 | blue | 처단 | 없음 |
| 등용 | blue | 등용 | 없음 |
| 무장 | white | 무장 | 없음 |
| 다음 | white | 다음 | 앞으로 |
| 승인 | cyan | 승인 | 체크 |
| 부인 | cyan | 부인 | 금지 |

초기 `다음` 좌표 `[1188, 576, 1320, 640]`는 실제로 `무장`을 가리킨 잘못된
탐색 결과라 폐기했습니다. 올바른 `다음`은 `[792, 576, 924, 640]`으로 별도
대조됐습니다. `개시`만 백색 장식형 전투 시작 버튼이라 screen QA 전까지
보류합니다.

## 안전 계약

- 기준 파일은 SHA-256
  `0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0`의
  Steam JP 1.1.7 백업이다.
- Switch 컨테이너·압축 페이로드·텍스처는 PC 산출물에 복사하지 않는다.
- 향후 후보는 기준 PC 텍스처의 검증된 donor만 사용하고, 변경된 BC3 블록이
  명시적 라벨 밴드의 4×4 확장 범위를 벗어나지 않음을 증명해야 한다.
- 구조 검증과 private 컨택트시트 QA에서 배경/아이콘/테두리 훼손이 없어야
  한다. 하나라도 실패하면 audit-only로 되돌린다.
- 스크립트의 모든 산출물은 `KR_PATCH_WORK/tmp` 아래 private 경로에만
  생성된다. 게임 설치, Git, 릴리즈에는 쓰지 않는다.

2026-07-16 엄격 donor 감사 결과도 **NO / defer**였다. PC EN은 JP와 픽셀이
동일했고, SC/TC는 중국어 글리프가 같은 위치에 겹쳐 language-invariant
background donor가 되지 못했다. JP 동일스킨의 exact-pixel mode도 일본어 획을
남겼다. 특히 `뒤로`의 PC 대상 셀은 버튼 경계를 가로지르므로 향후 별도 화면
검증 없이는 후보에서 제외한다. 근거는 private
`tmp/system_button_donor_analysis/report.json`에만 둔다.

검증 명령(합성 데이터만 사용):

```powershell
python -B -m unittest KR_PATCH_WORK\workstreams\steam_jp_system_buttons_v1\test_steam_jp_system_buttons_v1.py -v
```
