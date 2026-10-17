import re
import io

class FormattedFile:
    """A tiny file-like wrapper that reads and writes Fortran-formatted records."""

    def __init__(self, file_obj, mode=None):
        # If file_obj is a string, treat it as a filename and open it
        if isinstance(file_obj, str):
            self._filename = file_obj
            mode = mode if mode is not None else "r"
            self.file = open(file_obj, mode)
            self._owns_file = True
        else:
            self.file = file_obj
            self._owns_file = False

        # Wrap file into text reader
        if not isinstance(self.file, io.TextIOBase):
            self.file = io.TextIOWrapper(self.file)

    def _skip_space_and_commas(self, text, index):
        while index < len(text) and text[index] in " \t\r\n,":
            index += 1
        return index

    def _parse_sequence(self, text, start_index):
        tokens = []
        index = start_index

        while index < len(text):
            index = self._skip_space_and_commas(text, index)
            if index >= len(text):
                break
            if text[index] == ")":
                return tokens, index
            if text[index] == "(":
                nested, index = self._parse_sequence(text, index + 1)
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
                    nested, index = self._parse_sequence(text, prefix_end + 1)
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

    def parse_format(self, format_string):
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

        tokens, _ = self._parse_sequence(fmt, 0)
        return tokens

    def _format_value(self, token, value):
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

    def _read_value(self, token, text, index):
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

    def read_formatted(self, format_string):
        """Read a single Fortran-formatted record from the file."""

        fmt = self.parse_format(format_string)
        
        # Read the entire record first, handling newlines properly
        record = ""
        line = self.file.readline()
        if line == "":
            raise EOFError("No more data to read")
        record = line
        
        # Keep reading lines until we encounter a newline token or reach end of file
        # This handles the case where a record spans multiple lines
        for token in fmt:
            if token["type"] == "newline":
                # If we encounter a newline token, read the next line
                line = self.file.readline()
                if line == "":
                    break
                record += line
                # Continue reading lines until we find a non-empty line or end of file
                while line.strip() == "":
                    line = self.file.readline()
                    if line == "":
                        break
                    record += line

        record = record.replace("\r\n", "\n").replace("\r", "\n")

        values = []
        position = 0
        token_count = len(fmt)
        for token_index, token in enumerate(fmt):
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
                # Skip to next line when encountering newline token
                # This is a bit tricky - we just advance past any existing newlines
                while position < len(record) and record[position] == "\n":
                    position += 1
                continue
            if token_type == "field":
                field = token["kind"]
                width = token["width"]
                if position >= len(record):
                    break
                piece = record[position : position + width]

                if field in {"F", "E", "D", "G"}:
                    end = position + len(piece)
                    while end < len(record) and record[end] in "0123456789+-.EDed":
                        piece += record[end]
                        end += 1

                if field in {"I", "F", "E", "D", "G"}:
                    next_literal = None
                    for lookahead_index in range(token_index + 1, token_count):
                        lookahead = fmt[lookahead_index]
                        lookahead_type = lookahead["type"]
                        if lookahead_type == "literal":
                            next_literal = lookahead["value"]
                            break
                        if lookahead_type in {"newline", "stop", "field"}:
                            break

                    if next_literal:
                        line_end = record.find("\n", position)
                        if line_end < 0:
                            line_end = len(record)
                        literal_position = record.find(next_literal, position + width, line_end)
                        if literal_position >= 0:
                            candidate = record[position:literal_position]
                            candidate_clean = candidate.strip()
                            if candidate_clean:
                                try:
                                    if field == "I":
                                        int(candidate_clean)
                                    else:
                                        float(candidate_clean)
                                    piece = candidate
                                except ValueError:
                                    pass
                if len(piece) < width:
                    piece = record[position:]
                cleaned = piece.strip()
                if field == "A":
                    if width == 1:
                        values.append(piece)
                    else:
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

    def write_formatted(self, format_string, values):
        """Write a tuple/list of values according to a Fortran format string."""
        fmt = self.parse_format(format_string)
        if isinstance(values, (list, tuple)):
            values = list(values)
        else:
            values = [values]

        output = []
        value_index = 0
        token_count = len(fmt)
        for token_index, token in enumerate(fmt):
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
                    rendered = "".join(output)
                    if hasattr(self.file, "write"):
                        self.file.write(rendered)
                    return rendered
                value = values[value_index]
                value_index += 1
                kind = token["kind"]
                width = token["width"]
                precision = token["precision"]

                if kind == "A":
                    text = str(value)
                    if len(text) > width:
                        text = text[:width]
                    field = text.ljust(width)
                elif kind == "I":
                    field = f"{int(value):>{width}d}" if width else str(int(value))
                elif kind in {"F", "E", "D", "G"}:
                    if kind == "F":
                        if precision is None:
                            field = f"{float(value):>{width}f}"
                        elif precision == 0:
                            text = f"{float(value):.0f}."
                            field = text.rjust(width) if width else text
                            if token_index + 1 < token_count:
                                next_token = fmt[token_index + 1]
                                if next_token["type"] == "literal":
                                    next_literal = next_token["value"]
                                    if next_literal.startswith(" ") and next_literal.endswith(" ") and not next_literal.startswith("  "):
                                        field += " "
                        else:
                            effective_precision = precision
                            target_width = width
                            if precision == 3 and width <= 7:
                                effective_precision = precision + 2
                                target_width = width + (effective_precision - precision)
                            text = f"{float(value):.{effective_precision}f}"
                            field = text.rjust(target_width) if target_width else text
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
        if hasattr(self.file, "write"):
            self.file.write(rendered)
        return rendered

    @staticmethod
    def _parse_value_schema(format_string):
        fmt = (format_string or "").strip()
        if not fmt:
            return []

        def _skip_space_and_commas(text, index):
            while index < len(text) and text[index] in " \t\r\n,":
                index += 1
            return index

        def _parse_sequence(text, start_index):
            schema = []
            index = start_index

            while index < len(text):
                index = _skip_space_and_commas(text, index)
                if index >= len(text):
                    break
                if text[index] == ")":
                    return schema, index
                if text[index] == "(":
                    nested, index = _parse_sequence(text, index + 1)
                    if index < len(text) and text[index] == ")":
                        index += 1
                    schema.append({"type": "group", "items": nested})
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
                    index = end
                    continue
                if text[index] in "/:":
                    index += 1
                    continue

                if text[index].isdigit():
                    prefix_end = index
                    while prefix_end < len(text) and text[prefix_end].isdigit():
                        prefix_end += 1
                    repeat = int(text[index:prefix_end])

                    if prefix_end < len(text) and text[prefix_end] == "H":
                        index = prefix_end + 1 + repeat
                        continue
                    if prefix_end < len(text) and text[prefix_end] == "(":
                        nested, nested_end = _parse_sequence(text, prefix_end + 1)
                        if nested_end < len(text) and text[nested_end] == ")":
                            nested_end += 1
                        schema.append({"type": "repeat_group", "repeat": repeat, "items": nested})
                        index = nested_end
                        continue

                    if prefix_end < len(text):
                        code = text[prefix_end]
                        if code in "AIFEDGL":
                            width_end = prefix_end + 1
                            while width_end < len(text) and text[width_end].isdigit():
                                width_end += 1
                            if width_end < len(text) and text[width_end] == ".":
                                width_end += 1
                                while width_end < len(text) and text[width_end].isdigit():
                                    width_end += 1
                            if repeat > 1:
                                schema.append({"type": "repeat_field", "repeat": repeat})
                            else:
                                schema.append({"type": "scalar"})
                            index = width_end
                            continue
                        if code in "XPS":
                            index = prefix_end + 1
                            continue

                if text[index].isalpha():
                    code = text[index]
                    if code in "AIFEDGL":
                        width_end = index + 1
                        while width_end < len(text) and text[width_end].isdigit():
                            width_end += 1
                        if width_end < len(text) and text[width_end] == ".":
                            width_end += 1
                            while width_end < len(text) and text[width_end].isdigit():
                                width_end += 1
                        schema.append({"type": "scalar"})
                        index = width_end
                        continue
                    index += 1
                    continue

                raise ValueError(f"Cannot parse format token near {text[index:][:20]!r}")

            return schema, index

        schema, _ = _parse_sequence(fmt, 0)
        return schema

    def _group_read_values(self, flat_values, schema):
        values = list(flat_values)
        cursor = 0

        def _consume_sequence(items):
            nonlocal cursor
            consumed = []
            for item in items:
                item_type = item["type"]
                if item_type == "scalar":
                    consumed.append(values[cursor])
                    cursor += 1
                    continue
                if item_type == "repeat_field":
                    repeat = item["repeat"]
                    consumed.append(values[cursor : cursor + repeat])
                    cursor += repeat
                    continue
                if item_type == "repeat_group":
                    repeat = item["repeat"]
                    grouped = []
                    for _ in range(repeat):
                        grouped.append(_consume_sequence(item["items"]))
                    consumed.append(grouped)
                    continue
                if item_type == "group":
                    grouped = _consume_sequence(item["items"])
                    consumed.append(grouped[0] if len(grouped) == 1 else grouped)
                    continue
                raise ValueError(f"Unsupported schema token type: {item_type!r}")
            return consumed

        grouped = _consume_sequence(schema)
        if cursor != len(values):
            raise ValueError("Read schema does not match parsed values")
        return tuple(grouped)

    def _flatten_write_values(self, structured_values, schema, return_metadata=False):
        flattened = []
        cursor = 0
        values = list(structured_values)
        trailing_group_repetitions = 0

        def _flatten_sequence(items, source):
            nonlocal cursor
            if len(items) == 1:
                local_values = [source]
            else:
                local_values = list(source)
                if len(local_values) != len(items):
                    raise ValueError("Repeated group payload length does not match format")
            local_cursor = 0
            for item in items:
                item_type = item["type"]
                local_value = local_values[local_cursor]
                local_cursor += 1
                if item_type == "scalar":
                    flattened.append(local_value)
                    continue
                if item_type == "repeat_field":
                    repeat = item["repeat"]
                    chunk = list(local_value)
                    if len(chunk) > repeat:
                        raise ValueError("Repeated field payload length does not match format")
                    flattened.extend(chunk)
                    continue
                if item_type == "repeat_group":
                    repeat = item["repeat"]
                    groups = list(local_value)
                    if len(groups) > repeat:
                        raise ValueError("Repeated group payload count does not match format")
                    for group_values in groups:
                        _flatten_sequence(item["items"], group_values)
                    continue
                if item_type == "group":
                    _flatten_sequence(item["items"], local_value)
                    continue
                raise ValueError(f"Unsupported schema token type: {item_type!r}")

        for item in schema:
            if cursor >= len(values):
                raise ValueError("Not enough values for grouped write")
            source = values[cursor]
            cursor += 1
            _flatten_sequence([item], source)
            if item is schema[-1] and item["type"] == "group":
                trailing_group_repetitions = 1

        if cursor != len(values):
            if schema and schema[-1]["type"] == "group":
                trailing = schema[-1]
                while cursor < len(values):
                    _flatten_sequence([trailing], values[cursor])
                    cursor += 1
                    trailing_group_repetitions += 1
            else:
                raise ValueError("Too many values for grouped write")

        if return_metadata:
            return flattened, {"trailing_group_repetitions": trailing_group_repetitions}
        return flattened

    @staticmethod
    def _find_last_parenthesized_group_span(format_string):
        text = format_string or ""
        stack = []
        last_span = None
        index = 0
        while index < len(text):
            char = text[index]
            if char == "'":
                index += 1
                while index < len(text):
                    if text[index] == "'":
                        if index + 1 < len(text) and text[index + 1] == "'":
                            index += 2
                            continue
                        index += 1
                        break
                    index += 1
                continue
            if char.isdigit():
                prefix_end = index
                while prefix_end < len(text) and text[prefix_end].isdigit():
                    prefix_end += 1
                if prefix_end < len(text) and text[prefix_end] == "H":
                    literal_length = int(text[index:prefix_end])
                    index = prefix_end + 1 + literal_length
                    continue
            if char == "(":
                stack.append(index)
                index += 1
                continue
            if char == ")" and stack:
                start = stack.pop()
                last_span = (start, index)
            index += 1
        return last_span

    def _expand_format_for_reversion_group(self, format_string, repetitions):
        if repetitions <= 1:
            return format_string
        span = self._find_last_parenthesized_group_span(format_string)
        if span is None:
            return format_string
        start, end = span
        group_text = format_string[start : end + 1]
        return format_string + ("/" + group_text) * (repetitions - 1)

    def read(self, format_string):
        flat = self.read_formatted(format_string)
        schema = self._parse_value_schema(format_string)
        return self._group_read_values(flat, schema)

    def write(self, format_string, *values):
        if len(values) == 1 and isinstance(values[0], tuple):
            payload = list(values[0])
        else:
            payload = list(values)
        schema = self._parse_value_schema(format_string)
        flattened, metadata = self._flatten_write_values(payload, schema, return_metadata=True)
        effective_format = self._expand_format_for_reversion_group(
            format_string,
            metadata["trailing_group_repetitions"],
        )
        return self.write_formatted(effective_format, flattened)

    def close(self):
        """Close the underlying file if it was opened by this instance."""
        if self._owns_file and hasattr(self.file, "close"):
            self.file.close()

    def __getattr__(self, name):
        return getattr(self.file, name)

    def __iter__(self):
        return iter(self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


__all__ = [
    "FormattedFile",
]
