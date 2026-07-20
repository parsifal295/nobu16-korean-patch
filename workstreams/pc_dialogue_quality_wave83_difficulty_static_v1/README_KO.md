# Wave 83 — 정적 난이도 안내 대사 후보

이 작업공간은 `조금 어려움소임이라니`처럼 일본어 `0143` 활용 명령이 그대로
한국어에 남은 난이도 안내 네 record만 private candidate로 보정한다.

| 파일 | 좌표 | 표시 결과 |
| --- | --- | --- |
| Base `MSG/JP/msggame.bin` | `15:220` | `다소 어려운 일입니다.` / `신중히 판단하십시오.` |
| Base `MSG/JP/msggame.bin` | `15:270` | `다소 어려운 일입니다.` |
| PK `MSG_PK/JP/msggame.bin` | `15:223` | `다소 어려운 일입니다.` / `신중히 판단하십시오.` |
| PK `MSG_PK/JP/msggame.bin` | `15:273` | `다소 어려운 일입니다.` |

문장의 난이도·일의 성격·신중한 판단 요청을 모두 유지한다. 명칭 변경이나 의미
단위 삭제를 하지 않으며, 기존 literal marker 수와 수동 LF 수도 보존한다.

## 엄격한 입력 체인

- Base 입력은 현재 Steam `MSG/JP/msggame.bin`의 LF 복구 후 상태
  (`4E74E524…5374`)다.
- PK 입력은 Steam 파일이 아니라 Wave 82 private candidate
  `tmp/pc_dialogue_quality_wave82_b15_static_plans_v1/candidate/MSG_PK/JP/msggame.bin`
  (`3F6F85E5…C2C7`)이다.
- Wave 82의 `audit.v1.json`과 `build_manifest.v1.json`도 정확한 SHA-256으로
  고정해, 후보 체인이 바뀌면 W83은 빌드를 거부한다.

각 대상은 PC Base/PK 일본어 및 PC EN/SC/TC 같은 문맥의 record SHA-256을
고정 대조한다. 완전한 정적 `0143 <u32>`만 정확히 제거하며, runtime slot
`0143 01 00 00 00`와 `02xx` opcode는 대상에 없음을 증명한다. 비대상 record
byte identity, marker topology, opaque span, terminator, raw-LZ4 재파싱,
packed/raw SHA-256, 활성 글꼴 폭(최대 3줄·912px)을 함께 검증한다.

Switch 파일·Switch 번역문은 읽지 않으며, Steam 적용·Git stage/commit/push,
릴리즈, 네트워크 기능은 구현하지 않았다. 출력은 아래 private 경로뿐이다.

```text
tmp/pc_dialogue_quality_wave83_difficulty_static_v1/candidate/
```

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v `
  workstreams\pc_dialogue_quality_wave83_difficulty_static_v1\test_pc_dialogue_quality_wave83_difficulty_static_v1.py
& $py -B workstreams\pc_dialogue_quality_wave83_difficulty_static_v1\build_pc_dialogue_quality_wave83_difficulty_static_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave83_difficulty_static_v1\build_pc_dialogue_quality_wave83_difficulty_static_v1.py verify-private
```
