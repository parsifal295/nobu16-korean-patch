# Steam JP `msgev` ID 10564 3줄 압축 레이아웃

이 작업선은 Steam JP PK `MSG_PK/JP/msgev.bin`의 이벤트 대사 ID `10564` 한 건만 고친다.
기존 한국어는 일본어용 줄바꿈을 그대로 가져와 `따라야 / 한다고`, `아첨하는 / 역신으로`가 갈라졌다.

원문을 단순히 다시 줄바꿈해도 실제 48px 글꼴 기준 총 폭이 3,696px라 3줄 화면 폭에 들어가지 않는다. 따라서 이 항목만 의미를 유지해 압축하고, 기존 색상 ESC 토큰 5쌍과 줄 수 3줄은 그대로 유지한다.

- 대상: `MSG_PK/JP/msgev.bin` / ID `10564`
- 글꼴: `RES_JP/res_lang.bin` / G1N entry 6 / table 0
- 안전 줄폭: 912px
- 결과 줄폭: 816px / 888px / 768px
- 허용 입력: 현재 게임 상태와 v0.10.0 배포본의 알려진 `msgev.bin` 두 preimage

빌더는 게임 설치 파일과 글꼴을 읽기만 하며, 후보는 `KR_PATCH_WORK/tmp` 아래에만 만든다. 다른 ID, 실행 파일, 글꼴 리소스는 변경하지 않는다.

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_10564_compact_layout_v1\build_steam_jp_msgev_10564_compact_layout_v1.py verify

& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_10564_compact_layout_v1\build_steam_jp_msgev_10564_compact_layout_v1.py build
```

자동 일괄 줄바꿈 도구가 아니다. 이후 문제 대사는 같은 방식으로 ID별 화면 검수 후 별도 layout overlay에 추가한다.
