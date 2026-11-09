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

# La composición del top 30 global cambia al incorporar
# nuevas entidades. No exigir países concretos en ese ranking.
# Las coincidencias conocidas se verifican por separado,
# mediante búsquedas restringidas a cada país.

# Verificar búsquedas exactas sobre nombres realmente indexados.
# No depender de denominaciones que puedan cambiar entre capturas.
for (country in c("FR", "CZ", "PL", "UK")) {
  entities <- eulob_lobbies(country = country)

  stopifnot(nrow(entities) > 0L)

  query <- entities$name[[1L]]

  x <- eulob_search(
    query = query,
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
