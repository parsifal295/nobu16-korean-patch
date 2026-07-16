# Steam JP 전각·가운데점 정규화 v1

Steam PK 1.1.7의 일본어(`JP`) 경로 전용, 오프라인 텍스트 정규화 작업이다. 게임 설치 폴더, EXE, 폰트 파일은 이 작업에서 쓰지 않는다.

## 적용 근거와 범위

- 입력: `v0.9.0` 14파일 패치 ZIP (SHA-256은 공개 메타데이터에 고정)
- 근거: Switch 공개 배포본 `v2.2 → v2.3`의 고정 SHA-256 아카이브 차이
- 방식: Switch 좌표 정렬 차이에서 확인한 **문자 맵**만 도출한 뒤, 현재 Steam v0.9의 모든 한글 셀에 대해 좌표별 원문 UTF-16LE SHA-256이 맞는 경우에만 적용한다.
- 전각: Switch 증거에 실제로 있는 전각 숫자·괄호·문장부호·전각 공백의 ASCII 대응만 대상이다. 범용 Unicode/NFKC 변환은 하지 않는다.
- 가운데점: 실제 증거 방향은 `U+00B7 (·) → U+30FB`이지만, 현재 JP base G1N의 필수 table에 U+30FB 매핑이 없어 이번 pass에서는 **보류**한다. 영향 좌표·해시는 공개 메타데이터에 남기고, 기존 `·` 표기는 유지한다.

## 보존 규칙

ESC 제어코드, printf 토큰, 중괄호/꺾쇠/대괄호 태그, 기타 제어문자, PUA, CR/LF, 선행·후행 공백은 바꾸지 않는다. 따라서 이 작업은 강제 줄바꿈 제거 작업과 별도로 합성할 수 있다.

## 폰트 영향

새로 요구되는 대상 글리프가 모든 활성 JP G1N 계층에 매핑되어 있는지 검사한다. 성공 시에도 폰트 payload·전진폭은 변경하지 않는다.

## 실행

```powershell
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B .\build_steam_jp_fullwidth_normalization_v1.py emit-public
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B .\build_steam_jp_fullwidth_normalization_v1.py verify
```

`build`와 `restore`는 `KR_PATCH_WORK\tmp` 아래의 새 ZIP만 만들 수 있다. 결과는 좌표별 역연산과 after-hash 검사를 거쳐 정확히 v0.9 입력으로 복원되는지 검증한다. 이 workstream에는 게임 리소스나 배포 ZIP을 넣지 않는다.
