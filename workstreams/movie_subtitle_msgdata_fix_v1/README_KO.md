# 게임 내 동영상 자막 보정 v1

현행 Steam JP v0.90.0 한국어 `MSG_PK/JP/msgdata.bin` 위에 영화 자막 결함
8건만 적용하는 비배포 빌드 단계다.

수정 범위:

- 혼노지 영상의 빈 자막 1건 복구
- `다이코` 용어 통일
- `도요토미 은고`를 자연스러운 한국어로 수정
- `치도리가케`를 화면에서 이해 가능한 방책 설명으로 수정
- `육문전`의 저승길 노잣돈 비유가 자막만으로 드러나도록 수정
- 사나다·도쿠가와 관계의 `악연` 의미 복구
- `의의 장수` 문장 수정
- `誉田村(こんだむら)`를 `곤다무라`로 바로잡음

빌더는 v0.90.0 입력의 크기·packed/raw SHA-256·문자열 수와 각 수정 슬롯의
UTF-16LE 사전 해시를 검증한다. 결과물은 지정한 새 디렉터리에만 만들며 Steam
설치본을 쓰지 않는다.

```powershell
python -B workstreams\movie_subtitle_msgdata_fix_v1\build_movie_subtitle_msgdata_fix_v1.py `
  --input 'F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgdata.bin' `
  --output-root 'I:\Workspaces\NOBU16-Korean\repository\KR_PATCH_WORK\tmp\movie_subtitle_msgdata_fix_v1_20260729'
```

`verification.v1.json`은 영화 자막 구간 `17989..18240`의 252개 슬롯이 모두
채워졌는지, 일본어 가나와 기각된 용어가 남지 않았는지, 명시적 줄 수와 최대
줄 길이가 기존 1920×1080 실게임 검수 범위에 들어오는지 확인한다.

검증된 후보:

- packed 크기: `482,068`
- packed SHA-256:
  `4071B4CF9071318F1ED89502F8920E1290C7D8A71F3CB93EF4F7D8D766574210`
- 독립된 동일 입력 사본 두 개에서 재생성한 결과가 바이트 단위로 일치함
- 이미 보정된 후보를 입력하면 v0.90.0 입력 해시 검사에서 거부함
