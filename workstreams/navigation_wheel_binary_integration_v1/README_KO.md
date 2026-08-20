# 네비게이션 휠 B안 바이너리 통합 v1

## 입력

- 정적 후보: `tmp/navigation_wheel_layered_rebuild_v1/run_003`
- 정적 매니페스트 SHA-256: `12B024C4FAB0D22AF3BB17E59E18543BFBE446C89D5CFB856458C98BBF78D2A4`
- 대상: 현재 v0.94.0 리소스 타깃의 네 아카이브
- 글꼴: 정적 후보에 고정된 B(`SeoulHangang ExtraBold`)

Imagen·ImageGen 등 생성형 도구는 사용하지 않는다. 정적 후보는 공식 JP/SC/TC/EN 원본의 몸체·아이콘·상태 픽셀과 분리 렌더링한 B 글자 레이어로만 만들어졌다.

## 통합 방법

1. 현재 v0.94.0 대상 아카이브를 고정된 크기와 SHA-256으로 확인한다.
2. 카탈로그의 900개 논리 셀 안에서만 정적 후보 픽셀을 원하는 값으로 삼는다.
3. 기존 v0.94 휠은 몸체까지 축소된 완성 이미지였으므로 논리 셀 전체를 대상으로 원본 크기의 몸체·아이콘과 B 글자를 복원한다.
4. 원하는 값과 현행 타깃이 다른 픽셀이 닿는 4×4 BC3 블록만 결정론적으로 다시 인코딩한다.
5. 같은 BC3 블록 안이지만 논리 셀 밖인 픽셀은 현행 타깃의 디코딩 값을 요청값으로 유지한다.
6. 선택하지 않은 BC3 블록, 다른 G1T 텍스처, 중첩 LINK 슬롯, 바깥 LINK 엔트리는 바이트 단위로 보존한다.
7. 디코딩 왕복 뒤 선택 블록 밖 픽셀이 현행 타깃과 동일한지 검사한다.

이 단계는 결과를 저장소 `tmp` 아래에만 만들며 v0.94 패처 릴리스 트리와 Steam 설치에는 쓰지 않는다.

## 실행

```powershell
$py = 'tmp/navigation_wheel_layered_rebuild_v1/.venv/Scripts/python.exe'

& $py workstreams/navigation_wheel_binary_integration_v1/build_navigation_wheel_binary_integration_v1.py build `
  --output-root tmp/navigation_wheel_binary_integration_v1/run_001

& $py workstreams/navigation_wheel_binary_integration_v1/build_navigation_wheel_binary_integration_v1.py verify `
  --candidate-root tmp/navigation_wheel_binary_integration_v1/run_001
```

출력은 네 후보 아카이브, 원하는 PNG 대 실제 BC3 디코딩 접촉 시트 12개, `verification.v1.json`이다.
