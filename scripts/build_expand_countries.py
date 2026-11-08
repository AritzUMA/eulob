#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import importlib.util
import re
import shutil
import sys

import pandas as pd

ROOT = Path("/data/EU_scraping/Lobbies")
DATA = ROOT / "data"
STAGE = DATA / "staging" / "eulob_expand_candidate_v14"

CONFIG = {
    "AT": ("AT_lobbying_*.csv", "detail_Registerzahl", "list_name",
           "Austrian Lobbying Register"),
    "CY": ("CY_lobbying_*.csv", "Αρ. Μητρώου Εγγραφής (Α.Μ.Ε.)",
           "Ονοματεπώνυμο / Επωνυμία", "Cyprus Lobbying Register"),
    "FI": ("FI_lobbying_*.csv", "id", "companyName",
           "Finnish Transparency Register"),
    "IE": ("IE_lobbying_registrants_*.csv", "Id", "Name",
           "Irish Register of Lobbying"),
    "LT": ("LT_lobbying_*.csv", "registration_number", "name",
           "Lithuanian Lobbyists Register"),
    "RO": ("RO_lobbying_*.csv", "entity_id", "denumire",
           "Romanian Lobbying Register"),
    "ES": ("ES_lobbying_*.csv", "source_url", "org_name",
           "Spanish CNMC Interest Groups Register"),
    "FR": ("FR_lobbying_*.csv", "identifiantNational", "denomination",
           "French HATVP Register"),    "LV": ("LV_lobbying_*.csv", "registration_number", "legal_name",
           "Latvian Lobbying Register"),    "GR": ("GR_lobbying_*.csv",
           "Α.Μ.Δ.", "Επωνυμία ή Ονοματεπώνυμο",
           "Greek Lobbying Register"),    "BE": ("BE_lobbying_*.csv",
           "org_name", "org_name",
           "Belgian Chamber Lobby Register"),
}


def normalize_unique_dates(df):
    """Convertir las fechas de observación a YYYY-MM-DD."""
    from datetime import datetime

    result = df.copy()

    for column in ("first_seen", "last_seen"):
        def convert(value):
            value = str(value)

            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                return datetime.strptime(
                    value, "%Y-%m-%d"
                ).strftime("%Y-%m-%d")

            match = re.search(r"20\d{6}", value)

            if match is None:
                raise ValueError(
                    f"Fecha no reconocida: {column}={value!r}"
                )

            return datetime.strptime(
                match.group(), "%Y%m%d"
            ).strftime("%Y-%m-%d")

        result[column] = result[column].map(convert)

    if (result["first_seen"] > result["last_seen"]).any():
        raise ValueError("Fechas de observación inconsistentes")

    return result


def snapshot_date(path):
    m = re.search(r"(20\d{6})", path.stem)
    if not m:
        raise ValueError(f"Fecha no identificada: {path}")
    return m.group(1)

def read_csv(path):
    return pd.read_csv(
        path, dtype=str, keep_default_na=False,
        encoding="utf-8-sig"
    )


def build_country(country, cfg):
    import csv
    import json

    pattern, id_col, name_col, register = cfg

    files = sorted(
        (
            p for p in (ROOT / "output" / country).glob(pattern)
            if re.search(r"20\d{6}", p.stem)
        ),
        key=lambda p: (snapshot_date(p), p.name)
    )

    # Grecia: utilizar solo capturas posteriores a la corrección.
    if country == "GR":
        cutoff = "20261108_223022"
        files = [
            p for p in files
            if p.name.startswith("GR_lobbying_")
            and p.name.endswith(".csv")
            and len(p.stem.removeprefix("GR_lobbying_")) == 15
            and p.stem.removeprefix("GR_lobbying_").replace("_", "").isdigit()
            and p.stem.removeprefix("GR_lobbying_") >= cutoff
        ]

    if not files:
        raise RuntimeError(f"{country}: sin snapshots")

    entities = {}
    variants = defaultdict(set)
    history = []
    latest_ids = set()

    audit = []
    incidents = []

    for path in files:
        date = snapshot_date(path)

        with path.open(
            encoding="utf-8-sig", newline=""
        ) as f:
            reader = csv.reader(f, strict=False)
            header = next(reader)

            if len(header) != len(set(header)):
                raise RuntimeError(
                    f"{path.name}: columnas duplicadas"
                )

            if id_col not in header or name_col not in header:
                raise RuntimeError(
                    f"{path.name}: faltan columnas obligatorias"
                )

            rows = []
            malformed = 0

            for row in reader:
                line_number = reader.line_num

                if len(row) != len(header):
                    if (
                        country != "IE"
                        or len(row) != 19
                        or len(header) != 17
                    ):
                        raise RuntimeError(
                            f"{path.name}: fila {line_number}, "
                            f"{len(row)} campos, esperados {len(header)}"
                        )

                    # En Irlanda únicamente Id y Name son fiables.
                    # Los 19 campos originales se conservan aparte.
                    record = dict.fromkeys(header, "")
                    record[id_col] = row[0].strip()
                    record[name_col] = row[1].strip()

                    incidents.append({
                        "country": country,
                        "snapshot_file": path.name,
                        "line_number": line_number,
                        "expected_fields": len(header),
                        "actual_fields": len(row),
                        "original_fields": row,
                        "recovery": "id_name_only"
                    })

                    malformed += 1

                else:
                    record = dict(zip(header, row))

                rows.append(record)

        df = pd.DataFrame(rows, columns=header, dtype=str)

        df[id_col] = df[id_col].str.strip()
        df[name_col] = df[name_col].str.strip()


        if country == "LV":
            def fix_encoding(value):
                try:
                    return value.encode("latin-1").decode("utf-8")
                except (UnicodeError, UnicodeEncodeError):
                    return value

            df[name_col] = df[name_col].map(fix_encoding)

        valid_mask = (
            df[id_col].ne("") &
            df[name_col].ne("")
        )

        valid = df.loc[valid_mask].copy()


        if country in ("FR", "GR"):
            counts = valid.groupby(id_col)[name_col].nunique()
            conflicts = counts[counts > 1]

            if not conflicts.empty:
                raise RuntimeError(
                    f"{path.name}: IDs con nombres distintos: "
                    f"{conflicts.index.tolist()[:10]}"
                )

            valid = valid.drop_duplicates(
                subset=[id_col],
                keep="first"
            )

        elif valid[id_col].duplicated().any():
            raise RuntimeError(
                f"{path.name}: IDs duplicados entre filas válidas"
            )

        incomplete = int((~valid_mask).sum())

        # Histórico: todas las filas, incluidas las incompletas.
        df.insert(0, "snapshot_file", path.name)
        df.insert(1, "snapshot_date", date)
        df.insert(2, "lobby_id", df[id_col])

        history.append(df)

        # Solo entidades identificables en el índice.
        latest_ids = set(valid[id_col])

        for identifier, name in zip(
            valid[id_col], valid[name_col]
        ):
            variants[identifier].add(name)

            if identifier not in entities:
                entities[identifier] = {
                    "lobby_id": identifier,
                    "country": country,
                    "register": register,
                    "name": name,
                    "first_seen": path.stem,
                    "last_seen": path.stem,
                    "n_snapshots": 0,
                    "in_latest_snapshot": False,
                }

            entity = entities[identifier]
            entity["name"] = name
            entity["last_seen"] = path.stem
            entity["n_snapshots"] += 1

        audit.append({
            "country": country,
            "snapshot_file": path.name,
            "rows_total": len(df),
            "rows_indexed": len(valid),
            "rows_incomplete": incomplete,
            "rows_malformed_recovered": malformed,
        })

    if not entities:
        raise RuntimeError(
            f"{country}: ninguna entidad válida"
        )

    for identifier, entity in entities.items():
        entity["in_latest_snapshot"] = (
            identifier in latest_ids
        )
        entity["name_variants"] = sorted(
            variants[identifier]
        )

    unique = pd.DataFrame(entities.values())
    unique = unique.sort_values(
        "lobby_id"
    ).reset_index(drop=True)

    historical = pd.concat(
        history, ignore_index=True
    ).fillna("")

    unique = normalize_unique_dates(unique)
    unique.to_parquet(
        STAGE / "unique" / f"{country}.parquet",
        index=False
    )

    historical.to_parquet(
        STAGE / "history" / f"{country}.parquet",
        index=False
    )

    audit_dir = STAGE / "audit"
    audit_dir.mkdir(exist_ok=True)

    pd.DataFrame(audit).to_csv(
        audit_dir / f"{country}_snapshots.csv",
        index=False
    )

    if incidents:
        with (
            audit_dir / f"{country}_incidents.jsonl"
        ).open("w", encoding="utf-8") as f:
            for incident in incidents:
                f.write(
                    json.dumps(
                        incident, ensure_ascii=False
                    ) + "\\n"
                )

    print(
        f"{country}: {len(files)} snapshots | "
        f"{len(unique):,} entidades históricas | "
        f"{len(historical):,} observaciones | "
        f"{sum(x['rows_incomplete'] for x in audit)} "
        f"filas incompletas | "
        f"{len(incidents)} anomalías recuperadas",
        flush=True
    )

    return unique


