# Read-only Nilgiris village identifier reconciliation

**Scope:** source-attribute reconciliation only. No datasets were changed, merged, or generated. No geometry was assigned to any Village Master record; no event linkage, geocoding, fuzzy matching, labels, ML, predictions, or scores was performed.

## Inputs and method

- `data/processed/nilgiris_villages.csv`: 102 Village Master records.
- `data/raw/admin/vb_soi_tn.kmz`: 58 KMZ placemarks selected by exact `district = The Nilgiris` after trim/case-fold comparison.
- `data/sources/spatial_boundary_audit.md`: prior KMZ structure and validity audit.

The comparison preserved source values. Exact identifier equality was evaluated first: Village Master `district_lgd_code`, `taluk_lgd_code`, `village_lgd_code` against KMZ `dtcode`, `sdcode`, `vlcode`. Only after no identifier match was found was an **exact**, case-folded and whitespace-normalised equality test made for English village name together with district and taluk code. This was an audit test, not an automatic join. No fuzzy, prefix, suffix, transliteration, Tamil-name, or phonetic comparison was used.

The Village Master contains English and Tamil names. The KMZ exposes English `village`, `subdistric`, `district`, plus `block`/`bkcode`, but no Tamil village/taluk fields. Therefore a Tamil cross-source equality comparison is unavailable.

## Results and classification

| Classification | Count | Evidence |
| --- | ---: | --- |
| `EXACT_IDENTIFIER_MATCH` | 40 | `village_lgd_code = vlcode`; all also have `district_lgd_code = dtcode = 587` and equal taluk/subdistrict codes. |
| `EXACT_NAME_AND_ADMIN_MATCH` | 0 | No unmatched Village Master/KMZ pair has exact normalised English village name plus equal district and taluk code. |
| `POSSIBLE_SOURCE_VERSION_DIFFERENCE` | 0 record-level | Dataset-level scope/vintage difference is plausible, but no pair has direct official identifier evidence sufficient to classify it record-by-record. |
| `NAME_DIFFERENCE_BUT_UNVERIFIED` | 0 | No automatic suffix/prefix, spelling, transliteration, or fuzzy candidates were generated. |
| `VILLAGE_MASTER_ONLY` | 62 | No Nilgiris KMZ `vlcode` equals the Village Master code; no exact English-name-and-admin candidate exists. |
| `KMZ_ONLY` | 18 | No Village Master `village_lgd_code` equals the KMZ `vlcode`. |
| `OTHER_UNRESOLVED` | 0 | No further cross-source correspondence was asserted. |

The 40 exact village-code matches are:

```text
635080, 635081, 635082, 635083, 635084, 635085, 635086, 635087, 635088, 635089,
635090, 635091, 635092, 635093, 635094, 635095, 635096, 635097, 635098, 635099,
635100, 635101, 635102, 635103, 635104, 635105, 635106, 635107, 635108, 635109,
635110, 635111, 635112, 635113, 635114, 635117, 635118, 635119, 635120, 635121
```

For these exact-identifier matches, 11 displayed English village names and 26 displayed English taluk names are identical as source strings. The remaining display-name differences do not weaken identifier equality, but they demonstrate that names must not be used as a substitute identifier. The Village Master Tamil values are retained only in the Village Master; the KMZ has no equivalent Tamil attributes.

## Administrative-code and field compatibility

- All 58 Nilgiris KMZ records have `dtcode = 587`, equal to the Village Master district LGD code.
- KMZ `sdcode` values are exactly the Village Master taluk-LGD domain: 5754, 5755, 5756, 5757, 5758, 5759.
- All 40 exact `vlcode` matches also agree on `sdcode = taluk_lgd_code`.
- KMZ provides `block`/`bkcode`; Village Master does not provide an equivalent block field, so those values cannot be compared.
- Nilgiris KMZ has no blank or duplicate `vlcode`; Village Master has no duplicate `village_lgd_code`.
- Statewide KMZ has 11 duplicate nonblank `vlcode` groups involving 38 records, but none occurs in Nilgiris. This reinforces that code uniqueness must be rechecked whenever the KMZ is expanded beyond Nilgiris.

