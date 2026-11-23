# Retrieve Lobbying Organization Names and Register Identifiers

Retrieves name-to-register-identifier relationships from the bundled
EU-LOB catalogue, with optional territorial and register filters.

## Usage

``` r
eulob_lobbies(country = NULL, register = NULL, data_dir = NULL)
```

## Arguments

- country:

  Optional territorial code such as \`"ES"\` or \`"UE"\`. The code is
  converted to uppercase.

- register:

  Optional single register name. Matching is exact and case-sensitive.

- data_dir:

  Must be \`NULL\`. External catalogue directories are not supported in
  this version.

## Value

A data frame with six columns:

- name_id:

  Identifier associated with a normalized name.

- name:

  Recorded organization name.

- name_normalized:

  Normalized form used for searching and ordering.

- country:

  Territorial or register code.

- register:

  Name of the source register.

- lobby_id:

  Register-specific entry identifier.

Filters without matches return a zero-row data frame.

## Details

Each row represents a recorded relationship between a name and an
identifier in a lobbying register. Rows should not be interpreted as
globally deduplicated legal entities.

\`name_id\` identifies a normalized name in the catalogue. \`lobby_id\`
is the identifier supplied for a register entry; its format varies
across registers and may be a URL.

Results are ordered by normalized name, territorial code and register
identifier. Register filtering uses exact matching.

## See also

\[eulob_search()\], \[eulob_registers()\]

## Examples

``` r
head(eulob_lobbies(country = "ES"))
#>                                                            name_id
#> 1 0adc32d5cc1bcec043fd3530e8e59cdce829e6e171a5b301e21b644e5ba0ee8b
#> 2 937b5357beacf0c4ba17cc69b272b7115c6247c5168bbfc517a9956051b0a558
#> 3 3d87ee70c21c618d8c36d3c9dd3e85bcb98c378fcf7e36b588241c237f75c779
#> 4 d4895baac056124012490d9ced8fc1068c020aae88d86a104d3ec8ef76b52b1a
#> 5 015a5f561afb733fb07a15675c473af0287e6f3b275bf0fec4c5b693691f30d2
#> 6 5011991eca8dae299031bfd66eb61ea6b5fcb06331cffdfaa325929fac6d0393
#>                                                                                      name
#> 1                                                                     19N Strategies S.L.
#> 2                                          3C COMPLIANCE CORPORATE COMPLIANCE CONSULTANTS
#> 3                                                          ABC Arquitectura Modular, S.L.
#> 4                                                                ABECADE MANAGEMENT, S.L.
#> 5                                              ABS CONSULTORIA Y CONTROL DEL GASTO,  S.L.
#> 6 ACEMA  (ASOCIACIÓN DE COMERCIANTES DE ELECTRODOMESTICOS, MUEBLES DE COCINA Y AUTONOMOS)
#>                                                                          name_normalized
#> 1                                                                    19n strategies s.l.
#> 2                                         3c compliance corporate compliance consultants
#> 3                                                         abc arquitectura modular, s.l.
#> 4                                                               abecade management, s.l.
#> 5                                              abs consultoria y control del gasto, s.l.
#> 6 acema (asociación de comerciantes de electrodomesticos, muebles de cocina y autonomos)
#>   country                              register
#> 1      ES Spanish CNMC Interest Groups Register
#> 2      ES Spanish CNMC Interest Groups Register
#> 3      ES Spanish CNMC Interest Groups Register
#> 4      ES Spanish CNMC Interest Groups Register
#> 5      ES Spanish CNMC Interest Groups Register
#> 6      ES Spanish CNMC Interest Groups Register
#>                                                                                                       lobby_id
#> 1                                                        https://rgi.cnmc.es/gruposdeinteres/19n-strategies-sl
#> 2                           https://rgi.cnmc.es/gruposdeinteres/3c-compliance-corporate-compliance-consultants
#> 3                                              https://rgi.cnmc.es/gruposdeinteres/abc-arquitectura-modular-sl
#> 4                                                    https://rgi.cnmc.es/gruposdeinteres/abecade-management-sl
#> 5                                         https://rgi.cnmc.es/gruposdeinteres/abs-consultoria-control-gasto-sl
#> 6 https://rgi.cnmc.es/gruposdeinteres/acema-asociacion-comerciantes-electrodomesticos-muebles-cocina-autonomos
head(eulob_lobbies(
  country = "DE",
  register = "German Lobby Register"
))
#>                                                            name_id
#> 1 0dcf267ca8079e8e236450bb5204f5e8e5d5f82c023aa91b794e8f2d1f5d7c32
#> 2 fbb566495f6e31ff6331281d68ef5885edb74bb051a766aec8a518e5144a976f
#> 3 9ad9ef30879f5f8b5b51dc5d66ff7f6b1b965205779c67ced787f9d0fc6696ed
#> 4 253350b3d6209c0331cddfad1f5c8d925701445cc647ba6fa9fbc7cb0aeab358
#> 5 319ac424ce6538458a34b07766bb9e9a38627090c6c6b3f407556bbc7de4aaab
#> 6 bc19ed20858c68a3cc02fa001557d927b388b7f18915f8de4e1b350ddcb9ec13
#>                                                   name
#> 1 "Aktiv für eine nachhaltige öffentliche Beschaffung"
#> 2                                       "Bits & Bäume"
#> 3                             "MINT Zukunft schaffen!"
#> 4                   "Was hab' ich?" gemeinnützige GmbH
#> 5                             #ErnährungswendeAnpacken
#> 6                                         #GenoDigital
#>                                        name_normalized country
#> 1 "aktiv für eine nachhaltige öffentliche beschaffung"      DE
#> 2                                       "bits & bäume"      DE
#> 3                             "mint zukunft schaffen!"      DE
#> 4                   "was hab' ich?" gemeinnützige gmbh      DE
#> 5                             #ernährungswendeanpacken      DE
#> 6                                         #genodigital      DE
#>                register lobby_id
#> 1 German Lobby Register  R005719
#> 2 German Lobby Register  R005517
#> 3 German Lobby Register  R004129
#> 4 German Lobby Register  R005522
#> 5 German Lobby Register  R003658
#> 6 German Lobby Register  R002985
```
