# PK `msgdata` 직접 번역 배치 05

배치 04의 소유 ID를 제외한 `MSG_PK/SC/msgdata.bin`의 다음 일반 비공백 문자열 300개를 직접 한국어로 번역했다. 고정 대상 범위는 ID `27102~28759`이며 정책명·정책 설명·효과 수치·공성 설비·회전명·칭호·진행 조건을 포함한다.

같은 고정 범위에서 화면 번역 대상이 아닌 로마자·음가 조회 키 1,297개는 구조 제외로 분리했다. 선택 ID는 기존 배치 01~04 및 다른 등록 오버레이와 겹치지 않는다. 같은 SC 원문이 반복되는 20개 그룹은 모두 동일한 한국어 번역을 사용한다.

공식 PK JP/SC/EN/TC를 같은 ID로 대조해 번역했으며 공개 파일에는 공식 원문이나 완성 리소스를 넣지 않는다. SC 원문 해시를 고정하고 printf 토큰, ESC, PUA, 제어문자, 줄바꿈, 앞뒤 공백을 보존한다. 중복 ID, 기존 소유 ID 침범, 대상 밖 ID, CJK·가나 잔존, NUL은 모두 실패 처리한다. 화면 검증 전이므로 300개 모두 `runtime_reviewed=false`다.

재생성과 검증:

```powershell
python -B workstreams/msgdata_pk_native_batch05/build_msgdata_pk_native_batch05.py --stock-pk-sc <원본_MSG_PK_SC_msgdata.bin> --out-root workstreams/msgdata_pk_native_batch05
python -B -m unittest workstreams.msgdata_pk_native_batch05.tests.test_msgdata_pk_native_batch05 -v
```

결정적 공개 산출물 SHA-256:

- 오버레이: `FF19DBE0D56CDB7C8ED1DE70F0BA0820C29F4D62FF1939BF77970983EB9564E5`
- 정렬 증거: `253E66FAC55E7DD49903E6DBB41073753F5C7C4AD2C530752C98B998BF5AAD34`
- 검토 인덱스: `6E10C6A0D3A27226190EC6D40F20C79FCBEA1C2FB67CC6181F762178622A74AB`
- 생성 검증: `0764FE0B3F784AFE32F19AD64A67B6A9056494DA0F9C5B01F7BA012CEA68B785`
