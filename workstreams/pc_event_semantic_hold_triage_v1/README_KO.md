# PC 이벤트 semantic hold triage v1

현재 Steam에 아직 그대로 남아 있는 Base/PK 이벤트 보류 행을, 기존 PC-only 원장에서 재현 가능한 방식으로 분리한다. 이 workstream은 번역문을 만들거나 Steam 파일을 수정하지 않는다.

## 입력 범위

- Base `MSG/JP/ev_strdata.bin`: pristine PC JP, 현재 Steam KO, Steam PC SC/TC
- PK `MSG_PK/JP/msgev.bin`: pristine PC JP, 현재 Steam KO, Steam PC EN/SC/TC
- Base 원장: `tmp/translation_quality_audit_v1/semantic/ev_strdata_pc_only_full_audit.v1.jsonl`
- PK 원장: `tmp/translation_quality_pc_core_closure_v1/pc_coordinate_dispositions.source_free.v1.jsonl`

Base 이벤트에는 PC EN 리소스가 없으므로 Base의 완전 참조 서명은 JP/SC/TC다. Switch Korean, 과거 Korean 번역, generic overlay 번역문은 읽지 않는다.

## 재현 규칙

1. 기존 hold 행의 `current_ko_utf16le_sha256`가 현재 Steam 셀과 같을 때만 live hold로 유지한다.
2. JP·KO·PC 참조 언어 전체에서 런타임 토큰, printf, ESC, 줄바꿈, 바깥 여백, 기타 제어문자를 검사한다.
3. 런타임/printf/ESC가 있으면 `runtime_printf_esc_structural`, 나머지 레이아웃 제어가 있으면 `linebreak_or_whitespace_layout`, 모두 없으면 `pure_static_wording`으로 분류한다.
4. 정적 행은 같은 리소스의 완전 PC 문맥 서명으로 먼저 묶고, Base/PK 공통 JP/SC/TC 서명으로 교차 확인한다.

교차 앵커의 `consensus`는 현재 Korean 렌더링이 같은 원문군에서 동일하다는 기계적 확인일 뿐이다. 번역 품질을 승인하거나 새 번역문을 자동 생성하는 근거는 아니다.

## 현재 고정 계약

| 분류 | Base | PK | 합계 |
| --- | ---: | ---: | ---: |
| 런타임·printf·ESC 구조 | 145 | 618 | 763 |
| 줄바꿈·여백 레이아웃 | 9 | 86 | 95 |
| 순수 정적 문구 | 1 | 215 | 216 |

정적 문구의 JP/SC/TC 교차 앵커 결과는 `consensus` 25건, `conflict` 183건, `no_anchor` 8건이다. 즉, 사람의 문맥·용어 판단이 필요한 정적 큐는 191건이다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_semantic_hold_triage_v1\build_pc_event_semantic_hold_triage_v1.py --write --validate
& $py -B -m unittest workstreams.pc_event_semantic_hold_triage_v1.test_pc_event_semantic_hold_triage_v1
```

생성물은 `tmp/pc_event_semantic_hold_triage_v1/` 아래에만 작성된다. JSONL에는 ID, 해시, 구조 플래그, 분류, 앵커 ID와 해시만 기록하며 원문·번역문 본문은 기록하지 않는다.

`semantic_completion`은 항상 `false`다. 이 원장은 검수 우선순위와 안전한 자동 중복 확인만 제공한다.
