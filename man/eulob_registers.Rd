\name{eulob_registers}
\alias{eulob_registers}
\title{List lobbying registers}
\description{
Lists lobbying registers represented in the bundled catalogue.
}
\usage{
eulob_registers(country = NULL, data_dir = NULL)
}
\arguments{
\item{country}{Optional country code used to filter results.}
\item{data_dir}{Reserved argument. Must be NULL when using the bundled RDS catalogue.}
}
\value{
A data frame with country codes, register names and counts.
}
