# PC 이벤트 줄바꿈 Wave 24

이 workstream은 완료된 Wave 23의 11파일 private 후보만 입력으로 사용해 PK 이벤트
텍스트 5개를 재배치한다. Steam 설치본, Git, 원격 저장소, 릴리즈에는 쓰지 않는다.

## 범위

- 변경 리소스: `MSG_PK/JP/msgev.bin` 하나
- 변경 ID: `3725`, `4208`, `4677`, `4918`, `5351`
- 다른 10파일은 Wave 23 후보와 hash·크기가 byte-identical여야 한다.
- Wave 18의 정적 라벨 8개도 변경되지 않는지 함께 검증한다.

## 문맥과 레이아웃 원칙

- 순정 Steam PC 일본어와 PC EN/SC/TC만 문맥 앵커로 읽는다. Switch 한국어는 읽지 않는다.
- 기존 수동 개행 수·공백 수·ESC/printf/런타임 토큰을 보존한다.
- 실제 PC JP 이벤트 폰트 advance를 사용해 각 문구를 3줄 이하, 줄당 912px 이하로 검증한다.
- `4208`은 직역투인 `당주의 그릇`을 `당주로서의 자질`로, `4918`은 PC JP/SC/TC의 대조 쉼표에 맞춰 `이기고, 적으면`으로 보정한다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v KR_PATCH_WORK\workstreams\pc_event_layout_wave24_v1\test_pc_event_layout_wave24_v1.py
& $py -B KR_PATCH_WORK\workstreams\pc_event_layout_wave24_v1\build_pc_event_layout_wave24_v1.py hash
& $py -B KR_PATCH_WORK\workstreams\pc_event_layout_wave24_v1\build_pc_event_layout_wave24_v1.py build
& $py -B KR_PATCH_WORK\workstreams\pc_event_layout_wave24_v1\build_pc_event_layout_wave24_v1.py verify-private --candidate-root KR_PATCH_WORK\tmp\pc_event_layout_wave24_v1\candidate
```

`build`는 `tmp/pc_event_layout_wave24_v1/candidate`에 11파일 private 후보와
동일 `tmp` 경로의 audit·manifest만 만든다. 실제 Steam 적용과 게임 장면 QA는 이
workstream 범위 밖이다.
