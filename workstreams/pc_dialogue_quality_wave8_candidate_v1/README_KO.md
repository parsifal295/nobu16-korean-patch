# PC 인물 대사 품질 Wave 8 후보 v1

현재 Wave7 Steam 적용본을 입력으로 한 **로컬 후보**다. Steam 파일을 쓰는
기능과 릴리즈 절차는 포함하지 않는다.

## 범위

- 정적 인물 대사 30개 논리 후보: Base 18개 + PK 30개, 실제 `msggame` 레코드
  **48개**
- PK 오케하자마 이벤트 `msgev` **5개**: `4495`, `4502`, `4506`, `4508`, `4509`
- 총 변경 레코드/엔트리: **53개**

인물 대사는 남은 일본어 전용 `0143` 활용 명령만 제거하고 한국어 문장을
완결한다. 런타임 토큰은 대상에 포함하지 않는다. 이벤트는 기존 수동 3줄을
보존하며 실제 PK 이벤트 폰트로 줄당 912px 이하를 확인한다. `4504`의
`응? / 이것은?`은 PC EN/TC에도 있는 의도된 문장부호라 변경하지 않는다.

## 고정된 후보 출력

- Base `MSG/JP/msggame.bin`:
  `7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492`
- PK `MSG_PK/JP/msggame.bin`:
  `454A18B0F0ED5E39A3AC823AD0A30086C25226BF6E48D4580962DFEE84E24A32`
- PK `MSG_PK/JP/msgev.bin`:
  `1880A8052C916FAC7F262CCC8638477F5AA124F248A6468E0533A8E252AB55C5`

## 검증

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B `
  workstreams\pc_dialogue_quality_wave8_candidate_v1\build_pc_dialogue_quality_wave8_candidate_v1.py audit --write

& 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B `
  workstreams\pc_dialogue_quality_wave8_candidate_v1\build_pc_dialogue_quality_wave8_candidate_v1.py build `
  --output-root tmp\pc_dialogue_quality_wave8_candidate_v1\candidate-build `
  --manifest tmp\pc_dialogue_quality_wave8_candidate_v1\manifest-build.json

& 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest `
  workstreams\pc_dialogue_quality_wave8_candidate_v1\test_pc_dialogue_quality_wave8_candidate_v1.py
```

정적 검증이 통과해도 인물 대사와 오케하자마 이벤트의 실제 게임 장면 QA는
별도로 필요하다. 게임이 실행 중일 때는 적용하지 않는다.
