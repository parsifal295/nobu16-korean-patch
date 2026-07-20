# Wave 82 — B15 정적 계책 제안 대사 보정 후보

이 작업공간은 현재 Steam PC 한국어 `MSG_PK/JP/msggame.bin`을 읽기 전용으로
사용해, block 15의 정적 계책 제안 대사 두 건만 private candidate로 만든다.

| 좌표 | 현재 문제 | 목표 방향 |
| --- | --- | --- |
| `15:259` | `잠시 동안면`, `보이겠`, `이쪽이 위`처럼 일본어 `0143` 활용 명령에 의존해 문장이 끊긴다. | 방화 계책에 시간이 필요하고, 성 병사를 회유해 요충지를 장악하는 편의 승산이 높다는 뜻을 완결한다. |
| `15:261` | `빼내기의 건`, `안이(가)`, `돌아설지도 모`가 한국어 문장으로 끝나지 않는다. | 인재 포섭의 위험, 연고자를 통한 권유, 함께 돌아설 가능성을 모두 보존해 완결한다. |

두 대상은 런타임 인명·성·세력 슬롯(`0143 01 00 00 00`, `02xx`)이 없는
정적 대사다. 각 레코드의 완전한 정적 `0143 <u32>` 명령만 정확히 제거하고,
literal marker 수와 순서, 수동 개행 수(각 2개), 그 밖의 opaque bytes,
`05 05 05` 종료 코드는 보존한다. 문장 축약·인명/명칭 변경은 하지 않는다.

## 근거와 범위

- 현재 Steam PK 한국어 preimage: packed SHA-256
  `A8983770FF9026F018042D94F44AF7D0E67B6A7E01F42891B74386B32078791D`
- PC PK 일본어 원본 및 PC EN/SC/TC의 동일 좌표 record SHA-256을 모두 고정해
  의미 대조한다. Switch 파일·과거 Switch 번역문은 읽지 않는다.
- 활성 PC 글꼴로 3줄과 줄당 912px 이하, fallback glyph 없음까지 검사한다.
- 모든 비대상 record byte identity, raw-LZ4 재파싱, packed/raw SHA-256까지
  검증한다.

생성물은 다음 private 경로에만 기록된다.

```text
tmp/pc_dialogue_quality_wave82_b15_static_plans_v1/candidate/
```

Steam 설치 파일 적용, Git stage/commit/push, 릴리즈, 네트워크 기능은 구현하지
않았다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v `
  workstreams\pc_dialogue_quality_wave82_b15_static_plans_v1\test_pc_dialogue_quality_wave82_b15_static_plans_v1.py
& $py -B workstreams\pc_dialogue_quality_wave82_b15_static_plans_v1\build_pc_dialogue_quality_wave82_b15_static_plans_v1.py build
& $py -B workstreams\pc_dialogue_quality_wave82_b15_static_plans_v1\build_pc_dialogue_quality_wave82_b15_static_plans_v1.py verify-private
```
