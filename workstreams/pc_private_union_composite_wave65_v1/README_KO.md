# PC 원문 기반 W65: `내대신` 표기 정정

W65는 W64 후보를 그대로 이어받고, PK 대사 조각 네 곳의 `나이후`를
`내대신`으로 정정한다. 네 좌표 모두 pristine Steam PC 일본어 원문이
`内府`이며, 도쿠가와 이에야스를 가리키는 이 호칭은 음역이 아니라 관직명
`내대신`으로 번역한다.

- 대상: PK `17:274:1`, `17:276:1`, `17:357:0`, `17:405:1`
- 변경: `나이후` → `내대신`
- 각 조각의 폭: 변경 전후 모두 `144px`
- 수동 줄바꿈·런타임 토큰·제어 코드·폰트는 변경하지 않는다.

이 빌더는 W64 후보와 pristine PC 일본어만 읽는다. Switch 자료, Steam 게임
파일, Git, 네트워크, 공개 릴리즈에는 접근하거나 쓰지 않는다. 후보 출력은
`tmp/pc_private_union_composite_wave65_v1/candidate/`에만 생성된다.

```powershell
python -B -X utf8 workstreams\pc_private_union_composite_wave65_v1\test_pc_private_union_composite_wave65_v1.py
python -B -X utf8 workstreams\pc_private_union_composite_wave65_v1\build_pc_private_union_composite_wave65_v1.py profile
python -B -X utf8 workstreams\pc_private_union_composite_wave65_v1\build_pc_private_union_composite_wave65_v1.py build
python -B -X utf8 workstreams\pc_private_union_composite_wave65_v1\build_pc_private_union_composite_wave65_v1.py verify-private
python -B -X utf8 workstreams\pc_private_union_composite_wave65_v1\build_pc_private_union_composite_wave65_v1.py diff-check
```
