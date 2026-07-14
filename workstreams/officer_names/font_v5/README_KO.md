# 장수명 + MSGUI 합집합 폰트 v5

이 작업물은 SC 파일 전용 한글 패치의 `msgui` 전체 번역과 장수명 2,207명의 글자를
동시에 지원하는 Noto OFL 기반 G1N append-tail 폰트다. 프로세스 메모리, DLL 주입,
실행 파일, 레지스트리를 사용하지 않는다. 설치된 게임 파일은 읽거나 덮어쓰지 않고,
SHA-256이 순정값으로 고정된 별도 `res_lang.bin` 백업을 명시적 읽기 전용 입력으로만
받는다.

## 글자 집합

- 기존 MSGUI 수요: 625자, 완성형 한글 524자
- 장수명 수요: 완성형 한글 125자
- 교집합: 완성형 한글 95자
- 장수명으로 추가된 한글: 30자
- 최종 합집합: 655자, 완성형 한글 554자, 비한글 101자
- UI 제어·명령·게임 PUA 아이콘 제외: 20자
- 전체 장수명은 완성형 한글과 ASCII 공백만 사용한다.

기존 MSGUI에 없던 신규 30자는 다음과 같다.

```text
겐깃뇨덴렌롯멘몬베벳삿샤센셋쇼슌엔잇젠즈짓케켄큐톤폰핫햐헤홋
```

고정 해시는 다음과 같다.

| 항목 | SHA-256 |
|---|---|
| 공개 장수명 오버레이 | `2625B8261527217EB3592D6B6BD03BE38A666998D32C944D29917FD4598B63BC` |
| 기존 MSGUI demand 파일 | `7DBF97C2AC889F2FB33856A1A8096A1DB091C4D25DB411E73E95E5D0FB7E0D16` |
| 장수명 codepoint 목록 | `491F1A933DA51A426927DEFE247481CD3BBA8D57EDAD5C4482387528E19E94B8` |
| 합집합 codepoint 목록 | `25B07F5B7943D33367C18ACC071747555363378AA19A979F11F94B7E882265A4` |

`generate_officer_name_glyph_demand.py`는 상용 원문이 없는 공개 장수명 오버레이만 읽는다.
ID가 정확히 `0..2206`인지, 이름이 NFC 완성형 한글과 ASCII 공백 하나만 사용하는지,
공개 원문 해시가 정규형인지 검사한 뒤 demand를 만든다.

```powershell
& $Python -B workstreams\officer_names\font_v5\generate_officer_name_glyph_demand.py --check
```

## 독립 재현 빌드

`--stock-archive`는 필수다. 현재 설치된 `RES_SC\res_lang.bin`을 묵시적으로 선택하는
기본값은 없다. 입력은 SHA-256
`916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`인 순정 SC
archive여야 한다. 아래 `<PRISTINE_SC_ARCHIVE>`에는 별도 순정 백업 경로를 지정한다.

```powershell
$Font = 'workstreams\officer_names\font_v5'
$A = 'tmp\officer_font_v5_build_a'
$B = 'tmp\officer_font_v5_build_b'

foreach ($Out in @($A, $B)) {
  & $Python -B "$Font\build_font_v5.py" `
    --demand-file "$Font\corpus\msgui_0000_5099\glyph_demand.json" `
    --demand-file "$Font\corpus\msgev_officer_names_0000_2399\glyph_demand.json" `
    --p3-regression-demand "$Font\regression\p3_226.glyph_demand.json" `
    --stock-archive '<PRISTINE_SC_ARCHIVE>' `
    --powershell 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' `
    --output-root $Out
  if ($LASTEXITCODE -ne 0) { throw "font-v5 build failed: $Out" }
}

& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' `
  -NoProfile -NonInteractive -ExecutionPolicy Bypass `
  -File "$Font\compare_font_v5_builds.ps1" -BuildA $A -BuildB $B

& $Python -B "$Font\verify_font_v5.py" `
  --build-a $A --build-b $B `
  --stock-archive '<PRISTINE_SC_ARCHIVE>' `
  --release-root $Font `
  --output "$Font\verification.json"
```

출력 폴더는 존재하지 않거나 비어 있어야 한다. 두 빌드의 완성 `res_lang`과 G1N은
무시된 `tmp/` 아래 `private/`에만 생성한다. Git 작업 경로에는 다음만 둔다.

- `public/recipe.json`
- `public/payload/*.pixels` — 고정 Noto OFL 글꼴에서 프로젝트가 생성한 4bpp 픽셀
- `public/metrics/glyphs.jsonl`
- `public/licenses/OFL-NotoSansKR.txt`, `OFL-NotoSerifKR.txt`
- 상용 원문 바이트가 없는 `manifest.json`, `validation.json`, `verification.json`
- 빌더, 래스터라이저, 비교기, demand와 P3 회귀 fixture

완성 `res_lang.bin`, `.g1n`, 추출한 상용 atlas/entry, 비공개 SC/JP/EN 카탈로그는
Git과 배포본에 넣지 않는다.

## 검증 결과

- 독립 빌드 A/B: 공개 6파일, 비공개 검증 15파일까지 모두 바이트 동일
- recipe SHA-256: `1AF9ECD80228502A6FB8C4A54F7122164890A50C7D435F420DE3A09F900A9CB3`
- metrics SHA-256: `FDB468457B00D47CD86B6DD95B0E4C8E38A0DAB1A724FE9DE297233D14C813B8`
- 비공개 후보 archive SHA-256: `51D8B781D731D0EDA583EC8AD194DBDA470B9B85884C0390BEE194B897DAC5DB`
- recipe의 비레시피 공개 inventory: 5파일, 경로·크기·SHA-256 모두 실제 파일과 동일
- 장수명 125개 한글과 ASCII 공백: entry 6/7의 table 0/1 모두 누락 0
- 기존 MSGUI 625자: 네 map 모두 누락 0
- P3 226개 한글 픽셀·metrics 회귀: 바이트 동일
- 순정 archive와 현재 설치 파일: 빌드 전후 변경 없음

런타임 QA의 최장 11자 대상은 다음 세 명이다.

- ID 239 `이타베오카 고세츠사이`
- ID 1681 `히토츠야나기 나오모리`
- ID 1885 `마츠다이라 다다아키라`

유명 장수 회귀 기준은 ID 106 `아츠지 사다유키`, ID 216 `이시다 미츠나리`,
ID 558 `오다 노부나가`다.

이 산출물은 오프라인 검증을 통과했지만 아직 전체 장수 목록·상세·편집 화면의 실제
렌더와 정상 종료를 검증하지 않았으므로 `runtime_verified=false`,
`release_eligible=false`를 유지한다.
