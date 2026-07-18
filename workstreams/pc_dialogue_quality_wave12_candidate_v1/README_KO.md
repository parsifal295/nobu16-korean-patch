# PC 전용 정적 대사 품질 Wave 12 후보

이 작업공간은 Wave 9 개인 후보를 입력으로 받아 Base와 PK의 같은 정적 대사 한 건만 교정한다. Steam 설치본에는 쓰지 않으며, 적용·스테이지·커밋·푸시·릴리스 명령을 제공하지 않는다.

## 범위

대상은 다음 두 리소스의 `13:143:0`뿐이다.

- `MSG/JP/msggame.bin`
- `MSG_PK/JP/msggame.bin`

두 레코드의 현행 문안은 다음과 같다.

```text
당가는 아직 세력이 미약하오.
천하를 노리려면 영토를 넓혀 국력을 기르고,
전국의 다이묘에게 그 힘을 인정받아야 하오.
```

후보 문안은 의미와 존대체를 유지하면서 `당가` 표기를 자연스럽게 고치고, 세 줄을 912px 안에 맞춘다.

```text
우리 가문은 아직 역부족이오.
천하를 노리려면 영토를 넓혀 힘을 길러,
다이묘 모두에게 힘을 인정받아야 하오.
```

## PC 원문 근거

의미 검증은 PC 원문만 사용한다.

- pristine PC JP: `当家はまだまだ力不足 / 天下を狙うには領土を広げて力をつけ / 全国の大名に力を認めさせる必要があります`
- PC EN: `Our clan is still much too weak... expand our domain, grow our forces, and command the respect of every daimyª...`

Nintendo Switch 한국어 자산은 읽지 않으며 참고하지 않는다.

## 고정 계약

- Wave 9 입력 hash
  - Base: `7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492`
  - PK: `209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930`
- 후보 출력 hash
  - Base: `C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347`
  - PK: `F53BBB2FA4247A0CBAC4538DA84F94376DC40E83A7CF1491D4C1E81C9DE21CBF`
- 대상 레코드: `141B / 653E135A…BD41` → `131B / B55F1265…5EA6`
- literal marker는 `070701 … 070702` 하나이며, opaque span `""`, `050505`와 종료자는 그대로 보존한다.
- Steam JP 폰트 기준 줄 폭은 `672 / 912 / 888px`이고, fallback glyph를 허용하지 않는다.
- v0.11.2 글꼴과 별도 UI 이미지/HUD 자산 프로필 두 가지에서만 검증을
  허용한다. 대상 글리프 advance는 두 프로필에서 동일하며, 실제 실행 때도
  위 폭과 fallback glyph 없음이 다시 강제된다.

검증은 대상 외 레코드 불변, marker/opaque 보존, 실제 PC JP·EN 의미 앵커, 결정적 재빌드, 런타임 제어 토큰 부재를 강제한다. 정적 검증은 실게임 QA를 대체하지 않는다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v workstreams\pc_dialogue_quality_wave12_candidate_v1\test_pc_dialogue_quality_wave12_candidate_v1.py
& $py -B workstreams\pc_dialogue_quality_wave12_candidate_v1\build_pc_dialogue_quality_wave12_candidate_v1.py hash
& $py -B workstreams\pc_dialogue_quality_wave12_candidate_v1\build_pc_dialogue_quality_wave12_candidate_v1.py build
```

`build` 산출물은 `tmp/pc_dialogue_quality_wave12_candidate_v1` 아래에만 생성된다.
