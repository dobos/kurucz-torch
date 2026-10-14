import re


def parse_format(format_string):
    """Parse a Fortran format string into a simple token list.

    The parser accepts the subset of format syntax used by the Fortran sources in
    this project:

    * repeats like 2(I5,F7.2) or 10(1X,F8.2)
    * Hollerith literals like 5HTEFF , 9H  GRAVITY
    * field descriptors such as I, F, E, D, G, A, X and scale/sign tokens
    * nested parentheses and record separators /

    Each token is a dictionary with the keys needed by the read/write logic.
    """

    fmt = (format_string or "").strip()
    if not fmt:
        return []

    def _skip_space_and_commas(text, index):
        while index < len(text) and text[index] in " \t\r\n,":
            index += 1
        return index

    def _parse_sequence(text, start_index):
        tokens = []
        index = start_index

        while index < len(text):
            index = _skip_space_and_commas(text, index)
            if index >= len(text):
                break
            if text[index] == ")":
                return tokens, index
            if text[index] == "(":
                nested, index = _parse_sequence(text, index + 1)
                if index < len(text) and text[index] == ")":
                    index += 1
                tokens.extend(nested)
                continue
            if text[index] == "'":
                end = index + 1
                while end < len(text):
                    if text[end] == "'":
                        if end + 1 < len(text) and text[end + 1] == "'":
                            end += 2
                            continue
                        end += 1
                        break
                    end += 1
                tokens.append({"type": "literal", "value": text[index + 1 : end - 1]})
                index = end
                continue

            if text[index].isdigit():
                prefix_end = index
                while prefix_end < len(text) and text[prefix_end].isdigit():
                    prefix_end += 1
                prefix = text[index:prefix_end]
                if prefix_end < len(text) and text[prefix_end] == "H":
                    length = int(prefix)
                    literal = text[prefix_end + 1 : prefix_end + 1 + length]
                    tokens.append({"type": "literal", "value": literal})
                    index = prefix_end + 1 + length
                    continue
                if prefix_end < len(text) and text[prefix_end] == "(":
                    repeat = int(prefix)
                    nested, index = _parse_sequence(text, prefix_end + 1)
                    if index < len(text) and text[index] == ")":
                        index += 1
                    tokens.extend(nested * repeat)
                    continue

                if prefix_end < len(text):
                    code = text[prefix_end]
                    if code == "X":
                        tokens.append({"type": "skip", "count": int(prefix) if prefix else 1})
                        index = prefix_end + 1
                        continue
                    if code == "P":
                        tokens.append({"type": "scale", "value": int(prefix) if prefix else 1})
                        index = prefix_end + 1
                        continue
                    if code == "S":
                        tokens.append({"type": "sign", "mode": "S"})
                        index = prefix_end + 1
                        continue
                    if code in "AIFEDGL":
                        width_end = prefix_end + 1
                        while width_end < len(text) and text[width_end].isdigit():
                            width_end += 1
                        width_text = text[prefix_end + 1 : width_end]
                        width = int(width_text) if width_text else 1
                        precision = None
                        if width_end < len(text) and text[width_end] == ".":
                            precision_end = width_end + 1
                            while precision_end < len(text) and text[precision_end].isdigit():
                                precision_end += 1
                            precision = int(text[width_end + 1 : precision_end])
                            index = precision_end
                        else:
                            index = width_end
                        repeat = int(prefix) if prefix else 1
                        token = {"type": "field", "kind": code, "width": width, "precision": precision}
                        tokens.extend([token] * repeat)
                        continue

                # bare numeric prefix followed by a slash or colon, e.g. 1/ or 2:
                if prefix_end < len(text) and text[prefix_end] in "/:":
                    tokens.append({"type": "newline" if text[prefix_end] == "/" else "stop"})
                    index = prefix_end + 1
                    continue

            if text[index] == "/":
                tokens.append({"type": "newline"})
                index += 1
                continue
            if text[index] == ":":
                tokens.append({"type": "stop"})
                index += 1
                continue

            if text[index].isalpha():
                code = text[index]
                if code == "X":
                    tokens.append({"type": "skip", "count": 1})
                    index += 1
                    continue
                if code in "PS":
                    tokens.append({"type": "scale" if code == "P" else "sign", "value": 1 if code == "P" else "S"})
                    index += 1
                    continue
                if code in "AIFEDGL":
                    width_end = index + 1
                    while width_end < len(text) and text[width_end].isdigit():
                        width_end += 1
                    width_text = text[index + 1 : width_end]
                    width = int(width_text) if width_text else 1
                    precision = None
                    if width_end < len(text) and text[width_end] == ".":
                        precision_end = width_end + 1
                        while precision_end < len(text) and text[precision_end].isdigit():
                            precision_end += 1
                        precision = int(text[width_end + 1 : precision_end])
                        index = precision_end
                    else:
                        index = width_end
                    tokens.append({"type": "field", "kind": code, "width": width, "precision": precision})
                    continue

            raise ValueError(f"Cannot parse format token near {text[index:][:20]!r}")

        return tokens, index

    tokens, _ = _parse_sequence(fmt, 0)
    return tokens


def _format_value(token, value):
    kind = token["kind"]
    width = token["width"]
    precision = token["precision"]

    if kind == "A":
        text = str(value)
        if len(text) > width:
            text = text[:width]
        return text.rjust(width)
    if kind in {"I", "B", "O"}:
        return f"{value:>{width}d}" if width else str(value)
    if kind in {"F", "E", "D", "G"}:
        if kind == "F":
            spec = f"{width}.{precision}f" if precision is not None else f"{width}f"
        elif kind == "E":
            spec = f"{width}.{precision}E" if precision is not None else f"{width}E"
        else:
            spec = f"{width}.{precision}f" if precision is not None else f"{width}f"
        return format(float(value), spec)
    if kind == "L":
        return str(bool(value)).rjust(width)
    return str(value)


