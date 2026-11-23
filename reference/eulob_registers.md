# List Lobbying Registers in EU-LOB

Lists the lobbying registers included in the bundled catalogue,
optionally restricting the results to one territorial code.

## Usage

``` r
eulob_registers(country = NULL, data_dir = NULL)
```

## Arguments

- country:

  Optional single character string identifying a territorial code, such
  as \`"ES"\`, \`"DE"\` or \`"UE"\`. Leading and trailing whitespace is
  removed and the code is converted to uppercase.

- data_dir:

  Must be \`NULL\`. External catalogue directories are not supported in
  this version.

## Value

A data frame with columns:

- country:

  Territorial or register code.

- register:

  Name of the lobbying register.

- n_names:

  Number of distinct \`name_id\` values.

- n_entities:

  Number of distinct \`lobby_id\` values within the register.

If no register matches, the data frame has zero rows.

## Details

Results are ordered by territorial code and register name. The special
code \`"UE"\` refers to the EU Transparency Register. An unknown
territorial code returns an empty data frame.

## See also

\[eulob_countries()\], \[eulob_lobbies()\]

## Examples

``` r
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
eulob_registers(country = "ES")
#>   country                              register n_names n_entities
#> 1      ES Spanish CNMC Interest Groups Register     622        621
eulob_registers(country = "UE")
#>   country                 register n_names n_entities
#> 1      UE EU Transparency Register   18483      18447
```