## Village Master-only records

For every entry below, the exact evidence is the same: its Village Master district code is 587; its listed taluk code exists in the KMZ `sdcode` domain; however its `village_lgd_code` is absent from Nilgiris KMZ `vlcode`, and there is no exact normalised English village-name-and-admin match among KMZ-only records. KMZ has no Tamil village/taluk field with which to compare the preserved Tamil values. Classification: `VILLAGE_MASTER_ONLY`.

| Taluk LGD / English / Tamil | Village LGD code | Village English | Village Tamil |
| --- | --- | --- | --- |
| 5754 / Pandalur / பந்தலுார் | 932030 | Cherangode-1jenmam | சேரங்கோடு - 1 ஜென்மம் |
| 5754 / Pandalur / பந்தலுார் | 932033 | Cherangode-2 | சேரங்கோடு - 2 |
| 5754 / Pandalur / பந்தலுார் | 932036 | Cherangode-2jenmam | சேரங்கோடு - 2 ஜென்மம் |
| 5754 / Pandalur / பந்தலுார் | 932037 | Erumad-2 | எருமாடு - 2 |
| 5754 / Pandalur / பந்தலுார் | 932039 | Moonanad-1jenmam | மூனனாடு - 1 - ஜென்மம் |
| 5754 / Pandalur / பந்தலுார் | 932041 | Moonad-2 | மூனனாடு - 2 |
| 5754 / Pandalur / பந்தலுார் | 932044 | Moonanad-2jenmam | மூனனாடு - 2 ஜென்மம் |
| 5754 / Pandalur / பந்தலுார் | 932045 | Nelliyalam-1ca | நெல்லியாளம் - 1 - சீ ஏ |
| 5754 / Pandalur / பந்தலுார் | 932046 | Nelliyalam-2 | நெல்லியாளம் - 2 |
| 5754 / Pandalur / பந்தலுார் | 932048 | Nelliyalam-2jenman | நெல்லியாளம் - 2 ஜென்மம் |
| 5754 / Pandalur / பந்தலுார் | 932131 | Nelliyalam-1janmam | நெல்லியாளம் - 1 - ஜென்மம் |
| 5755 / Gudalur / கூடலூர் | 932079 | Cherumulli 1 | செறுமுள்ளி 1 |
| 5755 / Gudalur / கூடலூர் | 932081 | Devala 1 | தேவாலா 1 |
| 5755 / Gudalur / கூடலூர் | 932084 | Gudalur 1 | கூடலூர் 1 |
| 5755 / Gudalur / கூடலூர் | 932085 | Padanthorai 1 | பாடந்தொரை 1 |
| 5755 / Gudalur / கூடலூர் | 932087 | Cherumulli 2 | செறுமுள்ளி 2 |
| 5755 / Gudalur / கூடலூர் | 932090 | Padanthorai 2 | பாடந்தொரை 2 |
| 5755 / Gudalur / கூடலூர் | 932092 | Gudalur 2 | கூடலூர் 2 |
| 5755 / Gudalur / கூடலூர் | 932093 | Devala 2 | தேவாலா 2 |
| 5755 / Gudalur / கூடலூர் | 932095 | Gudalur - 2 Gr | கூடலூர் - 2 ஜி.ஆர். |
| 5755 / Gudalur / கூடலூர் | 932097 | Gudalur 1- Ca | கூடலூர் 1 - சி.ஏ |
| 5755 / Gudalur / கூடலூர் | 932099 | Gudalur 2 - Ca | கூடலூர் 2 - சிஏ |
| 5755 / Gudalur / கூடலூர் | 932101 | Devala 1 - Ca | தேவாலா 1 - சி.ஏ |
| 5755 / Gudalur / கூடலூர் | 932102 | Devala 2 - Ca | தேவாலா 2 - சிஏ |
| 5755 / Gudalur / கூடலூர் | 932104 | Padanthorai 1 -Ca | பாடந்தொரை 1 - சி.ஏ |
| 5755 / Gudalur / கூடலூர் | 932105 | Padanthorai 2 - Ca | பாடந்தொரை 2 - சிஏ |
| 5755 / Gudalur / கூடலூர் | 932106 | Cherumulli 2 Ca | செறுமுள்ளி 2 சி.ஏ |
| 5755 / Gudalur / கூடலூர் | 932108 | Sreemadurai - Ca | ஸ்ரீமதுரை - சி.ஏ |
| 5755 / Gudalur / கூடலூர் | 932110 | Gudalur 1 - Gr | கூடலூர் 1 ஜிஆர் |
| 5755 / Gudalur / கூடலூர் | 932112 | Ovalley 1 | ஒவேலி 1 |
| 5755 / Gudalur / கூடலூர் | 932113 | Ovalley 2 | ஒவேலி 2 |
| 5756 / Udhagai / உதகை | 932008 | Ebbanad 2 | எப்பநாடு 2 |
| 5756 / Udhagai / உதகை | 932010 | Kadanad 2 | கடநாடு 2 |
| 5756 / Udhagai / உதகை | 932013 | Kagguchi 2 | கக்குச்சி 2 |
| 5756 / Udhagai / உதகை | 932015 | Naduvattam | நடுவட்டம் |
| 5756 / Udhagai / உதகை | 932018 | Nanjanad2 | நஞ்சநாடு 2 |
| 5756 / Udhagai / உதகை | 932021 | Sholur | சோலுார் |
| 5756 / Udhagai / உதகை | 932022 | Thummanatty 2 | தும்மனட்டி 2 |
| 5757 / Kotagiri / கோத்தகிர | 931939 | Denad-Ii | தேனாடு - 2 |
| 5757 / Kotagiri / கோத்தகிர | 931944 | Jagathala-I | ஜகதளா - 1 |
| 5757 / Kotagiri / கோத்தகிர | 931946 | Jagathala-Ii | ஜகதளா - 2 |
| 5757 / Kotagiri / கோத்தகிர | 931966 | Kenkarai-Ii | கெங்கரை - 2 |
| 5757 / Kotagiri / கோத்தகிர | 931967 | Konavakorai -2 | கொணவக்கரை - 2 |
| 5757 / Kotagiri / கோத்தகிர | 931970 | Kotagiri 2 | கோத்தகிரி -2 |
| 5757 / Kotagiri / கோத்தகிர | 931972 | Kotagiri 3 | கோத்தகிரி - 3 |
| 5757 / Kotagiri / கோத்தகிர | 931974 | Nadhuhatty-2 | நடுஹட்டி -2 |
| 5757 / Kotagiri / கோத்தகிர | 931975 | Nedugula-Ii | நெடுகுளா - 2 |
| 5758 / Coonoor / குன்னூர் | 910517 | Hubathalai | உபதலை |
| 5758 / Coonoor / குன்னூர் | 931891 | Adigaratty 1 | அதிகரட்டி 1 |
| 5758 / Coonoor / குன்னூர் | 931894 | Athigaratty 2 | அதிகரட்டி 2 |
| 5758 / Coonoor / குன்னூர் | 931899 | Hulical 1 | உலிக்கல் 1 |
| 5758 / Coonoor / குன்னூர் | 931900 | Hulical 2 | உலிக்கல் 2 |
| 5758 / Coonoor / குன்னூர் | 931911 | Ketti 1 | கேத்தி 1 |
| 5758 / Coonoor / குன்னூர் | 931913 | Ketti 2 | கேத்தி 2 |
| 5758 / Coonoor / குன்னூர் | 931915 | Ketti 3 | கேத்தி 3 |
| 5758 / Coonoor / குன்னூர் | 931919 | Melur 2 | மேலூர் 2 |
| 5758 / Coonoor / குன்னூர் | 931931 | Melur 3 | மேலூர் 3 |
| 5759 / Kundah / குந்தா | 931981 | Balacola 2 | பாலகொலா 2 |
| 5759 / Kundah / குந்தா | 931984 | Ithalar 2 | இத்தலார் 2 |
| 5759 / Kundah / குந்தா | 931986 | Bikkatty | பிக்கட்டி |
| 5759 / Kundah / குந்தா | 931988 | Kil Kundah 1 | கீழ்குந்தா 1 |
| 5759 / Kundah / குந்தா | 931991 | Kil-Kundah 2 | கீழ்குந்தா-2 |

