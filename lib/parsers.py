# Parsing library

 # Shunting Yard Algorithm - https://en.wikipedia.org/wiki/Shunting_yard_algorithm
def shunting_yard(prop: str, precidence_dict: dict) -> str:
    output_queue = []
    operator_stack = []

    for token in prop:
        if token in precidence_dict.keys():
            if operator_stack and operator_stack[-1] != "(" and precidence_dict[operator_stack[-1]] == precidence_dict[token]:
                output_queue.append(operator_stack.pop())
                operator_stack.append(token)
                continue
            while operator_stack and operator_stack[-1] != "(" and precidence_dict[operator_stack[-1]] > precidence_dict[token]:
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)

        elif token == "(":
            operator_stack.append(token)

        elif token == ")":
            while operator_stack[-1] != "(":
                output_queue.append(operator_stack.pop())
            operator_stack.pop()

        else:
            output_queue.append(token)

    while operator_stack:
        output_queue.append(operator_stack.pop())

    return output_queue