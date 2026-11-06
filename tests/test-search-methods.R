library(eulob)

# Default configuration
stopifnot(
  identical(formals(eulob_search)$method, "cosine"),
  identical(formals(eulob_search)$q, 2L),
  is.null(formals(eulob_search)$min_similarity)
)

# Default approximate search
x <- eulob_search("Siemens Mobilty", limit = 5L)

stopifnot(
  is.data.frame(x),
  nrow(x) == 5L,
  x$name[1] == "Siemens Mobility GmbH",
  "similarity" %in% names(x),
  all(x$similarity >= 0 & x$similarity <= 1),
  all(diff(x$similarity) <= 0)
)

# All methods
for (method in c("cosine", "jaccard", "jw", "dl")) {
  result <- eulob_search(
    "Siemens Mobilty",
    method = method,
    limit = 5L
  )

  stopifnot(
    is.data.frame(result),
    "similarity" %in% names(result),
    nrow(result) <= 5L
  )
}

# Minimum similarity
filtered <- eulob_search(
  "Siemens Mobilty",
  min_similarity = 0.5,
  limit = 10L
)

stopifnot(all(filtered$similarity >= 0.5))

# Original fixed search
fixed <- eulob_search(
  "Siemens",
  method = "fixed",
  limit = 5L
)

stopifnot(
  is.data.frame(fixed),
  !"similarity" %in% names(fixed),
  all(grepl("siemens", tolower(fixed$name), fixed = TRUE))
)

# Country filter
de <- eulob_search(
  "Siemens",
  country = "DE",
  limit = 10L
)

stopifnot(all(de$country == "DE"))

# Invalid arguments
expect_error <- function(expr) {
  inherits(tryCatch(expr, error = identity), "error")
}

stopifnot(
  expect_error(eulob_search("test", method = "invalid")),
  expect_error(eulob_search("test", min_similarity = -1)),
  expect_error(eulob_search("test", min_similarity = 2)),
  expect_error(eulob_search("test", q = 0)),
  expect_error(eulob_search("test", p = -0.1))
)

cat("TEST SEARCH METHODS: OK\n")
