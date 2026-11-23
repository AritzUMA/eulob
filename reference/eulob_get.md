# Retrieve a Lobbying Register Entry by Identifier

Retrieves entries from the bundled EU-LOB catalogue using an exact
register-specific identifier.

## Usage

``` r
eulob_get(country, lobby_id, register = NULL, data_dir = NULL)
```

## Arguments

- country:

  Territorial code, such as "GR", "PL" or "UE".

- lobby_id:

  Non-empty character string identifying the entry within its source
  register.

- register:

  Optional exact register name.

- data_dir:

  Must be NULL. External catalogue directories are not supported in this
  version.

## Value

A data frame with the same columns as \`eulob_lobbies()\`. Returns zero
rows when no entry matches.

## Details

Identifiers are compared literally, without normalization or approximate
matching. Leading zeros are preserved.

A register entry may have more than one recorded name. Consequently,
multiple rows may be returned.

Identifiers are source-specific and are not necessarily official
identifiers or globally unique legal entity IDs.

## See also

\`eulob_lobbies()\`, \`eulob_search()\`

## Examples

``` r
eulob_get("GR", "44")
#>                                                            name_id
#> 1 ed4d26868354dbb26afd51fcdca55c4f24e2af5a3d1dd9a21c14f8895c834cee
#>                                  name                    name_normalized
#> 1 ACTION PUBLIC RELATIONS HELLAS  ΕΠΕ action public relations hellas επε
#>   country                register lobby_id
#> 1      GR Greek Lobbying Register       44
eulob_get("PL", "00266")
#>                                                            name_id
#> 1 e09e89fb7cd84be5504bad05f844e68967faa57baa4a41f0d1b87c9bc5e759ae
#>                               name                  name_normalized country
#> 1 - Kancelaria Prawna Spółka jawna - kancelaria prawna spółka jawna      PL
#>                                register lobby_id
#> 1 Polish Professional Lobbying Register    00266
```
