# PK `msgdata` 직접 번역 배치 04

현재 진행률에 등록된 배치 03까지의 소유권을 제외하고 `MSG_PK/SC/msgdata.bin`의 다음 미번역 표시 문자열을 다시 분류했다. ID `25006~27101` 고정 접두부에서 실제 의미가 있는 다음 300개를 직접 한국어로 번역했다. 정책·특성 효과, 합전 효과와 표제, 업적 조건, 명소명, 봉행·마음가짐·가문 전승 명칭이 포함된다.

같은 접두부의 나머지 642개는 표시 번역 대상이 아닌 구조 항목이다. `dummy` 자리표시자 32개, 발음·검색용 로마자 키 609개, 형식·제어 전용 토큰 1개를 별도 해시로 고정했다. 선택 300개와 구조 제외 642개가 고정 접두부 942개를 빠짐없이 설명한다.

공식 PK JP/SC/EN/TC를 같은 ID로 대조해 번역했으며 공개 파일에는 공식 원문이나 완성 리소스를 넣지 않는다. 각 오버레이 행은 원본 SC UTF-16LE 문자열 해시를 고정하고 printf, ESC, PUA, 제어문자, 줄바꿈, 가장자리 공백을 보존한다. 중복 ID, 기존 오버레이 소유권 침범, 대상 밖 ID, CJK·가나 잔존, NUL을 모두 실패 처리한다. 화면 검수 전이므로 300개 모두 `runtime_reviewed=false`다.

현재 설치본은 통합 패치 상태라 생성 시 SHA가 고정된 원본 SC `msgdata.bin`을 `--stock-pk-sc`로 지정한다.

```powershell
python -B workstreams/msgdata_pk_native_batch04/build_msgdata_pk_native_batch04.py --stock-pk-sc <원본_MSG_PK_SC_msgdata.bin> --out-root workstreams/msgdata_pk_native_batch04
python -B -m unittest workstreams.msgdata_pk_native_batch04.tests.test_msgdata_pk_native_batch04 -v
```

결정적 공개 산출물 SHA-256:

- 오버레이: `9AA64137BF915FF732CB1DD4C625F156E9784FD65F3779CE381F7DBF4D9E2B45`
- 정렬 증거: `F27F7D66C76189367C430535654E165DEADCBA70831FE889423E887176B05225`
- 검토 인덱스: `6AD360B7695C119DFDD47C942B70A72535084DBF2D3E1CD48A732D852437310F`
- 생성 검증: `97D61846C5298350440438679490A8D26303ADE4EDF6B3E6FE71BFD3C61CE572`
