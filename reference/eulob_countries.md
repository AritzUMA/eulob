# List Countries and Territorial Registers in EU-LOB

Lists the territorial codes represented in the bundled EU-LOB catalogue
and reports the number of distinct names and registered entities
associated with each code.

## Usage

``` r
eulob_countries(data_dir = NULL)
```

## Arguments

- data_dir:

  Must be \`NULL\`. External catalogue directories are not supported in
  this version.

## Value

A data frame with columns:

- country:

  Territorial or register code.

- n_names:

  Number of distinct \`name_id\` values.

- n_entities:

  Number of distinct register and \`lobby_id\` combinations within the
  code.

## Details

The catalogue contains national lobbying registers and the supranational
EU Transparency Register. The code \`"UE"\` identifies the latter and is
not an ISO country code.

Counts are computed from the bundled catalogue. They describe indexed
records, not deduplicated legal entities across Europe.

## See also

\[eulob_registers()\], \[eulob_lobbies()\]

## Examples

``` r
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
```
