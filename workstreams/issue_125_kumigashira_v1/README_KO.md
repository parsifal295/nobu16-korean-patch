# 이슈 125 `組頭` 신분명 통일

## 조사 결과

가신 신분 체계의 최하위 등급인 일본어 `組頭`가 한국어 리소스에서 `조장`과
`조두`로 나뉘어 있었다. 계층도 이미지와 공용 데이터는 이미 `조장`을 사용하지만,
Base·PK 튜토리얼 대사와 PK UI 일부는 `조두`를 사용해 같은 화면 안에서도 명칭이
달라졌다.

현재 v0.95 후보와 Steam 일본어판 1.1.7 원문을 좌표별로 대조한 결과, 게임 신분을
뜻하는 `조두`는 다음 35곳이다.

- Base `MSG/JP/msggame.bin`: 13곳
- PK `MSG_PK/JP/msggame.bin`: 19곳
- PK `MSG_PK/JP/msgui.bin`: 3곳

35곳의 같은 좌표에서 일본어 원문은 모두 `組頭`다. 최종 한국어 표기는 사용자가
지시한 `조장`으로 통일한다.

## 제외 범위

`MSG/JP/strdata.bin`과 `MSG_PK/JP/msgbre.bin`에 남은 `근습조두`, `칠수조 조두`는
게임의 신분 등급이 아니라 인물 열전에서 역사적 편제를 설명하는 표현이다. 이번
대사·UI 신분명 통일 범위에는 포함하지 않는다.

## 안전 조건

- 현재 v0.95 입력 세 파일과 순정 일본어 세 파일의 크기·SHA-256을 고정한다.
- `조두` 좌표와 일본어 `組頭` 좌표가 Base 13곳, PK 19곳, UI 3곳에서 정확히
  일치해야만 빌드한다.
- 대상 밖 대사와 UI 문자열은 바꾸지 않는다.
- `조두`와 `조장`은 모두 한 음절을 한 음절로 바꾸므로 UTF-16 길이, 개행과 제어
  구조가 유지되는지 확인한다.
- 빌더는 Steam 설치 폴더에 직접 출력하지 않는다.

## 실행

```powershell
python workstreams/issue_125_kumigashira_v1/build_issue_125_kumigashira_v1.py `
  --input-root <pinned input root> `
  --jp-root <Steam 1.1.7 Japanese stock root> `
  --output-root <empty scratch output>

python -m unittest workstreams/issue_125_kumigashira_v1/test_issue_125_kumigashira_v1.py
```

## 반영 상태 — 2026-09-05

v0.95 글꼴 A/B에 통합하고 승인된 Steam 설치본에 적용했다. 최종 파일의 대상
35곳을 다시 읽어 `조장` 표기를 확인했다. 인물 열전의 제외 용어는 유지했다.
[최종 통합 검증 기록](../v095_image_completion_v1/validation.v1.json)에 파일별
크기와 해시를 남겼다. 최종 설치본의 실게임 화면 검증은 수행하지 않았다.
