# PC 이벤트 의미·개행 후보 (Wave 54)

이 작업물은 Steam PC판 PK 이벤트 `MSG_PK/JP/msgev.bin`의 W45 한국어 입력만을 시작점으로 삼는 **비공개 후보**다. 게임 파일, Steam, Git, 네트워크, 릴리즈를 수정하지 않는다.

## 범위와 입력 고정

- 변경 ID는 정확히 8개다: `3202, 3900, 3934, 4140, 8510, 8723, 9359, 10045`.
- 한국어 입력: 설치된 Steam PC W45 `MSG_PK/JP/msgev.bin`
  - packed: `01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE` (994,739 bytes)
  - raw: `F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC` (990,828 bytes)
- 의미 확인은 보존된 Steam PC 일본어 원본의 각 동일 ID에 한정한다. 전체 테이블의 일반적인 인덱스 대응을 주장하지 않는다.
- PC 이외의 번역 텍스트는 열거나 근거로 사용하지 않는다.
- 출력은 `tmp/pc_event_semantic_reflow_wave54_v1/candidate/` 아래에만 생성된다.
- 후보 출력(8개 변경만 적용):
  - packed: `30CED81B2F9B3B02FE0F8EFFEA1D9CF05E513E854CCAC3B84C6B7213947EB429` (994,735 bytes)
  - raw: `E2F6BA4CEFD9CE9CE670F62D91631073F228C8CF53306433397C701D63648D22` (990,824 bytes)

## 공통 검증 계약

- 각 대상은 정확히 3줄이며, 활성 PC 이벤트 폰트 기준 각 줄이 912px 이하다.
- `ESC C[A-C]`/`ESC CZ` 순서, 런타임 토큰, printf 토큰, 제어 문자와 앞뒤 공백은 입력과 동일해야 한다.
- 수동 LF는 색상 태그 바깥에만 놓인다. 색상 이름·가문·지명은 태그 한 쌍 안에서 온전하게 유지한다.
- 원본/후보 모두 LZ4 압축 해제, 테이블 재파싱, 재구축, 재압축 동일성을 확인한다.

## 레코드별 검토

`ESC` 표기는 파일 안에서는 실제 제어문자이며, 아래에는 읽기 쉽게 `\x1b`로 표기했다.

### 3202

- JP: `\x1bCB甲斐源氏\x1bCZの古豪・\x1bCB武田家\x1bCZ。\x1bCB足利一門\x1bCZの\n名族・\x1bCB今川家\x1bCZ。\x1bCA今川\x1bCZの傘下から\n新天地・\x1bCC関東\x1bCZへ飛び出した\x1bCB北条家\x1bCZ。`
- 현재 KO: `\x1bCB카이 겐지\x1bCZ의 강호 \x1bCB다케다\x1bCZ. \x1bCB아시카가\n일문\x1bCZ의 명문 \x1bCB이마가와\x1bCZ. \x1bCA이마가와\x1bCZ에서\n독립해 \x1bCC간토\x1bCZ를 개척한 \x1bCB호조\x1bCZ.`
- 후보 KO: `\x1bCB카이 겐지\x1bCZ의 강호, \x1bCB다케다\x1bCZ.\n\x1bCB아시카가 일문\x1bCZ의 명문, \x1bCB이마가와\x1bCZ.\n\x1bCA이마가와\x1bCZ에서 독립해 \x1bCC간토\x1bCZ로 나선 \x1bCB호조\x1bCZ.`
- 이유: 가문·독립·간토 진출 관계를 자연스럽게 하고 태그 내부 개행을 제거한다. 폭: `600/744/888`.

### 3900

- JP: `\x1bCB大友家\x1bCZ第二十代当主・\x1bCA大友義鑑\x1bCZの嫡男。\n多芸多才ではあったが、\n生来病弱な人物であった。`
- 현재 KO: `\x1bCB오토모 가문\x1bCZ 제20대 당주 \x1bCA오토모\n요시아키\x1bCZ의 적자. 다재다능했지만,\n태어날 때부터 병약한 인물이었다.`
- 후보 KO: `\x1bCB오토모 가문\x1bCZ 제20대 당주,\n\x1bCA오토모 요시아키\x1bCZ의 적자. 다재다능하나,\n태어날 때부터 병약한 인물이었다.`
- 이유: 인물 소개의 당주·적자·병약 정보를 보존하면서 이름 태그를 온전히 둔다. 폭: `576/888/768`.

### 3934

- JP: `\x1bCA村上義清\x1bCZさえ倒せば、\n\x1bCC中信\x1bCZ・\x1bCC北信\x1bCZの諸勢力はなびいてくる。\n\x1bCA義清\x1bCZめを完膚なきまでに叩きのめす！`
- 현재 KO: `\x1bCA무라카미 요시키요\x1bCZ만 쓰러뜨리면, \x1bCC시나노\n중부\x1bCZ와 \x1bCC시나노 북부\x1bCZ의 세력은 저절로\n따른다. \x1bCA요시키요\x1bCZ를 철저히 짓밟아 주마!`
- 후보 KO: `\x1bCA무라카미 요시키요\x1bCZ만 쓰러뜨리면,\n\x1bCC시나노 중부\x1bCZ와 \x1bCC시나노 북부\x1bCZ의 세력은\n내게 따른다. \x1bCA요시키요\x1bCZ를 짓밟아 주마!`
- 이유: 중신·북신 세력의 귀속 관계와 위협의 어조를 유지한다. 폭: `744/816/864`.

