# 역사 이벤트 대사 batch14 v0.14

`msgev` ID 4691~4838의 실제 표시 대사 148개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.13, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 다케다 노부시게의 전사 | 4691~4719 | 29 |
| 아마카스 가게모치의 후위전 | 4720~4750 | 31 |
| 가게토라의 간토 간레이 취임 | 4751~4768 | 18 |
| 아네가코지 요시요리의 주나곤 자칭 | 4769~4799 | 31 |
| 노부나가가 네네에게 보낸 편지 | 4800~4810 | 11 |
| 구로다 간베에의 난세 출진 | 4811~4813 | 3 |
| 오다·마쓰다이라 기요스 동맹 | 4814~4838 | 25 |
| 합계 | 4691~4838 | 148 |

ID 4690은 v0.13의 마지막 대사다. ID 4838에서 기요스 동맹과 모토야스의 이에야스 개명 이후 관계가 정리되며, 다음 번역 시작점인 ID 4839부터는 오토모 요시시게가 연회와 주색에 빠지는 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 148개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 444개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 덴큐·사마노스케·오미노카미, 호로, 나무하치만 대보살, 오니미노, 쓰루가오카 하치만구, 우린케·다이나곤·주나곤, 노부나가의 ‘대머리 쥐’ 편지, 고데라 간베에 요시타카·구로다 조스이, 기요스 동맹 관련 독음·용어·역사적 맥락은 최종 용어집과 역사 검수가 필요하다.
- v0.12에서 사용한 미키 요시요리·아네가코지 요리쓰나·주나곤 표기를 이어받고, 기존 장수명·지명 표기의 아마카스 가게모치·가키자키 가게이에·바바 노부하루·교고쿠·기요스를 따랐다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.13 공개 overlay·근거·검토 인덱스·validation 52개를 개별 SHA-256으로 고정했다.
- 그 52개 경로·해시의 결정적 manifest SHA-256은 `20D02E9B409A1401707BC8457310C126F9A8424FB01223CF0ED6CFB78FB13BF0`이다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.14는 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4691_4838.v0.14.json` | `55C711208DE0A3039FC609EE38D4EF7DC0C63785DA950A4960051745CEF05EFA` |
| `evidence/alignment_evidence.v0.14.json` | `BA0DD48874CF1C1ABB76080412FE8C3B696F9B24EAAC6EA1525E3DD253D4E387` |
| `review/review_index.v0.14.json` | `5D3A42032FA982DC7B2418E3972F6283B26E97732E4498842C0F78DE22CC0F5E` |
| `validation.v0.14.json` | `A1AFBFAF519B28DF2CFA0398544E0E2CC01C02CFBE802F887A011E8A3167752B` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch14.py"

foreach ($Out in @(
  "tmp\dialogue_batch14_a",
  "tmp\dialogue_batch14_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch14 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch14.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch14 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
