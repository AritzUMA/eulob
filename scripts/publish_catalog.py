#!/usr/bin/env python3
"""Publicación validada del catálogo Parquet en el paquete R."""

import argparse
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parent
DEST = PACKAGE / "inst/extdata/catalog"

COLUMNS = {
    "names": [
        "name_id", "name_normalized", "name",
        "n_entities", "n_countries"
    ],
    "name_ids": [
        "name_id", "name_normalized", "name",
        "country", "register", "lobby_id"
    ]
}

R_CODE = r'''
args <- commandArgs(trailingOnly = TRUE)

for (name in c("names", "name_ids")) {
    csv <- file.path(args[1], paste0(name, ".csv"))
    output <- file.path(args[1], paste0(name, ".rds"))

    x <- read.csv(
        csv,
        colClasses = "character",
        stringsAsFactors = FALSE,
        check.names = FALSE,
        na.strings = character(0),
        fileEncoding = "UTF-8"
    )

    if (name == "names") {
        for (column in c("n_entities", "n_countries")) {
            values <- suppressWarnings(
                as.integer(x[[column]])
            )

            stopifnot(
                !anyNA(values),
                all(values >= 0L)
            )

            x[[column]] <- values
        }

        stopifnot(
            !anyDuplicated(x$name_id),
            !anyDuplicated(x$name_normalized)
        )
    }

    saveRDS(x, output)
    stopifnot(identical(x, readRDS(output)))
}

# La preservación histórica se comprueba por nombre
# normalizado y ámbito, no por identificador oficial.

old <- readRDS(args[2])
new <- readRDS(file.path(args[1], "name_ids.rds"))

keys <- c("name_normalized", "country", "register")

previous <- unique(old[keys])
current <- unique(new[keys])
current$present <- TRUE

comparison <- merge(
    previous,
    current,
    by = keys,
    all.x = TRUE,
    sort = FALSE
)

if (anyNA(comparison$present)) {
    stop("Se perderían nombres históricos del catálogo")
}

cat(
    "Nombres históricos conservados:",
    nrow(previous), "\n"
)
'''

