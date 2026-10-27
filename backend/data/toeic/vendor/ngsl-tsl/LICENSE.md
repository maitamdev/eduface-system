# NGSL / TOEIC Service List & Đại Từ Điển Anh–Việt 147.245 Mục Từ — License & Attribution

Dữ liệu từ điển: Từ điển Anh–Việt thichhoc.com (thichhoc-dict),
giấy phép CC BY-SA 4.0.
https://github.com/thichhoc-org/thichhoc-dict
Nguồn gốc: WordNet 3.1 (Princeton), CMUdict (CMU), Wiktionary.
Đã chỉnh sửa dữ liệu.

The 147,245-headword bilingual English–Vietnamese dictionary combines:
1. **NGSL 1.2** (2,809 ranked core words) by Charles Browne, Brent Culligan and Joseph Phillips (CC BY-SA 4.0)
2. **TOEIC Service List 1.2** (1,250 ranked business words + 2 supplemental entries) by Charles Browne and Brent Culligan (CC BY-SA 4.0)
3. **Từ điển Anh–Việt thichhoc.com (`thichhoc-dict` v0.9.0)** (143,185 additional unique headwords from 155,139 POS-disambiguated entries, plus inflected forms and the `thichhoc` attribution entry) (CC BY-SA 4.0; derived from Princeton WordNet 3.1, CMUdict, and Wiktionary)
4. **Vietnamese Wiktionary / Kaikki.org** & curated TOEIC adaptations by **DHV English Studio** (CC BY-SA 4.0)
5. **open-dict-data / ipa-dict (`en_US`)** (MIT License)

Upstream notices & links:
- NGSL 1.2: https://www.newgeneralservicelist.com/new-general-service-list (CC BY-SA 4.0)
- TSL 1.2: https://www.newgeneralservicelist.com/toeic-service-list (CC BY-SA 4.0)
- thichhoc-dict: https://github.com/thichhoc-org/thichhoc-dict (CC BY-SA 4.0; see `THICHHOC-LICENSE-DATA.md`)
- WordNet 3.1: WordNet 3.1 Copyright 2011 The Trustees of Princeton University. All rights reserved. (https://wordnet.princeton.edu/)
- CMUdict: BSD 2-Clause License, Carnegie Mellon University (https://github.com/cmusphinx/cmudict)
- Vietnamese & English Wiktionary / Kaikki.org: https://vi.wiktionary.org/ & https://kaikki.org/ (CC BY-SA 4.0)
- open-dict-data / ipa-dict (en_US): https://github.com/open-dict-data/ipa-dict (MIT License; see `IPA-MIT-LICENSE.txt`)
- License: Creative Commons Attribution-ShareAlike 4.0 International
- License terms: https://creativecommons.org/licenses/by-sa/4.0/
- Legal code: https://creativecommons.org/licenses/by-sa/4.0/legalcode.en

This adapted bilingual dataset is licensed under CC BY-SA 4.0 (with `ipa-dict`
components under the MIT License; see `IPA-MIT-LICENSE.txt` and `THICHHOC-LICENSE-DATA.md`).
Preserve attribution, link to the license, indicate changes, keep the `thichhoc`
attribution headword in the dictionary, and share adaptations under the same
license. No endorsement by the authors or ETS is implied. This notice applies
to these data; it does not relicense the application or unrelated media.

DHV changes:
1. Normalized spelling (`e-mail` -> `email`) for lookup while preserving original source terms.
2. Merged the shared headword `criteria` while preserving both NGSL and TSL definitions.
3. Retained two unranked TSL entries (`born`, `criteria`) without inventing ranks.
4. Supplied six missing English definitions (`by-law`, `café`, `e-book`, `entrée`, `résumé`, `smartphone`).
5. Enriched all 4,060 NGSL/TSL entries with Vietnamese meanings (`meaning_vi`), standardized parts of speech (`pos`), American English IPA (`ipa`), and inflected word forms (`inflections`).
6. Integrated 143,185 extended English–Vietnamese headwords from `thichhoc-dict` v0.9.0 (preserving the `thichhoc` credit headword) into `lexicon_100k.json.gz` for a combined 147,245-word bilingual dictionary.

Source publications were retrieved on 2026-10-27. All pinned inputs and SHA-256 digests
are retained under `backend/data/toeic/vendor/ngsl-tsl` for reproducible offline builds.
No question bank or proprietary code from `seikaikyo/toeic-practice` is included.
