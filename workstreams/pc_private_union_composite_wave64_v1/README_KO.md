# PC 비공개 통합 후보 W64

W64는 W63 위에 정적으로 증명된 이벤트 재개행만 더한다. 직접 PC 일본어 원문과 W63 PC 한국어 후보만 읽으며, Switch·다른 플랫폼·다른 언어 번역 파일은 읽지 않는다.

## 이벤트 수동 개행 57건

각 항목은 기존 수동 개행이 없는 912px 초과 한 줄이다. 문맥 단위에서 색상 태그 바깥의 기존 공백 하나만 LF로 바꿔 두 줄로 나눈다. 단어·문장부호·색상 태그·런타임 토큰·printf·기타 제어문자는 바꾸지 않는다.

- 대상: `5571`, `5820`, `5910`, `5918`, `6114`, `6176`, `6188`, `6462`, `6523`, `6665`, `6677`, `6695`, `6824`, `6841`, `6868`, `7021`, `7091`, `7153`, `7492`, `7697`, `8072`, `8121`, `8151`, `8182`, `8346`, `8414`, `8601`, `9102`, `9144`, `9164`, `9590`, `9636`, `9789`, `9794`, `9829`, `9880`, `9944`, `9952`, `9954`, `10058`, `10156`, `10158`, `10165`, `10166`, `10191`, `10346`, `10415`, `10504`, `10569`, `10591`, `10685`, `10714`, `10757`, `10801`, `10898`, `10915`, `10956`
- 결과: 모든 문장은 정확히 2줄이며 각 줄은 `216–888px` 범위, 최대 `912px` 이하이다.
- `6523`은 완결된 일반 이벤트 내레이션이라 포함한다.
- `11000`은 시간·장소 장면 헤딩이라 제목 UI 검수 대상으로 보류한다.

이 후보는 `tmp/pc_private_union_composite_wave64_v1/candidate/`에만 생성된다. 빌더는 Steam 파일·Git·네트워크·공개 릴리즈를 조작하지 않는다.

```powershell
python -B -X utf8 workstreams\pc_private_union_composite_wave64_v1\test_pc_private_union_composite_wave64_v1.py
python -B -X utf8 workstreams\pc_private_union_composite_wave64_v1\build_pc_private_union_composite_wave64_v1.py profile
python -B -X utf8 workstreams\pc_private_union_composite_wave64_v1\build_pc_private_union_composite_wave64_v1.py build
python -B -X utf8 workstreams\pc_private_union_composite_wave64_v1\build_pc_private_union_composite_wave64_v1.py verify-private
python -B -X utf8 workstreams\pc_private_union_composite_wave64_v1\build_pc_private_union_composite_wave64_v1.py diff-check
```