def build_italy():
    """Tres registros italianos; mismo esquema unique del paquete."""
    import csv
    import json
    from collections import defaultdict

    sources = [
        (
            "Camera dei Deputati",
            "IT_camera_*.csv",
            "entity_id",
            "name",
            "camera",
        ),
        (
            "Italian MIMIT Register",
            "IT_mimit_*.csv",
            "numero_registrazione",
            "nomeOrganizzazione",
            "standard",
        ),
        (
            "Tuscany Interest Groups Register",
            "IT_toscana_*.csv",
            "numero_pratica",
            "name",
            "standard",
        ),
    ]

    root = ROOT / "output" / "IT"
    entities = {}
    variants = defaultdict(set)
    history = []
    audits = []

    for register, pattern, id_col, name_col, mode in sources:
        files = []

        for path in root.glob(pattern):
            if not re.fullmatch(
                r"IT_(?:camera|mimit|toscana)_\d{8}_\d{6}\.csv",
                path.name
            ):
                continue

            # Captura Camera anterior a V2: no añadirla dos veces.
            if path.name == "IT_camera_20261106_143015.csv":
                continue

            files.append((path.stem, path, mode))

        if mode == "camera":
            for path in (root / "camera_v2").glob("*/entities.csv"):
                stamp = path.parent.name

                if not re.fullmatch(r"\d{8}_\d{6}", stamp):
                    continue

                summary = path.parent / "summary.json"

                if not summary.is_file():
                    raise RuntimeError(f"Falta summary.json: {path}")

                metadata = json.loads(
                    summary.read_text(encoding="utf-8")
                )

                # Nunca incluir pruebas parciales como snapshots.
                if metadata.get("mode") != "all":
                    continue

                if metadata.get("errors") != 0:
                    raise RuntimeError(f"Captura V2 con errores: {path}")

                files.append((
                    f"IT_camera_{stamp}_v2",
                    path,
                    "v2",
                ))

        files.sort(key=lambda x: x[0])

        if not files:
            raise RuntimeError(f"Sin snapshots: {register}")

        latest_ids = set()

        for snapshot, path, file_mode in files:
            with path.open(
                encoding="utf-8-sig", newline=""
            ) as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    raise ValueError(f"CSV vacío: {path}")

                if not {id_col, name_col}.issubset(reader.fieldnames):
                    raise ValueError(f"Columnas ausentes: {path}")

                rows = list(reader)

            if file_mode == "v2":
                rows = [
                    row for row in rows
                    if row.get("kind") == "legal"
                ]

            seen = {}
            valid_ids = set()
            incomplete = 0

            for row in rows:
                identifier = row[id_col].strip()
                name = row[name_col].strip()

                if not identifier:
                    incomplete += 1
                    continue

                if name == "Presidente della Camera":
                    name = ""

                key = (register, identifier)

                # Histórico mínimo: solo datos de entidad.
                history.append({
                    "snapshot_file": path.name,
                    "snapshot_date": snapshot.split("_")[2],
                    "lobby_id": identifier,
                    "org_name": name,
                    "country": "IT",
                    "registry_source": register,
                    "source_url": row.get(
                        "source_url", ""
                    ),
                })

                if not name:
                    incomplete += 1
                    continue

                if identifier in seen:
                    if seen[identifier] != name:
                        raise RuntimeError(
                            f"{path.name}: ID {identifier} "
                            "con denominaciones contradictorias"
                        )
                    continue

                seen[identifier] = name
                valid_ids.add(identifier)
                variants[key].add(name)

                if key not in entities:
                    entities[key] = {
                        "lobby_id": identifier,
                        "country": "IT",
                        "register": register,
                        "name": name,
                        "first_seen": snapshot,
                        "last_seen": snapshot,
                        "n_snapshots": 0,
                        "in_latest_snapshot": False,
                    }

                entity = entities[key]
                entity["name"] = name
                entity["last_seen"] = snapshot
                entity["n_snapshots"] += 1

            latest_ids = valid_ids

            audits.append({
                "country": "IT",
                "register": register,
                "snapshot_file": path.name,
                "rows_total": len(rows),
                "rows_indexed": len(valid_ids),
                "rows_incomplete": incomplete,
            })

        for (reg, identifier), entity in entities.items():
            if reg == register:
                entity["in_latest_snapshot"] = (
                    identifier in latest_ids
                )
                entity["name_variants"] = sorted(
                    variants[(reg, identifier)]
                )

        count = sum(
            reg == register for reg, _ in entities
        )

        print(
            f"IT / {register}: "
            f"{len(files)} snapshots | "
            f"{count} entidades",
            flush=True
        )

    unique = pd.DataFrame(list(entities.values()))
    unique = unique.sort_values(
        ["register", "lobby_id"]
    ).reset_index(drop=True)

    if unique.duplicated(
        ["country", "register", "lobby_id"]
    ).any():
        raise RuntimeError("Entidades italianas duplicadas")

    expected_columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]

    unique = unique[expected_columns]

    (STAGE / "audit").mkdir(exist_ok=True)

    unique = normalize_unique_dates(unique)
    unique.to_parquet(
        STAGE / "unique" / "IT.parquet",
        index=False
    )

    pd.DataFrame(history).to_parquet(
        STAGE / "history" / "IT.parquet",
        index=False
    )

    pd.DataFrame(audits).to_csv(
        STAGE / "audit" / "IT_snapshots.csv",
        index=False
    )

    print(
        f"IT: {len(unique)} entidades únicas | "
        f"{len(history)} observaciones",
        flush=True
    )

    return unique




