# PC PK 타이틀 이미지 G1T 코덱 프로브

`RES_SC/res_lang.bin`의 타이틀 라벨 경로 `/3/N`을 파일만으로 추출하고 다시 조립하는 소스 전용 프로브다. 게임 설치본, 실행 파일, 메모리, DLL, 후킹, 레지스트리는 다루지 않는다. 완성 이미지, G1T, LINK, `res_lang.bin` 후보는 Git에 넣지 않고 `tmp/**/private/`에만 만든다.

## 확인된 PC 구조

```text
RES_SC/res_lang.bin             LINK, 42 entries
└─ /3                           LINK variant, 32-byte fixed header, 110 entries
   └─ /0..109                   raw-LZ4 wrapper
      └─ GT1G0600               one texture, platform 0x0A
         └─ format 0x5B         NOBU16 PC alias decoded as linear BC3/DXT5
            └─ 512x128, 1 mip   65,536-byte block payload
```

Switch v1.3과 공통 대응 범위는 `/3/0..107`이다. PC에는 `/3/108..109` 두 장이 추가로 있다. Switch의 512×64 블록이나 G1T/LINK 바이트를 PC에 그대로 복사하지 않는다. 번역 픽셀만 참고해 PC 512×128 캔버스에서 다시 렌더링해야 한다.

## 사용법

입력은 사용자가 보유한 로컬 PC 후보나 백업이어야 한다. 출력 루트는 저장소의 `tmp` 아래만 허용된다.

```powershell
python -B tools/pc_g1t_title_codec.py extract `
  --archive tmp/<local-build>/private/candidate/res_lang.SC.seoulhangang-v1.bin `
  --index 0 `
  --output-root tmp/pc_g1t_probe

python -B tools/pc_g1t_title_codec.py rebuild `
  --archive tmp/<local-build>/private/candidate/res_lang.SC.seoulhangang-v1.bin `
  --png tmp/pc_g1t_probe/private/extract/3_000/title.png `
  --index 0 `
  --output-root tmp/pc_g1t_rebuild
```

추출 결과는 `title.png`, `title.rgba`, `metadata.json`이다. 재구축 결과는 `candidate/RES_SC/res_lang.bin`, `candidate_preview.png`, `rebuild_report.json`이다.

변경하지 않은 4×4 블록은 원본 BC3 16바이트를 그대로 보존한다. 변경한 블록만 표준 라이브러리 기반 결정적 인코더를 통과한다. 따라서 디코드한 PNG를 수정하지 않고 다시 넣으면 G1T, raw-LZ4 wrapper, `/3` LINK, 외부 `res_lang.bin`이 모두 원본과 바이트 단위로 같아야 한다.

## 검증과 경계

```powershell
python -B -m unittest tests.test_pc_g1t_title_codec -v
```

- 합성 자산 테스트 6개가 PNG, BC3, G1T, 32바이트 LINK, 외부 LINK, 입력 불변성을 검사한다.
- 로컬 실제 `/3/0` 무변경 A/B 재구축은 외부 후보까지 입력과 같은 SHA-256을 냈다.
- 한 픽셀 변경 A/B 재구축도 서로 같은 SHA-256을 냈으며, 4,096개 블록 중 4,095개는 원본 그대로였다.
- 이 검증은 컨테이너·코덱 검증이다. 한국어 타이틀 108장 렌더와 실제 게임 화면 검증을 대신하지 않는다.

