# Internal: load the catalogue bundled with the package.
.eulob_catalog <- function(table, data_dir = NULL) {
  stopifnot(table %in% c("names", "name_ids"))

  if (!is.null(data_dir)) {
    stop(
      "data_dir is not supported by the bundled RDS catalogue. ",
      "Omit data_dir to use the installed catalogue.",
      call. = FALSE
    )
  }

  path <- system.file(
    "extdata", "catalog", paste0(table, ".rds"),
    package = "eulob"
  )

  if (!nzchar(path)) {
    stop("EU-LOB catalogue file not found: ", table,
         call. = FALSE)
  }

  readRDS(path)
}

# Internal: validate optional country.
.eulob_country <- function(country) {
  if (is.null(country)) return(NULL)

  if (!is.character(country) ||
      length(country) != 1L ||
      is.na(country) ||
      !nzchar(trimws(country))) {
    stop("country must be a non-empty character string.",
         call. = FALSE)
  }

  toupper(trimws(country))
}

#' List Countries in the EU-LOB Catalogue
#'
#' @param data_dir Reserved for future external data sources.
#' @return Data frame with country, n_names and n_entities.
#' @export
eulob_countries <- function(data_dir = NULL) {
  x <- .eulob_catalog("name_ids", data_dir)

  countries <- sort(unique(x$country))

  result <- do.call(rbind, lapply(countries, function(cc) {
    y <- x[x$country == cc, , drop = FALSE]

    data.frame(
      country = cc,
      n_names = length(unique(y$name_id)),
      n_entities = nrow(unique(
        y[c("register", "lobby_id")]
      ))
    )
  }))

  rownames(result) <- NULL
  result
}

#' List Available Lobby Registers
#'
#' @param country Optional country code.
#' @param data_dir Reserved for future external data sources.
#' @return Data frame with register-level counts.
#' @export
eulob_registers <- function(country = NULL, data_dir = NULL) {
  x <- .eulob_catalog("name_ids", data_dir)
  country <- .eulob_country(country)

  if (!is.null(country)) {
    x <- x[x$country == country, , drop = FALSE]
  }

  keys <- unique(x[c("country", "register")])
  keys <- keys[order(keys$country, keys$register), , drop = FALSE]

  result <- lapply(seq_len(nrow(keys)), function(i) {
    y <- x[
      x$country == keys$country[i] &
      x$register == keys$register[i],
      ,
      drop = FALSE
    ]

    data.frame(
      country = keys$country[i],
      register = keys$register[i],
      n_names = length(unique(y$name_id)),
      n_entities = length(unique(y$lobby_id))
    )
  })

  if (!length(result)) {
    return(data.frame(
      country = character(),
      register = character(),
      n_names = integer(),
      n_entities = integer()
    ))
  }

  out <- do.call(rbind, result)
  rownames(out) <- NULL
  out
}

#' List Lobby Names
#'
#' @param country Optional country code.
#' @param register Optional register name.
#' @param data_dir Reserved for future external data sources.
#' @return Data frame with name-identifier relationships.
#' @export
eulob_lobbies <- function(country = NULL, register = NULL,
                          data_dir = NULL) {
  x <- .eulob_catalog("name_ids", data_dir)
  country <- .eulob_country(country)

  if (!is.null(country)) {
    x <- x[x$country == country, , drop = FALSE]
  }

  if (!is.null(register)) {
    stopifnot(
      is.character(register),
      length(register) == 1L,
      !is.na(register),
      nzchar(register)
    )
    x <- x[x$register == register, , drop = FALSE]
  }

  x <- x[
    order(x$name_normalized, x$country, x$lobby_id),
    c("name_id", "name", "name_normalized",
      "country", "register", "lobby_id"),
    drop = FALSE
  ]

  rownames(x) <- NULL
  x
}

#' Search Lobby Names
#'
#' Performs a case-insensitive literal substring search.
#'
#' @param query Text to search for.
#' @param country Optional country code.
#' @param limit Maximum number of results.
#' @param data_dir Reserved for future external data sources.
#' @return Data frame of matching name-identifier relationships.
#' @export
eulob_search <- function(query, country = NULL,
                         limit = 100L, data_dir = NULL) {
  if (!is.character(query) ||
      length(query) != 1L ||
      is.na(query) ||
      !nzchar(trimws(query))) {
    stop("query must be a non-empty character string.",
         call. = FALSE)
  }

  if (!is.numeric(limit) ||
      length(limit) != 1L ||
      is.na(limit) ||
      !is.finite(limit) ||
      limit < 1 ||
      limit != floor(limit) ||
      limit > .Machine$integer.max) {
    stop("limit must be a positive integer.", call. = FALSE)
  }

  x <- .eulob_catalog("name_ids", data_dir)
  country <- .eulob_country(country)

  if (!is.null(country)) {
    x <- x[x$country == country, , drop = FALSE]
  }

  matches <- grepl(
    tolower(query),
    x$name_normalized,
    fixed = TRUE
  )

  x <- x[matches, , drop = FALSE]

  x <- x[
    order(x$name_normalized, x$country, x$lobby_id),
    c("name_id", "name", "country", "register", "lobby_id"),
    drop = FALSE
  ]

  x <- head(x, as.integer(limit))
  rownames(x) <- NULL
  x
}
