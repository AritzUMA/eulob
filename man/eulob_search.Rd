\name{eulob_search}
\alias{eulob_search}
\title{Search lobbying organizations}
\description{
Searches organization names using a case-insensitive substring match.
}
\usage{
eulob_search(query, country = NULL, limit = 100L, data_dir = NULL)
}
\arguments{
\item{query}{Non-empty character string to search for.}
\item{country}{Optional country code used to filter results.}
\item{limit}{Maximum number of results to return.}
\item{data_dir}{Reserved argument. Must be NULL when using the bundled RDS catalogue.}
}
\value{
A data frame with matching organizations and their official identifiers.
}
