# Registers represented in the EU-LOB catalogue

Return the registers and their counts from the package's existing
catalogue indexes. No external metadata file is needed.

## Usage

``` r
eulob_sources(country = NULL, register = NULL, fields = NULL)
```

## Arguments

- country:

  Optional character vector of country codes.

- register:

  Optional character vector of register names.

- fields:

  Optional character vector of columns to return.

## Value

A data.frame containing country, register, n_names and n_entities, or a
selection of these columns.

## Details

Counts are derived from the existing catalogue. This function does not
provide institutional URLs, licences or snapshot statistics, which are
not contained in these indexes.

## See also

\[eulob_registers()\]

## Examples

``` r
eulob_sources()
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
eulob_sources(country = "ES")
#>   country                              register n_names n_entities
#> 1      ES Spanish CNMC Interest Groups Register     622        621
eulob_sources(country = "IT")
#>   country                         register n_names n_entities
#> 1      IT              Camera dei Deputati     455        455
#> 2      IT           Italian MIMIT Register     754        752
#> 3      IT Tuscany Interest Groups Register     139        139
eulob_sources(fields = c("country", "register"))
#>    country                                    register
#> 1       AT                  Austrian Lobbying Register
#> 2       BE              Belgian Chamber Lobby Register
#> 3       CY                    Cyprus Lobbying Register
#> 4       CZ                                 Czech RELOB
#> 5       DE                       German Lobby Register
#> 6       EE                     Estonian Lobby Meetings
#> 7       ES       Spanish CNMC Interest Groups Register
#> 8       FI               Finnish Transparency Register
#> 9       FR                       French HATVP Register
#> 10      GR                     Greek Lobbying Register
#> 11      IE                  Irish Register of Lobbying
#> 12      IT                         Camera dei Deputati
#> 13      IT                      Italian MIMIT Register
#> 14      IT            Tuscany Interest Groups Register
#> 15      LT               Lithuanian Lobbyists Register
#> 16      LU Luxembourg Chamber Interest Representatives
#> 17      LV                   Latvian Lobbying Register
#> 18      PL       Polish Professional Lobbying Register
#> 19      RO                  Romanian Lobbying Register
#> 20      UE                    EU Transparency Register
#> 21      UK            UK Consultant Lobbyists Register
```
