# 이슈 109 혼인 대사 정합화 v1

이 작업은 v0.92.0 최종 `msggame.bin` 벡터에서 동일한 일본어 원문 레코드를
Base와 PK 양쪽에 같은 한국어 레코드로 정합화한다. Steam에는 직접 쓰지 않고,
릴리스 리소스 명세에 겹쳐 넣을 두 파일만 별도 후보 루트에 생성한다.

- Base: `MSG/JP/msggame.bin` `(6, 3577)`
- PK: `MSG_PK/JP/msggame.bin` `(6, 3584)`
- 동적 토큰 순서: 관계·역할 `023C`, 대상 인물 `014301000000`
- 한국어 literal 0: `의 자격으로 `
- 한국어 literal 1: `에게 힘이 되어 줄 준비는\n되어 있겠지`
- 최종 Base·PK 레코드 SHA-256:
  `7BC4BDE66733FAC24ECC92C8D94A7D37342BF48742DE471CEB260E3CE533A325`

SC 번역 원본 좌표 `(6, 3582)`는 최신 PK JP 기반에서 `(6, 3584)`로 재배치된다.
같은 예전 번역문이 들어 있던 SC `(6, 3588)`은 일본어 의미와 제어 구조가 다른
PK `(6, 3590)` 계열이므로 이 수정 범위에 포함하지 않는다.

```powershell
python workstreams/issue109_marriage_support_v1/build_issue109_marriage_support_v1.py `
  --input-root I:/Workspaces/NOBU16-Korean/scratch/v0920-resource-input-20260808-02/target `
  --output-root I:/Workspaces/NOBU16-Korean/scratch/issue109-marriage-support-v1-candidate-01

python -m unittest workstreams/issue109_marriage_support_v1/test_issue109_marriage_support_v1.py
```

빌더는 입력 packed/raw 해시, 대상 레코드와 literal, 동적 토큰 바이트, 변경
레코드 집합, 최종 packed/raw/record 해시를 모두 고정한다. 출력 검증 JSON에는
시각이나 절대 경로를 넣지 않으므로 같은 입력의 두 빌드는 파일과 검증 보고서가
모두 바이트 단위로 동일하다.
