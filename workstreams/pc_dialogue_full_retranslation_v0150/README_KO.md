# v0.15.0 인물 대사 전수 재번역

이 workstream은 현재 Steam PC 한글 경로의 `msggame` 두 리소스를 처음부터
의미 검토하고 새 한국어 문장으로 재번역하기 위한 **전체 작업 원장**이다.
기존의 구조·잔존 문자 감사는 번역 의미가 완료되었다는 뜻이 아니므로, 과거
검수 상태와 무관하게 모든 현재 표시 리터럴을 `unreviewed`로 시작한다.

## 범위와 기준

| 리소스 | 순정 원문 | 현재 한글 대상 | 검토 단위 |
| --- | --- | --- | --- |
| `MSG/JP/msggame.bin` | Steam PC JP | Steam PC JP-route KO | 현재 리터럴 |
| `MSG_PK/JP/msggame.bin` | Steam PC JP | Steam PC JP-route KO | 현재 리터럴 |

- 판단 자료는 순정 PC 일본어 원문, 현재 Steam PC 한글, 같은 PC의 EN/SC/TC
  문맥뿐이다. Switch 한글 및 과거 한글 번역 파일은 읽지 않는다.
- 순정 JP와 현재 KO 사이에서 과거 수정이 여러 원문 리터럴을 한 KO 리터럴로
  합친 레코드가 있다. 이 경우에도 원문 레코드 전체를 한 검토 단위에 함께 넣어
  의미를 빠뜨리지 않는다.
- `52,803`은 printable 문자가 있는 기계적 후보 수다. 여기에는 인물 대사뿐 아니라
  동적 문법 조각·시스템 알림·내부 키 가능 항목이 섞여 있으므로, 전수조사에서
  `retranslated`, `runtime_fragment_pending`, `confirmed_non_display` 중 하나로
  판정한다. `confirmed_non_display`는 근거 없이 번역하지 않는다.
- 빈 현재 슬롯은 번역 대상이 아니지만, 원문 레코드와 함께 전수 원장에 기록한다.
- Steam 설치본과 게임 리소스는 절대 쓰지 않는다. 후보 빌드도 `tmp/` 아래에서만
  만든다. Steam 적용은 별도 릴리즈 승인 직전에만 가능하다.

## 생성물

