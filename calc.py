#!usr/bin/env python3.10

from dataclasses import dataclass
from typing import Callable


operators = [
    ["^", lambda left=None, right=None: [left ** right], 1],
    ["*", lambda left=None, right=None: [left * right], 2],
    ["/", lambda left=None, right=None: [left / right], 2],
    ["+", lambda left=0, right=None: [left + right], 3],
    ["-", lambda left=0, right=None: [left - right], 3],
]
operators_list = [i[0] for i in operators]
parentheses = [
    ["(", ")", lambda inside: inside],
    ["|", "|", lambda inside: abs(inside)],
]
parentheses_list = [i[0] for i in parentheses]
numbers_list = "1234567890."


def find_exact(item, array):  # .index() finds item by equality, not by ids
    return next((c for c, x in enumerate(array) if x is item), None)


def get_first_number(raw: str):
    if raw.startswith("."):
        raw = "0" + raw
    num_len = 1
    while True:
        try:
            float(raw[:num_len])
        except ValueError:
            return float(raw[:num_len-1]), raw[num_len-1:]
        num_len += 1
        if num_len >= len(raw):
            return float(raw), ""


def parse_expression_to_tokens(expression: str):
    # print(expression)
    answer = []
    while expression != "":
        s = expression[0]
        match s:
            case s if s in numbers_list:
                n, r = get_first_number(expression)
                expression = r
                answer.append(n)
            case s if s in operators_list:
                expression = expression[1:]
                operator = operators[operators_list.index(s)]
                answer.append(Operator(*operator))
            case s if s in parentheses_list:
                parenthese = parentheses[parentheses_list.index(s)]

                ending_parenthese_index = -1
                unclosed_parentheses_count = 0
                for c, i in enumerate(expression):
                    if i == parenthese[1] and unclosed_parentheses_count:
                        unclosed_parentheses_count -= 1
                    elif i == parenthese[0]:
                        unclosed_parentheses_count += 1
                    if not unclosed_parentheses_count:
                        ending_parenthese_index = c
                        break
                if unclosed_parentheses_count:
                    raise ValueError("parenthese not paired!")

                ending_parenthese = EndingParenthese(parenthese[1])
                answer += [
                    StartingParenthese(parenthese[0], ending_parenthese, parenthese[2]),
                    *parse_expression_to_tokens(expression[1:ending_parenthese_index]),
                    ending_parenthese,
                    *parse_expression_to_tokens(expression[ending_parenthese_index+1:])
                ]
                expression = ""
            case s if s in " ":
                expression = expression[1:]
            case _:
                raise ValueError("unknown symbol!")
    return answer


def solve_tokens(tokens):
    # [print(i) for i in tokens]
    # print()

    tmp = [(c, i) for c, i in enumerate(tokens) if isinstance(i, StartingParenthese)]
    if tmp:
        starting_parenthese_index, parenthese = tmp[0]
        ending_parenthese_index = find_exact(parenthese.pair, tokens)
        return solve_tokens(
            tokens[:starting_parenthese_index] +
            [parenthese.func(solve_tokens(tokens[starting_parenthese_index + 1:ending_parenthese_index]))] +
            tokens[ending_parenthese_index + 1:]
        )
    del tmp

    current_priority = 0
    while True:
        if len(tokens) == 1:
            return tokens[0]

        current_priority += 1
        operators_to_process = [i for i in tokens if isinstance(i, Operator) if i.priority == current_priority]
        for op in operators_to_process:
            c = find_exact(op, tokens)
            if c == 0:
                tokens = op.func(right=tokens[1]) + tokens[2:]
            elif c == len(tokens) - 1:
                tokens = tokens[:-2] + op.func(left=tokens[-2])
            else:
                tokens = tokens[:c-1] + op.func(tokens[c-1], tokens[c+1]) + tokens[c+2:]


def solve(expr):
    return solve_tokens(parse_expression_to_tokens(expr))


def main():

    to_solve = input("what you want to solve? ")
    print("solved!", solve(to_solve))
    # [print(i) for i in parse_expression_to_tokens(to_solve)]


# token classes
@dataclass
class Operator:
    symbol: str
    func: Callable
    priority: int


@dataclass
class EndingParenthese:
    symbol: str


@dataclass
class StartingParenthese:
    symbol: str
    pair: EndingParenthese
    func: Callable


if __name__ == "__main__":
    main()
