# 역사 이벤트 대사 초벌 배치

장수명·설치기 작업과 충돌하지 않도록 독립 작업한 `msgev` 대사 배치다. 설치된 게임 파일은 수정하지 않았으며, 배포 가능한 산출물에는 정식판 원문을 넣지 않았다.

## 후속 배치 v0.2: ID 3230~3308

기존 28개 다음에 이어지는 연속 79개를 별도 오버레이로 번역했다. 이 배치는 현재 제작 중인 Font-v6·설치 후보에 넣지 않고, 다음 글꼴 리비전과 다음 배포본의 입력으로만 유지한다.

| 사건 | ID | 수량 |
|---|---:|---:|
| 가네가사키 퇴각 | 3230~3244 | 15 |
| 히에이산 소각 | 3245~3260 | 16 |
| 미카타가하라 전투 | 3261~3276 | 16 |
| 프란치스코 하비에르의 일본 도래 | 3277~3286 | 10 |
| 기후와 천하포무 명명 | 3287~3308 | 22 |

SC·JP·EN의 동일 ID를 대조해 의미 단위와 사건 경계를 확인했다. ID 3229는 기존 v0.1의 마지막 항목이고, ID 3309부터는 지역 통일 엔딩용 내부 키·대사 묶음이 시작되므로 제외했다.

### v0.2 번역·검수 상태

- 79개 모두 자동 보조 초벌인 `translated`이며 사람 문체 검수와 실제 화면 검수가 필요하다.
- ESC 색상 코드의 종류·순서, 줄바꿈 수와 순서, 서식 토큰, 앞뒤 공백, 일반 제어문자, PUA 문자를 원문 SC와 전부 같게 유지했다.
- 작성 줄의 최대 길이는 ESC 코드를 제외하고 28코드포인트다. 24자를 넘는 항목은 19개이며 런타임 레이아웃 판정이 아니다.
- 고유명·시대어 검수 주의 항목 14개를 `review/review_index.v0.2.json`에 ID별로 기록했다.
- 특히 ID 3254의 종교 건축·관직 용어, ID 3261의 `상락`, ID 3281의 `프란치스코 하비에르`, ID 3282의 `야지로`, ID 3294~3297의 `기산`·`곡부`, ID 3301의 `천하포무`는 용어집 확정 때 다시 확인해야 한다.

### v0.2 글꼴 후속 조건

- 렌더 대상 고유 문자는 442개, 그중 완성형 한글은 423개다.
- 장수명 Font-v5에 없는 한글은 86개다. 정확한 목록과 해시 `C4253D1F677195C068C0837FE066EDF2471D706435EF8440CD1E6229D520A029`는 `validation.v0.2.json`에 있으며 번역 교정 때마다 자동 재계산된다.
- 현재 Font-v6·설치기에는 이 배치를 넣지 않는다. 후속 글꼴 리비전에서 `validation.v0.2.json`의 문자 집합 해시와 누락 목록을 입력으로 추가하고, 네 글꼴 표의 누락 0개를 다시 확인해야 한다.

### v0.2 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_event_continuation_3230_3308.v0.2.json` | `2EF36C22207A8B9A1CBFDB1212A8DBA2A8C49EDAF2D68BF95DDFB07404CDA637` |
| `evidence/alignment_evidence.v0.2.json` | `73A2B18423C1E7A6081F2500218A260EA04A0411F07729BF5344443F9ADAD033` |
| `review/review_index.v0.2.json` | `F90BDE5F561C489D2251A0EB6CF81FA5B4B04E4C8030682AFEC77A7B86073B7A` |
| `validation.v0.2.json` | `D235D88BADEAC9159F1E3684BAA0F3FED35E1F4E2C3FCEA499C1E2AD85685F31` |
| `verification.v0.2.json` | `B46D67212D2B00B5DEABF1A60627ABE1EF6AB70D16B9EEC94C284D638987739B` |

공개 파일에는 프로젝트가 작성한 한국어, 안정 ID, 원문별 UTF-16LE SHA-256, 제어 구조와 검증 메타데이터만 있다. 정식판 원문·완전한 원본 또는 결과 리소스는 없다. 통합 한자 영역 문자와 히라가나·가타카나 수는 모두 0개다.

