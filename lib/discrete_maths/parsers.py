"""
Parser library

Used to parse a given input string into different data structures or formats
"""

def shunting_yard(input_string: str, precidence_dict: dict) -> str:
    """Convert an infix string to a postfix string using the shunting yard algorithm
    
    :param input_string: The infix string to convert
    :type input_string: str
    :param precidence_dict: A dictionary containing the precidence of each operator
    :type precidence_dict: dict
    """
    output_queue = []
    operator_stack = []

    for token in input_string:
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