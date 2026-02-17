from pathlib import Path
import io

import pandas as pd


def detect_encoding(raw: bytes) -> str:
    # BOM checks
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if raw.startswith(b"\xff\xfe"):
        return "utf-16le"
    if raw.startswith(b"\xfe\xff"):
        return "utf-16be"

    # Heurística: si hay muchos 0x00, probablemente UTF-16 sin BOM
    null_ratio = raw.count(b"\x00") / max(1, len(raw))
    if null_ratio > 0.1:
        # suele ser LE en Windows
        return "utf-16le"

    # fallback típico INE/Windows
    return "cp1252"


def guess_delimiter(text: str) -> str:
    sample = text[:2000]
    counts = {
        ";": sample.count(";"),
        ",": sample.count(","),
        "\t": sample.count("\t"),
        "|": sample.count("|"),
    }
    # el que más aparezca
    return max(counts, key=counts.get)


def main():
    inp = Path("data/raw/ine/turismo_provincia_mes.csv")
    if not inp.exists():
        raise FileNotFoundError(inp)

    raw = inp.read_bytes()
    enc = detect_encoding(raw)
    text = raw.decode(enc, errors="replace")

    # Normaliza saltos de línea
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    print("Encoding detectado:", enc)
    print("¿Contiene \\n?:", "\n" in text, "| nº de \\n:", text.count("\n"))
    print("Primeros 300 chars:\n", text[:300])

    delim = guess_delimiter(text)
    print("Delimitador sugerido:", repr(delim))

    # Intentamos parsear con pandas. Si viene todo en una línea, igual funciona;
    # si no, lo veremos porque sale 1 columna.
    df = pd.read_csv(io.StringIO(text), sep=delim, engine="python")

    print("\nShape:", df.shape)
    print("Columnas:", list(df.columns)[:20])
    print("\nHead (5 filas):")
    print(df.head())

    out = Path("data/raw/ine/turismo_provincia_mes_clean.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    print("\nOK: guardado CSV limpio UTF-8 en:", out)


if __name__ == "__main__":
    main()