다음 명령은 모든 원문·현재 한글·PC 문맥을 `tmp/`의 **private** 큐에만 쓴다.
저장소에는 정식판 문장이나 완전한 리소스를 추가하지 않는다.

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_dialogue_full_retranslation_v0150\build_pc_dialogue_full_retranslation_v0150.py --write --validate
```

출력 경로는 `tmp/pc_dialogue_full_retranslation_v0150/`이다.

- `review_queue.private.v1.jsonl`: 레코드별 JP·현재 KO·PC EN/SC/TC 문맥이 있는
  실제 번역 작업 큐다.
- `target_ledger.source_free.v1.jsonl`: 원문·번역 본문 없이 좌표·해시·배치·상태만
  기록한 전수 원장이다.
- `review_batches.source_free.v1.json`: 각 배치의 대상 개수와 좌표 범위다.
- `summary.source_free.v1.json`: 입력 리소스 해시, 개수, 전수성 결과다.

모든 표시 리터럴을 검토한 뒤에는 private `review_decisions.private.v1.jsonl`에
좌표별 새 번역과 검토 상태를 넣고 다음처럼 검증한다.

```powershell
& $py -B workstreams\pc_dialogue_full_retranslation_v0150\build_pc_dialogue_full_retranslation_v0150.py --validate-decisions
& $py -B workstreams\pc_dialogue_full_retranslation_v0150\build_pc_dialogue_full_retranslation_v0150.py --build-candidate
```

진행 중인 배치 조각은 완결 전수 파일과 분리해 `--validate-partial-decisions`로
검증한다. 이 검증은 제출된 좌표의 중복·원문/현재 대상 해시·토큰·공백·가나/한자
잔류를 모두 검사하지만, 아직 제출되지 않은 좌표가 있다는 이유로 실패하지 않는다.
전체 후보 빌드는 종전과 같이 모든 표시 좌표가 승인될 때까지 차단된다.

후보 빌드는 새 번역이 모든 현재 표시 리터럴을 정확히 한 번씩 덮는지, 원문·현재
한글 기준 해시가 같은지, 런타임 토큰·ESC 태그·printf 토큰·외곽 공백이 보존됐는지
확인한 뒤 격리된 `candidate/`에만 쓴다. 줄바꿈 수를 바꾼 항목은 decision에서
`runtime_verified` 레이아웃 검토를 명시해야 한다. 이는 `msggame`의 보수적
검증 규칙이며, PK `msgev` 이벤트 대사에 관한 912px 규칙을 이 리소스에
전용하지 않는다.

번역 판단은 `STYLE_GUIDE_KO.md`와 `glossary.v1.json`을 따른다. 용어집에 없는
시대어·관직·인명·사건은 임의로 확정하지 않고 `historical_review_required`로
보류한 뒤 출처를 확인한다.

## 현재 진행

- `base_msggame_B001_S01`: 좌표 `2:80:0`~`2:94:0`의 20개 리터럴을 새로
  번역했다.
- `base_msggame_B001_S02`: 좌표 `2:95:0`~`2:116:1`의 30개 리터럴을 새로
  번역했다.
- `base_msggame_B001_S03`: 좌표 `2:117:0`~`2:131:2`의 33개 리터럴을 새로
  번역했다.
- `base_msggame_B001_S04`: 좌표 `2:132:0`~`2:146:1`의 27개 리터럴을 새로
  번역했다.
- `base_msggame_B001_S05`: 좌표 `2:147:0`~`2:162:1`의 24개 리터럴을 새로
  번역했다.
- `base_msggame_B001_S06`: 좌표 `2:163:0`~`2:180:1`의 23개 리터럴을 새로
  번역했다.
- `base_msggame_B001_S07`: 좌표 `2:181:0`~`2:200:2`의 52개 리터럴을 새로
  번역했다.
- `base_msggame_B001_S08`: 내부 문법·폰트 시험 블록 `1:7:0`~`1:30:2`의
  표시 리터럴 71개를 구조적 근거에 따라 `confirmed_non_display`로 판정하고
  현재 값을 보존했다. 근거는 `non_display_classification.source_free.v1.json`에
  원문 없이 기록한다.
- `base_msggame_B001_S09`~`S11`: 좌표 `2:201:0`~`2:271:2`의 표시 리터럴
  118개를 새로 번역했다. 반복 전투 대사, 역사 고유어, 인명·수치·활용 명령
  조각을 함께 검토했다.
- `base_msggame_B001_S12`~`S15`: 좌표 `2:272:0`~`2:423:0`의 표시 리터럴
  200개를 전수 분류했다. 실제 대사·런타임 조각 114개를 새로 번역하고, 명시적
  미사용 특성 더미 슬롯 86개는 구조 근거를 남긴 뒤 현재 값을 보존했다.
- `base_msggame_B001_S16`~`S19`: 좌표 `2:424:0`~`2:584:0`의 표시 리터럴
  200개를 전수 분류했다. 실제 대사·런타임 조각 141개를 새로 번역하고, 앞선
  슬롯 표에서 이어지는 명시적 미사용 특성 더미 59개는 현재 값을 보존했다.
- `base_msggame_B001_S20`~`S28`: 좌표 `2:585:0`~`4:49:0`의 표시 리터럴
  200개를 새로 번역했다. 전투·배웅 대사와 사망 보고, 저장·설정 UI를 포함하며,
  고정 문구 88개와 런타임 결합 조각 112개로 분류했다.
- `base_msggame_B001_S29`~`S38`: 좌표 `4:50:0`~`6:471:0`의 표시 리터럴
  200개를 새로 번역했다. 평정·정책·거래·장수 배치·포상·혼례·당주 교체에
  관한 인물 반응이며, 고정 대사 191개와 런타임 결합 조각 9개로 분류했다.
- `base_msggame_B001_S39`~`S48`: 좌표 `6:472:0`~`6:656:0`의 표시 리터럴
  200개를 새로 번역했다. 당주 교체·추방·군단 운용·건의 대기·공성·침공 징후·
  영지 통치 반응이며, 고정 대사 102개와 런타임 결합 조각 98개로 분류했다.
- `base_msggame_B001_S49`~`S58`: 좌표 `6:657:0`~`6:842:1`의 표시 리터럴
  200개를 새로 번역했다. 영지 통치·격무·평정중 합류·가문 성장·충성 저하·
  대인 갈등·부상 반응이며, 고정 대사 139개와 런타임 결합 조각 61개로 분류했다.
- `base_msggame_B001_S59`~`S68`: 좌표 `6:843:0`~`6:1040:0`의 표시 리터럴
  200개를 새로 번역했다. 부상·질병·정책·병량 거래·인사이동·포상·결연·은거
  반응이며, 고정 대사 196개와 런타임 결합 조각 4개로 분류했다.
- `base_msggame_B001_S69`~`S77`: 좌표 `6:1041:0`~`6:1210:1`의 표시 리터럴
  200개를 새로 번역했다. 은거·추방·군단 편제·평정 종료·논공행상·상인 거래·
  군단 지침이며, 고정 대사 137개와 런타임 결합 조각 63개로 분류했다.
- 생성 검토 큐 `base_msggame-B008`~`base_msggame-B017`는 각각 표시 대상
  199개, 199개와 200개짜리 여덟 배치 전부가 분류되어 의미 범위 검토가 완료됐다.
  작성용 segment의 `B001` 명칭과 생성 큐 batch 번호는 서로 다른 식별자다.
- 누적 승인·분류는 1,998개다. 실제 재번역 1,007개, 런타임 조각 775개,
  비표시 내부 데이터 216개로 구성된다.
- 정적 재번역 1,007개와 비표시 보존 216개, 합계 1,223개는 후보 반영 자격을 갖췄다.
  동적 인명·세력·수치·활용 명령과 결합되는 775개는 의미 검증을 통과했으며
  실게임 조사 결합 검수가 남았다.
- 진행 수치는 `progress.source_free.v1.json`에 원문 없이 기록한다.
