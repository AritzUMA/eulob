library(eulob)

# Unicode normalization must match the catalog index.
pairs <- list(
  c("Straße", "Strasse"),
  c("Grayling", "GRAYLING"),
  c("Straße", "STRASSE")
)

for (pair in pairs) {
  for (method in c("fixed", "cosine", "jaccard", "jw", "dl")) {
    a <- eulob_search(
      pair[1], method = method, limit = 20L
    )
    b <- eulob_search(
      pair[2], method = method, limit = 20L
    )

    stopifnot(
      identical(a$name_id, b$name_id),
      identical(a$country, b$country)
    )

    if ("similarity" %in% names(a)) {
      stopifnot(
        isTRUE(all.equal(
          a$similarity, b$similarity,
          tolerance = 1e-12
        ))
      )
    }
  }
}

# Canonically equivalent Unicode spellings.
composed <- "\u00c9lectricit\u00e9"
decomposed <- "E\u0301lectricite\u0301"

a <- eulob_search(composed, method = "cosine", limit = 10L)
b <- eulob_search(decomposed, method = "cosine", limit = 10L)

stopifnot(
  identical(a$name_id, b$name_id),
  isTRUE(all.equal(a$similarity, b$similarity))
)

cat("OK: normalización Unicode coherente\n")
