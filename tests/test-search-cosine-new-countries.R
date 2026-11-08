library(eulob)

# Catálogo europeo ampliado: 19 ámbitos con entradas.
countries <- eulob_countries()

stopifnot(
  nrow(countries) == 19L,
  sum(countries$n_entities) == 42265L
)

# Prueba real del algoritmo de coseno implementado por eulob.
results <- eulob_search(
  query = "Grayling",
  method = "cosine",
  q = 2L,
  limit = 30L
)

stopifnot(
  is.data.frame(results),
  nrow(results) > 0L,
  all(c("name", "country", "similarity") %in% names(results)),
  all(is.finite(results$similarity)),
  all(results$similarity >= 0 & results$similarity <= 1),
  all(diff(results$similarity) <= 1e-10)
)

# Resultado exacto conocido del registro europeo.
stopifnot(
  any(
    results$name == "Grayling" &
    results$country == "UE" &
    abs(results$similarity - 1) < 1e-10
  )
)

# Coincidencias previamente verificadas en países nuevos.
stopifnot(
  all(c("FR", "CZ", "PL", "UK") %in% results$country)
)

# Verificar búsqueda específica en cada nuevo país.
examples <- c(
  FR = "GRAYLING FRANCE",
  CZ = "Grayling Czech Republic s.r.o.",
  PL = "Grayling Poland Sp. z o.o.",
  UK = "Grayling Communications Limited"
)

for (country in names(examples)) {
  x <- eulob_search(
    query = examples[[country]],
    country = country,
    method = "cosine",
    q = 2L,
    limit = 5L
  )

  stopifnot(
    nrow(x) >= 1L,
    all(x$country == country),
    any(abs(x$similarity - 1) < 1e-10)
  )
}

cat("OK: búsqueda por coseno con nuevos países\n")
