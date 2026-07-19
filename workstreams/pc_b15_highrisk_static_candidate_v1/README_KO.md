# PC B15 highrisk 문법 private candidate v1

## 범위

W45 PC KO preimage을 직접 읽어 Base와 PK에서 각각 한 리터럴만 바꾸는 private 후보다. 기존 pc_b15_static_quality_candidate_v2는 읽거나 변경하지 않는다. Steam 적용, Git 변경, 커밋, 푸시, 릴리스, 네트워크 작업은 하지 않는다.

출력은 다음 private 경로에만 생성한다.

- F:/Games/NOBU16/KR_PATCH_RELEASE_V0116/tmp/pc_b15_highrisk_static_candidate_v1/candidate/MSG/JP/msggame.bin
- F:/Games/NOBU16/KR_PATCH_RELEASE_V0116/tmp/pc_b15_highrisk_static_candidate_v1/candidate/MSG_PK/JP/msggame.bin

## 승인된 변경

| 파일 | 좌표 | preimage | candidate |
| --- | --- | --- | --- |
| Base | 15:2348:0 | 우선 가신들이 건의를 제안할 수 있도록 / 공략할 세력을 정하고 | 우선 가신들이 건의할 수 있도록 / 공략할 세력을 정하고 |
| PK | 15:2379:0 | 우선 가신들이 건의를 제안할 수 있도록 / 공략할 세력을 정하고 | 우선 가신들이 건의할 수 있도록 / 공략할 세력을 정하고 |

한글 UTF-16LE 본문이 각 파일에서 8바이트 줄어든다. 이 때문에 B15 block size와 이후 block offset, raw·packed size가 각각 8바이트 줄어드는 것은 의도된 구조 변화다.

## 명시적 Hold

다음 B15 record는 파일별 모든 리터럴을 source와 candidate 사이에서 동일함을 검증하며 후보에 넣지 않는다.

- 15:2257
- 15:2258
- 15:2279

## W45 및 output profile pin

| 파일 | preimage packed / raw SHA-256 | wrapper prefix | preimage packed / raw 바이트 | candidate packed / raw SHA-256 | candidate packed / raw 바이트 |
| --- | --- | --- | --- | --- | --- |
| Base | F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB / 27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D | 0101F6A1FB7F0000 | 1,504,410 / 1,498,508 | B69C95ADC52B7261E409B49E7CE907A10049439C629473E6D6DEF31E59DB0952 / 35C566AF0E9F24A04E91D0CDBBD5C8057924BE5D40D1A958ACC5E49D0675F818 | 1,504,402 / 1,498,500 |
| PK | 0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092 / 737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E | 0101442672020000 | 1,806,538 / 1,799,456 | D1FFFD772CD35B14113ED18076F572284D2B372234396AC3B9F74ED31FE814F7 / 5D89EFA87DC51E29F91357B1B95C4D74B1CF7E1406024AC893917DA98EC30CD5 | 1,806,530 / 1,799,448 |

Base wrapper compressed size는 1,504,386에서 1,504,378로, PK는 1,806,514에서 1,806,506으로 변한다. wrapper prefix는 그대로다.

## 검증 계약

- W45 packed·raw preimage hash와 target preimage literal을 먼저 검사한다.
- candidate packed·raw hash, wrapper prefix, 출력 크기를 고정한다.
- target 이외 모든 record.data와 모든 비대상 리터럴은 byte/text-identical이어야 한다.
- target record의 literal marker와 불투명 제어 스켈레톤, LF 수, literal topology는 보존한다.
- target의 길이 변화에 따라 B15 block만 -8바이트, 이후 block offset만 -8바이트 이동하는지 검사한다.
- candidate를 다시 파싱·재구축해 raw byte-exact인지 확인한다.
- Hold 3개 record의 모든 리터럴이 바뀌지 않았는지 확인한다.

## 재현 명령

worktree 루트에서 실행한다. output root는 worktree의 tmp 하위로만 제한된다.

    py -3 -B workstreams/pc_b15_highrisk_static_candidate_v1/build_pc_b15_highrisk_static_candidate_v1.py build
    py -3 -B workstreams/pc_b15_highrisk_static_candidate_v1/build_pc_b15_highrisk_static_candidate_v1.py verify-private
    py -3 -B workstreams/pc_b15_highrisk_static_candidate_v1/build_pc_b15_highrisk_static_candidate_v1.py diff-check
    py -3 -B workstreams/pc_b15_highrisk_static_candidate_v1/test_pc_b15_highrisk_static_candidate_v1.py
