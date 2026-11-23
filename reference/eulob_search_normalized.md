# Search normalized lobbying names and candidate equivalences

Searches original lobbying registrations using a conservative nominal
matching method or an expanded exploratory method.

## Usage

``` r
eulob_search_normalized(
  query,
  method = c("strict", "exploratory", "both"),
  limit = 100L,
  min_similarity = 0.88,
  candidate_filter = c("focused", "all")
)
```

## Arguments

- query:

  A single non-empty organization name.

- method:

  One of `"strict"`, `"exploratory"` or `"both"`.

- limit:

  Maximum number of name records to return.

- min_similarity:

  Minimum similarity for exploratory fuzzy candidates, from 0 to 1.

- candidate_filter:

  Use `"focused"` to prioritize lexical matches, or `"all"` to preserve
  all exploratory candidates.

## Details

Strict mode includes exact name matches, documented registration aliases
and highly conservative orthographic candidates. Exploratory mode also
includes fuzzy and shared-prefix candidates. The both option returns the
expanded results with their matching levels identified. No method
verifies common legal identity.

## Value

A data frame retaining the original country, register, lobby identifier
and name, with matching evidence, similarity and review indicators.
