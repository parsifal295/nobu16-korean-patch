# PC 인물 대사 B17 직접 감사 정적 품질 v3

이 작업은 새 번역 후보를 만드는 작업이 아니다. 최신 Wave97 private candidate를
엄격 입력으로 다시 열어 보니, B17 직접 감사 v2의 고신뢰 정적 정정이 이미 모두
반영되어 있었다. 따라서 같은 44건을 이진 재치환하면 중복 변경이 된다.

결론은 다음과 같다.

- Base `MSG/JP/msggame.bin`: 4 literal이 이미 반영됨
- PK `MSG_PK/JP/msggame.bin`: 40 literal이 이미 반영됨
- 합계: **44/44 pre-applied, missing 0, binary replacement 0**
- 새 private candidate 및 MSGGAME 바이너리 출력은 만들지 않음
- Steam 적용, Git, 네트워크, 릴리스 동작은 없음

## 엄격 입력과 직접 PC 근거

입력은 반드시 아래 Wave97 private candidate의 정확한 4파일이어야 한다.

`tmp/pc_dialogue_quality_wave97_pk_security_development_static_v1/candidate/`

- `MSG/JP/msggame.bin` — `27C0…51B2`
- `MSG_PK/JP/msggame.bin` — `E507…6540`
- `audit.v1.json` — `54BF…5A2`
- `build_manifest.v1.json` — `AA24…4AEB`

고신뢰 정적 target 표는 B17 직접 감사 v2와 기존 static v2 builder를 SHA-256으로
고정해 읽는다. 모든 행에서 Wave97 KO가 그 target과 정확히 같고, direct PC JP
literal도 고정값과 정확히 일치해야 한다.

PK는 direct PC JP/EN/SC/TC record 근거를 모두 보관한다. Base는 설치된 PC에
`MSG/EN/msggame.bin`이 없으므로 JP/SC/TC만 같은 resource에서 읽으며, PK EN을
Base EN 근거로 대체하지 않는다. 이 경계는 JSON의 각 Base 행에 명시한다.

## 검증 범위

정적 고신뢰 범위는 기존 B17 v2와 동일한 44 literal/44 record다. 여기에는
`17:950:0–2`의 `선봉 격파` → `선봉 ` 및 `17:971:0`의 잘못 삽입된 `내가` 제거도
포함한다. 두 경우 모두 runtime token이나 후행 literal은 건드리지 않는 고정
literal 정정이다.

각 행은 다음을 검증·기록한다.

- historical KO preimage, approved static target, strict Wave97 KO
- direct PC JP 및 직접 PC EN/SC/TC record anchor
- opaque skeleton, literal marker/token topology, 마지막 literal 뒤 terminator tail
- LF/CR/control signature, 기존 수동 개행 수, raw G1N 폭과 줄 수
- 고정 인물 대사 기준(전각 48px, 반각 24px, 최대 3줄, 888px guide)

Wave97 B17 전체도 direct PC JP와 대조한다. Base는 33 record/66 literal,
PK는 1,159 record/2,256 literal이며 opaque skeleton, marker topology,
terminator tail, LF topology가 모두 일치해야 한다. LF는 839 literal에 총 849개로
확인되며, 이 작업은 LF를 추가·삭제·이동하지 않는다.

## 명시적 제외/HOLD

다음은 이번 정적 커버리지에서 제외한다.

- runtime 이름/조사: Base `17:5:3`; PK `17:226:0–3`, `17:510:0–2`,
  `17:920:0–1`, `17:991:0–1`
- `Color.Blue` / `Color.Default`: PK `17:282:0`
- 진행 수치/괄호 cosmetic HOLD와 B17 전체 LF 변경
- `888px` raw-G1N guide를 이미 초과한 6행: PK `17:54:0`, `504:0`, `852:0`,
  `971:0`, `1073:0`, `1093:0`

마지막 6행은 warning/HOLD로만 남긴다. 이 artifact는 문장 축약이나 수동 개행
재배치를 허용하지 않으므로, 별도 레이아웃 검수에서 문맥 단위로 다뤄야 한다.

## 산출물과 실행

- `audit.v3.json`: 44개 pre-applied 행과 직접 PC 근거, 구조/레이아웃/HOLD 감사
- `manifest.v3.json`: binary output이 없다는 no-op 계약과 audit hash
- `audit_pc_dialogue_b17_direct_static_quality_v3.py`: 읽기 전용 재검증기
- `test_pc_dialogue_b17_direct_static_quality_v3.py`: 회귀 테스트

검증 명령:

```powershell
python workstreams/pc_dialogue_b17_direct_static_quality_v3/audit_pc_dialogue_b17_direct_static_quality_v3.py verify-artifacts
python -m unittest workstreams/pc_dialogue_b17_direct_static_quality_v3/test_pc_dialogue_b17_direct_static_quality_v3.py -v
```

두 명령 모두 파일을 쓰지 않는다. `candidate` 디렉터리나 Steam 게임 파일을 만들거나
수정하지 않는 것이 이 작업의 핵심 계약이다.
