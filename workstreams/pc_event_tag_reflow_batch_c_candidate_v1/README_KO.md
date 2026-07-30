# PC PK 이벤트 태그·줄바꿈 후보 C (private)

## 범위와 안전성

- 대상은 **직접 PC** PK 이벤트 테이블 `MSG_PK/JP/msgev.bin`뿐이다.
- 입력은 현재 W45 한국어 테이블, pristine PC 일본어 테이블, 현재 PC 이벤트 폰트, 커밋된 C 검토 보고서만 사용한다.
- Switch 파일·경로·번역은 열지 않는다.
- 빌더는 `tmp/pc_event_tag_reflow_batch_c_candidate_v1/candidate/` 아래에만 후보를 쓴다. Steam 게임 리소스, transaction, Git, 네트워크, 릴리즈 기능은 구현하지 않는다.

## 고정 입력과 결과

| 항목 | packed SHA-256 / 크기 | raw SHA-256 / 크기 |
| --- | --- | --- |
| W45 PC 한국어 입력 | `01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE` / 994,739 | `F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC` / 990,828 |
| pristine PC 일본어 증거 | `03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002` / 555,784 | `4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE` / 890,428 |
| C 후보 출력 | `DE3B6899F82D7C9A0781AD54AF635EF2061C59BF8DFA0E6BFD984EB5343FD31A` / 994,727 | `0F42CB7EBF50D147723586BE2EDECF403CA64E507D8E91CB1E581C7A9EDCC765` / 990,816 |

폰트 폭은 고정 PC 이벤트 폰트 유틸리티
`workstreams/pc_event_quality_wave31_static_v1/build_pc_event_quality_wave31_static_v1.py`
(`71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A`)로 계산한다.
모든 대상은 1~3줄, 줄당 최대 912px이며 수동 LF는 색상 태그 바깥에만 있다.

## 검토된 변경

정확한 대상 ID는 다음 11개다.

`3960, 8138, 8451, 8704, 9131, 9137, 9795, 9806, 10534, 10800, 10803`

| ID | 줄 폭(px) | 대상 UTF-16LE SHA-256 |
| --- | --- | --- |
| 3960 | 648 / 912 / 672 | `E73C8511A443313D01FD3623882D2A2F6BE0E50CA500AF71B95835C922FA1326` |
| 8138 | 552 / 744 / 864 | `FE27AAF7D81B1A8F25CE8007437D4FD71B81DE239BF7220DB4E09054EB417100` |
| 8451 | 384 / 792 / 696 | `1A82271C0FC660EFAE8BEC4C2C46232C836E326E005466287C35AC771E6B9F83` |
| 8704 | 552 / 528 / 696 | `635605D280134F9067F47F631DA8DE727CDA953D4D8341461EBC9EA2A083540F` |
| 9131 | 576 / 600 / 768 | `F9BAEAC9CBF23435E41B06C27BAC5F45BE772933D72F3EC650B4557C1396CE72` |
| 9137 | 816 / 768 / 336 | `F3ECC0B5E5457999585357AD2090340CFD0F9642BFCB70E2F6687B29836BDE76` |
| 9795 | 840 / 864 / 552 | `3898F5706E362D5ED5FF62C2F97517FCD9110CE9A7D72DC2C8F734B24E56DAF9` |
| 9806 | 504 / 720 / 840 | `2DEC1248E7E0BB0770166CF194CDE3DAD33A7BDD962D55C45A38E4A2CFB3C5AF` |
| 10534 | 264 / 696 / 720 | `60D123724E0444A75B3014A9842B0BB5132C960742A867DBC9A4FB66E8CF34B1` |
| 10800 | 816 / 672 / 384 | `ED95647B8734EC67867DFC9D49078A3EFAC05C2C534D52A439F2298A68AFC7BA` |
| 10803 | 744 / 528 / 696 | `493C1FDE64FAEFAD5E20D1CEFF471F61A9333253BEFD76572F7C4E9D011CCF7F` |

3960은 이름만 바꾸는 기존 3960 컴포넌트를 **의도적으로 대체하는 전체 의미·이름·줄바꿈 변경**이다. 둘을 함께 적용하면 안 된다. 고정 원문은 다음과 같다.

```text
교묘한 수였으나, <ESC>CA모토나리<ESC>CZ의<LF>
끝까지 비정한 결단으로 <ESC>CB이노우에 일파<ESC>CZ의<LF>
가문 내 영향력은 일소되었다.
```

## 실행과 확인

```powershell
py -3 -B .\workstreams\pc_event_tag_reflow_batch_c_candidate_v1\test_pc_event_tag_reflow_batch_c_candidate_v1.py -v
py -3 -B .\workstreams\pc_event_tag_reflow_batch_c_candidate_v1\build_pc_event_tag_reflow_batch_c_candidate_v1.py build
py -3 -B .\workstreams\pc_event_tag_reflow_batch_c_candidate_v1\build_pc_event_tag_reflow_batch_c_candidate_v1.py verify-private
py -3 -B .\workstreams\pc_event_tag_reflow_batch_c_candidate_v1\build_pc_event_tag_reflow_batch_c_candidate_v1.py diff-check
```

후보에는 `MSG_PK/JP/msgev.bin`, `audit.v1.json`, `candidate_manifest.v1.json` 세 파일만 있어야 한다.
