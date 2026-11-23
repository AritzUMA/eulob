# Search Lobbying Organization Names

Searches organization names in the bundled EU-LOB catalogue using
configurable string-matching methods.

## Usage

``` r
eulob_search(
  query,
  country = NULL,
  limit = 100L,
  data_dir = NULL,
  method = "cosine",
  min_similarity = NULL,
  q = 2L,
  p = 0.1
)
```

## Arguments

- query:

  Non-empty character string to search for.

- country:

  Optional territorial code, such as \`"ES"\` or \`"UE"\`. Converted to
  uppercase before filtering.

- limit:

  Positive whole number specifying the maximum number of returned rows.
  Default is \`100L\`.

- data_dir:

  Must be \`NULL\`. External catalogue directories are not supported in
  this version.

- method:

  Matching algorithm. One of \`"cosine"\` (default), \`"jaccard"\`,
  \`"jw"\`, \`"dl"\` or \`"fixed"\`.

- min_similarity:

  Optional minimum similarity between 0 and 1. Default is \`NULL\`,
  meaning no threshold. Used only for approximate matching.

- q:

  Positive integer specifying the character q-gram length for cosine and
  Jaccard similarity. Default is \`2L\`.

- p:

  Jaro-Winkler prefix scaling factor between 0 and 0.25. Default is
  \`0.1\`. Used only with \`method = "jw"\`.

## Value

A data frame containing:

- name_id:

  Identifier associated with a normalized name.

- name:

  Recorded organization name.

- country:

  Territorial or register code.

- register:

  Name of the source register.

- lobby_id:

  Register-specific entry identifier.

- similarity:

  Numeric similarity score between 0 and 1, included only for
  approximate matching methods.

Results are limited to the requested number of rows. If no rows satisfy
the search criteria, an empty data frame with the corresponding columns
is returned.

## Details

The default method is cosine similarity using character bigrams
(\`method = "cosine", q = 2L\`).

Approximate matching is implemented using the \`stringdist\` package.
The available methods are:

\- \`"cosine"\`: cosine similarity of character q-grams. -
\`"jaccard"\`: Jaccard similarity of character q-grams. - \`"jw"\`:
Jaro-Winkler similarity. - \`"dl"\`: Damerau-Levenshtein similarity. -
\`"fixed"\`: case-insensitive literal substring matching.

Approximate methods return a similarity score between 0 and 1, where
higher values indicate greater string similarity.

When \`min_similarity = NULL\`, no minimum similarity threshold is
applied. Consequently, approximate methods may return low-scoring or
unrelated results when no close match exists. A positive threshold can
be specified to restrict the results.

The \`"fixed"\` method preserves the original substring-search behavior.
It does not calculate similarity scores and ignores the
approximate-matching parameters.

Results represent name-to-register-identifier relationships, not
necessarily unique legal entities. The same organization name may appear
in several registers.

Approximate results are ordered by decreasing similarity, followed by
normalized name, territorial code and register identifier. Fixed results
are ordered by normalized name, territorial code and register
identifier.

Similarity is lexical rather than semantic. High similarity does not
establish that two names refer to the same legal entity.

## See also

\[eulob_lobbies()\], \[eulob_countries()\]

## Examples

``` r
eulob_search("Siemens Mobilty", limit = 5)
#>                                                            name_id
#> 1 886cfb164a75037f241e58df09612262a680303566d75ee448edbd88548e96d5
#> 2 34df671592b1b4112b727f1364685b7c70c8769199f652abcf9f780e2679f4d0
#> 3 027cc69b2aa750fa82d22362969ca0fb749ac4306423fc08bc0ad0f87f766136
#> 4 027cc69b2aa750fa82d22362969ca0fb749ac4306423fc08bc0ad0f87f766136
#> 5 01e35ac5bf9b36d13ba9a1fb6c01d06009d09ada1f0a592c1b5176249bf0f106
#>                    name country                       register
#> 1      Siemens Mobility      BE Belgian Chamber Lobby Register
#> 2  SIEMENS MOBILITY SAS      FR          French HATVP Register
#> 3 Siemens Mobility GmbH      DE          German Lobby Register
#> 4 Siemens Mobility GmbH      EE        Estonian Lobby Meetings
#> 5            Siemens AG      DE          German Lobby Register
#>                                                                lobby_id
#> 1                                                      Siemens Mobility
#> 2                                                             833751431
#> 3                                                               R001892
#> 4 name:027cc69b2aa750fa82d22362969ca0fb749ac4306423fc08bc0ad0f87f766136
#> 5                                                               R001875
#>   similarity
#> 1  0.8970852
#> 2  0.7970811
#> 3  0.7768986
#> 4  0.7768986
#> 5  0.6236096
eulob_search("association", method = "fixed", limit = 5)
#>                                                            name_id
#> 1 a8f41729cfea39273ee33095a8c5fdb9496113088b22cc4b9b10f57e38e3f0da
#> 2 3499ebb98b68a54cf6e565d773efb0a724dff9306a23f514bc43f9754fe4cebb
#> 3 50698694a6c015e087e54b9f740105049e0ba6343666a0cb93f14f320db8ec0d
#> 4 a88daa1741da17b939b03f6c8476706d42d5dc4bfb1d60d8ffddf915e9a21ec3
#> 5 7e798e17b6d995d4ba9ae8bee95cf1ebb50604cd76f82f3f5ba7c5ff69ec934c
#>                                                  name country
#> 1             #ApresJ20 Association Covid Long France      UE
#> 2                           #NotInOurGame Association      UE
#> 3                           5G Automotive Association      UE
#> 4               5GAA - 5G Automotive Association e.V.      DE
#> 5 6G Smart Networks and Services Industry Association      UE
#>                   register         lobby_id
#> 1 EU Transparency Register 9164858100243-53
#> 2 EU Transparency Register  954575646509-16
#> 3 EU Transparency Register  802312827842-26
#> 4    German Lobby Register          R006931
#> 5 EU Transparency Register  944198631623-17
eulob_search("university", country = "UE", limit = 5)
#>                                                            name_id
#> 1 60ba06101b8c258aa6dbf5d01f41cc8853f1b99a4441aa358f1bc10efd1855ff
#> 2 54dc5fdb61a43c6211342c9145a0ddb47f430b6b239ce942d529deb1924c5766
#> 3 0fb5c4b5b9c122a95e140d55ffe921042e4bc36e0d9c4e8f1a10249e3c7f1846
#> 4 6897907a26009a77d34e48adf8eeedd5f014c0b0c0d690f2796a67d1de545213
#> 5 b85a1a866c0c7fe88231630e8e08277aa3f737557ac04ec46d62c726bdfadcbf
#>                      name country                 register         lobby_id
#> 1        CEVRO University      UE EU Transparency Register 6598206106012-61
#> 2        Ghent University      UE EU Transparency Register  006043210924-49
#> 3      Tampere University      UE EU Transparency Register  699681335670-44
#> 4 University of Liverpool      UE EU Transparency Register  533239893129-81
#> 5       Aarhus University      UE EU Transparency Register   62420437302-96
#>   similarity
#> 1  0.7745967
#> 2  0.7745967
#> 3  0.7647191
#> 4  0.7559289
#> 5  0.7500000
eulob_search("Siemens", method = "jw", limit = 5)
#>                                                            name_id
#> 1 01e35ac5bf9b36d13ba9a1fb6c01d06009d09ada1f0a592c1b5176249bf0f106
#> 2 01e35ac5bf9b36d13ba9a1fb6c01d06009d09ada1f0a592c1b5176249bf0f106
#> 3 7dc054c49058a066f596ee0b8849f14a8e3044daa4fa656aa5f66008d11296f9
#> 4 9cda2dfc4e5a85907a918ed9899876cc70feddbe035f61d80ca8f355eadd91e1
#> 5 8f266712cdfb6e0c986d3a72f253ac5a17d692582f70da3fe75ff550c047b58f
#>              name country                   register              lobby_id
#> 1      Siemens AG      DE      German Lobby Register               R001875
#> 2      Siemens AG      UE   EU Transparency Register         4266797770-31
#> 3     SIEMENS SPA      IT     Italian MIMIT Register 2025-1736414201805-96
#> 4   SIEMENS S.A.S      FR      French HATVP Register             562016774
#> 5 Siemens Limited      IE Irish Register of Lobbying                   284
#>   similarity
#> 1  0.9400000
#> 2  0.9400000
#> 3  0.9272727
#> 4  0.9076923
#> 5  0.8933333
eulob_search("zzzxxyy_no_existe_123", method = "fixed")
#> [1] name_id  name     country  register lobby_id
#> <0 rows> (or 0-length row.names)
```