def _read_value(token, text, index):
    kind = token["kind"]
    width = token["width"]
    if kind == "A":
        value = text[index : index + width]
        return value.rstrip(), index + width
    if kind == "I":
        piece = text[index : index + width]
        value = piece.strip()
        return int(value) if value else 0, index + width
    if kind in {"F", "E", "D", "G"}:
        piece = text[index : index + width]
        value = piece.strip()
        if value == "":
            return 0.0, index + width
        return float(value), index + width
    if kind == "X":
        return None, index + width
    raise ValueError(f"Unsupported field kind: {kind!r}")


def read_formatted(file_obj, format_string):
    """Read a single Fortran-formatted record from a file-like object."""
    fmt = parse_format(format_string)
    if hasattr(file_obj, "read"):
        record = file_obj.read()
    else:
        record = file_obj
    if record == "":
        raise EOFError("No more data to read")
    record = record.replace("\r\n", "\n").replace("\r", "\n")

    values = []
    position = 0
    for token in fmt:
        token_type = token["type"]
        if token_type == "literal":
            literal = token["value"]
            if position + len(literal) > len(record):
                raise ValueError(f"Hollerith literal {literal!r} does not fit the record")
            actual = record[position : position + len(literal)]
            if actual != literal:
                # allow the common case where the record contains a trailing space
                if actual.strip() != literal.strip():
                    raise ValueError(f"Expected literal {literal!r}, got {actual!r}")
            position += len(literal)
            continue
        if token_type == "skip":
            position += token["count"]
            continue
        if token_type == "newline":
            while position < len(record) and record[position] in "\n":
                position += 1
            continue
        if token_type == "field":
            field = token["kind"]
            width = token["width"]
            if position >= len(record):
                break
            piece = record[position : position + width]
            if len(piece) < width:
                piece = record[position:]
            cleaned = piece.strip()
            if field == "A":
                values.append(cleaned)
            elif field in {"I", "F", "E", "D", "G"}:
                if cleaned == "":
                    values.append(0 if field == "I" else 0.0)
                elif field == "I":
                    values.append(int(cleaned))
                else:
                    values.append(float(cleaned))
            else:
                raise ValueError(f"Unsupported formatted field type: {field!r}")
            position += len(piece)
            continue
        if token_type == "scale":
            continue
        if token_type == "sign":
            continue
        if token_type == "stop":
            break
        raise ValueError(f"Unsupported token type: {token_type!r}")

    return tuple(values)


def write_formatted(file_obj, format_string, values):
    """Write a tuple/list of values according to a Fortran format string."""
    fmt = parse_format(format_string)
    if isinstance(values, (list, tuple)):
        values = list(values)
    else:
        values = [values]

    output = []
    value_index = 0
    for token in fmt:
        token_type = token["type"]
        if token_type == "literal":
            output.append(token["value"])
            continue
        if token_type == "skip":
            output.append(" " * token["count"])
            continue
        if token_type == "newline":
            output.append("\n")
            continue
        if token_type == "scale":
            continue
        if token_type == "sign":
            continue
        if token_type == "stop":
            break
        if token_type == "field":
            if value_index >= len(values):
                raise ValueError(f"Not enough values for format {format_string!r}")
            value = values[value_index]
            value_index += 1
            kind = token["kind"]
            width = token["width"]
            precision = token["precision"]

            if kind == "A":
                text = str(value)
                if len(text) > width:
                    text = text[:width]
                field = text.rjust(width)
            elif kind == "I":
                field = f"{int(value):>{width}d}" if width else str(int(value))
            elif kind in {"F", "E", "D", "G"}:
                if kind == "F":
                    if precision is None:
                        field = f"{float(value):>{width}f}"
                    else:
                        field = f"{float(value):>{width}.{precision}f}"
                elif kind == "E":
                    if precision is None:
                        field = f"{float(value):>{width}E}"
                    else:
                        field = f"{float(value):>{width}.{precision}E}"
                else:
                    if precision is None:
                        field = f"{float(value):>{width}f}"
                    else:
                        field = f"{float(value):>{width}.{precision}f}"
            elif kind == "L":
                field = str(bool(value)).rjust(width)
            else:
                raise ValueError(f"Unsupported field kind: {kind!r}")
            output.append(field)
            continue
        raise ValueError(f"Unsupported token type: {token_type!r}")

    rendered = "".join(output)
    if hasattr(file_obj, "write"):
        file_obj.write(rendered)
    return rendered


class FormattedFile:
    """A tiny file-like wrapper that reads and writes Fortran-formatted records."""

    def __init__(self, file_obj, format_string):
        self.file = file_obj
        self.format_string = format_string
        self.tokens = parse_format(format_string)

    def read(self):
        return read_formatted(self.file, self.format_string)

    def write(self, *values):
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            payload = list(values[0])
        else:
            payload = list(values)
        return write_formatted(self.file, self.format_string, payload)

    def __getattr__(self, name):
        return getattr(self.file, name)

    def __iter__(self):
        return iter(self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.file, "close"):
            self.file.close()


__all__ = [
    "parse_format",
    "read_formatted",
    "write_formatted",
    "FormattedFile",
]