# PC PK 이벤트 색상 태그 개행 — Batch B private 후보

이 workstream은 pc_event_tag_reflow_batch_b_v1의 확정 PC 전용 검토 결과 중
정확히 10개 W45 PK 이벤트 레코드만 private 후보로 조립한다.

후보 출력은 tmp/pc_event_tag_reflow_batch_b_candidate_v1/candidate/ 아래에만 생긴다.
Steam 게임 파일, Git, 네트워크, 릴리즈, 트랜잭션에는 쓰기 기능이 없다.
Switch 파일·경로·번역문은 읽거나 검색하지 않는다.

## 핀

| 구분 | packed | raw |
| --- | --- | --- |
| W45 KO MSG_PK/JP/msgev.bin | 994739 / 01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE | 990828 / F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC |
| pristine PC JP MSG_PK/JP/msgev.bin | 562226 / A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84 | 894800 / 07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E |
| private output | 994695 / 5325EE8C902CE834A2C18D243A23D40393873ED167D925FF7F105E8CDA6299AF | 990784 / 5AF0C7070FB7543F00329DCCC10469A6D5AC5A69DD2EF1E1E83928D3D711C45D |

- KO input: F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin
- JP evidence: F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin
- 실제 이벤트 글꼴: RES_JP/res_lang.bin, SHA-256 3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7

## 범위 및 레코드 계약

변경 ID는 다음 10개뿐이다.

5297, 5302, 5817, 5857, 5884, 6300, 6396, 6501, 7735, 7779

각 Change에는 W45 current KO preimage hash, target hash, 같은 ID의 PC JP
hash와 anchor, 실제 이벤트 글꼴 폭을 고정한다. 빌드마다 태그 순서와
런타임/printf/C0 제어 토큰, 앞뒤 공백을 비교하고, 색상 span 내부 LF,
4줄 이상, 912px 초과를 거부한다. 후보 재압축 후에는 parser/LZ4 왕복,
정확한 10개 ID diff, packed/raw output profile도 다시 검사한다.

| ID | target UTF-16LE SHA-256 | PC JP anchor | 폭(px) |
| ---: | --- | --- | --- |
| 5297 | 9EBB11CDB5D9D40963D0DC5353FF076998C3B54EED190B5C438A7A2C536E2F14 | 晴政, 石川高信, 勇将, 南部家 | 408 / 744 / 840 |
| 5302 | 1D91D4494BFAEBA694F5D5981658F41B0FFC25E4ACB3E63463207ED9D782054B | 織田家, 斎藤家, 和睦, 信長, 上洛 | 768 / 552 / 384 |
| 5817 | 02C5898CC5EE2378ACE2241880030504DD6335E8182D6411AD8A64C750C60913 | 最上家, 最上義守, 嫡男, 最上義光 | 504 / 768 / 840 |
| 5857 | 24C67703F1FF86F4EDE1365EFD09E08305B15FA9EA122F7F7C64C80BD9F53F2D | 肥前, 少弐家, 龍造寺隆信, 勢力を拡大 | 576 / 816 / 816 |
| 5884 | 0CDDCBD019EAE7EA79A5FB8466CA82E1AC002DF025A66793BEB0362EFDA0BC5B | 伊達家, 天文の乱, 晴宗, 新たな歩み | 624 / 744 / 912 |
| 6300 | F4984DD22F3419C750580928B1CC9EF0CBE3FA163D5FA55EC801E5E4FCEB2C57 | 越前, 戦国大名, 朝倉家, 幕を閉じた | 528 / 528 / 456 |
| 6396 | 8CD535360DCD73D493202545809539A22D29A15BE3CFB25E1ACAE2C83A17DB59 | 兼定, 長宗我部家, 動揺 | 744 / 720 / 384 |
| 6501 | A12AA04B4584401F2687F845BEBC0B7874836B1A6C33D9249FF5C9E6AA7E6FEC | 長篠, 武田勝頼, わずかな供回り, 甲斐 | 576 / 744 / 672 |
| 7735 | 93EE82C6E72FA7BF5E15C6D2E0C51E3DF664B5A210EE897D822EF0ABD52EAC8C | 距離的な面, 北条家, 勝頼, 岩殿城 | 864 / 408 / 672 |
| 7779 | E6A7C01124574220B46E35C12D89872A7B272F496A6A904605FC715F6D444508 | 長篠, 武田勝頼, 家中の改革 | 576 / 504 / 552 |

## root 수정 literal

5302와 5884는 보고서의 이전 초안이 아니라 다음 final literal을 정확히 사용한다.

~~~text
5302
그러나 \x1bCB오다 가문\x1bCZ과 \x1bCB사이토 가문\x1bCZ의
화친이 깨져, \x1bCA노부나가\x1bCZ는
상경하지 못했다.

5884
서로 불만을 품은 채였지만,
\x1bCB다테 가문\x1bCZ의 덴분의 난은 끝났다.
\x1bCA하루무네\x1bCZ를 당주로 새 출발을 맞았다……
~~~

5302의 첫 줄은 그러나로 시작하며 화친이 깨져를 보존한다.
5884의 마지막 줄은 반드시 새 출발을 맞았다여야 한다. 둘 중 하나라도
다르면 보고서 literal, target hash, private output profile 검증이 실패한다.

## 실행

~~~powershell
py -3 -B .\workstreams\pc_event_tag_reflow_batch_b_candidate_v1\build_pc_event_tag_reflow_batch_b_candidate_v1.py build
py -3 -B .\workstreams\pc_event_tag_reflow_batch_b_candidate_v1\build_pc_event_tag_reflow_batch_b_candidate_v1.py verify-private
py -3 -B .\workstreams\pc_event_tag_reflow_batch_b_candidate_v1\build_pc_event_tag_reflow_batch_b_candidate_v1.py diff-check
py -3 -B -m unittest .\workstreams\pc_event_tag_reflow_batch_b_candidate_v1\test_pc_event_tag_reflow_batch_b_candidate_v1.py -v
~~~

build는 기존 candidate를 덮어쓰지 않는다. private tmp root 밖의 경로 및 tmp
root 자체는 거부한다.
