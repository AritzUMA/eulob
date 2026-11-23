# Getting Started with eulob

## Introduction

`eulob` provides offline access to EU-LOB, a catalogue of names and
entries from European lobbying and transparency registers.

The catalogue contains 19 territorial scopes and 21 registers. Its
entries should not automatically be interpreted as unique legal
organizations.

## Load the package

``` r

library(eulob)
eulob_version()
#> [1] '0.2.1.9000'
```

## Explore countries and registers

List territorial coverage and available registers.

``` r

head(eulob_countries())
#>   country n_names n_entities
#> 1      AT     499        487
#> 2      BE     194        194
#> 3      CY     384        382
#> 4      CZ     134        134
#> 5      DE    7359       7181
#> 6      EE    2643       2643
head(eulob_registers())
#>   country                       register n_names n_entities
#> 1      AT     Austrian Lobbying Register     499        487
#> 2      BE Belgian Chamber Lobby Register     194        194
#> 3      CY       Cyprus Lobbying Register     384        382
#> 4      CZ                    Czech RELOB     134        134
#> 5      DE          German Lobby Register    7359       7181
#> 6      EE        Estonian Lobby Meetings    2643       2643
```

The code `UE` represents the supranational EU Transparency Register and
is not an ISO country code.

Filter the catalogue by country:

``` r

eulob_registers(country = "IT")
#>   country                         register n_names n_entities
#> 1      IT              Camera dei Deputati     455        455
#> 2      IT           Italian MIMIT Register     754        752
#> 3      IT Tuscany Interest Groups Register     139        139
eulob_sources(country = "ES")
#>   country                              register n_names n_entities
#> 1      ES Spanish CNMC Interest Groups Register     622        621
```

[`eulob_sources()`](https://eulob.lobbyresearch.org/reference/eulob_sources.md)
reports register-level counts using the existing catalogue indexes.

## Retrieve lobbying register entries

[`eulob_lobbies()`](https://eulob.lobbyresearch.org/reference/eulob_lobbies.md)
returns names and identifiers from the selected territorial scope or
register.

``` r

spanish <- eulob_lobbies(country = "ES")
head(spanish, 5)
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
```

An individual entry can be retrieved by its source-specific identifier:

``` r

if (nrow(spanish) > 0L) {
  entry <- spanish[1L, ]
  head(eulob_get(
    country = entry$country,
    lobby_id = entry$lobby_id,
    register = entry$register
  ))
}
#>                                                            name_id
#> 1 0adc32d5cc1bcec043fd3530e8e59cdce829e6e171a5b301e21b644e5ba0ee8b
#>                  name     name_normalized country
#> 1 19N Strategies S.L. 19n strategies s.l.      ES
#>                                register
#> 1 Spanish CNMC Interest Groups Register
#>                                                lobby_id
#> 1 https://rgi.cnmc.es/gruposdeinteres/19n-strategies-sl
```

## Search for organization names

The default search uses cosine similarity over character bigrams:

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
head(eulob_search("universidad", country = "ES", limit = 5))
#>                                                            name_id
#> 1 5598a9945c517a334e25f5e41229406c348b5e532b25984557bfa38bd4c5d82e
#> 2 67fe78c152983c9525071e48fd380cfebe3eb32064f86b4c0f352cecacb350fa
#> 3 8c0ee1a085a591e0c1b17bc1feba418db99dedf3f27493427958ec49f25f96fd
#> 4 a5d691602f0590cff31c2d99a37842bb0610bf509ac7b9694952a264f09962f3
#> 5 a79a331276d618cdcc8682a6ef5df43c3cdba62467eeed70da0131cf0f4c5bb5
#>                                                                                                  name
#> 1                                                                 FUNDACIÓN UNIVERSITARIA SAN ANTONIO
#> 2                                                                           Fundación Ciudadana Civio
#> 3                   Asociación de Universidades con Titulaciones en Información y Comunicación (ATIC)
#> 4                                                                       Energy Ingenieria Aplicada SL
#> 5 AGITCV (Asociación de Graduados en Ingeniería en Telecomunicación y TIC de la Comunidad Valenciana)
#>   country                              register
#> 1      ES Spanish CNMC Interest Groups Register
#> 2      ES Spanish CNMC Interest Groups Register
#> 3      ES Spanish CNMC Interest Groups Register
#> 4      ES Spanish CNMC Interest Groups Register
#> 5      ES Spanish CNMC Interest Groups Register
#>                                                                                                               lobby_id
#> 1                                              https://rgi.cnmc.es/gruposdeinteres/fundacion-universitaria-san-antonio
#> 2                                                        https://rgi.cnmc.es/gruposdeinteres/fundacion-ciudadana-civio
#> 3              https://rgi.cnmc.es/gruposdeinteres/asociacion-universidades-titulaciones-informacion-comunicacion-atic
#> 4                                                    https://rgi.cnmc.es/gruposdeinteres/energy-ingenieria-aplicada-sl
#> 5 https://rgi.cnmc.es/gruposdeinteres/agitcv-asociacion-graduados-ingenieria-telecomunicacion-tic-comunidad-valenciana
#>   similarity
#> 1  0.4879500
#> 2  0.3077935
#> 3  0.2963189
#> 4  0.2711631
#> 5  0.2607250
```

For case-insensitive literal substring matching, select
`method = "fixed"`:

``` r

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

Additional approximate name-search methods include Jaccard, Jaro-Winkler
and Damerau-Levenshtein.

These methods compare text, not semantic representations or verified
legal identities.

## Search normalized-name candidates

[`eulob_search_normalized()`](https://eulob.lobbyresearch.org/reference/eulob_search_normalized.md)
searches a separate bundled candidate index.

It supports three modes:

- `strict`: strict normalized-name candidates.
- `exploratory`: exploratory candidate matching.
- `both`: both candidate categories.

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

Candidate results are intended to assist manual assessment. They are not
evidence of verified legal identity.

## Find shared names across registers

[`eulob_cross_registers()`](https://eulob.lobbyresearch.org/reference/eulob_cross_registers.md)
identifies names appearing across multiple territorial scopes.

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

Names appearing in several registers are not necessarily the same legal
organization.

## Understand identifiers

The catalogue distinguishes:

- `name_id`: identifier for a normalized name.
- `name_normalized`: normalized name representation.
- `name`: recorded name.
- `country`: territorial or supranational scope.
- `register`: source register.
- `lobby_id`: register-specific identifier.

Some register identifiers originate from official registration systems;
others are derived from source records.

Identifiers should always be interpreted within their corresponding
register.

## Reproducibility

The bundled catalogue can be queried without an internet connection.
Record the package version, search methods and filters used in any
analysis.

``` r

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
eulob_version()
#> [1] '0.2.1.9000'
```

For details on the indexing structure and methodological limitations,
see *Understanding the EU-LOB Catalogue*.
