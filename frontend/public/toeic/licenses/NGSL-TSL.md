# NGSL / TOEIC Service List — data license and attribution

The word lists, ranks and English definitions in `lexicon.json` are derived from
NGSL 1.2 by Charles Browne, Brent Culligan and Joseph Phillips, and TOEIC Service
List 1.2 by Charles Browne and Brent Culligan.

- NGSL: https://www.newgeneralservicelist.com/new-general-service-list
- TSL: https://www.newgeneralservicelist.com/toeic-service-list
- License: Creative Commons Attribution-ShareAlike 4.0 International
- License terms: https://creativecommons.org/licenses/by-sa/4.0/
- Legal code: https://creativecommons.org/licenses/by-sa/4.0/legalcode.en

This adapted dataset is also licensed under CC BY-SA 4.0. Preserve attribution,
link to the license, indicate changes, and share adaptations under the same
license. No endorsement by the authors or ETS is implied. This notice applies
to these data; it does not relicense the application or unrelated media.

DHV changes: normalized spelling for lookup, merged the shared headword criteria
while preserving both definitions, retained two unranked TSL entries without
inventing ranks, and supplied six missing English definitions (by-law, café,
e-book, entrée, résumé, smartphone). The definitions are English, not Vietnamese.
The JSON records source membership, ranks, adaptations and source-file SHA-256
digests. Its 4,060 unique headwords comprise 4,059 ranked entries plus the
unranked headword born; criteria is already ranked in NGSL.

Source publications were retrieved on 2026-10-27. The source XLSX/CSV files are
retained under backend/data/toeic/vendor/ngsl-tsl for reproducible offline builds.
No question bank or proprietary code from seikaikyo/toeic-practice is included.
