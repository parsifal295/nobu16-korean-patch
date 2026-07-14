# 성·거점 이름 한글 초안 v0.1

이 작업 스트림은 SC 기반 파일 전용 패치에서 사용하는 주 성 이름 블록을 식별하고,
공식 EN 로마자 표기를 기계적으로 한글로 옮긴 **검수 전 초안**이다. 설치 게임 파일,
프로세스 메모리, 실행 파일, DLL, 레지스트리는 변경하지 않았다.

## 확인된 리소스와 ID

SC·EN·JP 모두 `MSG_PK/<언어>/msgdata.bin`의 같은 ID를 사용한다. 세 파일은 각각
29,210개 문자열이며, 압축 해제 후 변경 없는 parse/rebuild가 바이트 동일하다.

| 용도 | ID | 개수 | 확인 결과 |
|---|---:|---:|---|
| 사용자 표시용 주 성 이름 | `9151..9542` | 392 | SC·EN·JP 모두 비어 있지 않고 같은 ID로 정렬 |
| 주 성 이름 읽기 | `9543..9934` | 392 | SC·JP는 392개, EN은 빈 문자열 392개 |
| 공용 성 종류 접미사 | `9936..9940` | 5 | 주 이름과 별도로 합성되는 공유 슬롯 |
| 공용 접미사 읽기 | `9942..9946` | 5 | SC·JP에 존재, EN은 빈 문자열 |

공용 접미사는 이번 오버레이에서 바꾸지 않는다. 따라서 `ko`에는 성 종류를 붙이지
않았다. 실제 화면에서는 게임이 별도 공유 슬롯을 조합하며, 전략 지도의 세로 표시는
이미 수용한 SC 경로의 알려진 제한으로 남는다.

인접 범위도 조사했지만 성 이름으로 단정하지 않고 제외했다.

| 제외 범위 | 개수 | 판정 |
|---|---:|---|
| `9947..13974` | 4,028 | 지명과 특수 표지가 섞인 별도 블록이며 canonical 성 ID 연결이 확인되지 않음 |
| `13975..14046` | 72 | 별도 고대 지방 이름 블록 |
| `14047..14118` | 72 | 위 지방의 SC·JP 읽기 블록 |

따라서 이번 392개는 증거가 확정된 주 성 이름만 포함한다. 제외된 4,028개 중 실제
거점·군·지역 표지가 어떤 데이터 레코드와 연결되는지는 별도 역매핑이 필요하다.

고정한 입력은 다음과 같다.

| 언어 | wrapper SHA-256 | raw SHA-256 |
|---|---|---|
| SC | `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E` | `1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF` |
| EN | `15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1` | `DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32` |
| JP | `9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38` | `119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0` |

원문 자체를 공개 증거에 넣지 않고 각 언어의 392개 블록을 길이 구분 방식으로 해시한
결과는 `evidence/resource_id_map.v0.1.json`에 있다.

## 초안 정책과 범위

- 총 392개 모두 `automatic_draft_review_needed` 상태다.
- 단일 로마자 이름 370개는 `en_romaji`, 지역 구분어가 포함된 20개는
  `en_romaji_words` 방식이다.
- EN 표기만으로 음절 경계가 모호한 2개는 공식 JP 읽기의 음절말 `n`과 뒤따르는
  `y` 경계만 참조하는 `en_romaji_jp_n_y_boundary` 방식이다. ID 9201은
  `덴진야마`, ID 9478은 `다몬야마`로 생성된다.
- 한국어 값은 NFC 완성형 한글과 ASCII 공백만 사용한다.
- 서로 다른 한국어 값은 385개이며, 가장 긴 값은 공백 포함 8자다.
- 예시 검수점은 ID 9168 `오다와라`, ID 9204 `요시다 고리야마`,
  ID 9346 `야마토 고리야마`다.

이것은 번역 완료본이 아니다. EN 로마자에 기반한 자동 음역이므로 통용 한국어 지명,
역사 용례, 장음, 연탁, 지역 구분어 표기는 사람이 전수 검수해야 한다. 같은 표기가
여러 ID에 있는 경우도 의도적으로 합치지 않았다.

