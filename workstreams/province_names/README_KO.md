# 옛 지방명 72개 한국어 오버레이 v0.2

`MSG_PK/SC/msgdata.bin`의 ID `13975..14046`은 에조부터 쓰시마까지 옛 지방명
72개가 SC·EN·JP에서 같은 순서로 정렬된 연속 블록이다. v0.2는 합법적으로 보유한
세 언어의 순정 리소스를 동일 ID로 전수 대조하고, 72개 모두 `reviewed`로 확정한
source-free 공개 오버레이다. 게임 파일이나 설치기를 직접 수정하지 않는다.

v0.1은 초벌 번역의 재현 가능한 merge base로 그대로 보존한다. 전수 검수 결과
잘못된 ID 대응이나 수정할 표기가 없어, v0.1 대비 한글 문자열 변경 수는 `0`이다.

## 진행 상태

| 범위 | 검수 완료 / 전체 | 상태 |
|---|---:|---|
| ID `13975..14046` | `72 / 72` | 전수 검수 완료 |

## 표기 결정

- 성·지명과 같은 지리 명칭의 일본어 `つ`는 `쓰`로 적는다. 따라서 `무쓰`,
  `시모쓰케`, `셋쓰`, `사쓰마`, `쓰시마`를 유지한다.
- 촉음과 결합한 `っちゅう`는 `엣추`, `빗추`로 적는다.
- 일본어 장음은 별도 모음을 덧붙이지 않는다. `고즈케`, `도토미`, `오미`,
  `스오`, `호키`, `휴가`, `오스미`가 이 원칙을 따른다.
- `기이`는 장음 부호가 아니라 일본어 `きい`의 두 모음이므로 줄이지 않는다.
- 서로 다른 지방인 ID `13986`과 `14034`는 모두 통용 표기 `아와`가 맞다.
- 장수 개인명의 `츠` 표기 정책과 지명 정책은 서로 분리한다.

## 공개 파일

| 파일 | 내용 |
|---|---|
| `public/province_names_ko_13975_14046.v0.1.json` | 보존된 72개 초벌 merge base |
| `public/province_names_ko_13975_14046.v0.2.json` | 72개 `reviewed` 공개 오버레이 |
| `validation.v0.2.json` | 순정 리소스 핀·ID 블록 해시·검수 결과 |
| `build_province_names_v02.py` | v0.1과 순정 SC·EN·JP를 검증해 v0.2를 만드는 결정적 builder/merge 도구 |
| `tests/test_province_names.py` | 범위·정책·source-free·재현성 검증 |

공개 JSON에는 정식판 SC·JP·EN 문자열과 완성 `msgdata.bin`을 넣지 않는다.
validation에는 원문 대신 SHA-256, 크기, ID 범위와 개수만 기록한다. 최종 패치에서는
장수명·성 이름·지방명 오버레이를 같은 순정 SC `msgdata.bin`에 ID 오름차순으로
병합해야 한다.

## 로컬 재생성

SC 입력은 한글 패치가 적용된 현재 파일이 아니라 고정 SHA-256과 일치하는 순정
백업이어야 한다. 출력에는 원문이 기록되지 않는다.

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Province = 'workstreams\province_names'

& $Python -B "$Province\build_province_names_v02.py" `
  --sc '<순정 SC MSG_PK\SC\msgdata.bin 또는 순정 백업>' `
  --en '<순정 EN MSG_PK\EN\msgdata.bin>' `
  --jp '<순정 JP MSG_PK\JP\msgdata.bin>' `
  --output-root $Province
```

현재 공개 v0.2 산출물 SHA-256은
`2EF65EBDEF21521857477EA180E7FBC7AB92F1626FC69D06BD6262E97BFDBDF5`다.

## 검증

```powershell
python -B -m unittest workstreams/province_names/tests/test_province_names.py
```

테스트는 v0.1 보존, 72개 연속 ID, 모든 엔트리의 `reviewed` 상태, 공개 원문 부재,
SC·EN·JP 블록 핀, 결정적 v0.1→v0.2 병합, 주요 표기 결정을 확인한다.