### v0.2 격리 검증과 재생성

순정 SC 백업 복사본 두 개에 79개 작업을 적용해 결과 리소스·매니페스트·레시피의 A/B 바이트 동일성을 검사한다. 완전한 결과 리소스는 `tmp/dialogue_batch2_recipe_verification` 아래에만 생성하며 배포하지 않는다.

- 격리 결과 리소스 SHA-256: `853607541A04521F4233A20EF2FD555ADF8B2BA813141FF7E825E9D31C03F6D7`
- 격리 매니페스트 SHA-256: `88AF4BEA4BD4FED25AC9193A62EEB8196B1B3F7D591B56DD24D74E1F8ACEFB0D`
- 격리 레시피 SHA-256: `1A014C9330F334F1BEF2642E68F4E82D76B354C68E101E01983DF69FFA5AB633`

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Dialogue = 'workstreams\dialogue'
$A = 'tmp\dialogue_batch2_a'
$B = 'tmp\dialogue_batch2_b'
$Scratch = 'tmp\dialogue_batch2_recipe_verification'

foreach ($Out in @($A, $B, $Dialogue)) {
  & $Python -B "$Dialogue\build_event_dialogue_batch2.py" --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch2 build failed: $Out" }
}

& $Python -B "$Dialogue\verify_event_dialogue_batch2.py" `
  --build-a $A `
  --build-b $B `
  --final-root $Dialogue `
  --scratch-root $Scratch
if ($LASTEXITCODE -ne 0) { throw 'dialogue batch2 verification failed' }
```

최종 배포에서는 장수명(0~2399), 기존 대사 v0.1(3202~3229), 이번 v0.2(3230~3308)를 순정 SC 하나를 기준으로 ID 오름차순 병합하고 레시피를 새로 만들어야 한다. 어느 한 결과 `msgev.bin`을 다른 결과 위에 덮어쓰면 안 된다.

## 첫 배치 v0.1

## 범위

- 리소스: `MSG_PK/SC/msgev.bin`
- 언어 정렬: SC·JP·EN 각각 17,910개 문자열
- 선택 ID: 3202~3229, 연속 28개
- 3202~3214: 카이·사가미·스루가 삼국동맹
- 3215~3229: 이쓰쿠시마 전투
- 경계: 3201은 세 언어 모두 빈 항목이며 3230부터 다음 사건이 시작된다.

SC·JP·EN의 같은 숫자 ID를 대조했고, 선택한 28개는 모두 의미 단위가 일치함을 확인했다. 공개 근거 파일에는 원문 대신 각 언어 문자열의 UTF-16LE SHA-256과 제어 구조만 기록했다.

## 번역 상태

- 28개 모두 자동 보조 초벌인 `translated` 상태다.
- 28개 모두 사람 문체 검수와 실제 화면 검수가 필요하다.
- 고유명 읽기, 동맹명 표기, 참고 언어 간 의미 차이 등 구체적 주의 항목 9개는 `review/review_index.v0.1.json`에 ID별로 표시했다.
- ID 3202의 `강호`와 ID 3218의 `신역`은 원뜻을 보존한 초벌 표현이다. 이번 배치에서는 유지하지만 실제 화면 문체와 이용자 이해도를 기준으로 사람이 다시 검수해야 한다.
- ESC 색상 코드, 줄바꿈 순서, 앞뒤 공백, 서식 토큰, 일반 제어문자, PUA 문자를 28개 모두 보존했다.
- ESC 코드를 제외한 작성 줄의 최대 길이는 24 유니코드 코드포인트다. 이는 화면 폭을 위한 휴리스틱일 뿐이며 런타임 통과 판정은 아니다.

## 폰트 통합 차단

- 교정된 28개 대사의 고유 한글은 270개다.
- 현재 장수명용 `officer_names/font_v5`의 한글 554개와 대조하면 다음 40개가 없다.
- `갔깊깼꼭꼼꾀끼낳뇌눴닥닷딸땅떨뚫렀먹밤빛섬슨식쌓쓸암였잃잦젯졌죽쥔짝째척켜튿틈혀`
- 따라서 대사 오버레이만 장수명 결과에 병합해서는 안 된다. 위 글자를 corpus에 추가한 폰트 vNext를 만들고 네 글꼴 표에서 누락 0개를 확인하기 전에는 배포할 수 없다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_event_opening_3202_3229.v0.1.json` | `98C77E79256EE7B5A5CAAFAF95FDC1467F20A90F8E508E3EE975629B4EFD1C7F` |
| `evidence/alignment_evidence.v0.1.json` | `7AE5DF4851B4BF288C6E3EF42399A2F3F1FBD04F287E59931EA722C0AF89A37C` |
| `review/review_index.v0.1.json` | `2DE2BE324877ED3E6D298BE4E63AC0D4F15A09C588E5A2D79B8BA402B8C69BEC` |
| `validation.json` | `38C9294159DFDFD4CA6508EEA86B19BF175D9BB82DF7C3290AEDDBDD69823D44` |
| `verification.json` | `5E468BDF40E62E731834047ED6B088F75A40AF786D2ED732DE1D73FFC1F7B330` |