def build_czechia():
    """Conservar todos los CSV e indexar todas las denominaciones."""
    import re
    from collections import defaultdict

    root = ROOT / "output" / "CZ"
    files = sorted(root.rglob("*.csv"))

    if not files:
        raise RuntimeError("No hay archivos de CZ")

    history = []
    entities = defaultdict(lambda: {
        "names": set(),
        "snapshots": set()
    })
    audit = []

    for file in files:
        match = re.search(r"(20\d{6}_\d{6})", file.stem)
        if not match:
            raise RuntimeError(f"Fecha desconocida: {file.name}")

        snapshot = match.group(1)
        date = (
            snapshot[:4] + "-" +
            snapshot[4:6] + "-" +
            snapshot[6:8]
        )

        df = pd.read_csv(
            file, dtype=str, keep_default_na=False,
            encoding="utf-8-sig", low_memory=False
        )

        is_activity = "org_name" in df.columns

        for record in df.to_dict("records"):
            row = dict(record)
            row["snapshot_file"] = str(file.relative_to(root))
            row["snapshot_date"] = date
            history.append(row)

            if not is_activity:
                continue

            name = row.get("org_name", "").strip()
            if not name:
                continue

            entities[name]["names"].add(name)
            entities[name]["snapshots"].add(snapshot)

        audit.append({
            "snapshot_file": str(file.relative_to(root)),
            "snapshot_date": date,
            "rows_total": len(df),
            "record_type": (
                "activity" if is_activity else "catalog"
            )
        })

        print(f"CZ / {file.name}: {len(df)} filas")

    activity_snapshots = sorted({
        re.search(r"(20\d{6}_\d{6})", item["snapshot_file"]).group(1)
        for item in audit
        if item["record_type"] == "activity"
    })

    if not activity_snapshots:
        raise RuntimeError("CZ no contiene archivos de actividad")

    latest = activity_snapshots[-1]
    rows = []

    for name, item in sorted(entities.items()):
        dates = sorted(item["snapshots"])
        rows.append({
            "lobby_id": name,
            "country": "CZ",
            "register": "Czech RELOB",
            "name": name,
            "first_seen": dates[0],
            "last_seen": dates[-1],
            "n_snapshots": len(dates),
            "in_latest_snapshot": latest in item["snapshots"],
            "name_variants": sorted(item["names"])
        })

    columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]

    unique = pd.DataFrame(rows, columns=columns)

    for folder in ("unique", "history", "audit"):
        (STAGE / folder).mkdir(parents=True, exist_ok=True)

    unique = normalize_unique_dates(unique)
    unique.to_parquet(
        STAGE / "unique" / "CZ.parquet", index=False
    )
    pd.DataFrame(history).fillna("").to_parquet(
        STAGE / "history" / "CZ.parquet", index=False
    )
    pd.DataFrame(audit).to_csv(
        STAGE / "audit" / "CZ_snapshots.csv", index=False
    )

    print(
        f"CZ: {len(files)} archivos | "
        f"{len(history)} observaciones | "
        f"{len(unique)} entidades"
    )

    return unique





def build_estonia():
    """Reconstruir el índice estonio desde participantes estructurados."""
    import hashlib
    import json
    import re
    import tempfile
    import unicodedata
    from collections import defaultdict
    from pathlib import Path
    from datetime import datetime
    import os

    old_root = ROOT / "output" / "EE"
    structured_root = ROOT / "output" / "EE_structured"

    register = "Estonian Lobby Meetings"

    columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]

    def normalize(value):
        value = unicodedata.normalize("NFKC", str(value or ""))
        value = value.casefold()
        return re.sub(r"\s+", " ", value).strip()

    # Cada nombre normalizado identifica una entrada.
    # Las equivalencias semánticas entre nombres diferentes
    # no se inventan: requieren una correspondencia verificada.
    entities = defaultdict(lambda: {
        "dates": set(),
        "variants": set()
    })

    history = []
    audit = []
    snapshots = set()

    def add_participants(participants, snapshot):
        if not isinstance(participants, list):
            raise RuntimeError("participants_json no contiene una lista")

        count = 0

        for participant in participants:
            if not isinstance(participant, dict):
                raise RuntimeError("Participante no estructurado")

            name = participant.get("organization") or ""

            if not isinstance(name, str):
                raise RuntimeError("Nombre de organización inválido")

            if not name.strip():
                continue

            normalized = normalize(name)

            if not normalized:
                continue

            entities[normalized]["dates"].add(snapshot)
            entities[normalized]["variants"].add(name.strip())
            count += 1

        return count

    # =========================================================
    # 1. HISTÓRICOS REPARADOS
    # =========================================================

    old_files = sorted(
        old_root.glob("EE_lobby_meetings_*.csv")
    )

    if len(old_files) != 11:
        raise RuntimeError(
            f"Esperados 11 históricos EE; encontrados {len(old_files)}"
        )

    historical_rows = 0

    for file in old_files:
        match = re.fullmatch(
            r"EE_lobby_meetings_([0-9]{4}-[0-9]{2}-[0-9]{2})[.]csv",
            file.name
        )

        if not match:
            raise RuntimeError(f"Fecha inválida: {file.name}")

        snapshot = match.group(1)
        datetime.strptime(snapshot, "%Y-%m-%d")

        df = pd.read_csv(
            file,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig"
        )

        required = [
            "Kohtumise aeg  Sort ascending",
            "Teema",
            "Asutus",
            "Ametiisik",
            "Lobist, organisatsioon",
            "participants_json",
            "participants_parse_status"
        ]

        if any(col not in df.columns for col in required):
            raise RuntimeError(
                f"Histórico sin reparar: {file.name}"
            )

        if (df["snapshot_date"] != snapshot).any():
            raise RuntimeError(
                f"Fecha de captura inconsistente: {file.name}"
            )

        count = 0

        for record in df.to_dict("records"):
            status = record["participants_parse_status"]

            if status not in (
                "parsed", "repaired_manual", "empty"
            ):
                raise RuntimeError(
                    f"Registro pendiente en {file.name}: {status}"
                )

            participants = json.loads(
                record["participants_json"]
            )

            if status == "empty" and participants:
                raise RuntimeError("Fila vacía con participantes")

            count += add_participants(
                participants, snapshot
            )

            # Conservar literalmente todas las columnas
            # y los contenidos históricos.
            row = dict(record)
            row["snapshot_file"] = file.name
            row["snapshot_date"] = snapshot
            history.append(row)

        snapshots.add(snapshot)
        historical_rows += len(df)

        audit.append({
            "snapshot_file": file.name,
            "snapshot_date": snapshot,
            "rows_total": len(df),
            "rows_with_participant": count,
            "status": "ok"
        })

        print(
            f"EE histórico / {file.name}: "
            f"{len(df)} reuniones | "
            f"{count} participaciones con organización",
            flush=True
        )

    if historical_rows != 66130:
        raise RuntimeError(
            f"Esperadas 66130 filas históricas: {historical_rows}"
        )

    # =========================================================
    # 2. EXTRACCIONES ESTRUCTURADAS, ACTUALES Y FUTURAS
    # =========================================================

    structured_files = sorted(
        structured_root.glob("full_*/meetings.csv")
    )

    if not structured_files:
        raise RuntimeError(
            "No se encuentran capturas estructuradas de Estonia"
        )

    structured_rows = 0

    for file in structured_files:
        manifest_path = file.parent / "manifest.json"

        if not manifest_path.is_file():
            raise RuntimeError(
                f"Falta manifest: {file.parent}"
            )

        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        if manifest.get("status") != "complete_verified":
            raise RuntimeError(
                f"Captura no verificada: {file.parent}"
            )

        df = pd.read_csv(
            file,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig"
        )

        required = [
            "collected_at", "meeting_date", "topic",
            "institution", "participants_json"
        ]

        if any(col not in df.columns for col in required):
            raise RuntimeError(
                f"Esquema estructurado incompatible: {file}"
            )

        dates = set()
        count = 0

        for record in df.to_dict("records"):
            collected_at = record["collected_at"]

            if not collected_at:
                raise RuntimeError(
                    f"Captura sin collected_at: {file}"
                )

            # Fecha de captura, nunca fecha de reunión.
            snapshot = datetime.fromisoformat(
                collected_at.replace("Z", "+00:00")
            ).date().isoformat()

            dates.add(snapshot)

            participants = json.loads(
                record["participants_json"]
            )

            count += add_participants(
                participants, snapshot
            )

            row = dict(record)
            row["snapshot_file"] = str(
                file.relative_to(ROOT / "output")
            )
            row["snapshot_date"] = snapshot

            history.append(row)

        if len(dates) != 1:
            raise RuntimeError(
                f"Captura con varias fechas: {file}"
            )

        snapshot = next(iter(dates))
        snapshots.add(snapshot)
        structured_rows += len(df)

        audit.append({
            "snapshot_file": str(
                file.relative_to(ROOT / "output")
            ),
            "snapshot_date": snapshot,
            "rows_total": len(df),
            "rows_with_participant": count,
            "status": "ok"
        })

        print(
            f"EE estructurado / {file.parent.name}: "
            f"{len(df)} reuniones | "
            f"{count} participaciones con organización",
            flush=True
        )

    # =========================================================
    # 3. ÍNDICE DE ORGANIZACIONES
    # =========================================================

    latest = max(snapshots)
    rows = []

    for normalized, info in sorted(entities.items()):
        dates = sorted(info["dates"])
        variants = sorted(
            info["variants"],
            key=lambda x: (normalize(x), x)
        )

        lobby_id = "name:" + hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

        rows.append({
            "lobby_id": lobby_id,
            "country": "EE",
            "register": register,
            "name": variants[0],
            "first_seen": dates[0],
            "last_seen": dates[-1],
            "n_snapshots": len(dates),
            "in_latest_snapshot": latest in info["dates"],
            "name_variants": variants
        })

    unique = pd.DataFrame(rows, columns=columns)

    if unique.empty:
        raise RuntimeError("Índice EE vacío")

    unique["n_snapshots"] = unique[
        "n_snapshots"
    ].astype("int64")

    unique["in_latest_snapshot"] = unique[
        "in_latest_snapshot"
    ].astype(bool)

    if unique.duplicated(
        ["country", "register", "lobby_id"]
    ).any():
        raise RuntimeError("Identificadores duplicados EE")

    if not unique["name"].map(normalize).is_unique:
        raise RuntimeError("Nombres normalizados duplicados")

    # =========================================================
    # 4. GUARDAR EN EL STAGING EXISTENTE
    # =========================================================

    for folder in ("unique", "history", "audit"):
        (STAGE / folder).mkdir(parents=True, exist_ok=True)

    reference = STAGE / "unique" / "AT.parquet"

    if not reference.exists():
        raise RuntimeError(
            "Falta índice AT para validar esquema y tipos"
        )

    # Validar primero en un directorio temporal que se
    # elimina automáticamente después de la operación.
    with tempfile.TemporaryDirectory(
        prefix="ee_validate_", dir=STAGE
    ) as tmp:
        tmp = Path(tmp)

        unique_tmp = tmp / "EE.parquet"
        history_tmp = tmp / "EE_history.parquet"
        audit_tmp = tmp / "EE_snapshots.csv"

        unique = normalize_unique_dates(unique)
        unique.to_parquet(unique_tmp, index=False)
        pd.DataFrame(history).to_parquet(
            history_tmp, index=False
        )
        pd.DataFrame(audit).to_csv(
            audit_tmp, index=False
        )

        ref = pd.read_parquet(reference)
        check = pd.read_parquet(unique_tmp)

        if list(check.columns) != list(ref.columns):
            raise RuntimeError("Esquema EE incompatible")

        for col in ref.columns:
            if str(check[col].dtype) != str(ref[col].dtype):
                raise RuntimeError(
                    f"Tipo incompatible EE/{col}: "
                    f"{check[col].dtype} != {ref[col].dtype}"
                )

        if len(check) != len(unique):
            raise RuntimeError("Error al guardar índice EE")

        if len(pd.read_parquet(history_tmp)) != len(history):
            raise RuntimeError("Error al guardar histórico EE")

        # Solo ahora se sustituyen los ficheros
        # derivados de Estonia, nunca otros países.
        os.replace(
            unique_tmp, STAGE / "unique" / "EE.parquet"
        )
        os.replace(
            history_tmp, STAGE / "history" / "EE.parquet"
        )
        os.replace(
            audit_tmp, STAGE / "audit" / "EE_snapshots.csv"
        )

    print(
        f"EE: {len(old_files)} históricos antiguos | "
        f"{len(structured_files)} capturas estructuradas | "
        f"{len(history)} reuniones-observación | "
        f"{len(unique)} nombres normalizados | "
        f"{len(snapshots)} fechas de captura",
        flush=True
    )

    return unique



