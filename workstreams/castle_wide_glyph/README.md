# 성 이름 단일 광폭 글리프 실험

전략 지도에서 간체중문 경로의 성 이름은 한글로 바꿔도 세로로 쌓인다. 이 작업 스트림은 이름 전체를 하나의 넓은 글리프에 넣었을 때 파일만으로 가로 표시에 가까운 결과를 얻을 수 있는지 검증한다. 메시지 단독, 폰트 단독, 결합 후보는 올바른 작업 디렉터리에서 모두 부팅을 통과했지만, 사용자가 세로 표시를 허용하고 번역을 우선하기로 결정하여 실제 지도 시각 판정은 보류했다. 현재 결과물은 연구용 진단 후보이며 배포용 패치가 아니다.

## A/B 진단 하네스

`Invoke-WideCastleNameOnlyProbe.ps1`은 아래 다섯 동작만 제공한다.

- `Status`: 두 설치 파일, 비공개 후보, 백업, 저널 상태를 읽기만 한다.
- `ApplyMessageOnly`: 시험 메시지만 적용하고 폰트는 정품으로 둔다.
- `ApplyFontOnly`: 메시지는 정품으로 두고 시험 폰트만 적용한다.
- `ApplyBoth`: 시험 메시지와 시험 폰트를 함께 적용한다.
- `Restore`: 두 파일을 검증된 정품 백업으로 되돌린다.

이 조합으로 공백이나 잘림이 메시지 라우팅 때문인지, 글리프 데이터 때문인지, 둘의 결합에서만 생기는지 분리할 수 있다. 스크립트는 게임을 실행하지 않으므로 각 조합 적용 후 게임 실행과 화면 확인은 사용자가 직접 한다.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Invoke-WideCastleNameOnlyProbe.ps1 -Action Status
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Invoke-WideCastleNameOnlyProbe.ps1 -Action ApplyMessageOnly
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Invoke-WideCastleNameOnlyProbe.ps1 -Action ApplyFontOnly
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Invoke-WideCastleNameOnlyProbe.ps1 -Action ApplyBoth
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Invoke-WideCastleNameOnlyProbe.ps1 -Action Restore
```

모든 동작은 실행 중인 `NOBU16*` 프로세스가 있으면 거부된다. 설치 파일은 고정된 두 경로와 정품/시험 SHA-256만 허용한다. 첫 변경 전에 두 정품 백업을 검증하며, 배타 잠금, 진행 저널, 같은 볼륨의 원자적 교체, 실패 시 역순 자동 복원을 사용한다. `Restore`는 비공개 시험 파일이 이미 지워졌어도 검증된 정품 백업만으로 완료할 수 있고, 실패 처리도 정품 상태로 수렴한다. 이전 작업이 중단된 저널이 남아도 두 설치 파일이 허용된 해시 중 하나일 때만 현재 조합을 새 트랜잭션의 시작점으로 삼는다. 알 수 없는 파일 해시나 저널 형식은 덮어쓰지 않는다.

## 비공개 입력과 공개 범위

완성된 `msgdata.bin`과 `res_lang.bin`은 상용 원본 데이터를 포함하므로 Git과 배포본에 넣지 않는다. 로컬 빌드 결과는 다음 무시 경로에 있어야 한다.

```text
private/wrapper_candidate/MSG_PK/SC/msgdata.bin
private/wrapper_candidate/RES_SC/res_lang.bin
```

공개 범위에는 빌드 및 감사 소스, Noto KR에서 만든 프로젝트 소유 글리프 픽셀, 미리보기, 해시와 구조 메타데이터만 포함한다. `Build-SingleGlyphCastleProbe.ps1`과 `Build-PrivateWrappedCandidate.ps1`이 로컬 정품 파일에서 비공개 후보를 재구성한다.

## 정적 검증

`Test-WideCastleABHarness.ps1`은 하네스를 실행하지 않고 PowerShell AST, 고정 동작, 두 대상 경로, 네 정품/시험 해시, 금지 명령, 원자 교체와 백업/저널 안전장치를 검사한다. 결과는 `metadata/wide_castle_ab_harness_static_audit.json`에 기록된다.

`Audit-PublicWorkstream.ps1`은 `private/`를 제외한 공개 트리에서 완전한 상용 리소스 형식, 허용하지 않은 바이너리, 원문 메타데이터, 비정상 크기를 검사한다.

실행 A/B와 순정 복원 결과는 `reports/wide_castle_ab_runtime_2026-07-14.md`에 기록한다.
