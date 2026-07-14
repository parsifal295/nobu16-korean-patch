# 역사 이벤트 대사 초벌 배치 v0.1

장수명·설치기 작업과 충돌하지 않도록 독립 작업한 `msgev` 대사 배치다. 설치된 게임 파일은 수정하지 않았으며, 배포 가능한 산출물에는 정식판 원문을 넣지 않았다.

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
