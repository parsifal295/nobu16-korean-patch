# 역사 이벤트 대사 batch21 v0.21

`msgev` ID 5629~5748의 실제 표시 대사 120개를 한국어 초벌 번역했다. 입력 배치는 기존 v0.1~v0.20, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일을 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 이마가와 협공 동맹 | 5629~5639 | 11 |
| 아마고 가문의 멸망 | 5640~5654 | 15 |
| 우키타 나오이에의 독립 | 5655~5676 | 22 |
| 호조 사부로가 우에스기 가게토라가 되다 | 5677~5697 | 21 |
| 가모 야스히데의 원복 | 5698~5700 | 3 |
| 아마고 재흥군의 거병 | 5701~5720 | 20 |
| 다케다의 오다와라 기습과 미마세토게 전투 | 5721~5748 | 28 |
| 합계 | 5629~5748 | 120 |

ID 5628은 v0.20의 마지막 대사다. 다음 번역 시작점은 ID 5749이며, 오토모 가문이 주변 세력을 끌어들여 모리 포위망을 만드는 새 사건이 시작된다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 의미를 가리키는 실제 표시 대사만 포함했다.

## 번역·검증 상태

- 120개 모두 자동 초벌 뒤 사람이 문체를 대조했으며 실제 게임 화면 검수는 아직 필요하다.
- 같은 ID의 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 360개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 스루가·도토미 두 나라, 오이가와강, 주고쿠 11개국, 우키타 요시이에, 엣소 동맹, 삼국제일, 비사문천, 신구토, 오키섬, 깃카와, 저돌적인 무사, 호조·다케다 전역 맥락, 미마세토게는 최종 용어집과 실제 화면 검수가 필요하다.
- 공개 overlay·근거·검수 인덱스·validation에서 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.20 공개 overlay·근거·검수 인덱스·validation 80개를 개별 SHA-256으로 고정했다.
- 그 80개 경로·해시의 결정론적 manifest SHA-256은 `F88FB58807EEC0A34C28151F9D15CC1CF015524876F0A57AB8EAA611DAF3B6D7`다.
- 빌드 전후 설치별 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교했으며 빌더는 게임 파일에 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치별 불변만 증명한다. v0.21은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_5629_5748.v0.21.json` | `EB34E1613FE97736B8C0B5A308956431E6BA0756FB4076E19AA5F52291743854` |
| `evidence/alignment_evidence.v0.21.json` | `0527A2BEFE4ECDA85347FF7707F0ADF60644068E902A323BD9ECA1BA95D64B21` |
| `review/review_index.v0.21.json` | `6AA964CB89C096CD3558A73D0D8CB173BDE6A164E63B35E0C678223B07F0E682` |
| `validation.v0.21.json` | `71091235581C26D22EBEEBB52F05DC9F2BC08D55CAD4253552A8092B75F93476` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch21.py"

foreach ($Out in @(
  "tmp\dialogue_batch21_a",
  "tmp\dialogue_batch21_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch21 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch21.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch21 tests failed" }
```

세 번의 출력에서 overlay·근거·검수 인덱스·validation은 각각 바이트 단위로 같아야 한다.
