# 인물 대사 템플릿 결합 개행 복구 v1

이 작업공간은 현재 Steam PC 한국어 `msggame`에서 확인된 템플릿 결합 오류만
후보 파일로 만든다. 문장, 번역 표현, 런타임 토큰, `02xx`/`0143` 명령은 바꾸지
않는다.

대상은 총 20개 물리 레코드다.

- Base `MSG/JP/msggame.bin`: block 8 record 258–262, 268–272
- PK `MSG_PK/JP/msggame.bin`: block 8 record 264–268, 274–278

각 대상에서 literal 0의 끝에 LF 하나만 넣는다.

- `등의 풍작이 되었다` → `등의 풍작이 되었다\n`
- `등의 피해가 있었다` → `등의 피해가 있었다\n`

literal 1·2는 원문 바이트 경계를 그대로 유지하고, literal 바깥의 opaque span,
`02xx`, `0143 <u32>`, `050505` 종료 코드는 정확히 같아야 한다. Base/PK의
순정 PC 일본어 원본과도 대상 레코드별 control skeleton이 같은지 확인한다.

빌더는 Steam 설치본을 읽기만 하며, 결과는 다음 임시 경로에만 쓴다.

`tmp/pc_person_dialogue_template_lf_repair_v1/candidate/`

Steam 적용·Git push·릴리스·커밋 기능은 이 workstream에 없다.

초기 전달값 `69F1…`(Base), `D1AE…`(PK)는 해당 후보 파일·raw SHA·생성
방법이 남아 있지 않아 검증할 수 없었다. 현재 Steam 입력을 고정하고
`msggame_format.rebuild_packed_with_literals`로 다시 만든 후보는 입력과 같은
literal-only raw-LZ4 wrapper를 유지한다. 따라서 이 workstream은 실제 측정된
후보 packed/raw SHA-256만 사용하며, 이전 두 값은 참고용 불검증 기록으로만
남긴다.

실행:

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams/pc_person_dialogue_template_lf_repair_v1/test_pc_person_dialogue_template_lf_repair_v1.py
& $py -B workstreams/pc_person_dialogue_template_lf_repair_v1/build_pc_person_dialogue_template_lf_repair_v1.py
```

빌더는 현재 Steam 입력 SHA-256, 순정 일본어 source SHA-256, 대상 20건,
비대상 레코드 byte identity, literal marker 순서/개수, LZ4 재파싱, raw 크기
각 +20바이트, 그리고 두 후보 파일의 고정 SHA-256을 한 번에 검증한다.