def build_luxembourg():
    """Indexar entidades registradas y conservar todas las reuniones."""
    import re
    from collections import defaultdict

    root = ROOT / "output" / "LU"
    files = sorted(root.rglob("*.csv"))

    if not files:
        raise RuntimeError("No hay archivos CSV de Luxemburgo")

    register = "Luxembourg Chamber Interest Representatives"

    entities = {}
    variants = defaultdict(set)
    snapshots = defaultdict(set)
    history = []
    audit = []
    pending = []

    required = {
        "registration_numbers",
        "entities_represented",
        "interest_representatives"
    }

    for file in files:
        match = re.search(
            r"(20\d{6})_(\d{6})",
            file.stem
        )

        if not match:
            raise RuntimeError(
                f"Fecha no reconocida: {file.name}"
            )

        stamp = match.group(1) + "_" + match.group(2)
        date = (
            stamp[:4] + "-" +
            stamp[4:6] + "-" +
            stamp[6:8]
        )

        df = pd.read_csv(
            file,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
            low_memory=False
        )

        missing = required - set(df.columns)
        if missing:
            raise RuntimeError(
                f"{file.name}: columnas ausentes: {missing}"
            )

        valid_rows = 0
        ambiguous_rows = 0
        ids_in_snapshot = set()

        for row_number, record in enumerate(
            df.to_dict("records"), start=2
        ):
            row = dict(record)
            row["snapshot_file"] = str(
                file.relative_to(root)
            )
            row["snapshot_date"] = date

            # Todas las observaciones se conservan.
            history.append(row)

            raw_id = row["registration_numbers"].strip()
            raw_name = row["entities_represented"].strip()

            # Solo vinculamos una inscripción inequívoca.
            # No inferimos relaciones entre varias entidades e IDs.
            if not re.fullmatch(r"[A-Za-z]\d+", raw_id):
                ambiguous_rows += 1
                pending.append({
                    "snapshot_file": file.name,
                    "row_number": row_number,
                    "registration_numbers": raw_id,
                    "entities_represented": raw_name,
                    "reason": "missing_or_multiple_registration"
                })
                continue

            if not raw_name:
                ambiguous_rows += 1
                pending.append({
                    "snapshot_file": file.name,
                    "row_number": row_number,
                    "registration_numbers": raw_id,
                    "entities_represented": raw_name,
                    "reason": "missing_entity_name"
                })
                continue

            # Formato observado:
            # Nombre (denominación extendida) - dirección
            name = raw_name.split(" (", 1)[0].strip()

            if " - " in name:
                name = name.split(" - ", 1)[0].strip()

            if not name:
                ambiguous_rows += 1
                continue

            identifier = raw_id.upper()

            if identifier not in entities:
                entities[identifier] = name

            variants[identifier].add(name)
            ids_in_snapshot.add(identifier)
            valid_rows += 1

        for identifier in ids_in_snapshot:
            snapshots[identifier].add(stamp)

        audit.append({
            "snapshot_file": str(file.relative_to(root)),
            "snapshot_date": stamp,
            "rows_total": len(df),
            "rows_with_entity": valid_rows,
            "rows_pending_review": ambiguous_rows,
            "distinct_ids": len(ids_in_snapshot)
        })

        print(
            f"LU / {file.name}: {len(df)} filas | "
            f"{len(ids_in_snapshot)} entidades | "
            f"{ambiguous_rows} pendientes",
            flush=True
        )

    latest = max(a["snapshot_date"] for a in audit)

    rows = []

    for identifier, name in sorted(entities.items()):
        dates = sorted(snapshots[identifier])

        rows.append({
            "lobby_id": identifier,
            "country": "LU",
            "register": register,
            "name": name,
            "first_seen": dates[0],
            "last_seen": dates[-1],
            "n_snapshots": len(dates),
            "in_latest_snapshot": latest in snapshots[identifier],
            "name_variants": sorted(variants[identifier])
        })

    columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]

    unique = pd.DataFrame(rows, columns=columns)

    for folder in ("unique", "history", "audit"):
        (STAGE / folder).mkdir(parents=True, exist_ok=True)

    unique = normalize_unique_dates(unique)
    unique.to_parquet(
        STAGE / "unique" / "LU.parquet",
        index=False
    )

    pd.DataFrame(history).to_parquet(
        STAGE / "history" / "LU.parquet",
        index=False
    )

    pd.DataFrame(audit).to_csv(
        STAGE / "audit" / "LU_snapshots.csv",
        index=False
    )

    pd.DataFrame(
        pending,
        columns=[
            "snapshot_file", "row_number",
            "registration_numbers",
            "entities_represented", "reason"
        ]
    ).to_csv(
        STAGE / "audit" / "LU_pending_review.csv",
        index=False
    )

    if unique.duplicated(
        ["country", "register", "lobby_id"]
    ).any():
        raise RuntimeError("Identificadores duplicados en LU")

    print(
        f"LU: {len(files)} archivos | "
        f"{len(history)} observaciones | "
        f"{len(unique)} entidades | "
        f"{len(pending)} filas pendientes",
        flush=True
    )

    return unique




