# Understanding the EU-LOB Catalogue

## Introduction

EU-LOB is a catalogue of names and entries recorded in European lobbying
and transparency registers.

This vignette describes the package’s territorial coverage, catalogue
indexes, identifiers and methodological limitations.

## Territorial and register coverage

The bundled catalogue includes 19 territorial scopes and 21 registers.

``` r

library(eulob)
eulob_countries()
#>    country n_names n_entities
#> 1       AT     499        487
#> 2       BE     194        194
#> 3       CY     384        382
#> 4       CZ     134        134
#> 5       DE    7359       7181
#> 6       EE    2643       2643
#> 7       ES     622        621
#> 8       FI    1395       1690
#> 9       FR    4064       4117
#> 10      GR      56         56
#> 11      IE    3057       3049
#> 12      IT    1317       1346
#> 13      LT     366        432
#> 14      LU     160        120
#> 15      LV      24         24
#> 16      PL     655        658
#> 17      RO     107        109
#> 18      UE   18483      18447
#> 19      UK     575        575
eulob_registers()
#>    country                                    register n_names n_entities
#> 1       AT                  Austrian Lobbying Register     499        487
#> 2       BE              Belgian Chamber Lobby Register     194        194
#> 3       CY                    Cyprus Lobbying Register     384        382
#> 4       CZ                                 Czech RELOB     134        134
#> 5       DE                       German Lobby Register    7359       7181
#> 6       EE                     Estonian Lobby Meetings    2643       2643
#> 7       ES       Spanish CNMC Interest Groups Register     622        621
#> 8       FI               Finnish Transparency Register    1395       1690
#> 9       FR                       French HATVP Register    4064       4117
#> 10      GR                     Greek Lobbying Register      56         56
#> 11      IE                  Irish Register of Lobbying    3057       3049
#> 12      IT                         Camera dei Deputati     455        455
#> 13      IT                      Italian MIMIT Register     754        752
#> 14      IT            Tuscany Interest Groups Register     139        139
#> 15      LT               Lithuanian Lobbyists Register     366        432
#> 16      LU Luxembourg Chamber Interest Representatives     160        120
#> 17      LV                   Latvian Lobbying Register      24         24
#> 18      PL       Polish Professional Lobbying Register     655        658
#> 19      RO                  Romanian Lobbying Register     107        109
#> 20      UE                    EU Transparency Register   18483      18447
#> 21      UK            UK Consultant Lobbyists Register     575        575
```

The code `UE` identifies the EU Transparency Register. The United
Kingdom is included separately.

Historical Netherlands observations are retained in the upstream
research data, but Netherlands entries are excluded from the searchable
catalogue because individual entities could not be reliably identified.

## Catalogue size

The distributed catalogue contains:

- 40,482 normalized name records.
- 42,599 name-to-register relationships.
- 42,265 distinct country-register-identifier entries.
- 18,279 normalized-name candidate pairs.

The first three quantities represent different indexing units. Candidate
pairs are not additional lobbying organizations.

## Internal data organization

The package distributes three RDS objects in `inst/extdata/catalog/`.

### Names index

`names.rds` contains:

- `name_id`
- `name_normalized`
- `name`
- `n_entities`
- `n_countries`

Each row represents a normalized-name identifier.

### Name-to-register relationships

`name_ids.rds` contains:

- `name_id`
- `name_normalized`
- `name`
- `country`
- `register`
- `lobby_id`

These relationships link names to entries within individual registers
and territorial scopes.

### Normalized candidate index

