\name{eulob_lobbies}
\alias{eulob_lobbies}
\title{Retrieve lobbying organizations}
\description{
Retrieves organization names and official register identifiers from the bundled catalogue.
}
\usage{
eulob_lobbies(country = NULL, register = NULL, data_dir = NULL)
}
\arguments{
\item{country}{Optional country code used to filter results.}
\item{register}{Optional lobbying register name used to filter results.}
\item{data_dir}{Reserved argument. Must be NULL when using the bundled RDS catalogue.}
}
\value{
A data frame with names, normalized names, name identifiers, countries, registers and lobby identifiers.
}