def build_netherlands():
    """Conservar agendas ministeriales sin inventar organizaciones."""
    import re

    root = ROOT / "output" / "NL"
    files = sorted(root.rglob("*.csv"))

    if not files:
        raise RuntimeError("No se encontraron CSV de NL")

    history = []
    audit = []

    for file in files:
        match = re.search(
            r"(20[0-9]{6})_([0-9]{6})",
            file.stem
        )

        if not match:
            raise RuntimeError(
                f"Fecha no reconocida: {file.name}"
            )

        stamp = match.group(1) + "_" + match.group(2)
        date = (
            stamp[:4] + "-" +
            stamp[4:6] + "-" +
            stamp[6:8]
        )

        try:
            df = pd.read_csv(
                file,
                dtype=str,
                keep_default_na=False,
                encoding="utf-8-sig",
                low_memory=False
            )
        except pd.errors.EmptyDataError:
            audit.append({
                "snapshot_file": str(file.relative_to(root)),
                "snapshot_date": date,
                "rows_total": 0,
                "status": "empty"
            })
            continue

        for record in df.to_dict("records"):
            row = dict(record)
            row["snapshot_file"] = str(
                file.relative_to(root)
            )
            row["snapshot_date"] = date
            history.append(row)

        audit.append({
            "snapshot_file": str(file.relative_to(root)),
            "snapshot_date": date,
            "rows_total": len(df),
            "status": "preserved"
        })

        print(
            f"NL / {file.name}: "
            f"{len(df)} observaciones conservadas",
            flush=True
        )

    for folder in ("unique", "history", "audit"):
        (STAGE / folder).mkdir(parents=True, exist_ok=True)

    pd.DataFrame(history).to_parquet(
        STAGE / "history" / "NL.parquet",
        index=False
    )

    pd.DataFrame(audit).to_csv(
        STAGE / "audit" / "NL_snapshots.csv",
        index=False
    )

    # Esquema idéntico al resto de países, sin entidades ficticias.
    columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]


    # Parquet vacío con esquema Arrow estándar y sin metadatos
    # de extensión Pandas incompatibles.
    import pyarrow as pa
    import pyarrow.parquet as pq

    nl_schema = pa.schema([
        pa.field("lobby_id", pa.string()),
        pa.field("country", pa.string()),
        pa.field("register", pa.string()),
        pa.field("name", pa.string()),
        pa.field("first_seen", pa.string()),
        pa.field("last_seen", pa.string()),
        pa.field("n_snapshots", pa.int64()),
        pa.field("in_latest_snapshot", pa.bool_()),
        pa.field("name_variants", pa.list_(pa.string())),
    ])

    empty_table = pa.Table.from_arrays(
        [
            pa.array([], type=field.type)
            for field in nl_schema
        ],
        schema=nl_schema
    )

    pq.write_table(
        empty_table,
        STAGE / "unique" / "NL.parquet",
        compression="zstd"
    )

    print(
        f"NL: {len(files)} archivos | "
        f"{len(history)} observaciones históricas | "
        "0 entidades verificables",
        flush=True
    )