`eulob_normalized_candidates.rds` supports the exploratory matching
functionality provided by
[`eulob_search_normalized()`](https://eulob.lobbyresearch.org/reference/eulob_search_normalized.md).

It contains candidate name pairs and matching attributes, not an
independent collection of organizations.

## Understanding identifiers

`name_id` identifies a normalized name in the catalogue. It is not a
harmonized European legal entity identifier.

`lobby_id` is specific to a source register. It may correspond to an
official registration number, a source-derived key or another
source-specific identifier.

A normalized name can be associated with multiple register entries, and
different recorded names may refer to one organization.

## Explore catalogue relationships

``` r

head(eulob_lobbies(country = "ES"), 5)
#>                                                            name_id
#> 1 0adc32d5cc1bcec043fd3530e8e59cdce829e6e171a5b301e21b644e5ba0ee8b
#> 2 937b5357beacf0c4ba17cc69b272b7115c6247c5168bbfc517a9956051b0a558
#> 3 3d87ee70c21c618d8c36d3c9dd3e85bcb98c378fcf7e36b588241c237f75c779
#> 4 d4895baac056124012490d9ced8fc1068c020aae88d86a104d3ec8ef76b52b1a
#> 5 015a5f561afb733fb07a15675c473af0287e6f3b275bf0fec4c5b693691f30d2
#>                                             name
#> 1                            19N Strategies S.L.
#> 2 3C COMPLIANCE CORPORATE COMPLIANCE CONSULTANTS
#> 3                 ABC Arquitectura Modular, S.L.
#> 4                       ABECADE MANAGEMENT, S.L.
#> 5     ABS CONSULTORIA Y CONTROL DEL GASTO,  S.L.
#>                                  name_normalized country
#> 1                            19n strategies s.l.      ES
#> 2 3c compliance corporate compliance consultants      ES
#> 3                 abc arquitectura modular, s.l.      ES
#> 4                       abecade management, s.l.      ES
#> 5      abs consultoria y control del gasto, s.l.      ES
#>                                register
#> 1 Spanish CNMC Interest Groups Register
#> 2 Spanish CNMC Interest Groups Register
#> 3 Spanish CNMC Interest Groups Register
#> 4 Spanish CNMC Interest Groups Register
#> 5 Spanish CNMC Interest Groups Register
#>                                                                             lobby_id
#> 1                              https://rgi.cnmc.es/gruposdeinteres/19n-strategies-sl
#> 2 https://rgi.cnmc.es/gruposdeinteres/3c-compliance-corporate-compliance-consultants
#> 3                    https://rgi.cnmc.es/gruposdeinteres/abc-arquitectura-modular-sl
#> 4                          https://rgi.cnmc.es/gruposdeinteres/abecade-management-sl
#> 5               https://rgi.cnmc.es/gruposdeinteres/abs-consultoria-control-gasto-sl
head(eulob_lobbies(country = "DE"), 5)
#>                                                            name_id
#> 1 9a1ef4c8cf286515d6e76a4a8c92965338bf4e4087a4d3f78ad19b748820d2a6
#> 2 68a9756c563e8b2bd327aed33127987f94719256fa8480f8ee893227fc62ada3
#> 3 0dcf267ca8079e8e236450bb5204f5e8e5d5f82c023aa91b794e8f2d1f5d7c32
#> 4 25af054d715ea23bee0183ed153c031c4c1dd3e8209a147491f7829f6991973d
#> 5 fbb566495f6e31ff6331281d68ef5885edb74bb051a766aec8a518e5144a976f
#>                                                   name
#> 1          .ausgestrahlt - gemeinsam gegen Atomenergie
#> 2       'Biodiversity in Good Company' Initiative e.V.
#> 3 "Aktiv für eine nachhaltige öffentliche Beschaffung"
#> 4                               „Bargeld zählt!“ e. V.
#> 5                                       "Bits & Bäume"
#>                                        name_normalized country
#> 1          .ausgestrahlt - gemeinsam gegen atomenergie      DE
#> 2       'biodiversity in good company' initiative e.v.      DE
#> 3 "aktiv für eine nachhaltige öffentliche beschaffung"      DE
#> 4                               „bargeld zählt!“ e. v.      DE
#> 5                                       "bits & bäume"      DE
#>                register lobby_id
#> 1 German Lobby Register  R006946
#> 2 German Lobby Register  R003246
#> 3 German Lobby Register  R005719
#> 4 German Lobby Register  R007195
#> 5 German Lobby Register  R005517
```

Register-level counts can be examined with:

``` r

eulob_sources(country = "IT")
#>   country                         register n_names n_entities
#> 1      IT              Camera dei Deputati     455        455
#> 2      IT           Italian MIMIT Register     754        752
#> 3      IT Tuscany Interest Groups Register     139        139
```

`n_names` counts distinct name identifiers. `n_entities` counts distinct
register entries under the relevant register or territorial grouping.

Neither represents globally deduplicated legal organizations.

## Name searches

[`eulob_search()`](https://eulob.lobbyresearch.org/reference/eulob_search.md)
performs direct textual searches using cosine similarity by default.

Supported alternatives include Jaccard, Jaro-Winkler,
Damerau-Levenshtein and literal substring search.

``` r

head(eulob_search("association", limit = 5))
#>                                                            name_id
#> 1 0b55697294d8e327c1a8c74cd0f7ca92f13de122ae855ebacbffbeda7ae411d8
#> 2 331695501b01339e839bfc135728b55f78ef86e64505e00b009809dcbbc11b55
#> 3 331695501b01339e839bfc135728b55f78ef86e64505e00b009809dcbbc11b55
#> 4 9d6c5daa7e249c736f5c77aa030384df6f7f61eb28fb3e8a53ed65f8b6d0cf2a
#> 5 1ee04df15601d8a5cb9e7f9af2495b6bc8a0164558b5fc1fba138463a7b97461
#>                name country                      register         lobby_id
#> 1 SCION Association      UE      EU Transparency Register 7144255101975-12
#> 2   GSM Association      IE    Irish Register of Lobbying             3893
#> 3   GSM Association      LT Lithuanian Lobbyists Register LOB-JA-2026-0040
#> 4   KNX ASSOCIATION      UE      EU Transparency Register 0042312101158-89
#> 5   PRI Association      DE         German Lobby Register          R004486
#>   similarity
#> 1  0.8764598
#> 2  0.8451543
#> 3  0.8451543
#> 4  0.8451543
#> 5  0.8451543
head(eulob_search(
  "universidad",
  method = "fixed",
  limit = 5
))
#>                                                            name_id
#> 1 8e289c45060039076c027f2863bffe3754c61b739de87d090ac1ff37bb042686
#> 2 8c0ee1a085a591e0c1b17bc1feba418db99dedf3f27493427958ec49f25f96fd
#> 3 e4285c165934ab6e7338195ec7c9ef94bd7821074835cfcbef5417d2fd046325
#> 4 37305b3246e68176be0d88fbd2fe42bb30af59208a4c32d886099b8566747a66
#> 5 dd8d39fbefab64f15f58c7b74b5a53f5e4a5ebd5d60dac2d2d59463130858cff
#>                                                                                name
#> 1                                                AP institute | Universidad Nebrija
#> 2 Asociación de Universidades con Titulaciones en Información y Comunicación (ATIC)
#> 3                 Conferencia de Rectores y Rectoras de las Universidades Españolas
#> 4                                Conselho de Reitores das universidades portuguesas
#> 5                                   Faculdade de Ciências da Universidade de Lisboa
#>   country                              register
#> 1      UE              EU Transparency Register
#> 2      ES Spanish CNMC Interest Groups Register
#> 3      UE              EU Transparency Register
#> 4      UE              EU Transparency Register
#> 5      UE              EU Transparency Register
#>                                                                                                  lobby_id
#> 1                                                                                        8897419105147-11
#> 2 https://rgi.cnmc.es/gruposdeinteres/asociacion-universidades-titulaciones-informacion-comunicacion-atic
#> 3                                                                                         071771920040-91
#> 4                                                                                         688867827027-92
#> 5                                                                                         103316717831-58
```

[`eulob_search_normalized()`](https://eulob.lobbyresearch.org/reference/eulob_search_normalized.md)
additionally provides strict and exploratory retrieval through its
candidate index.

``` r

head(eulob_search_normalized(
  "association",
  method = "strict",
  limit = 5
))
#>  [1] country               register              lobby_id             
#>  [4] name                  matched_name          match_type           
#>  [7] similarity            evidence              match_level          
#> [10] requires_match_review identity_verified     candidate_relevance  
#> [13] candidate_relation    candidate_filter     
#> <0 rows> (or 0-length row.names)
```

## Shared names across registers

``` r

head(eulob_cross_registers(
  min_countries = 2L,
  limit = 5L
))
#>                                                            name_id
#> 1 e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 2 e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 3 e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 4 e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 5 1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 6 1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#>                                   name country
#> 1                              Blic Oy      FI
#> 2                              Blic Oy      GR
#> 3                              BLIC OY      PL
#> 4                              Blic Oy      UE
#> 5 Ontario Teachers' Pension Plan Board      DE
#> 6 Ontario Teachers' Pension Plan Board      FI
#>                                register        lobby_id n_countries n_entities
#> 1         Finnish Transparency Register            2257           4          4
#> 2               Greek Lobbying Register              56           4          4
#> 3 Polish Professional Lobbying Register           00651           4          4
#> 4              EU Transparency Register 687078815005-93           4          4
#> 5                 German Lobby Register         R000355           4          4
#> 6         Finnish Transparency Register            1496           4          4
```

A shared normalized name does not demonstrate that different register
entries belong to the same legal entity.

## Methodological limitations

Important considerations include:

- Registers may use different inclusion criteria.
- Reporting obligations and update schedules can vary.
- Entries may represent organizations, individuals, participant names or
  other source-specific units.
- Identical normalized names do not prove common identity.
- Different names may refer to the same organization.
- Register counts are not direct measures of lobbying activity.
- Absence from a register does not establish absence of lobbying.
- Search candidates require independent interpretation.

## Reproducibility

The package distributes a fixed catalogue snapshot rather than
performing live queries to institutional registers.

``` r

eulob_version()
#> [1] '0.2.1.9000'
eulob_info()
#> $project
#> [1] "EU-LOB"
#> 
#> $full_name
#> [1] "An Open and Incremental Database of Registered Lobbying Organizations in the European Union"
#> 
#> $package
#> [1] "eulob"
#> 
#> $version
#> [1] "0.2.1.9000"
#> 
#> $repository
#> [1] NA
#> 
#> $data_version
#> [1] NA
```

Researchers should report the package version, search parameters and
selection criteria used in their analyses.