공개 JSON의 통합 한자 영역 문자와 히라가나·가타카나는 각각 0개다. 오버레이·정렬 근거·검수 인덱스는 중복/대소문자 충돌 키와 예상 밖 키를 거부하는 엄격 스키마로 검증한다. 완전한 원본·완전한 결과 리소스·실행 파일 바이트는 포함하지 않는다.

## 검증 결과

- 생성 A/B와 최종 공개 4개 산출물: 바이트 단위 동일
- 선택 원문 해시: 28개 × 3언어, 총 84개 일치
- SC 대체문 형식 불변조건: 28/28 통과
- 격리된 원본에서 파일 전용 빌드 A/B: 바이트 단위 동일
- 격리 빌드 작업 수: 28
- 격리 결과 리소스 SHA-256: `522C97F1C90C2052A31319DAEBBD9C58471FE33CBB07B3865F29E9439210F7F5`
- 격리 매니페스트 SHA-256: `61FC8C1A3A021794F5203BDEC612D1615FA62133DF7001A245FA37BB29E9C73D`
- 격리 레시피 SHA-256: `1F4F4FE3AFD96BCF503FE3CA4A7A373F979CF5F182FDA44D88FECD4170CA78F3`

완전한 격리 결과 리소스는 `tmp/dialogue_recipe_verification` 아래에만 있으며 배포 대상이 아니다.

## 통합 주의

이 오버레이는 장수명 오버레이와 같은 순정 SC `msgev` 해시를 기준으로 하며 ID 범위는 겹치지 않는다. 최종 배포본에서는 두 오버레이의 항목을 ID 오름차순으로 병합한 뒤 하나의 레시피를 다시 만들어야 한다. 여기서 검증한 단독 결과 리소스를 장수명 결과 위에 그대로 덮어쓰면 안 된다.

## 재생성

```powershell
$PythonCandidates = @(
  (Get-Command python -ErrorAction SilentlyContinue).Source
  (Get-Command py -ErrorAction SilentlyContinue).Source
  "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) }
$Python = $PythonCandidates | Select-Object -First 1
if (-not $Python) { throw 'Python 3 실행 파일을 찾지 못했습니다.' }

$Dialogue = 'workstreams\dialogue'
$A = 'tmp\dialogue_batch_a'
$B = 'tmp\dialogue_batch_b'
$Scratch = 'tmp\dialogue_recipe_verification'

foreach ($Out in @($A, $B, $Dialogue)) {
  & $Python -B "$Dialogue\build_event_dialogue_batch.py" --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue build failed: $Out" }
}

& $Python -B "$Dialogue\verify_event_dialogue_batch.py" `
  --build-a $A `
  --build-b $B `
  --final-root $Dialogue `
  --scratch-root $Scratch
if ($LASTEXITCODE -ne 0) { throw 'dialogue verification failed' }
```

기본 입력은 순정 SC 백업과 설치 디렉터리의 읽기 전용 JP·EN 리소스다. 세 입력 모두 고정된 크기와 SHA-256이 다르면 생성기가 중단된다.
