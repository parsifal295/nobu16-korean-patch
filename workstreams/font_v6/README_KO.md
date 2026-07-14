# Font-v6: 통합 번역 글리프 코퍼스

Font-v6는 MSGUI v0.2, 장수명, 대사, 성 이름 번역을 함께 표시하기 위한 SC 가로쓰기용 파일 패치 글꼴 작업물이다. 기존 `officer_names/font_v5`는 변경하지 않으며, Font-v6는 별도 버전으로만 빌드한다.

이 작업물은 메모리 패치, DLL 주입, 실행 파일 수정, 레지스트리 변경을 사용하지 않는다. 빌더는 명시적으로 지정한 순정 `res_lang.bin` 백업을 읽고 `KR_PATCH_WORK/tmp` 아래에 검증용 후보를 만든다. 배포 트리에는 Noto OFL 글리프 픽셀, 구조 레시피, 검증 메타데이터와 라이선스만 둘 수 있다.

## 고정 입력

| 코퍼스 | 문자 / 한글 | SHA-256 |
|---|---:|---|
| `corpus/msgui_0000_5099/glyph_demand.json` | 625 / 524 | `7DBF97C2AC889F2FB33856A1A8096A1DB091C4D25DB411E73E95E5D0FB7E0D16` |
| `corpus/msgev_officer_names_0000_2399/glyph_demand.json` | 125 / 125 | `A4AB899D785F461AB9CE09174FB503373012D4EC8E8ACBE8CCBF08BDA8BE8754` |
| `corpus/msgev_dialogue_3202_3229/glyph_demand.json` | 285 / 270 | `71921713787E57A0BCEB429AB11764379CEABBDC78A82BC52EB2DCC10DC07570` |
| `corpus/msgdata_castle_names_9151_9542/glyph_demand.json` | 88 / 88 | `C7DDF8106E6634FEB50940B8646D27A64A91EADD67546B5F1C60D31A6B76B79B` |

빌더와 검증기는 위 네 경로와 해시를 정확히 요구한다. 다른 파일, 중복 입력, 빠진 입력은 거부한다.

고정 통합 결과는 다음과 같다.

- 렌더 대상 700자: 한글 599자 + 비한글 101자
- 렌더 대상 코드포인트 SHA-256: `64DBBA110E35B359709008E07D8A584B445B9EFD952EB54FB122D9A73EBBFFA9`
- 한글 코드포인트 SHA-256: `AC38EE12A7C19033281E76ABB4FB0E7CF9466EE6D0C7AFAB00F1FDAA57FEF4EF`
- 원문 비공백 합집합 720자, 글꼴 제외 토큰 20자
- 실제 Noto 래스터 합집합 638자, canonical `U+XXXX\n` SHA-256 `3E60696B9F4F9A1BFDCBD66171C4D064847F80C63D50E29A87FF0B4B9C335672`
- 표 0 추가 600자, canonical `U+XXXX\n` SHA-256 `26CFE8A693AA88688F55C15A971900372EE48AEBD51325CFFFE9CC57820E1905`
- 표 1 추가 638자, canonical `U+XXXX\n` SHA-256 `3E60696B9F4F9A1BFDCBD66171C4D064847F80C63D50E29A87FF0B4B9C335672`
- 비공개 전체 래스터 크기: entry 6은 1,469,952바이트, entry 7은 653,312바이트 (`2 tables × 638 glyphs`)
- 공개 compact 픽셀 크기: entry 6은 1,426,176바이트, entry 7은 633,856바이트 (`600 + 638 appends`)
- 공개 metrics 행 수: 2,476행 (`600 + 638 + 600 + 638`)
- Font-v5 대비 신규 한글 45자: `갓갔깊깼꼭꼼꾀끼낳뇌눴닛닥닷돗딸땅떨뚫렀먹밤빗빛섬슨식쌓쓸암였잃잦젯졌죽쥔짝째척켜튿틈푸혀`

## 독립 A/B 빌드

게임 설치 파일을 입력으로 직접 지정하지 말고, SHA-256이 `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`인 순정 SC 글꼴 백업을 사용한다.

```powershell
$Python = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
$Font = 'KR_PATCH_WORK\workstreams\font_v6'
$Stock = 'KR_PATCH_BACKUP\officer_names_v0_1\stock\font.stock.bak'
$A = 'KR_PATCH_WORK\tmp\font_v6_build_a'
$B = 'KR_PATCH_WORK\tmp\font_v6_build_b'

foreach ($Out in @($A, $B)) {
  & $Python -B "$Font\build_font_v6.py" `
    --stock-archive $Stock `
    --output-root $Out
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "$Font\compare_font_v6_builds.ps1" -BuildA $A -BuildB $B

& $Python -B "$Font\verify_font_v6.py" `
  --build-a $A `
  --build-b $B `
  --stock-archive $Stock `
  --release-root $Font `
  --output "$Font\verification.json"
```

검증기는 네 demand의 정확한 합집합, A/B 전체 바이트 동일성, 4개 글리프 맵의 700자 비공백 매핑, 순정 비한글과 공백 글리프 보존, P3 226자 회귀, 공개 페이로드 크기와 인벤토리를 모두 확인한다. 런타임 화면 검증 전에는 `release_eligible`이 항상 `false`다.

## 버전 격리

- `officer_names/font_v5`의 스크립트, 코퍼스, 공개 산출물은 수정하지 않는다.
- Font-v6 빌드의 전체 G1N/LINK 후보는 `tmp/.../private`에만 존재하며 배포 금지다.
- 설치 게임의 `RES_SC/res_lang.bin`은 빌더나 검증기가 수정하지 않는다.
