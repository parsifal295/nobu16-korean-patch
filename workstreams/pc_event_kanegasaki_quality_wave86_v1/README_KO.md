# W86 가네가사키 퇴각 이벤트 품질 검수

이 작업 스트림은 PK 이벤트 ID `3230`~`3244`의 15행을 PC JP 원문 및 PC EN/SC/TC 문맥으로 전수 검수한다.
변경 행은 `3231`, `3234`, `3238`이며 나머지 12행은 직접 대조 후 유지한다.

현재 이 작업 스트림은 **W85 후보의 경로·packed/raw 프로필을 받기 전에는 후보를 만들 수 없도록 의도적으로 잠겨 있다.** W85의 실제 온디스크 후보와 프로필을 받으면, 그 파일만을 엄격한 선행 입력으로 고정한다. Steam 설치본·중간 후보·순정 JP 파일을 선행 입력으로 대체하지 않는다.

한국어 수동 개행은 원문 일본어 개행을 이식하지 않고 의미 단위로 배치한다. 문장 축약·정보 삭제·인명 변경은 하지 않는다. PK 실게임 검사는 원본 G1N 전각 `48px`, 반각 `24px`, 한 줄 raw `960px` 이하, 최대 `4줄`을 사용한다. 보고용 실효 폭은 `ceil(raw * 30 / 48)`이며 통과 게이트가 아니다.

이 장면에는 런타임 인명 토큰이 없어 별도 예약 폭이 없다. 색상 태그·제어 구조는 보존하며 태그 내부에 개행을 넣지 않는다.

후보 산출물은 준비가 끝난 뒤에만 `tmp/pc_event_kanegasaki_quality_wave86_v1/candidate-final/`에 생성한다. 이 작업에는 Steam 적용·Git 커밋/푸시·릴리스가 포함되지 않는다.

W85 입력 전에는 다음 읽기 전용 작성 검증만 가능하다.

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_kanegasaki_quality_wave86_v1\build_pc_event_kanegasaki_quality_wave86_v1.py authoring-check
& $py -B -m unittest workstreams\pc_event_kanegasaki_quality_wave86_v1\test_pc_event_kanegasaki_quality_wave86_v1.py -v
```
