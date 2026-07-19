# PC B14 static-quality private candidate v1

## 범위

PC W45 Base/PK 한국어 msggame.bin과 exact pristine PC 일본어 파일만 입력으로 사용한다. Switch/SC 자료는 열거나 검색하지 않는다.

대상은 정확히 10개 literal과 10개 record다.

| 리소스 | 좌표 | 변경 |
| --- | --- | --- |
| Base MSG/JP/msggame.bin | 14:32:3, 14:113:1, 14:117:3 | 조장 계열을 조두로 통일. 모음말 뒤 조사는 으로서에서 로서로 함께 보정. |
| PK MSG_PK/JP/msggame.bin | 14:48:3, 14:51:1 | 조장 계열을 조두로 통일. 필요한 조사도 함께 보정. |
| PK MSG_PK/JP/msggame.bin | 14:156:1 | 시대장 → 사무라이대장 |
| PK MSG_PK/JP/msggame.bin | 14:157:1 | 족경대장 → 아시가루대장 |
| PK MSG_PK/JP/msggame.bin | 14:225:1 | 원문에 근거 없는 공훈을 얻고 제거 |
| PK MSG_PK/JP/msggame.bin | 14:226:1 | 별명 계열을 별호 계열로 통일하고 을/는/이/과 조사를 맞춤 |
| PK MSG_PK/JP/msggame.bin | 14:227:1 | 이명 계열을 별호 계열로 통일하고 조사를 맞춤 |

제외 대상은 PK 14:69:0, 14:163:1 (国衆取込 명칭 선택 보류)와 PK 14:140:3 (시간 조건 뉘앙스 Hold)이다.

## 고정 profile

| 리소스 | W45 KO packed / raw SHA-256 | candidate packed / raw SHA-256 |
| --- | --- | --- |
| Base | F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB / 27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D | 1026BA0B43F7CFC172F49D2FB48FF9AC4B3B2511087BF0A2791BD82128B62675 / 86D3D55F53365AE0AA6A75C76955CCC4ABE9C2C1B9922DB0202B3314C45AF69D |
| PK | 0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092 / 737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E | 268E70CC0040A597E561E57972D7C68AD87329AFB3DBE4D36B62CB42BDEF815F / 129BF95062EEE0251B9A5A04922AAAA20FF275FA99AC2D5B1CA6A4543DF7EA29 |

Pristine PC JP packed hashes are Base EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4 and PK 31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210.

## 검증 보증

- 각 target은 exact W45 KO UTF-16LE preimage hash와 pristine PC JP literal hash를 고정한다.
- whole archive에서 위 10 record 이외의 record.data는 byte-identical이어야 한다.
- 대상 record도 literal UTF-16 payload 이외의 opaque bytecode/control skeleton은 동일해야 한다.
- 수동 LF, ESC/runtime/printf/제어문자 signature를 보존한다.
- parser raw round-trip, packed round-trip, output profile, private file set을 검증한다.

## 실행

    py -3 -B .\workstreams\pc_b14_static_quality_candidate_v1\test_pc_b14_static_quality_candidate_v1.py -v
    py -3 -B .\workstreams\pc_b14_static_quality_candidate_v1\build_pc_b14_static_quality_candidate_v1.py build
    py -3 -B .\workstreams\pc_b14_static_quality_candidate_v1\build_pc_b14_static_quality_candidate_v1.py verify-private
    py -3 -B .\workstreams\pc_b14_static_quality_candidate_v1\build_pc_b14_static_quality_candidate_v1.py diff-check

출력은 private tmp/pc_b14_static_quality_candidate_v1/candidate 아래에만 만든다.

- MSG/JP/msggame.bin
- MSG_PK/JP/msggame.bin
- audit.v1.json
- candidate_manifest.v1.json

Steam 게임 파일 적용, transaction, Git, 네트워크, commit, push, release 기능은 구현하지 않는다.
