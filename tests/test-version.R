library(eulob)

version <- eulob_version()

stopifnot(
  inherits(version, "package_version"),
  as.character(version) ==
    as.character(utils::packageVersion("eulob"))
)

cat("TEST VERSION: OK\n")
