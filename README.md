# eulob

**eulob** is an R package for accessing and exploring EU-LOB,
an open and incremental database of registered lobbying
organizations in the European Union.

The package includes a local catalogue that can be queried
without an internet connection.

## Available lobbying registers

| Code | Register |
|------|----------|
| AT | Austrian Lobbying Register |
| CY | Cyprus Lobbying Register |
| DE | German Lobby Register |
| ES | Spanish CNMC Interest Groups Register |
| FI | Finnish Transparency Register |
| IE | Irish Register of Lobbying |
| LT | Lithuanian Lobbyists Register |
| RO | Romanian Lobbying Register |
| UE | EU Transparency Register |

The code UE represents the supranational EU register and
is not an ISO country code.

## Installation

Install from a local source checkout before the CRAN release:

    install.packages(".", repos = NULL, type = "source")

## Getting started

Load the package:

    library(eulob)

List available countries and registers:

    eulob_countries()
    eulob_registers()

Explore the Spanish register:

    eulob_registers(country = "ES")
    head(eulob_lobbies(country = "ES"))

Search for organizations:

    eulob_search("association", limit = 10)
    eulob_search("universidad", country = "UE", limit = 10)

Inspect package metadata:

    eulob_info()
    eulob_version()

## Main functions

- eulob_countries(): territorial coverage and counts.
- eulob_registers(): available lobbying registers.
- eulob_lobbies(): organization names and register identifiers.
- eulob_search(): case-insensitive substring search.
- eulob_info(): project and package metadata.
- eulob_version(): installed package version.

## Data structure

The bundled catalogue contains 31,238 distinct name records
and 32,664 name-to-register-identifier relationships.

These relationships do not necessarily represent distinct
legal entities.

The name_id field identifies a normalized name.
The lobby_id field contains a register-specific identifier,
which may be an official URL.

## Search limitations

Searches use case-insensitive literal substring matching
against normalized names.

The package does not currently provide fuzzy matching,
semantic search or cross-register entity resolution.

## Reproducibility

The catalogue is bundled with the package. Collection dates,
data provenance and independent catalogue versioning must
be documented before the first CRAN submission.

## License

MIT License. See DESCRIPTION and LICENSE.
