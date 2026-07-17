# msgev PC canonical-title repair v1

`MSG_PK/JP/msgev.bin`의 중국어 병음 잔재 62개를, 같은 Steam PC 리소스 안의 정식 표제 JP→KO 앵커로만 복원하는 격리 후보군이다. 제안 문자열은 각 canonical anchor의 현재 PC KO 표제와 정확히 같으며, 신규 문장을 합성하지 않는다.

입력은 아래 다섯 Steam PC 파일과 pristine Steam PC JP 백업뿐이다.

- pristine PC JP: `KR_PATCH_BACKUP/.../originals/MSG_PK/JP/msgev.bin`
- current Steam PC KO: `MSG_PK/JP/msgev.bin`
- Steam PC EN/SC/TC: 각 `MSG_PK/{EN,SC,TC}/msgev.bin`

Switch, `F:\Games\NOBU16\MSG_PK\SC`, historic Korean workstream, generic overlay의 한국어 payload는 읽거나 근거로 사용하지 않는다. 이 validator는 generic overlay 자체를 열지 않는다. 62건의 중복·현재값·canonical anchor·서식은 PC 원문과 이 private 후보 묶음만으로 검증하며, 최종 오버레이의 좌표 충돌은 통합 builder가 별도로 거부한다.

`private_candidates.v1.jsonl`은 현재값·원본 JP·canonical JP·제안 KO의 UTF-16LE SHA-256을 포함한다. `validation.v1.json`은 한국어 문자열을 싣지 않는 source-free 계약이다.

검증 명령:

```powershell
python .\build_translation_quality_msgev_pc_canonical_title_repair_v1.py
python .\build_translation_quality_msgev_pc_canonical_title_repair_v1.py --proofs
python .\test_translation_quality_msgev_pc_canonical_title_repair_v1.py
```

모든 명령은 읽기 전용이다. Steam, generic overlay, Git을 변경하지 않는다.
