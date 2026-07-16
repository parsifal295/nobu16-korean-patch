# Steam JP PK msgev P1 기본 이벤트 재사용

`MSG_PK/JP/msgev.bin`의 활성 JP 잔여 P1-01 185건을 처리한다. 같은 JP
UTF-16LE 해시가 이미 검증된 기본 `ev_strdata` 한글 오버레이에 존재할 때만
그 한글을 재사용하고, 동일 원문이 없는 3건만 프로젝트 번역으로 보완한다.

빌더는 Wave09의 결정적 JP 기준본에서 사설 후보만 `tmp` 아래 생성한다.
Steam 설치본·릴리즈·GitHub와 원문 텍스트는 변경하거나 포함하지 않는다.

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\msgev_pk_base_ev_reuse_p1_v1\build_msgev_pk_base_ev_reuse_p1_v1.py verify
& $py -B -m unittest workstreams\msgev_pk_base_ev_reuse_p1_v1\test_msgev_pk_base_ev_reuse_p1_v1.py -v
```
