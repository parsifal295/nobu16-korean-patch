# Switch v1.1 PK `msgev` 이식 카탈로그

이 작업 흐름은 Switch 한글 패치의 이벤트 대사 중 PC PK의 `MSG_PK/SC/msgev.bin`에 구조적으로 안전하게 이식할 수 있는 7,025개만 추출한다. 결과물은 파일 전용 오버레이와 검증 기록이며, 실행 중 메모리·DLL·후킹·EXE·레지스트리를 변경하지 않는다.

## 출처와 저작자 표기

- 원본 한글 패치: [snake7594/nobunaga-shinsei-korean-patch](https://github.com/snake7594/nobunaga-shinsei-korean-patch)
- 릴리스: [v1.1](https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1)
- 저작자/계정: `snake7594`
- 제공 아카이브: `NobunagaShinsei_KoreanPatch_v1.1.zip`
- 아카이브 SHA-256: `931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6`

Switch 원문과 번역의 저작권·출처는 위 한글 패치 저작자에게 귀속된다. 이 작업 흐름은 PC PK 호환성을 검증한 좌표별 한글 대체문만 기록하며, ZIP과 게임 원문 리소스는 결과물에 넣지 않는다.

## 엄격한 선택 기준

각 ID는 다음을 모두 통과해야 한다.

- Switch v1.1의 값이 의미 있는 한글을 포함한다.
- PC 기본판 `MSG/JP/ev_strdata.bin`와 PC PK `MSG_PK/JP/msgev.bin`의 같은 ID 일본어 기준문이 정확히 일치한다.
- Switch 한글 값이 그 공통 일본어 기준문과 다르다.
- PC PK 순정 SC 백업과 printf, ESC, 제어문자, 줄바꿈 불변성이 정확히 일치한다.
- 기존 공개 PK `msgev` 카탈로그 5,469개 ID와 겹치지 않는다.
- CJK 통합 한자 또는 가나가 한 글자라도 있으면 제외한다. 이 필터로 20개가 빠져, 구조 통과 7,045개 중 7,025개만 남는다.

대괄호 동적 토큰은 이 선택 기준에는 포함하지 않는다. 토큰 순서나 값이 다른 8개는 제외하지 않고 검토 인덱스에 런타임 확인 대상으로 표시한다.

## 산출물

- `public/msgev_ko_switch_v11_ported_7025.v1.json`: PK SC용 source-free 한글 오버레이
- `evidence/switch_v11_pk_msgev_alignment.v1.json`: Switch·기본판 JP·PK JP·PK SC의 해시 및 구조 검증 기록
- `review/switch_v11_pk_msgev_review.v1.json`: PC PK 화면·문맥 검토 대상
- `validation.v1.json`: 3회 재현 빌드, 입력 고정값, 제외 사유, 재구성 해시

모든 공개 JSON은 일본어·중국어 원문을 보관하지 않는다. 완성된 게임 리소스도 내보내지 않는다.

## 재현

```powershell
python -B workstreams/switch_msgev_v11/build_switch_msgev_v11.py `
  --game-root F:\Games\NOBU16 `
  --repo-root F:\Games\NOBU16\KR_PATCH_WORK `
  --archive F:\Games\NOBU16\KR_PATCH_WORK\tmp\third_party_switch_v11\NobunagaShinsei_KoreanPatch_v1.1.zip `
  --out-root F:\Games\NOBU16\KR_PATCH_WORK\workstreams\switch_msgev_v11
```

```powershell
python -B -m unittest workstreams.switch_msgev_v11.tests.test_switch_msgev_v11 -v
```

재현 과정은 입력 ZIP과 순정 리소스를 읽기만 한다. PK 대상 전체 파일은 메모리에서만 재구성해 해시를 검증하고 디스크에 쓰지 않는다.
