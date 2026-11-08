library(eulob)

# ============================================================
# EU-LOB: pruebas del catálogo de 19 ámbitos
# ============================================================

countries <- eulob_countries()
registers <- eulob_registers()

de <- eulob_lobbies(country = "DE")
ue <- eulob_lobbies(country = "UE")
all <- eulob_lobbies()

# 1. Integridad general

expected_entities <- c(
  AT = 487L,
  BE = 194L,
  CY = 382L,
  CZ = 134L,
  DE = 7181L,
  EE = 2643L,
  ES = 621L,
  FI = 1690L,
  FR = 4117L,
  GR = 10L,
  IE = 3049L,
  IT = 1346L,
  LT = 432L,
  LU = 120L,
  LV = 24L,
  PL = 704L,
  RO = 109L,
  UE = 18447L,
  UK = 575L
)

actual_entities <- setNames(
  countries$n_entities,
  countries$country
)

stopifnot(
  nrow(countries) == 19L,
  setequal(countries$country, names(expected_entities)),
  sum(countries$n_entities) == 42265L,
  nrow(registers) == 21L,
  identical(
    unname(actual_entities[names(expected_entities)]),
    unname(expected_entities)
  )
)

# 2. Integridad de los registros

for (country in names(expected_entities)) {
  stopifnot(
    nrow(eulob_registers(country)) == (if (country == 'IT') 3L else 1L),
    nrow(eulob_lobbies(country = country)) > 0L
  )
}

# 3. Conservación de Alemania y Unión Europea

stopifnot(
  nrow(de) == 7363L,
  nrow(ue) == 18497L
)

# 4. Integridad del catálogo de denominaciones

stopifnot(
  nrow(all) == 42599L,
  length(unique(all$name_id)) == 40476L,
  length(unique(all$country)) == 19L
)

# 5. Búsqueda

results <- eulob_search("European", limit = 10L)

stopifnot(
  is.data.frame(results),
  nrow(results) > 0L,
  nrow(results) <= 10L
)

cat("TODAS LAS PRUEBAS DEL CATÁLOGO: OK\\n")
