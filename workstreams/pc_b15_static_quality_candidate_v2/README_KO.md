# PC B15 정적 품질 private candidate v2

## 범위

W45 PC KO preimage을 고정한 private 후보이다. B15에서 승인된 10개 리터럴만 바꿨다. Steam 적용, Git 변경, 커밋, 푸시, 릴리스, 네트워크 작업은 하지 않았다.

후보 출력은 다음 private 경로에만 있다.

- F:/Games/NOBU16/KR_PATCH_RELEASE_V0116/tmp/pc_b15_static_quality_candidate_v2/candidate/MSG/JP/msggame.bin
- F:/Games/NOBU16/KR_PATCH_RELEASE_V0116/tmp/pc_b15_static_quality_candidate_v2/candidate/MSG_PK/JP/msggame.bin

## 재현 명령

worktree 루트에서 아래 명령을 실행한다. output root는 worktree의 tmp 하위로만 제한된다.

    py -3 -B workstreams/pc_b15_static_quality_candidate_v2/build_pc_b15_static_quality_candidate_v2.py build
    py -3 -B workstreams/pc_b15_static_quality_candidate_v2/build_pc_b15_static_quality_candidate_v2.py verify-private
    py -3 -B workstreams/pc_b15_static_quality_candidate_v2/build_pc_b15_static_quality_candidate_v2.py diff-check
    py -3 -B workstreams/pc_b15_static_quality_candidate_v2/test_pc_b15_static_quality_candidate_v2.py

## W45 PC preimage 및 출력 프로필 pin

| 파일 | W45 PC KO preimage packed SHA-256 | preimage raw SHA-256 | wrapper prefix | packed / raw 바이트 |
| --- | --- | --- | --- | --- |
| Base MSG | F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB | 27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D | 0101F6A1FB7F0000 | 1,504,410 / 1,498,508 |
| PK MSG | 0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092 | 737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E | 0101442672020000 | 1,806,538 / 1,799,456 |

| 파일 | candidate packed SHA-256 | candidate raw SHA-256 | packed / raw 바이트 | wrapper compressed size |
| --- | --- | --- | --- | --- |
| Base MSG | F8D6B86536654D0E0FE8C721F8068964C8F908759CC372E5DDBAB4D8489ACB04 | F23B2869E9D2526B5C49D809C7489E6B954FC285DBC2E2EBFE91A2E528F5B440 | 1,504,410 / 1,498,508 | 1,504,386 |
| PK MSG | 712798DA7ACF7182340BC996359F45F324FF4CE41D41699420819406F1E95EBC | 03E505277F9CB4D8AE15715742802A4DC6BA782BE410ED7E404E3464D08C6962 | 1,806,538 / 1,799,456 | 1,806,514 |

두 출력은 각 preimage의 wrapper prefix와 압축 프로필을 그대로 사용했다. 원본과 candidate의 packed·raw 크기 및 wrapper compressed size도 각각 같다.

## 승인된 변경 10개

좌표는 `block:record:literal`이다. 모든 변경은 같은 길이의 UTF-16LE 문자열 치환이며, LF 수와 리터럴 마커·불투명 제어 바이트는 보존했다.

| 파일 | 좌표 | preimage | candidate | 건수 |
| --- | --- | --- | --- | ---: |
| Base | `15:1875:1`, `15:1890:1` | `↵마술 훈련을 실시해↵병사를 강화하고` | `↵승마 훈련을 실시해↵병사를 강화하고` | 2 |
| Base | `15:1460:0` | `공성이란 성장의 마음을 치는 것↵` | `공성이란 성주의 마음을 치는 것↵` | 1 |
| PK | `15:1475:0` | `공성이란 성장의 마음을 치는 것↵` | `공성이란 성주의 마음을 치는 것↵` | 1 |
| Base | `15:2030:1`, `15:2114:1` | `을 용서해 주십시오` | `을 허락해 주십시오` | 2 |
| Base | `15:2131:1` | `을 용서하시오` | `을 허락하시오` | 1 |
| PK | `15:2060:1`, `15:2144:1` | `을 용서해 주십시오` | `을 허락해 주십시오` | 2 |
| PK | `15:2161:1` | `을 용서하시오` | `을 허락하시오` | 1 |

## 명시적 Hold

다음은 후보에 넣지 않았고 candidate에서 preimage와 완전히 같다.

- Base `15:1434:0-1`: 위협·자 이음부
- Base `15:2254:0-1`, PK `15:2285:0-1`: 헌언의 용서

이 항목들은 중간 런타임 macro 결합을 확인하기 전까지 Hold다.

## 독립 검증

생성 후 candidate 파일을 새로 읽어 다음을 모두 통과했다.

- preimage SHA-256이 위 W45 pin과 일치한다.
- candidate packed SHA-256이 위 출력 hash와 일치한다.
- candidate를 해제·파싱한 뒤 raw를 재구축하면 byte-exact다.
- 모든 블록의 offset, size, 레코드 수, 레코드 relative offset과 data 길이가 preimage와 같다.
- Base는 정확히 6개 레코드와 6개 리터럴, PK는 정확히 4개 레코드와 4개 리터럴만 달라졌다.
- 승인되지 않은 모든 레코드의 `record.data`는 preimage와 byte-identical다.
- 리터럴 마커를 제거한 제어 스켈레톤은 모든 레코드에서 preimage와 동일하다.
- 전 리터럴의 LF 개수는 preimage와 동일하다.
- raw 바이트 차이는 target record 범위 안에만 있다: Base 22바이트, PK 14바이트. target 밖 raw 차이는 0바이트다.
- Hold 좌표의 리터럴은 preimage와 동일함을 별도 확인했다.

KO와 JP의 기존 B15 literal topology 차이는 이 후보 검증의 통과 조건으로 사용하지 않았다. 검증 기준은 W45 PC KO preimage 대비 승인된 10개 literal 이외의 보존이다.
