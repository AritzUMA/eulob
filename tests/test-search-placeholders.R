library(eulob)

markers <- c("[ND] [ND]", "N/A")

# The original records must remain accessible.
all <- eulob_lobbies()

stopifnot(nrow(all) == 42599L)

found <- all[
  all$name %in% markers,
  ,
  drop = FALSE
]

stopifnot(
  nrow(found) == 7L,
  sum(found$name == "[ND] [ND]") == 6L,
  sum(found$name == "N/A") == 1L
)

# No placeholder may be returned as a search result.
for (method in c("fixed", "cosine", "jaccard", "jw", "dl")) {

  for (query in c("[ND]", "N/A", "Grayling")) {

    result <- eulob_search(
      query,
      method = method,
      limit = 100L
    )

    stopifnot(
      is.data.frame(result),
      !any(result$name %in% markers)
    )
  }
}

# Searching the exact marker still must not return that marker.
for (marker in markers) {

  result <- eulob_search(
    marker,
    method = "cosine",
    limit = 100L
  )

  stopifnot(!any(result$name == marker))
}

# A legitimate record must remain searchable after filtering.
legitimate <- eulob_search(
  "University Medical Center Groningen",
  method = "fixed",
  country = "UE",
  limit = 100L
)

stopifnot(
  nrow(legitimate) > 0L,
  any(grepl(
    "University Medical Center Groningen",
    legitimate$name,
    fixed = TRUE
  )),
  !any(legitimate$name %in% markers)
)

# Cross-register lookup must exclude missing-name markers,
# including when the minimum number of countries is one.
for (marker in markers) {

  result <- eulob_cross_registers(
    name = marker,
    min_countries = 1L
  )

  stopifnot(nrow(result) == 0L)
}

shared <- eulob_cross_registers(min_countries = 1L)

stopifnot(
  !any(shared$name %in% markers)
)

cat("OK: marcadores excluidos sin alterar datos originales\n")
