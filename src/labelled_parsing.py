"""Conservative derived parser for explicitly labelled prose numbers.
Does not modify the frozen parser, raw responses or historical scores.
"""
import re
from src.parsing import parse_response, ParseResult

NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"

def parse_labelled(response, required_fields):
    original = parse_response(response, required_fields)
    if all(f in original.values for f in required_fields):
        return original
    if not isinstance(response, str):
        return original
    values = dict(original.values)
    text = response.replace('`', '').replace('**', '').replace(chr(34), '')
    for field in required_fields:
        pattern = re.compile(r'(?<![\w])' + re.escape(field) + r'\s*[:=]\s*(' + NUMBER + r')(?![\w.])', re.I)
        candidates = []
        for match in pattern.finditer(text):
            tail = text[match.end():].lstrip(' \t')
            # Never mistake the first operand of a calculation for its result.
            if tail.startswith(('/', '*', '+', '-', '=')):
                # A chain is accepted only when the remaining same-line text is
                # arithmetic followed by an explicit final numeric result.
                line = text[match.start():].split('\n', 1)[0]
                chain = re.fullmatch(re.escape(field) + r'\s*[:=]\s*[0-9.eE+*/() \t=-]+?=\s*(' + NUMBER + r')\s*', line, re.I)
                if chain:
                    candidates.append(float(chain.group(1)))
                continue
            candidates.append(float(match.group(1)))
        if len(candidates) == 1:
            values[field] = {'value': candidates[0], 'unit': None}
        elif len(candidates) > 1:
            values.pop(field, None)  # repeated labels require explicit review
    return ParseResult('DERIVED_LABELLED_PROSE', values, 'Exact labels only; units not inferred; equations and ambiguous repetitions require review')
