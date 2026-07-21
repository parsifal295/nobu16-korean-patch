# W98 기후 명명 이벤트 전수 검수

범위는 PK `MSG_PK/JP/msgev.bin`의 기후 명명 장면 `3287–3308` 22행이다.
최신 `manual_compact` 전체 복원 private 후보만 한국어 바이너리 입력으로 쓰고,
순정 Steam PC 일본어와 PC EN/SC/TC를 읽기 전용 의미 근거로 대조한다. 스위치판
한글은 열거나 기준으로 사용하지 않는다.

## 검수 결과

22행을 전부 다시 읽었다. 이 중 아래 12행만 후보에서 변경한다.

| 좌표 | 분류 | 조치 |
| ---: | --- | --- |
| 3288 | 문맥 개행 | `천하로 나아갈 발판` 명사구를 분리하지 않음 |
| 3293 | 의미+문맥 | `城下町`을 `성하 마을`로 바로잡음 |
| 3295 | 문맥 개행 | 유래 질문·추론·명명 제안을 문장 단위로 분리 |
| 3298–3300 | 문맥 개행 | `기후라 부르겠다`, `새로 만들겠다`, 권유 구문을 어절 중간에서 분리하지 않음 |
| 3302 | 의미+문맥 | `周`를 `주나라`로 바로잡아 주 무왕임을 명시 |
| 3303–3305 | 문맥 개행 | 풀이·긴 이야기·마음에 드는군을 각각 의미 단위로 유지 |
| 3306 | 의미+문맥 | `善哉、善哉`의 반복 찬탄을 `훌륭합니다, 훌륭합니다`로 복원 |
| 3307 | 문맥 개행 | 이노쿠치→기후와 이나바야마성→기후성의 두 결과를 분리 |

나머지 10행은 원문·PC 다국어 대조 후 현재 문안과 개행을 유지한다. 문장을
축약하거나 의미를 삭제하지 않는다.

## 레이아웃

이 이벤트 대사에는 Static Patch 007 현재 기준을 적용한다.

- 글자 크기 30px, 유효 폭 912px, 최대 4줄
- 원본 G1N 폭은 전각 48px·반각 24px
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- 각 행마다 표시 문자열, 원본 폭, 환산 실효 폭, 전각/반각 수, 줄 수,
  912px 초과 여부를 private `audit.v1.json`에 기록한다.

색상 태그·제어 코드·종료 구조를 유지하며 태그 내부에는 개행을 넣지 않는다.
일본어 원문의 줄바꿈은 이식하지 않고 한국어 의미 단위에서 새로 판단한다.

## 실행

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_gifu_quality_wave98_v1\build_pc_event_gifu_quality_wave98_v1.py build
& $py -B workstreams\pc_event_gifu_quality_wave98_v1\build_pc_event_gifu_quality_wave98_v1.py verify-private
& $py -B -m unittest -v workstreams\pc_event_gifu_quality_wave98_v1\test_pc_event_gifu_quality_wave98_v1.py
```

산출물은 `tmp/pc_event_gifu_quality_wave98_v1/candidate-final/`에만 쓴다.
Steam 적용, Git 커밋·푸시, 릴리즈는 이 작업의 범위가 아니다.
