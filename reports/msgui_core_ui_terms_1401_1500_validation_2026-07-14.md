# msgui ID 1401-1500 번역 배치 검증 기록

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_1401_1500.v0.1.json`
- 배치 SHA-256: `4BBAAB0D5FFB89B77DC89FBFC2C8FC89571287B1BFE3F4F17E7C2A3A58F68CEB`
- 성격: 개발 전용. 공식 원문을 포함하므로 공개 패치에는 이 파일을 직접 포함하지 않는다.
- 상태: 초벌 `translated`. 실제 게임 화면에서 문맥과 폭을 확인하기 전에는 `reviewed`로 올리지 않는다.

## 범위와 보류

- 조사 범위: ID 1401-1500, 총 100개
- 번역: 100개
- 보류: 0개
- SC/JP/EN/TC가 모두 공백인 구조 문자열: 0개
- ID 연속성: 1401-1500 전부 존재, 중복 ID 0개

## 용어·문맥 판단

- ID 1403 `腰兵糧`은 부대가 지니는 군량이라는 뜻을 살려 `휴대 군량`, ID 1404 `追加兵糧`은 `추가 군량`으로 구분했다.
- ID 1410/1411은 각각 `본거지 해금 정책`/`모든 성 해금 정책`으로 옮겨 해금 범위를 분리했다.
- ID 1416-1418 `城下施設`은 기존 용어 흐름에 맞춰 `성하 시설`, `성하 시설 1`, `성하 시설 2`로 통일했다.
- ID 1420 `元服前`은 역사 용어를 유지해 `원복 전`으로 번역했다.
- ID 1431 `日分`은 앞에 동적 일수가 붙는 접미 문자열이므로 `일분`, ID 1432 `日後`는 `일 후`로 구분했다.
- ID 1434 `知行武将が不在`는 시스템 고유명 `지행`을 보존해 `지행 무장 부재`로 번역했다.
- ID 1452 `代官化武将`은 상태 변화가 드러나도록 `대관 전환 무장`, ID 1454는 `대관을 지행으로 남기기`로 번역했다.
- ID 1457 `家中内訳`은 가신단 구성 내역이라는 문맥으로 `가중 내역`을 선택했다.
- ID 1479 `取次`는 단순한 대리인이 아니라 외교 중개 역할이므로 기존 ID 1290 `중개 무장`과 맞춰 `중개`로 번역했다.
- ID 1490은 영문판 `Province` 대신 원문 `軍団`을 따라 `군단 보유 금전`, ID 1492 `城石高`는 `성 석고`로 번역했다.

## 동적 토큰·기호·제어문자 계약

printf 포함 ID는 5개다.

- ID 1425: `%d` → `약 %d개월`
- ID 1440: `%d`, `%2d`의 순서와 폭 지정자를 그대로 유지 → `%d년%2d월`
- ID 1453: `%d`, `%d`와 `/` 유지 → `건설 구획 %d/%d`
- ID 1456: `%d` 유지 → `%d명`
- ID 1474: `%s` 유지 → `%s 상태 회복`

추가 기호 검토:

- ID 1401/1402의 `/`를 각각 `원군/중재`, `혼인/직위`에 유지했다.
- ID 1422의 평가 기호 `△`는 바꾸지 않았다. 이 때문에 배치 100개 중 실제 바이너리 변경은 99개다.
- ID 1464/1477/1480의 전각 괄호 `（ ）`를 그대로 보존했다.
- ESC, PUA, 기타 제어문자, 줄바꿈이 포함된 항목은 0개다.
- 허용하지 않은 invariant override는 0개다.

## 동일 SC 해시 번역 일관성 검토

이번 범위와 이미 번역된 범위를 함께 묶어 동일 SC UTF-16LE 해시를 검사했다.

- ID 528/1415 `根据地` → `본거지`: 일치
- ID 1113/1466 `影响` → `영향`: 일치
- ID 1498/1500 `颁布` → `발령`: 일치
- ID 48/1413의 SC는 모두 `指挥`로 해시가 같지만 문법과 정렬 원문이 다르다. ID 48은 JP `采配する`, EN `Give Command`인 동작형이어서 기존 `지휘함`; ID 1413은 JP `指揮`, EN `Role`인 명사형 항목이어서 `지휘`로 유지했다. 이는 미검출 불일치가 아니라 다국어 문맥에 근거한 의도적 예외다.

이번 범위의 나머지 동일 해시 항목은 아직 상대 ID가 미번역이거나, 번역된 상대가 없어 충돌이 발생하지 않았다.

## 단독 임시 병합·검증·빌드

정식 `msgui.catalog.p3.jsonl`의 복사본에 이번 배치만 병합했다.

- merge-batch: 입력 100개, 변경 100개
- validate: 5,100행, `valid=true`, 오류 0, 경고 0
- 상태: `translated=379`, `untranslated=3683`, `empty=1038`
- buildable: 379개
- 실제 바이너리 변경: 378개
- 대상 크기: 86,495바이트
- 대상 SHA-256: `71C67643A0479413DF05005540E1154CC49684FC5EC388DD1ABD81D5CE749BFD`
- 대상 raw 크기: 86,132바이트
- 대상 raw SHA-256: `2581B92D6429D33935AE71F7AD3C09317155F9063AF270595C70EEF8BD3D055B`
- 글리프 수요: 275자
- 한글 음절 수요: 260자
- 빌드 manifest SHA-256: `10F2547E8D2731404A43655080528CE6CFCCDDB7E71D84022B395BBDB1BB12E0`
- glyph demand SHA-256: `D0ADA55D3018CAEC3E0C8AA7CC31D9A2260ECDD1C5EC917A56C0D60835D8CE5F`
- `installed_game_files_modified=false`

## ID 401-1500 누적 임시 병합·검증·빌드

완료된 401-500부터 1401-1500까지 11개 배치를 `msgui.catalog.p3.jsonl` 복사본에 순서대로 병합했다.

- 각 merge 단계: 모두 검증 통과
- 누적 validate: 5,100행, `valid=true`, 오류 0, 경고 0
- 상태: `translated=1368`, `untranslated=2694`, `empty=1038`
- 누적 buildable: 1,368개
- 누적 실제 바이너리 변경: 1,313개
- 대상 크기: 87,949바이트
- 대상 SHA-256: `88D940821894BD91CFF8E5F69B2A0E2C26403CA61242D5F8C20531182CEEA906`
- 대상 raw 크기: 87,580바이트
- 대상 raw SHA-256: `6E529C11FA1FDFF99E3B5F16B07AC9F585D59061C85B7D9708885C5C1D791AD5`
- 글리프 수요: 426자
- 한글 음절 수요: 375자
- 빌드 manifest SHA-256: `1764F19FE105BBE59FA5459514AD960E79238114AAC056188B874418D59A9FE6`
- glyph demand SHA-256: `D4DE357461EDC577A05B990A96607B3AB86A63C0674A541675AD6098E39F91A8`
- 임시 누적 catalog SHA-256: `779F3A8BA744A97E030966295C23181409329CF6A9E8F9D18027AF1B9C20B125`
- 독립 반복 빌드에서 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다.
- `installed_game_files_modified=false`

누적 입력 배치 SHA-256:

- ID 401-500: `156591250736D7F89A4D1D71104B8E1F98C9E9C41C79A22CB50610126D3E5466`
- ID 501-600: `DC008C5D571352D7602287C570DDEF74E97132EF95094D252034FBAFA8685B69`
- ID 601-700: `A8FCFC73BA2A1EDCC4B4FBE2CB61A4E98B1B4F53A91F73807334160F316B96F4`
- ID 701-800: `BA530701325A43476D20D91A0578928A3E13A60FFC2F92E99F35125D7AA4DFD8`
- ID 801-900: `E6DCDB1C376C587490DD3491A4BED4BEFA3DD17EFE61A2561515BF29697219DA`
- ID 901-1000: `3180C3A2B3B9DAC0DD53BEC7D888F61F2F83F1CF4BBBA2D1015969ADE90645B4`
- ID 1001-1100: `4CEC4FD4CDDE0AD64FFE7EF5F239A094891442FDB6146490D6EDA347204BBD04`
- ID 1101-1200: `898E6FA7A579BC658E2E079E4FFC781F3E7CB77540A681A2AF9A2EA20D43B515`
- ID 1201-1300: `3C9CFEC2AB27210049AFEBB68F919B9E8DEDBF1E78E58210D16871BABF359F15`
- ID 1301-1400: `D0F8E3A42A83A3697E7ACE82C6ADE8DCFD016949EB4AD704F834BBF420A8A665`
- ID 1401-1500: `4BBAAB0D5FFB89B77DC89FBFC2C8FC89571287B1BFE3F4F17E7C2A3A58F68CEB`

## 원본·canonical·배포본 무변경 확인

- `msgui.meta.json`: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- `msgui.catalog.p3.jsonl`: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- `msgui.catalog.p4.jsonl`: `BD011811546521A1228DBC920886767CD6DFCA496B156898954457289BB988BC`
- 설치본 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치본 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- 공개 v0.2 ZIP: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- P3/P4 canonical, Font-v4, v0.2 공개 배포본, 진행 중 v0.3-dev 경로에는 쓰지 않았다.
- 실제 쓰기 범위는 새 번역 배치, 이 보고서, `KR_PATCH_WORK/tmp/translate_1401_1500_validation` 아래 임시 검증 산출물뿐이다.

다음 정식 통합 시에는 배치만 canonical 복사본에 병합하고, 누적 426자 글리프 수요를 새 폰트 마일스톤 입력으로 재검증해야 한다.
