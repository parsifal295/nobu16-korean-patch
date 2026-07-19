# PC 원문 기반 W66: 정적 오역·태그·줄바꿈 정정

W66은 W65 후보를 기반으로 다음만 추가 정정한다.

- Base/PK `msggame` 정적 리터럴 46개: 조사·존대·구두점 오류, `心証`·`霊場`·`郡代`·`敵城調略`·`難事` 등의 오역, 종료 확인문, 상인·튜토리얼 대사, 보이는 ASCII `n` 오타.
- `msgev` 정적 이벤트 15개: 지명·인물·세력 색상 태그가 한국어 어순 때문에 뒤바뀐 문장을 PC 일본어 원문 태그 순서에 맞춰 복원.

`n`이 보이던 Base `6:2777:0`·PK `6:2783:0`은 수동 줄바꿈을 각각 `0 → 2`로 바꾼다.
Base `6:1144:0`·`8:1172:0`도 각각 `1 → 2`로 바꾸며, Base `8:1173:0`·`8:1176:0`은
줄 수는 보존한 채 개행 위치만 다시 잡는다. 이 여섯 대상은 모두 3줄 이하·한 줄 최대
`912px` 이하이며, 모든 이벤트 대상도 동일한 한도와 제어 바이트 보존을 고정한다.

이 빌더는 W65 후보와 pristine Steam PC 일본어만 읽고, 후보는
`tmp/pc_private_union_composite_wave66_v1/candidate-final2/`에만 생성한다. Switch 자료,
폰트, Steam 게임 파일, Git, 네트워크, 공개 릴리즈는 건드리지 않는다.

```powershell
python -B -X utf8 workstreams\pc_private_union_composite_wave66_v1\build_pc_private_union_composite_wave66_v1.py profile
# 새 후보를 만들 때에는 profile 결과를 EXPECTED_FINAL_* 상수에 먼저 고정한다.
python -B -X utf8 workstreams\pc_private_union_composite_wave66_v1\test_pc_private_union_composite_wave66_v1.py
python -B -X utf8 workstreams\pc_private_union_composite_wave66_v1\build_pc_private_union_composite_wave66_v1.py build
python -B -X utf8 workstreams\pc_private_union_composite_wave66_v1\build_pc_private_union_composite_wave66_v1.py verify-private
python -B -X utf8 workstreams\pc_private_union_composite_wave66_v1\build_pc_private_union_composite_wave66_v1.py diff-check
```