def build_poland():
    """Construir Polonia usando exclusivamente capturas Docling."""
    import re
    from collections import defaultdict

    root = ROOT / "output" / "PL"
    register = "Polish Professional Lobbying Register"

    pattern = re.compile(
        r"^Poland_Professional_Lobbying_Register_"
        r"(20\d{6})_(\d{6})\.csv$"
    )

    files = []
    for path in root.glob("*.csv"):
        match = pattern.fullmatch(path.name)
        if match:
            files.append((match.group(1) + "_" + match.group(2), path))

    files.sort()

    if not files:
        raise RuntimeError("PL: no hay capturas Docling fechadas")

    stamps = [stamp for stamp, _ in files]
    if len(stamps) != len(set(stamps)):
        raise RuntimeError("PL: timestamps duplicados")

    required = {
        "numer_kolejny", "data_wpisu", "nazwa",
        "adres", "krs", "data_wykreslenia",
        "sygnatura_akt", "uwagi", "pagina_pdf"
    }

    entities = {}
    variants = defaultdict(set)
    observations = defaultdict(set)
    history = []
    audit = []

    latest_stamp = stamps[-1]
    latest_ids = set()

    for stamp, path in files:
        df = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
            low_memory=False
        )

        missing = required - set(df.columns)
        if missing:
            raise RuntimeError(
                f"{path.name}: faltan columnas {sorted(missing)}"
            )

        df["numer_kolejny"] = df["numer_kolejny"].str.strip()
        df["nazwa"] = df["nazwa"].str.strip()

        if df.empty:
            raise RuntimeError(f"{path.name}: CSV vacío")

        if not df["numer_kolejny"].str.fullmatch(r"\d{5}").all():
            raise RuntimeError(
                f"{path.name}: identificadores incorrectos"
            )

        if df["numer_kolejny"].duplicated().any():
            raise RuntimeError(
                f"{path.name}: identificadores duplicados"
            )

        if df["nazwa"].isin(["", "-"]).any():
            raise RuntimeError(f"{path.name}: nombres vacíos")

        if df["nazwa"].str.fullmatch(r"[\d\s./-]+").any():
            raise RuntimeError(
                f"{path.name}: posibles fechas en nombres"
            )

        date = (
            stamp[:4] + "-" +
            stamp[4:6] + "-" +
            stamp[6:8]
        )

        current_ids = set(df["numer_kolejny"])

        for record in df.to_dict("records"):
            identifier = record["numer_kolejny"]
            name = record["nazwa"]

            history.append({
                **record,
                "snapshot_file": path.name,
                "snapshot_date": date,
                "lobby_id": identifier,
                "country": "PL",
                "register": register,
                "extraction_method": "docling"
            })

            variants[identifier].add(name)
            observations[identifier].add(stamp)

            # Nombre de la captura más reciente observada.
            entities[identifier] = name

        if stamp == latest_stamp:
            latest_ids = current_ids

        audit.append({
            "country": "PL",
            "snapshot_file": path.name,
            "snapshot_date": stamp,
            "rows_total": len(df),
            "distinct_entries": len(current_ids),
            "rows_incomplete": 0,
            "rows_date_as_name": 0
        })

        print(
            f"PL / {path.name}: {len(df)} inscripciones",
            flush=True
        )

    rows = []

    for identifier in sorted(entities):
        seen = sorted(observations[identifier])

        rows.append({
            "lobby_id": identifier,
            "country": "PL",
            "register": register,
            "name": entities[identifier],
            "first_seen": seen[0],
            "last_seen": seen[-1],
            "n_snapshots": len(seen),
            "in_latest_snapshot": identifier in latest_ids,
            "name_variants": sorted(variants[identifier])
        })

    columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]

    unique = pd.DataFrame(rows, columns=columns)
    unique = normalize_unique_dates(unique)

    for folder in ("unique", "history", "audit"):
        (STAGE / folder).mkdir(parents=True, exist_ok=True)

    unique.to_parquet(
        STAGE / "unique" / "PL.parquet",
        index=False
    )

    pd.DataFrame(history).to_parquet(
        STAGE / "history" / "PL.parquet",
        index=False
    )

    pd.DataFrame(audit).to_csv(
        STAGE / "audit" / "PL_snapshots.csv",
        index=False
    )

    pd.DataFrame(
        columns=[
            "snapshot_file", "row_number",
            "numer_kolejny", "nazwa", "reason"
        ]
    ).to_csv(
        STAGE / "audit" / "PL_pending_review.csv",
        index=False
    )

    print(
        f"PL: {len(files)} capturas Docling | "
        f"{len(history)} observaciones | "
        f"{len(unique)} inscripciones únicas",
        flush=True
    )

    return unique


def build_poland_legacy():
    """Conservar todas las capturas y evitar fusionar entidades distintas."""
    import hashlib
    import re
    import unicodedata
    from collections import defaultdict

    root = ROOT / "output" / "PL"
    files = sorted(
        p for p in root.rglob("*.csv")
        if p.name != "PL_docling_658_provisional.csv"
    )

    if not files:
        raise RuntimeError("No hay CSV de Polonia")

    register = "Polish Professional Lobbying Register"

    date_pattern = re.compile(
        r"\\d{1,2}\\.\\d{1,2}\\.\\d{4}\\.?"
    )

    entities = {}
    variants = defaultdict(set)
    snapshots = defaultdict(set)
    history = []
    audit = []
    pending = []

    latest_snapshot = ""

    for file in files:
        match = re.search(
            r"(20[0-9]{6})_([0-9]{6})",
            file.stem
        )

        if not match:
            raise RuntimeError(
                f"Fecha desconocida: {file.name}"
            )

        stamp = match.group(1) + "_" + match.group(2)
        date = (
            stamp[:4] + "-" +
            stamp[4:6] + "-" +
            stamp[6:8]
        )

        latest_snapshot = max(latest_snapshot, stamp)

        df = pd.read_csv(
            file,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
            low_memory=False
        )

        required = {"numer_kolejny", "nazwa"}
        if not required.issubset(df.columns):
            raise RuntimeError(
                f"{file.name}: faltan columnas {required - set(df.columns)}"
            )

        indexed = set()
        incomplete = 0
        invalid_dates = 0

        for row_number, record in enumerate(
            df.to_dict("records"), start=2
        ):
            row = dict(record)
            row["snapshot_file"] = str(
                file.relative_to(root)
            )
            row["snapshot_date"] = date

            # Histórico completo, incluso filas incompletas.
            history.append(row)

            number = row["numer_kolejny"].strip()
            name = row["nazwa"].strip()

            reason = None

            if not number or not name:
                reason = "incomplete"
                incomplete += 1

            elif date_pattern.fullmatch(name):
                reason = "date_in_name"
                invalid_dates += 1

            if reason:
                pending.append({
                    "snapshot_file": file.name,
                    "row_number": row_number,
                    "numer_kolejny": number,
                    "nazwa": name,
                    "reason": reason
                })
                continue

            # Una misma inscripción puede contener varias
            # denominaciones: no fusionarlas por numer_kolejny.
            normalized = unicodedata.normalize(
                "NFKC", name
            ).casefold()

            normalized = re.sub(
                r"\\s+", " ", normalized
            ).strip()

            digest = hashlib.sha256(
                normalized.encode("utf-8")
            ).hexdigest()

            identifier = f"{number}:{digest}"
            indexed.add(identifier)

            variants[identifier].add(name)
            snapshots[identifier].add(stamp)

            if identifier not in entities:
                entities[identifier] = name
            else:
                # Preferir la denominación de la última captura.
                entities[identifier] = name

        audit.append({
            "snapshot_file": str(file.relative_to(root)),
            "snapshot_date": stamp,
            "rows_total": len(df),
            "distinct_entries": len(indexed),
            "rows_incomplete": incomplete,
            "rows_date_as_name": invalid_dates
        })

        print(
            f"PL / {file.name}: "
            f"{len(df)} filas | "
            f"{len(indexed)} entradas | "
            f"{incomplete} incompletas | "
            f"{invalid_dates} fechas como nombre",
            flush=True
        )

    rows = []

    for identifier, name in sorted(entities.items()):
        stamps = sorted(snapshots[identifier])

        rows.append({
            "lobby_id": identifier,
            "country": "PL",
            "register": register,
            "name": name,
            "first_seen": stamps[0],
            "last_seen": stamps[-1],
            "n_snapshots": len(stamps),
            "in_latest_snapshot": latest_snapshot in snapshots[identifier],
            "name_variants": sorted(variants[identifier])
        })

    columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]

    unique = pd.DataFrame(rows, columns=columns)

    if unique.duplicated(
        ["country", "register", "lobby_id"]
    ).any():
        raise RuntimeError("Identificadores duplicados en PL")

    for folder in ("unique", "history", "audit"):
        (STAGE / folder).mkdir(parents=True, exist_ok=True)

    unique = normalize_unique_dates(unique)
    unique.to_parquet(
        STAGE / "unique" / "PL.parquet",
        index=False
    )

    pd.DataFrame(history).to_parquet(
        STAGE / "history" / "PL.parquet",
        index=False
    )

    pd.DataFrame(audit).to_csv(
        STAGE / "audit" / "PL_snapshots.csv",
        index=False
    )

    pd.DataFrame(
        pending,
        columns=[
            "snapshot_file", "row_number",
            "numer_kolejny", "nazwa", "reason"
        ]
    ).to_csv(
        STAGE / "audit" / "PL_pending_review.csv",
        index=False
    )

    print(
        f"PL: {len(files)} archivos | "
        f"{len(history)} observaciones | "
        f"{len(unique)} entradas indexadas | "
        f"{len(pending)} filas pendientes",
        flush=True
    )

    return unique




