# Canonical Sources — magic-linguistic-scope

Maintainer-facing reading list. Snapshot 2026-04-23.

## Foundational

- **Joshi, P., Santy, S., Budhiraja, A., Bali, K., Choudhury, M.** (2020). *The State and Fate of Linguistic Diversity and Inclusion in the NLP World*. ACL 2020. https://aclanthology.org/2020.acl-main.560/
  - Origin of the 0-5 resource class taxonomy used throughout this skill.

## Typology databases

- **Dryer, M. S., & Haspelmath, M. (eds.)** (2013). *The World Atlas of Language Structures Online*. MPI-EVA. https://wals.info/
- **Skirgård, H., et al.** (2023). *Grambank reveals the importance of genealogical constraints on linguistic diversity*. Science Advances 9(16). https://grambank.clld.org/
- **Littell, P., Mortensen, D. R., Lin, K., Kairis, K., Turner, C., Levin, L.** (2017). *URIEL and lang2vec: Representing languages as typological, geographical, and phylogenetic vectors*. EACL.
- **Croft, W.** (2003). *Typology and Universals* (2nd ed.). Cambridge University Press.
- **Comrie, B.** (1989). *Language Universals and Linguistic Typology* (2nd ed.). University of Chicago Press.

## Glottolog and language identification

- **Hammarström, H., Forkel, R., Haspelmath, M., Bank, S.** (eds.). *Glottolog 5.0*. https://glottolog.org/
- **ISO 639-3 standard**, SIL International. https://iso639-3.sil.org/

## Transfer learning & cross-lingual NLP

- **Lin, Y.-H., et al.** (2019). *Choosing Transfer Languages for Cross-Lingual Learning*. ACL.
  - Empirical model for transfer-source prediction; complements URIEL distance.
- **Pires, T., Schlinger, E., Garrette, D.** (2019). *How Multilingual is Multilingual BERT?*. ACL.
- **de Vries, W., Wieling, M., Nissim, M.** (2022). *Make the Best of Cross-lingual Transfer: Evidence from POS Tagging with Over 100 Languages*. ACL.
- **Pfeiffer, J., et al.** (2020). *MAD-X: An Adapter-Based Framework for Multi-Task Cross-Lingual Transfer*. EMNLP.

## Vitality and ethics-adjacent

- **Lewis, M. P., & Simons, G. F.** (2010). *Assessing endangerment: Expanding Fishman's GIDS*. Revue Roumaine de Linguistique. (Origin of EGIDS scale.)
- **UNESCO** (2003). *Language Vitality and Endangerment*. UNESCO Ad Hoc Expert Group.
- **Eberhard, D. M., Simons, G. F., Fennig, C. D.** (eds.). *Ethnologue: Languages of the World* (current edition). SIL International. https://www.ethnologue.com/

## Refresh procedure

- WALS is essentially frozen (last full update 2013; minor patches via Zenodo).
- Grambank refreshed annually via CLLD.
- URIEL refresh requires recomputing the cached `uriel_top100_distances.json` from the latest CMU release.
- Glottolog refreshes 1-2× per year.
- Joshi class assignments: re-evaluate annually as new datasets ship.
