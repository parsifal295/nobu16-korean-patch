# Steam JP PK 비로고 메뉴 라벨 감사 v1

이 workstream은 Steam 일본어판 1.1.7의 다음 **비로고** 이미지 묶음만 읽기 전용으로
조사한다.

```
RES_JP_PK/res_lang_pk.bin /18
  └─ 43개의 512×128, PC BC3(0x5B) 단일 텍스처 슬롯
```

`/18`은 PK의 혼합 메뉴·보상·BGM·콘텐츠 라벨 후보군이다. 제품 로고, 타이틀 화면,
브랜드 아트, 역사 에피소드 카드에는 손대지 않는다. 특히 `/3`, `/24`는 이
workstream의 입력·출력·후보 범위에 포함되지 않으며, `RES_JP/res_lang.bin /4` 및
`RES_JP_PK/res_lang_pk.bin /21`의 타이틀 카드도 제외한다.

## 현재 판정

- Switch 공개 v2.x 배포본에는 `RES_JP_PK/res_lang_pk.bin`이 없으므로 `/18`의
  한국어 픽셀을 Switch에서 직접 이식할 수 없다.
- PC JP/EN/SC/TC의 같은 `/18`을 대조해 **PC-native 구조와 언어별 텍스트 위치만**
  확인한다. 언어 리소스·G1T·BC3·PNG는 저장소에 넣지 않는다.
- 슬롯별 실제 화면 소비, 한국어 문구, 텍스트 전용 안전 사각형이 아직 확정되지
  않았으므로 후보 생성은 명시적으로 비활성화되어 있다.

따라서 이 workstream은 다음 구현 묶음을 식별하는 감사 도구이며, 게임 적용 도구가
아니다. `/5` 시스템 버튼처럼 배경 보존 증거가 없는 영역을 억지로 덮어쓰지 않는다.

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'

& $py -B workstreams\steam_jp_pk_menu_labels_audit_v1\build_steam_jp_pk_menu_labels_audit_v1.py inspect `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16 `
  --output-root tmp\steam_jp_pk_menu_labels_audit_v1\run_a `
  --preview

& $py -B workstreams\steam_jp_pk_menu_labels_audit_v1\build_steam_jp_pk_menu_labels_audit_v1.py verify `
  --output-root tmp\steam_jp_pk_menu_labels_audit_v1\run_a

& $py -B -m unittest workstreams\steam_jp_pk_menu_labels_audit_v1\test_steam_jp_pk_menu_labels_audit_v1.py -v
```

`inspect`는 `tmp/` 아래에만 보고서와 private PNG contact sheet을 만든다. `build`
명령은 의도적으로 실패한다. 게임 설치, Git, GitHub, 릴리즈를 쓰는 코드가 없다.

## 후보로 올리기 전 게이트

1. 43개 슬롯 각각을 실제 PK 화면과 1:1로 매핑한다.
2. 화면 성격이 로고·타이틀·브랜드 아트가 아닌 UI 라벨임을 확정한다.
3. 한국어 문구 및 PC JP 텍스트 전용의 4×4 BC3 block-aligned 사각형을 확정한다.
4. PC JP 원본 `/18`의 선택 슬롯만 다시 조립하고, 나머지 outer/inner/G1T 바이트를
   보존하는 private 후보·재추출·화면 QA를 통과한다.

그 전에는 이 묶음을 배포/적용 대상으로 취급하지 않는다.