### 4140

- JP: `\x1bCB朝倉家\x1bCZ当主・\x1bCA朝倉義景\x1bCZの曽祖父の兄弟であり\n家中の軍事を一手に司る重鎮であった。`
- 현재 KO: `\x1bCB아사쿠라 가문\x1bCZ 당주·\x1bCA아사쿠라\n요시카게\x1bCZ의 증조부와 형제로,\n가문의 군사를 도맡은 중진이었다.`
- 후보 KO: `\x1bCB아사쿠라 가문\x1bCZ 당주·\n\x1bCA아사쿠라 요시카게\x1bCZ의 증조부의 형제이며,\n가문의 군사를 총괄한 중진이었다.`
- 이유: 가계 관계와 군사 총괄 역할을 유지한다. 폭: `480/912/768`.

### 8510

- JP: `源平藤橘の名家の上に\x1bCB豊臣家\x1bCZが君臨する\n\x1bCA秀吉\x1bCZが作った、新たな世の始まりであった。`
- 현재 KO: `겐페이토키쓰의 명가 위에 \x1bCB도요토미\n가문\x1bCZ이 군림한다 \x1bCA히데요시\x1bCZ가\n만든 새로운 세상의 시작이었다.`
- 후보 KO: `겐페이토키쓰의 명가 위에\n\x1bCB도요토미 가문\x1bCZ이 군림하는\n\x1bCA히데요시\x1bCZ가 만든 새 시대의 시작이었다.`
- 이유: ‘히데요시가 만든 새 시대’라는 원문 문법을 복원한다. 폭: `576/576/888`.

### 8723

- JP: `\x1bCB蘆名家\x1bCZ第十八代当主・\x1bCA蘆名盛隆\x1bCZは、\n\x1bCB二階堂家\x1bCZの出身で妻は\x1bCA伊達輝宗\x1bCZの妹である。`
- 현재 KO: `\x1bCB아시나 가문\x1bCZ 제18대 당주 \x1bCA아시나\n모리타카\x1bCZ는, \x1bCB니카이도 가문\x1bCZ 출신으로\n아내는 \x1bCA다테 데루무네\x1bCZ의 여동생이다.`
- 후보 KO: `\x1bCB아시나 가문\x1bCZ 18대 당주,\n\x1bCA아시나 모리타카\x1bCZ는 \x1bCB니카이도 가문\x1bCZ 출신.\n아내는 \x1bCA다테 데루무네\x1bCZ의 여동생이다.`
- 이유: 가문 출신과 혼인 관계를 명확히 한다. 폭: `528/888/816`.

### 9359

- JP: `失礼いたしました。\nそれがしは\x1bCC美濃\x1bCZの出にて、\x1bCA明智十兵衛光秀\x1bCZ。\n\x1bCB越前朝倉家\x1bCZの厄介になっております。`
- 현재 KO: `실례하였소이다. 소인은 \x1bCC미노\x1bCZ 태생으로,\n\x1bCA아케치 주베에 미쓰히데\x1bCZ. \x1bCB에치젠\n아사쿠라가\x1bCZ에 몸을 의탁하고 있소이다.`
- 후보 KO: `실례하였소이다. 소인은 \x1bCC미노\x1bCZ 출신이오.\n\x1bCA아케치 주베에 미쓰히데\x1bCZ라 하오.\n\x1bCB에치젠 아사쿠라가\x1bCZ에 의탁 중이오.`
- 이유: 자기소개·출신·의탁 관계를 원문 순서로 복원한다. 폭: `888/720/768`.

### 10045

- JP: `そして\x1bCB伊達\x1bCZ・\x1bCB佐竹\x1bCZ・\x1bCB奥羽諸将\x1bCZを糾合すれば\n\x1bCA内府\x1bCZと一戦交えることもできよう。`
- 현재 KO: `그리고 \x1bCB다테\x1bCZ·\x1bCB사타케\x1bCZ·\x1bCB오우의\n여러 장수\x1bCZ를 규합하면\n\x1bCA내대신\x1bCZ과 한판 승부를 벌일 수도 있겠지.`
- 후보 KO: `그리고 \x1bCB다테\x1bCZ·\x1bCB사타케\x1bCZ를 규합하고\n\x1bCB오우의 여러 장수\x1bCZ까지 모은다면,\n\x1bCA내대신\x1bCZ과 일전을 벌일 수도 있겠지.`
- 이유: 다테·사타케·오우 제장의 규합이라는 원문 병렬 구조를 복원한다. 폭: `720/720/792`.

## 실행

```powershell
py -3 -B -m unittest workstreams\pc_event_semantic_reflow_wave54_v1\test_pc_event_semantic_reflow_wave54_v1.py -v
py -3 -B workstreams\pc_event_semantic_reflow_wave54_v1\build_pc_event_semantic_reflow_wave54_v1.py profile
py -3 -B workstreams\pc_event_semantic_reflow_wave54_v1\build_pc_event_semantic_reflow_wave54_v1.py build
py -3 -B workstreams\pc_event_semantic_reflow_wave54_v1\build_pc_event_semantic_reflow_wave54_v1.py verify-private
```

출력 프로필은 빌더에 고정돼 있다. 후보는 아직 Steam 적용 대상이 아니다.
