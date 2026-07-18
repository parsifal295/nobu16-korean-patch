# PC Block 17 static quality candidate v1

이 workstream은 W45 Steam PC 한국어 MSGGAME을 읽어 **PK Block 17의 정적 literal 31개만** private candidate로 만드는 빌더다. 게임 설치 파일, Git, 네트워크, 릴리스에는 쓰지 않는다.

## 입력 고정

- Base Korean W45: `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB`
- Base PC JP: `EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4`
- PK Korean W45: `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092`
- PK PC JP: `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210`

Base Block 17은 33 records/66 literal slots, PK Block 17은 1,159 records/2,256 literal slots여야 한다. 후보 출력은 `tmp/pc_b17_static_quality_candidate_v1/candidate/MSG_PK/JP/msggame.bin`에만 생긴다.

고정된 후보 출력은 packed `B03D4EFBFC61BD1BCCFC5472052805D79CC215996394211D23DB197B3CC4D9C9` (1,806,510 bytes), raw `66B41C98CDED3F5F7091D18AE9FA89CC3F70457142E07EDE2E35FF6426352DB1` (1,799,428 bytes)다.

## 정확한 적용 범위

아래 31개 record/31개 literal만 적용한다.

`17:8:0, 17:12:1, 17:27:0, 17:54:0, 17:80:3, 17:104:1, 17:400:1, 17:417:3, 17:504:0, 17:510:2, 17:561:0, 17:562:0, 17:563:0, 17:637:0, 17:766:0, 17:852:0, 17:871:0, 17:872:1, 17:894:0, 17:950:0, 17:951:0, 17:952:0, 17:1001:0, 17:1051:0, 17:1064:1, 17:1065:0, 17:1073:0, 17:1120:0, 17:1132:0, 17:1137:0, 17:1151:0`

Root 확정 문구는 다음과 같다.

- `17:510:2`: `으로 돌아서`
- `17:872:1`: `는 아군이다. 피아를 혼동하지 마라!`

모든 적용 literal은 기존 수동 LF 개수를 유지한다. 해당 레코드의 literal 밖 byte, marker, 런타임 placeholder, 제어 바이트는 byte-for-byte 불변이어야 한다.

## hold

`17:920:0`, `17:920:1`은 런타임 이름 뒤 조사와 명령이 조합되는 대사다. 정적 후보에서는 반드시 제외한다. 이 두 slot은 후보 출력에서 원본과 동일해야 한다.

명명 표준화와 `退き口`의 UI 고유명 여부도 이 후보의 범위 밖이다.

## 검증

`derive-pins`는 출력 pin을 읽기 전용으로 산출한다. pin을 빌더에 고정한 뒤 아래를 실행한다.

```powershell
py -3 -B .\workstreams\pc_b17_static_quality_candidate_v1\build_pc_b17_static_quality_candidate_v1.py build
py -3 -B -m unittest .\workstreams\pc_b17_static_quality_candidate_v1\test_pc_b17_static_quality_candidate_v1.py -v
py -3 -B .\workstreams\pc_b17_static_quality_candidate_v1\build_pc_b17_static_quality_candidate_v1.py verify-private
py -3 -B .\workstreams\pc_b17_static_quality_candidate_v1\build_pc_b17_static_quality_candidate_v1.py diff-check
```

테스트는 PC JP/KO 4개 입력 해시, 31개 정확한 변경 좌표/문구, 모든 비대상 literal과 opaque control bytes, raw parser 및 packed LZ4 roundtrip을 검증한다. 실게임 및 UI 줄바꿈 QA는 별도 단계다.