def validate(stage):
    directory = stage / "indexes/names"
    data = {}

    for name, columns in COLUMNS.items():
        path = directory / f"{name}.parquet"

        if not path.is_file():
            raise FileNotFoundError(path)

        df = pd.read_parquet(path)

        if list(df.columns) != columns:
            raise RuntimeError(
                f"Esquema incompatible: {name}"
            )

        if df[columns].isna().any().any():
            raise RuntimeError(
                f"Valores ausentes en {name}"
            )

        data[name] = df

    names = data["names"]
    relations = data["name_ids"]

    if names["name_id"].duplicated().any():
        raise RuntimeError("Nombres duplicados por name_id")

    if names["name_normalized"].duplicated().any():
        raise RuntimeError("Nombres normalizados duplicados")

    if relations.duplicated(
        ["name_id", "country", "register", "lobby_id"]
    ).any():
        raise RuntimeError("Relaciones duplicadas")

    if set(names.name_id) != set(relations.name_id):
        raise RuntimeError("Relaciones y nombres inconsistentes")

    mapping = names[
        ["name_id", "name_normalized"]
    ].merge(
        relations[["name_id", "name_normalized"]].drop_duplicates(),
        on="name_id",
        suffixes=("_names", "_relations"),
        validate="one_to_one"
    )

    if len(mapping) != len(names) or not (
        mapping.name_normalized_names ==
        mapping.name_normalized_relations
    ).all():
        raise RuntimeError("Normalización inconsistente")

    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        type=Path,
        default=ROOT / "data/staging/eulob_expand_candidate_v14"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Publicar los tres archivos después de validarlos"
    )
    args = parser.parse_args()

    stage = args.stage.resolve()
    data = validate(stage)

    print("\n========== CATÁLOGO ==========")
    print("Nombres:", len(data["names"]))
    print("Relaciones:", len(data["name_ids"]))

    # Los ficheros intermedios se eliminan automáticamente.
    with tempfile.TemporaryDirectory(
        prefix=".eulob_publish_",
        dir=DEST
    ) as directory:
        tmp = Path(directory)

        for name, df in data.items():
            df.to_csv(
                tmp / f"{name}.csv",
                index=False,
                encoding="utf-8"
            )

        subprocess.run(
            [
                "Rscript", "--vanilla", "-e", R_CODE,
                str(tmp),
                str(DEST / "name_ids.rds")
            ],
            check=True
        )

        prepared = {
            "names.rds": tmp / "names.rds",
            "name_ids.rds": tmp / "name_ids.rds"
        }

        for filename in prepared:
            if not (DEST / filename).is_file():
                raise FileNotFoundError(DEST / filename)


        # =====================================================
        # COMPARACION INCREMENTAL
        # =====================================================

        # Los RDS se comparan como objetos de R, no como bytes.
        # Dos serializaciones distintas pueden representar
        # exactamente el mismo data.frame.

        compare_rds = r"""
args <- commandArgs(trailingOnly = TRUE)

old <- readRDS(args[1])
new <- readRDS(args[2])

# Comparar contenido, no atributos ni orden físico.
canonical <- function(x) {
    stopifnot(is.data.frame(x))

    x <- as.data.frame(
        lapply(x, identity),
        check.names = FALSE,
        stringsAsFactors = FALSE
    )

    # Ordenar por todas las columnas para conservar duplicados.
    idx <- do.call(
        order,
        c(unname(x), list(na.last = TRUE, method = "radix"))
    )

    x <- x[idx, , drop = FALSE]
    rownames(x) <- NULL
    x
}

same <- identical(names(old), names(new)) &&
    identical(
        lapply(old, typeof),
        lapply(new, typeof)
    ) &&
    identical(canonical(old), canonical(new))

cat(if (same) "SAME" else "DIFFERENT")
"""

        differences = {}

        for filename, candidate in prepared.items():
            current = DEST / filename

            if filename.endswith(".rds"):
                result = subprocess.run(
                    [
                        "Rscript",
                        "--vanilla",
                        "-e",
                        compare_rds,
                        str(current),
                        str(candidate)
                    ],
                    check=True,
                    capture_output=True,
                    text=True
                )

                status = result.stdout.strip()

                if status not in ("SAME", "DIFFERENT"):
                    raise RuntimeError(
                        f"Comparación inválida: {filename}: {status}"
                    )

                changed = status == "DIFFERENT"

            else:
                changed = (
                    current.read_bytes() != candidate.read_bytes()
                )

            differences[filename] = changed

        print("\n========== COMPARACIÓN INCREMENTAL ==========")

        for filename, changed in differences.items():
            print(
                filename,
                "MODIFICADO" if changed else "SIN CAMBIOS"
            )

        if not any(differences.values()):
            print("\nCATÁLOGO YA ACTUALIZADO")
            print("Ningún archivo sustituido")
            print("Ningún backup necesario")
            return

        print("\nSe han detectado cambios en el catálogo.")

        if not args.apply:
            print("\nPREVISUALIZACIÓN VALIDADA")
            print("Ningún archivo del catálogo sustituido")
            return

        backup = ROOT / "backups" / (
            "eulob_catalog_" +
            datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        )
        backup.mkdir(parents=True, exist_ok=False)

        for filename in prepared:
            shutil.copy2(DEST / filename, backup / filename)

        replaced = []

        try:
            for filename, source in prepared.items():
                # No sustituir archivos cuyo contenido no ha cambiado.
                if not differences[filename]:
                    continue

                destination = DEST / filename

                # Preparar la sustitución en el mismo sistema de archivos.
                candidate = tmp / (filename + ".ready")
                shutil.copy2(source, candidate)

                candidate.replace(destination)
                replaced.append(filename)

            # Validar los tres archivos publicados.
            for filename, source in prepared.items():
                destination = DEST / filename

                if filename.endswith(".rds"):
                    result = subprocess.run(
                        [
                            "Rscript",
                            "--vanilla",
                            "-e",
                            compare_rds,
                            str(destination),
                            str(source)
                        ],
                        check=True,
                        capture_output=True,
                        text=True
                    )

                    if result.stdout.strip() != "SAME":
                        raise RuntimeError(
                            f"Verificación posterior fallida: {filename}"
                        )

                elif destination.read_bytes() != source.read_bytes():
                    raise RuntimeError(
                        f"Verificación posterior fallida: {filename}"
                    )

        except Exception:
            for filename in reversed(replaced):
                shutil.copy2(
                    backup / filename,
                    DEST / filename
                )
            raise

        print("\nCATÁLOGO PUBLICADO")
        print("Archivos:", ", ".join(replaced))
        print("Backup:", backup)


if __name__ == "__main__":
    main()
