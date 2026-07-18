# PC 인물 대사 품질 위험 후보 v1

이 workstream은 현재 Steam PC 적용본의 `MSG/JP/msggame.bin`과
`MSG_PK/JP/msggame.bin`만 읽어, 다음 수정 파동에서 우선 검토할 인물 대사
후보 30개를 고정한다. 게임 파일, Steam 설치본, 기존 workstream은 바꾸지
않는다.

후보의 공통 신호는 다음과 같다.

- 현재 한국어 레코드가 일본어 전용 `0143` 활용 명령을 아직 보유한다.
- 같은 PC 레코드의 EN/SC/TC는 그 명령을 보유하지 않는다.
- 한국어 본문에는 종결어미 누락, 조사 결합 오류, 또는 남은 일본식 종결부호가
  실제로 보인다.
- 레코드는 `0143` 조각과 정상 종료 `050505` 외에는 비문자 바이트가 없는 정적
  대사다. 따라서 런타임 인명·세력·시설 토큰을 건드리지 않는다.

각 후보는 Base와 PK의 같은 원문이면 한 묶음으로 기록하고, PK 전용 원문은 PK
좌표만 기록한다. Wave 7의 12개 좌표는 명시적으로 제외한다. Switch 한국어는
열거나 참조하지 않는다.

추가로 실게임에서 확인된 PK `msgev` 오케하자마 범위 `4494`–`4510`은 별도 우선
대조했다. 이 범위의 확정 후보는 `4495`(우마마와리슈), `4502`(가이도 제일의 무사·
지부타이후), `4506`(애도), `4508`(수식어·문장 연결), `4509`(고소슨) 다섯 건이다.
`4504`의 `응? / 이것은?`은 PC EN·TC에도 물음표가 있어 의도된 문장부호로 명시적
제외했다.

권장 수정은 자동 적용안이 아니다. 실제 적용 전에는 각 레코드를 단일 한국어
리터럴로 재구성하고 `0143`만 제거하며, 기존 수동 줄 수를 보존해야 한다. 이후
해당 대사가 실제 게임에서 표시되는 장면으로 QA한 뒤에만 릴리즈 후보에 포함한다.

검증:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B `
  workstreams\pc_dialogue_quality_triage_v1\build_pc_dialogue_quality_triage_v1.py --write --validate
```

생성물은 이 workstream 아래의 `pc_dialogue_quality_triage_candidates.v1.json`,
`pk_msgev_okehazama_4494_4510_priority.v1.json`, `validation.v1.json`뿐이다.
