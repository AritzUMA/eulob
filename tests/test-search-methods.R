library(eulob)

# 1. Buscar una entidad conocida del catálogo ampliado.
# Verificamos comportamiento, no una posición histórica fija.

for (method in c("cosine", "jaccard", "jw", "dl")) {

  x <- eulob_search(
    query = "Grayling",
    method = method,
    limit = 10L
  )

  stopifnot(
    is.data.frame(x),
    nrow(x) > 0L,
    nrow(x) <= 10L,
    all(c("name", "country", "similarity") %in% names(x)),
    all(is.finite(x$similarity)),
    all(x$similarity >= 0 & x$similarity <= 1),
    all(diff(x$similarity) <= 1e-10)
  )

  cat("OK:", method, "-", nrow(x), "resultados\n")
}

# 2. Comprobar el método por defecto: coseno con bigramas.

default <- eulob_search("Grayling", limit = 10L)

cosine <- eulob_search(
  "Grayling",
  method = "cosine",
  q = 2L,
  limit = 10L
)

stopifnot(identical(default, cosine))

# 3. Una coincidencia exacta debe alcanzar similitud 1.

exact <- eulob_search(
  "Grayling",
  method = "cosine",
  limit = 10L
)

stopifnot(
  any(
    exact$name == "Grayling" &
    abs(exact$similarity - 1) < 1e-10
  )
)

# 4. El filtro de país debe respetarse.

fr <- eulob_search(
  "Grayling",
  country = "FR",
  method = "cosine",
  limit = 10L
)

stopifnot(
  nrow(fr) > 0L,
  all(fr$country == "FR")
)

# 5. El umbral mínimo debe respetarse.

filtered <- eulob_search(
  "Grayling",
  method = "cosine",
  min_similarity = 0.8,
  limit = 20L
)

stopifnot(
  all(filtered$similarity >= 0.8)
)

# 6. El método fixed debe mantener búsquedas literales.

fixed <- eulob_search(
  "Grayling",
  method = "fixed",
  limit = 10L
)

stopifnot(
  is.data.frame(fixed),
  nrow(fixed) > 0L,
  nrow(fixed) <= 10L,
  all(grepl("Grayling", fixed$name, ignore.case = TRUE))
)

# 7. Una búsqueda fija inexistente devuelve cero resultados.

empty <- eulob_search(
  "nonexistent_name_xyz_123",
  method = "fixed"
)

stopifnot(
  is.data.frame(empty),
  nrow(empty) == 0L
)

cat("\nOK: todos los métodos de búsqueda\n")
