library(eulob)

info <- eulob_info()

stopifnot(
  is.list(info),
  identical(info$project, "EU-LOB"),
  identical(info$package, "eulob"),
  identical(
    info$version,
    as.character(utils::packageVersion("eulob"))
  )
)

cat("TEST INFO: OK\n")
