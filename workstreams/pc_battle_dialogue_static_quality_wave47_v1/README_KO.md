# Wave 47 — PK 전투 대사 정적 품질 후보

이 작업물은 Steam PC의 `MSG_PK/JP/msggame.bin` block 17에서 확인한 전투 대사 품질 보정 후보입니다. 원문 근거는 pristine Steam PC 일본어이며, PC EN/SC/TC는 문맥 확인에만 사용했습니다. Switch 한국어는 읽지 않습니다.

- 안전 후보: 34개 레코드. `02xx` 런타임 슬롯과 `0143` 명령이 없는 정적 레코드만 포함합니다.
- 보존: literal marker, opaque byte, 수동 줄바꿈 수, 레코드 종료 코드.
- 폭 제한: 모든 후보는 최대 3줄·912px 이하입니다.
- 예: `요시히로 주군` → `요시히로님`, `가와고에성에 패하다니` → `가와고에성이…`, 가문·부대·지명 경계의 누락 공백 보정.

검토한 65개 중 나머지 31개는 문구 자체는 맞지만 대상 줄이 912px를 넘습니다. 이들은 자동 후보에 넣지 않고 `DISPLAY_QA_HOLDS`로 유지합니다. UI별 재개행과 실게임 화면 검수가 끝나기 전에는 적용하지 않습니다.

이 스크립트는 `tmp/pc_battle_dialogue_static_quality_wave47_v1/candidate` 아래에만 후보 파일을 만들 수 있습니다. Steam 파일 쓰기, 백업 거래, Git 조작, 네트워크/릴리즈 기능은 없습니다.

```powershell
py -3 -X utf8 workstreams\pc_battle_dialogue_static_quality_wave47_v1\build_pc_battle_dialogue_static_quality_wave47_v1.py build
py -3 -X utf8 workstreams\pc_battle_dialogue_static_quality_wave47_v1\build_pc_battle_dialogue_static_quality_wave47_v1.py verify-private
py -3 -X utf8 -m unittest workstreams\pc_battle_dialogue_static_quality_wave47_v1\test_pc_battle_dialogue_static_quality_wave47_v1.py -v
```
