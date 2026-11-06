library(eulob)

all <- eulob_cross_registers()
three <- eulob_cross_registers(min_countries = 3L)
g <- eulob_cross_registers("Grünenthal GmbH")
limited <- eulob_cross_registers(limit = 10L)
empty <- eulob_cross_registers("nonexistent_name_xyz_123")

stopifnot(
  length(unique(all$name_id)) == 1027L,
  nrow(all) == 2095L,
  length(unique(three$name_id)) == 7L,
  nrow(g) == 3L,
  setequal(g$country, c("DE", "IE", "UE")),
  length(unique(limited$name_id)) == 10L,
  nrow(limited) == 32L,
  nrow(empty) == 0L,
  identical(names(empty), names(all))
)

expect_error <- function(expr) {
  inherits(tryCatch(expr, error = identity), "error")
}

stopifnot(
  expect_error(eulob_cross_registers(name = "")),
  expect_error(eulob_cross_registers(name = NA_character_)),
  expect_error(eulob_cross_registers(min_countries = 0)),
  expect_error(eulob_cross_registers(min_countries = 1.5)),
  expect_error(eulob_cross_registers(limit = 0))
)

cat("TEST CROSS REGISTERS: OK\n")