## KMZ-only records

All 18 retain `district = The Nilgiris`, `dtcode = 587`, and an `sdcode` present in the Village Master taluk domain, but their `vlcode` is absent from Village Master and no exact name-and-admin match exists. Classification: `KMZ_ONLY`. Values below are original KMZ attributes; blank block values and `bkcode` values are preserved.

| KMZ `vlcode` | `village` | `subdistric` / `sdcode` | `block` / `bkcode` |
| --- | --- | --- | --- |
| 252595 | Devarshola Tp | Gudalur / 5755 | *(blank)* / 0 |
| 252920 | Gudalur M | Gudalur / 5755 | *(blank)* / 0 |
| 252594 | Nelliyalam M | Panthalur / 5754 | *(blank)* / 0 |
| 252597 | O Valley Tp | Gudalur / 5755 | *(blank)* / 0 |
| 635116 | Hubbathala CT | Coonoor / 5758 | *(blank)* / *(blank)* |
| 252602 | Jagathala Tp | Kotagiri / 5757 | *(blank)* / 0 |
| 277302 | Wellington Cb | Coonoor / 5758 | *(blank)* / 0 |
| 252603 | Kethi Tp | Coonoor / 5758 | *(blank)* / 0 |
| 252605 | Coonoor M | Coonoor / 5758 | *(blank)* / 0 |
| 252607 | Adikaratti Tp | Coonoor / 5758 | *(blank)* / 0 |
| 252608 | Huligal Tp | Coonoor / 5758 | *(blank)* / 0 |
| 252609 | Bikketti Tp | Kundah / 5759 | *(blank)* / 0 |
| 252610 | Kilkunda Tp | Kundah / 5759 | *(blank)* / 0 |
| 252601 | Kotagiri Tp | Kotagiri / 5757 | *(blank)* / 0 |
| 252598 | Sholur Tp | Udhagamandalam / 5756 | *(blank)* / 0 |
| 252599 | Naduvattam Tp | Udhagamandalam / 5756 | *(blank)* / 0 |
| 252600 | Udhagamandalam M | Udhagamandalam / 5756 | *(blank)* / 0 |
| 635115 | Aravankad Ts CT | Coonoor / 5758 | *(blank)* / *(blank)* |

## Scope/vintage interpretation and decision

The available evidence is consistent with different administrative scope and/or vintage: 40 common village identifiers, 62 Village Master-only identifiers (many have numbered, `Ca`, `Gr`, or `janmam` display terms), and 18 KMZ-only records with displayed `Tp`, `M`, `CT`, or `Cb` descriptors. This is an evidence-based observation about source attributes, not a claim that any differently coded records correspond.

The KMZ cannot currently be treated as a complete authoritative modelling-unit boundary dataset for the 102-record Village Master universe. It demonstrably covers 40 exact Village Master identifiers, but available evidence does not establish whether the remaining 62 represent revenue villages, revenue subdivisions, or a different version/scope; likewise it does not explain the 18 KMZ-only units. Therefore it cannot be concluded that the KMZ covers all revenue villages; it covers an identified subset plus additional unmatched units.

Required next evidence, before any geometry association: authoritative source-version/vintage metadata and an official crosswalk or revised boundary release explaining all 80 unmatched identifiers. Until then, ML and event-to-village linkage remain **BLOCKED**.
