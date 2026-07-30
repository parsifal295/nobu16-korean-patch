# PC PK 이벤트 3956 이름·문맥·줄바꿈 private 후보

이 workstream은 Steam PC에 설치된 W45 `MSG_PK/JP/msgev.bin`을 입력으로 하여 이벤트 ID `3956` 한 건만 다시 조립하는 **private 후보**다. Steam 게임 파일, 트랜잭션, Git, 네트워크, 릴리스는 이 스크립트의 범위에 없으며, 출력은 `tmp/pc_event_3956_name_semantic_reflow_v1/candidate/` 아래에만 생긴다.

- W45 입력 packed SHA-256: `01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE`
- W45 입력 raw SHA-256: `F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC`
- 후보 packed SHA-256: `D7CA54F9F942251B980B6D0ECC88347FAF794408EBA6AFC779B43897D6532218`
- 후보 raw SHA-256: `73EFCEAB8E609B0806D85CCE31E9489AFD916046BA85669F89F49CC0370C1AFB`

## 변경 범위

변경 ID는 정확히 `[3956]`뿐이다. `이노에` 표기를 `이노우에`로 바로잡고, 실제 PC 이벤트 글꼴에서 3줄·각 912px 이하를 만족하도록 문장을 다음 literal target으로 고정한다.

```text
ESC-CA모토나리ESC-CZ는 몰래 ESC-CA이노우에 모토카네ESC-CZ를
자객으로 암살해 동요한 ESC-CB이노우에 일파ESC-CZ의
저택을 급습해 일족 30여 명을 숙청했다.
```

위 `ESC-C*` 표기는 README에서만 제어 문자를 보이게 풀어쓴 것이며, 실제 후보에는 U+001B ESC 제어 바이트가 들어간다. 실제 글꼴 폭은 `840 / 912 / 912px`이다. 모든 색상 태그는 줄바꿈 전에 닫히며, ESC 태그 순서·런타임 토큰·printf 토큰·C0 제어 문자·앞뒤 공백의 서명은 원문과 동일한지 검사한다.

## 문맥 압축의 한계

3줄에 맞추기 위해 생략한 어휘는 속도 강조어 `단숨에`뿐이다. 비밀성은 `몰래`로 유지하고, 자객에 의한 암살, 그로 인한 이노우에 일파의 동요, 저택 급습, 일족 30여 명 숙청은 모두 남긴다. 따라서 자동 줄바꿈이나 일반적인 전수 치환이 아니라 ID 3956에만 적용되는 검토 완료 literal target이다.

## 검증

```powershell
py -3 -B .\workstreams\pc_event_3956_name_semantic_reflow_v1\build_pc_event_3956_name_semantic_reflow_v1.py build
py -3 -B .\workstreams\pc_event_3956_name_semantic_reflow_v1\build_pc_event_3956_name_semantic_reflow_v1.py verify-private
py -3 -B -m unittest -v .\workstreams\pc_event_3956_name_semantic_reflow_v1\test_pc_event_3956_name_semantic_reflow_v1.py
py -3 -B .\workstreams\pc_event_3956_name_semantic_reflow_v1\build_pc_event_3956_name_semantic_reflow_v1.py diff-check
```

검증은 W45 input packed/raw 해시와 record count, ID 변경 범위, 원문/target UTF-16LE 해시, 제어·태그·런타임 서명, 실제 이벤트 글꼴 폭, LZ4 및 메시지 테이블 왕복, private 출력 파일 집합을 모두 확인한다. `diff-check`는 Git을 사용하지 않고 이 private workstream의 authoring 파일 공백과 후보 무결성만 확인한다.