def build_united_kingdom():
    """Procesar originales y joined; conservar todas las observaciones."""
    import csv
    import hashlib
    import re
    import unicodedata
    from collections import defaultdict
    import pyarrow as pa
    import pyarrow.parquet as pq

    root = ROOT / "output" / "UK"
    files = sorted(root.rglob("*.csv"))

    if not files:
        raise RuntimeError("No hay CSV de Reino Unido")

    register = "UK Consultant Lobbyists Register"
    fields = []
    metadata = []
    latest_snapshot = ""

    # Primera pasada: cabeceras y fechas de todos los CSV.
    for file in files:
        match = re.fullmatch(
            r"UK_lobbying(_joined)?_(\d{8}_\d{6})\.csv",
            file.name
        )

        if not match:
            raise RuntimeError(
                f"Archivo UK no reconocido: {file.name}"
            )

        kind = "joined" if match.group(1) else "original"
        stamp = match.group(2)

        if kind == "original":
            latest_snapshot = max(latest_snapshot, stamp)

        with file.open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            reader = csv.DictReader(handle)
            header = reader.fieldnames

        if not header:
            raise RuntimeError(
                f"CSV sin cabecera: {file.name}"
            )

        if "name" not in header:
            raise RuntimeError(
                f"Falta name en {file.name}"
            )

        for field in header:
            if field and field not in fields:
                fields.append(field)

        metadata.append((file, kind, stamp))

    if not latest_snapshot:
        raise RuntimeError(
            "No se encontraron capturas originales UK"
        )

    extra = [
        "snapshot_file",
        "snapshot_date",
        "export_kind"
    ]

    if set(extra) & set(fields):
        raise RuntimeError(
            "Conflicto con columnas de procedencia"
        )

    all_fields = fields + extra

    schema = pa.schema([
        pa.field(field, pa.string())
        for field in all_fields
    ])

    for folder in ("unique", "history", "audit"):
        (STAGE / folder).mkdir(
            parents=True, exist_ok=True
        )

    destination = STAGE / "history" / "UK.parquet"
    writer = pq.ParquetWriter(
        destination, schema=schema,
        compression="zstd"
    )

    entities = {}
    variants = defaultdict(set)
    snapshots = defaultdict(set)
    audit = []

    total_rows = 0
    batch = []

    def flush():
        if not batch:
            return
        table = pa.Table.from_pylist(
            batch, schema=schema
        )
        writer.write_table(table)
        batch.clear()

    try:
        for file, kind, stamp in metadata:
            date = (
                stamp[:4] + "-" +
                stamp[4:6] + "-" +
                stamp[6:8]
            )

            rows_count = 0
            named_count = 0
            ids_in_file = set()

            with file.open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                reader = csv.DictReader(handle)

                for record in reader:
                    rows_count += 1
                    total_rows += 1

                    row = {
                        field: (
                            record.get(field) or ""
                        )
                        for field in fields
                    }

                    row["snapshot_file"] = str(
                        file.relative_to(root)
                    )
                    row["snapshot_date"] = date
                    row["export_kind"] = kind

                    batch.append(row)

                    if len(batch) >= 10000:
                        flush()

                    name = row["name"].strip()

                    if not name:
                        continue

                    named_count += 1

                    normalized = unicodedata.normalize(
                        "NFKC", name
                    ).casefold()

                    normalized = re.sub(
                        r"\s+", " ", normalized
                    ).strip()

                    identifier = "name:" + hashlib.sha256(
                        normalized.encode("utf-8")
                    ).hexdigest()

                    variants[identifier].add(name)
                    ids_in_file.add(identifier)
                    snapshots[identifier].add(stamp)

                    if identifier not in entities:
                        entities[identifier] = name
                    elif kind == "original":
                        entities[identifier] = name

            audit.append({
                "snapshot_file": str(
                    file.relative_to(root)
                ),
                "snapshot_date": stamp,
                "export_kind": kind,
                "rows_total": rows_count,
                "rows_with_name": named_count,
                "distinct_entities": len(ids_in_file)
            })

            print(
                f"UK / {file.name}: "
                f"{rows_count} filas | "
                f"{len(ids_in_file)} denominaciones",
                flush=True
            )

        flush()

    finally:
        writer.close()

    rows = []

    for identifier, name in sorted(entities.items()):
        stamps = sorted(snapshots[identifier])

        rows.append({
            "lobby_id": identifier,
            "country": "UK",
            "register": register,
            "name": name,
            "first_seen": stamps[0],
            "last_seen": stamps[-1],
            "n_snapshots": len(stamps),
            "in_latest_snapshot": (
                latest_snapshot in snapshots[identifier]
            ),
            "name_variants": sorted(
                variants[identifier]
            )
        })

    columns = [
        "lobby_id", "country", "register", "name",
        "first_seen", "last_seen", "n_snapshots",
        "in_latest_snapshot", "name_variants"
    ]

    unique = pd.DataFrame(rows, columns=columns)

    if unique.duplicated(
        ["country", "register", "lobby_id"]
    ).any():
        raise RuntimeError(
            "Identificadores UK duplicados"
        )

    unique = normalize_unique_dates(unique)
    unique.to_parquet(
        STAGE / "unique" / "UK.parquet",
        index=False
    )

    pd.DataFrame(audit).to_csv(
        STAGE / "audit" / "UK_snapshots.csv",
        index=False
    )

    print(
        f"UK: {len(files)} archivos | "
        f"{total_rows} observaciones | "
        f"{len(unique)} entidades indexadas",
        flush=True
    )

    return unique