특히 EN 원문부터 지역 구분어가 붙어 있는 ID 9522 `에치고타카다`와 ID 9527
`이요마츠야마`의 공백 여부는 수동 검수 후보로 남긴다. 이번 자동 초안에서는 원문의
단어 경계를 그대로 보존하므로 두 값을 바꾸지 않았다.

## 공개·비공개 경계

공개 작업 트리에는 다음만 둔다.

- `public/castle_names_ko_9151_9542.v0.1.json`: ID·한글 초안·검수 상태만 포함
- `evidence/resource_id_map.v0.1.json`: 리소스 해시와 ID 범위 증거
- `manifest.json`, `validation.json`, `verification.json`
- 생성기, 독립 검증기, 이 문서

SC·EN·JP 원문 정렬표는 A/B 빌드의 `private/castle_names_alignment.v0.1.json`에만
생성하며 배포 금지다. 공개 오버레이에는 `SC`, `EN`, `JP`, `source`, `text`,
`translation` 원문 필드가 없고, 통합 한자 코드포인트도 없다. 완성 `msgdata.bin`과
적용 recipe는 아직 만들지 않았다.

## 재현과 검증

출력 폴더는 존재하지 않거나 비어 있어야 한다.

```powershell
$PythonCandidates = @(
  (Get-Command python -ErrorAction SilentlyContinue).Source
  (Get-Command py -ErrorAction SilentlyContinue).Source
  "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) }
$Python = $PythonCandidates | Select-Object -First 1
if (-not $Python) { throw 'Python 3 실행 파일을 찾지 못했습니다.' }

$Fontless = 'workstreams\castle_names'
$SC = 'backups\officer_name_probe_v0_1\msgdata.SC.stock.bin'
$EN = 'F:\Games\NOBU16\MSG_PK\EN\msgdata.bin'
$JP = 'F:\Games\NOBU16\MSG_PK\JP\msgdata.bin'
$A = 'tmp\castle_names_repro\build_a'
$B = 'tmp\castle_names_repro\build_b'
$Verify = 'tmp\castle_names_repro\verification.json'

foreach ($Out in @($A, $B)) {
  & $Python -B "$Fontless\generate_castle_name_draft.py" `
    --sc $SC --en $EN --jp $JP --output-root $Out
  if ($LASTEXITCODE -ne 0) { throw "castle-name build failed: $Out" }
}

& $Python -B "$Fontless\verify_castle_name_draft.py" `
  --build-a $A `
  --build-b $B `
  --release-root $Fontless `
  --output $Verify
```

검증 결과:

- A/B 산출물 5파일은 공개·비공개를 포함해 모두 바이트 동일
- 392개 ID 연속성·상태·한글 문자 규칙 통과
- SC·EN·JP 블록 해시와 고유 문자열 수 고정값 통과
- 공개 원문 필드 0, 공개 트리 8개 텍스트 전체의 통합 한자 0, 비공개 디렉터리 0,
  금지 확장자 0, 공개 파일·디렉터리 인벤토리 정확히 일치
- 설치 게임 파일 변경 없음

주요 SHA-256:

| 산출물 | SHA-256 |
|---|---|
| 공개 한글 초안 | `465F0CA873E310C20FAF9DF7D247B4A5025991774E1C4F8F320BC4125A93AE13` |
| 리소스·ID 증거 | `A6CF012C157020A102489CAD7FCC1FF62B29BCA6431B189177903A935BED5ED6` |
| manifest | `BC5A1B506BB536E4E07994995AAA358BA382B1D8C004E3AFE2A5F25815BE3E10` |
| validation | `B1B31A887036EAE2233385C28EC2AF74D7354E0336BEE69F06AE967F85C2C299` |
| verification | `9DDC6F5A3AF31EEDE36E18FF11899F39FE0E72A9BE8F6B305BCB73E5E8D2041F` |
| 비공개 원문 정렬표 | `6169A149F4F52D368751E0EE7B802B57704E76A1E747C0A98628596C43BA7E8F` |
