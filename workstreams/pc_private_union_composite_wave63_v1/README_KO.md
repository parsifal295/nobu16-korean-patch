# PC 비공개 통합 후보 W63

W63는 W62 위에 직접 PC 일본어 원문으로 다시 증명한 정적 수정만 추가한다. Switch·다른 플랫폼·다른 언어 번역 파일은 읽지 않는다.

## 인물 대사 10건

- PK `6:1230:1`, `6:1231:1`, `6:1232:1`, `6:1234:1`–`6:1238:1`: `원군을 보낼 아군`을 `원군을 청할 아군`으로 수정한다. 이름 토큰 `026432`은 첫 literal 뒤에 그대로 있고, 바뀌는 글자 수·3줄 개행·폰트 폭은 동일하다.
- Base `9:3622:1`, PK `9:3867:1`: `의 모계에 미혹되어라!`를 `의 계략에 미혹되어라!`로 수정한다. 이름 토큰 `024635`과 앞 literal의 개행은 그대로다.

## PK 이벤트 태그/문장 4건

- `4960`: 가문명 색상 태그가 `해방됐다`를 감싸던 오류를 `이마가와`에 되돌리고, `今川の軛より放たれた`의 의미를 복원한다.
- `10386`: 지명 `세키가하라`는 CC, 인물/직함 `내대신`은 CA 태그로 바로잡는다.
- `10483`, `10484`: `다테`·`우에스기`는 CB, `내대신`은 CA 태그로 원문 순서에 맞춰 복구한다.

네 이벤트 문장은 모두 기존과 동일한 ESC 토큰 순서·개수와 줄 수를 유지한다. 이벤트 폰트로 재계산한 최대 폭은 각각 912px 이하이며 3줄을 넘지 않는다. `4960`의 `[bs1871]` 런타임 토큰은 두 번 모두 그대로 보존한다.

이 후보는 `tmp/pc_private_union_composite_wave63_v1/candidate/`에만 생성된다. 빌더는 Steam 파일·Git·네트워크·공개 릴리즈를 조작하지 않는다.

```powershell
python -B -X utf8 workstreams\pc_private_union_composite_wave63_v1\test_pc_private_union_composite_wave63_v1.py
python -B -X utf8 workstreams\pc_private_union_composite_wave63_v1\build_pc_private_union_composite_wave63_v1.py profile
python -B -X utf8 workstreams\pc_private_union_composite_wave63_v1\build_pc_private_union_composite_wave63_v1.py build
python -B -X utf8 workstreams\pc_private_union_composite_wave63_v1\build_pc_private_union_composite_wave63_v1.py verify-private
python -B -X utf8 workstreams\pc_private_union_composite_wave63_v1\build_pc_private_union_composite_wave63_v1.py diff-check
```
