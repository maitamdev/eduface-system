# NGSL / TOEIC Service List & Bilingual English–Vietnamese Dictionary — License & Attribution

The word lists, ranks and English definitions in `lexicon.json` are derived from
NGSL 1.2 by Charles Browne, Brent Culligan and Joseph Phillips, and TOEIC Service
List 1.2 by Charles Browne and Brent Culligan. Vietnamese meanings (`meaning_vi`)
and part-of-speech tags (`pos`) are derived from Vietnamese Wiktionary (extracted
via Kaikki.org / Wiktextract) and curated TOEIC adaptations by DHV English Studio.
American English phonetic transcriptions (`ipa`) are derived from `open-dict-data/ipa-dict`.

- NGSL 1.2: https://www.newgeneralservicelist.com/new-general-service-list (CC BY-SA 4.0)
- TSL 1.2: https://www.newgeneralservicelist.com/toeic-service-list (CC BY-SA 4.0)
- Vietnamese Wiktionary / Kaikki.org: https://vi.wiktionary.org/ & https://kaikki.org/ (CC BY-SA 4.0)
- open-dict-data / ipa-dict (en_US): https://github.com/open-dict-data/ipa-dict (MIT License)
- License: Creative Commons Attribution-ShareAlike 4.0 International
- License terms: https://creativecommons.org/licenses/by-sa/4.0/
- Legal code: https://creativecommons.org/licenses/by-sa/4.0/legalcode.en

This adapted bilingual dataset is licensed under CC BY-SA 4.0 (with `ipa-dict`
components under the MIT License; see `IPA-MIT-LICENSE.txt`). Preserve attribution,
link to the license, indicate changes, and share adaptations under the same
license. No endorsement by the authors or ETS is implied. This notice applies
to these data; it does not relicense the application or unrelated media.

DHV changes:
1. Normalized spelling (`e-mail` -> `email`) for lookup while preserving original source terms.
2. Merged the shared headword `criteria` while preserving both NGSL and TSL definitions.
3. Retained two unranked TSL entries (`born`, `criteria`) without inventing ranks.
4. Supplied six missing English definitions (`by-law`, `café`, `e-book`, `entrée`, `résumé`, `smartphone`).
5. Enriched all 4,060 entries with Vietnamese meanings (`meaning_vi`), standardized parts of speech (`pos`), and American English IPA (`ipa`).

Source publications were retrieved on 2026-10-27. All pinned inputs and SHA-256 digests
are retained under `backend/data/toeic/vendor/ngsl-tsl` for reproducible offline builds.
No question bank or proprietary code from `seikaikyo/toeic-practice` is included.
