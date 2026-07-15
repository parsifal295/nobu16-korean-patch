# 역사 이벤트 대사 batch23 v0.23

`msgev` ID 5874~6019의 실제 표시 대사 146개를 한국어 초벌 번역했다. 기존 v0.1~v0.22 산출물, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않았다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 다테 가문의 덴분의 난 종결 | 5874~5884 | 11 |
| 아네가와 전투와 엔도 나오쓰네 | 5885~5914 | 30 |
| 이마야마 전투 | 5915~5937 | 23 |
| 혼간지의 노부나가 항쟁 | 5938~5955 | 18 |
| 제육천마왕의 서신 | 5956~5976 | 21 |
| 모리 모토나리의 마지막 꽃놀이 | 5977~5999 | 23 |
| 미쓰히데의 사카모토성 | 6000~6006 | 7 |
| 모리 모토나리의 죽음 | 6007~6019 | 13 |
| 합계 | 5874~6019 | 146 |

다음 번역 시작점은 ID 6020이다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 번호를 가리키는 실제 표시 대사만 포함했다.

## 번역·검증 상태

- 146개 모두 사람이 문맥을 대조해 작성한 초벌 번역이며, 실제 게임 화면 검수는 아직 필요하다.
- 각 ID의 SC·JP·EN 참조를 대조했다. 공개 근거에는 원문 대신 438개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이고 최댓값은 32다. 길이 예외는 없다.
- 인명·지명·관직·불교 용어 등 판단이 필요한 항목 20개는 검수 색인에 별도로 표시했다.
- 공개 overlay·근거·검수 색인·validation에서 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.22 공개 overlay·근거·검수 색인·validation 88개를 개별 SHA-256으로 고정했다.
- 그 88개 경로·해시의 결정론적 manifest SHA-256은 `C590C2510CA1DB1A875042858432BD8F67A3B20B3BD9BC6427D877D7723B7FFE`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256이 같음을 검증했다.
- v0.23은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_5874_6019.v0.23.json` | `EDCE4AF6BC0CA2C0E5F00C7C186D2744F5621D145DC98C805F61DE289374F5C8` |
| `evidence/alignment_evidence.v0.23.json` | `6FC7B0AB0720E83CC1D912D3D1DE2051FA5D4480AC861FC452BC8235D7A010DC` |
| `review/review_index.v0.23.json` | `52F3129C2B71504450A9C5C20E900F98B579AB2BF4F652BCFE87EBBAFA566564` |
| `validation.v0.23.json` | `E3FE49CB5DAD8F9D09302F6AE19F8FA39787A8B1D8C18F95E7D04F0F321D3035` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch23.py"

foreach ($Out in @(
  "tmp\dialogue_batch23_a",
  "tmp\dialogue_batch23_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch23 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch23.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch23 tests failed" }
```

세 번의 출력에서 overlay·근거·검수 색인·validation은 각각 바이트 단위로 같아야 한다.