def main():
    if STAGE.exists():
        raise FileExistsError(
            f"Ya existe {STAGE}. No se sobrescribe."
        )

    (STAGE / "unique").mkdir(parents=True)
    (STAGE / "history").mkdir()
    (STAGE / "indexes" / "names").mkdir(parents=True)

    indexes = []

    # Preservar los índices existentes de Alemania y UE.
    for country in ("DE", "UE"):
        src = DATA / "unique" / f"{country}.parquet"
        dst = STAGE / "unique" / f"{country}.parquet"
        df = normalize_unique_dates(pd.read_parquet(src))
        df.to_parquet(dst, index=False)
        indexes.append(df)

    for country, cfg in CONFIG.items():
        indexes.append(build_country(country, cfg))

    indexes.append(build_italy())
    indexes.append(build_czechia())
    indexes.append(build_estonia())
    indexes.append(build_luxembourg())
    build_netherlands()
    indexes.append(build_poland())
    indexes.append(build_united_kingdom())

    all_df = pd.concat(indexes, ignore_index=True)

    keys = ["country", "register", "lobby_id"]
    if all_df.duplicated(keys).any():
        raise RuntimeError("Entidades duplicadas en índice global")

    all_df.to_parquet(
        STAGE / "indexes" / "all_lobbies.parquet",
        index=False
    )

    # Reutilizar sin modificar el constructor original.
    script = ROOT / "scripts" / "build_name_catalog.py"
    spec = importlib.util.spec_from_file_location(
        "eulob_original_names", script
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.SOURCE = STAGE / "unique"
    module.DEST = STAGE / "indexes" / "names"
    module.COUNTRIES = (
        "AT", "CY", "DE", "ES", "FI",
        "IE", "LT", "RO", "UE", "FR", "LV", "GR", "IT", "BE", "CZ", "EE", "LU", "PL", "UK"
    )
    module.main()

    # Garantizar que ninguna relación anterior desaparece.
    old = pd.read_parquet(
        DATA / "indexes" / "names" / "name_ids.parquet"
    )
    new = pd.read_parquet(
        STAGE / "indexes" / "names" / "name_ids.parquet"
    )

    columns = [
        "name_id", "name_normalized",
        "name", "country", "register", "lobby_id"
    ]

    old_relations = set(
        old[columns].itertuples(index=False, name=None)
    )
    new_relations = set(
        new[columns].itertuples(index=False, name=None)
    )

    missing = old_relations - new_relations
    if missing:
        raise RuntimeError(
            f"Se perderían {len(missing)} relaciones antiguas"
        )

    expected = {
        "AT": 487, "CY": 377, "FI": 1384,
        "IE": 3032, "LT": 424, "RO": 108,
        "ES": 620
    }

    for country, minimum in expected.items():
        n = len(all_df[all_df.country == country])
        if n < minimum:
            raise RuntimeError(
                f"{country}: {n} entidades, esperadas al menos {minimum}"
            )

    print("\n========== VALIDACIÓN FINAL ==========")
    print("Ámbitos:", all_df.country.nunique())
    print("Entidades históricas:", len(all_df))
    print("Relaciones anteriores conservadas:", len(old_relations))
    print("Relaciones totales:", len(new))
    print("Nombres únicos:",
          len(pd.read_parquet(
              STAGE / "indexes" / "names" / "names.parquet"
          )))
    print("CANDIDATO CONSTRUIDO CORRECTAMENTE")
    print("Directorio:", STAGE)



def rebuild_global_indexes():
    """Regenerar índices globales desde los índices nacionales existentes."""
    import os
    import tempfile

    countries = (
        "AT", "BE", "CY", "CZ", "DE", "EE", "ES",
        "FI", "FR", "GR", "IE", "IT", "LT", "LU",
        "LV", "PL", "RO", "UE", "UK"
    )

    keys = ["country", "register", "lobby_id"]
    source = STAGE / "unique"
    indexes_dir = STAGE / "indexes"

    print("========== ÍNDICES NACIONALES ==========", flush=True)

    available = {
        p.stem for p in source.glob("*.parquet")
        if p.stem != "NL"
    }

    if available != set(countries):
        raise RuntimeError(
            f"Ámbitos inesperados: {available ^ set(countries)}"
        )

    frames = []

    for country in countries:
        df = pd.read_parquet(source / f"{country}.parquet")

        if df.empty:
            raise RuntimeError(f"{country}: índice vacío")

        if not df["country"].eq(country).all():
            raise RuntimeError(f"{country}: país inconsistente")

        if df.duplicated(keys).any():
            raise RuntimeError(f"{country}: IDs duplicados")

        frames.append(df)
        print(f"{country}: {len(df):,}", flush=True)

    combined = pd.concat(frames, ignore_index=True)

    if combined.duplicated(keys).any():
        raise RuntimeError("Duplicados en índice global")

    old_path = indexes_dir / "all_lobbies.parquet"
    old = pd.read_parquet(old_path)

    if list(old.columns) != list(combined.columns):
        raise RuntimeError("Esquema incompatible")

    old_keys = set(
        old[keys].itertuples(index=False, name=None)
    )
    new_keys = set(
        combined[keys].itertuples(index=False, name=None)
    )

    missing = old_keys - new_keys

    # Polonia: migración de IDs provisionales con hash
    # a números oficiales de cinco dígitos.
    legacy_pl = {
        key for key in missing
        if key[0] == "PL"
        and key[1] == "Polish Professional Lobbying Register"
        and re.fullmatch(
            r"[0-9]{5}:[0-9a-f]{64}", str(key[2])
        )
    }

    if legacy_pl:
        current_pl = combined.loc[combined.country == "PL"]
        if len(legacy_pl) != 704 or len(current_pl) != 658:
            raise RuntimeError(
                "PL: migración histórica no reconocida"
            )
        if not current_pl.lobby_id.astype(str).str.fullmatch(
            r"[0-9]{5}"
        ).all():
            raise RuntimeError(
                "PL: identificadores oficiales inválidos"
            )

    unexpected_missing = missing - legacy_pl

    if unexpected_missing:
        raise RuntimeError(
            f"Desaparecerían {len(unexpected_missing)} "
            f"entidades históricas. "
            f"Ejemplos: {list(sorted(unexpected_missing))[:5]}"
        )

    script = ROOT / "scripts" / "build_name_catalog.py"
    spec = importlib.util.spec_from_file_location(
        "eulob_name_catalog", script
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with tempfile.TemporaryDirectory(
        prefix=".eulob_rebuild_",
        dir=STAGE
    ) as directory:

        tmp = Path(directory)
        candidate_all = tmp / "all_lobbies.parquet"

        combined.to_parquet(candidate_all, index=False)

        module.SOURCE = source
        module.DEST = tmp / "names"
        module.COUNTRIES = countries
        module.main()

        candidate_names = module.DEST / "names.parquet"
        candidate_relations = module.DEST / "name_ids.parquet"

        check_all = pd.read_parquet(candidate_all)
        names = pd.read_parquet(candidate_names)
        relations = pd.read_parquet(candidate_relations)

        recovered = set(
            relations[keys].itertuples(index=False, name=None)
        )

        if recovered != new_keys:
            raise RuntimeError("Integridad de entidades incorrecta")

        if len(check_all) != len(new_keys):
            raise RuntimeError("Recuento global inconsistente")

        if not names["name_id"].is_unique:
            raise RuntimeError("Nombres duplicados")

        if relations.duplicated(
            ["name_id", *keys]
        ).any():
            raise RuntimeError("Relaciones duplicadas")

        if set(names["name_id"]) != set(relations["name_id"]):
            raise RuntimeError("Catálogo de nombres inconsistente")

        print("\n========== VALIDACIÓN ==========")
        print("Entidades:", len(check_all))
        print("Nombres:", len(names))
        print("Relaciones:", len(relations))
        print("Entidades desaparecidas:", len(missing))

        replacements = [
            (candidate_all, old_path),
            (
                candidate_names,
                indexes_dir / "names" / "names.parquet"
            ),
            (
                candidate_relations,
                indexes_dir / "names" / "name_ids.parquet"
            )
        ]

        backup = tmp / "previous"
        backup.mkdir()

        for i, (_, destination) in enumerate(replacements):
            if not destination.is_file():
                raise FileNotFoundError(destination)

            shutil.copy2(
                destination,
                backup / f"{i}.parquet"
            )

        completed = []

        try:
            for i, (candidate, destination) in enumerate(replacements):
                os.replace(candidate, destination)
                completed.append((i, destination))

            final_all = pd.read_parquet(old_path)
            final_names = pd.read_parquet(
                indexes_dir / "names" / "names.parquet"
            )
            final_relations = pd.read_parquet(
                indexes_dir / "names" / "name_ids.parquet"
            )

            if (
                len(final_all) != len(check_all)
                or len(final_names) != len(names)
                or len(final_relations) != len(relations)
            ):
                raise RuntimeError("Verificación posterior incorrecta")

            final_keys = set(
                final_all[keys].itertuples(index=False, name=None)
            )
            final_recovered = set(
                final_relations[keys].itertuples(index=False, name=None)
            )

            if final_keys != new_keys or final_recovered != new_keys:
                raise RuntimeError("Integridad posterior incorrecta")

        except Exception:
            for i, destination in reversed(completed):
                os.replace(
                    backup / f"{i}.parquet",
                    destination
                )
            raise

    print("\nÍNDICES GLOBALES RECONSTRUIDOS CORRECTAMENTE")
    print("Staging:", STAGE)
    print("Entidades:", len(combined))
    print("Nombres:", len(names))
    print("Relaciones:", len(relations))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--rebuild-global":
        rebuild_global_indexes()
    elif len(sys.argv) == 1:
        main()
    else:
        raise SystemExit("Uso: build_expand_countries.py [--rebuild-global]")
