# PC-only 전체 텍스트 coverage manifest v1

이 workstream은 10개 PC 텍스트 리소스의 기존 감사/closure ledger를 하나로
병합해, 각 `resource + coordinate`가 정확히 한 번만 나타나는지 검증한다.
대상 좌표 수는 **159,341개**다.

| 입력 묶음 | 리소스 | 좌표 수 |
| --- | --- | ---: |
| full audit | `ev_strdata`, `msgbre`, `msgire`, `msgstf`, `msgui` | 26,110 |
| core msggame closure | `base_msggame`, `pk_msggame` | 53,786 |
| PC core closure | `strdata`, `msgdata`, `msgev` | 79,445 |

`ev_strdata` full audit은 당시 active-builder 좌표 106개를 의도적으로
제외했다. 이 manifest는 해당 audit의 PC coordinate universe(0–17,867)와
source-free summary의 제외 수를 대조해 **그 106개 좌표의 여집합만** 보완한다.
generic overlay 또는 그 안의 한국어 문구는 읽지 않는다.

모든 입력은 Switch Korean, historic Korean, Steam 쓰기 여부를 해당 input의
provenance 필드로 검사한다. 통합 ledger는 source-free이며, 정적/기계적
coverage는 번역 의미 품질의 완료 판정이 아니므로 `semantic_completion`은 항상
`false`다.

실행:

```powershell
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' `
  workstreams\translation_quality_pc_coverage_manifest_v1\build_pc_only_coverage_manifest_v1.py --write

& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' `
  workstreams\translation_quality_pc_coverage_manifest_v1\build_pc_only_coverage_manifest_v1.py --validate
```

출력은 `tmp/translation_quality_pc_coverage_manifest_v1/` 아래에만 생성되며,
게임 파일, Steam 설치본, 기존 generic workstream, 커밋은 변경하지 않는다.
