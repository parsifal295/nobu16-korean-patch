# 성 이름 단일 광폭 글리프 실험

전략 지도에서 SC 성 이름이 세로로 쌓이는 문제를 파일만으로 우회할 수 있는지 확인하는 공개 소스 작업대다. 메시지 ID `9168`을 예약 글리프 `U+D792` 하나로 바꾸고, 그 글리프 픽셀 안에 `오다와라성`을 가로로 합성한다. 구조 감사는 통과했지만 지도 화면 런타임 판정은 아직 완료되지 않았으므로 배포 가능한 패치가 아니다.

## 공개 범위

- PowerShell/Python 빌드·감사·적용/복원 소스
- Noto KR에서 생성한 4bpp 글리프 픽셀과 PNG 미리보기
- ID와 예약 코드포인트의 대응표
- 완성 후보의 크기·SHA-256·구조 감사 결과만 담은 원문 제거 메타데이터

글리프 픽셀의 원본 폰트와 OFL 전문은 `vendor/noto/`에 고정되어 있고, `raster/raster_request.json`에 폰트 파일 SHA-256과 래스터 설정을 기록한다.

다음 항목은 저작권이 있는 게임 데이터가 포함되므로 Git과 배포본에서 제외한다.

- 완성 `msgdata.bin`, `res_lang.bin`
- 원본 또는 수정 G1N, 압축 해제 메시지 표
- SC 원문 문자열과 원문 카탈로그
- `private/` 아래에서 로컬로 생성되는 모든 후보와 중간 파일

## 재현 순서

1. 정품 설치 파일과 Python 3 경로를 준비한다. 모든 stock 입력은 스크립트의 고정 SHA-256을 통과해야 한다.
2. `Build-SingleGlyphCastleProbe.ps1 -Python <python.exe>`로 stock wrapper에서 필요한 입력을 `private/input/`에 추출하고, `private/candidate/` 아래에 원시 후보를 만든다.
3. `Build-PrivateWrappedCandidate.ps1 -Python <python.exe>`로 두 게임용 wrapper를 `private/wrapper_candidate/` 아래에 만든다.
4. `Audit-WrappedCandidate.py`로 변경 ID, LINK 엔트리, G1N 추가 레코드와 보존 영역을 다시 검증한다.
5. `Invoke-WideCastleNameOnlyProbe.ps1 -Action Status`로 상태를 확인한 뒤 필요할 때만 `Apply`한다. 게임 실행은 사용자가 직접 하며 스크립트가 실행하지 않는다. 시험 직후 `Restore`로 고정 해시의 stock 파일을 복원한다.

`Sanitize-PublicMetadata.ps1`은 로컬 시험 메타데이터에서 `source_sc`, `before` 계열 필드와 절대 경로를 제거해 `metadata/`의 공개판을 다시 만든다. `Audit-PublicWorkstream.ps1`은 CJK 원문 문자, 상용 리소스 magic, 파일 크기와 공개 픽셀 해시를 검사한다.

## 안전 전제

이 작업대는 디스크의 두 리소스 파일만 대상으로 한다. 프로세스 메모리 접근, DLL 주입, 후킹, 실행 파일 수정, 레지스트리 변경, 게임 실행 기능은 두지 않는다. 적용기는 stock/probe 해시 게이트, 게임 프로세스 검사, 검증 백업, 작업 잠금, journal, 같은 볼륨의 원자 교체와 실패 시 자동 복원을 사용한다.

성공 판정은 지도에서 합성 글리프가 가로로 보이고 잘림이나 회전이 없으며, 별도로 붙는 공용 접미사가 어떻게 배치되는지 스크린샷으로 확인하는 것이다. 실패하더라도 이 공개 소스와 감사 기록은 파일 전용 경로의 한계를 재현하는 증거로 남긴다.
