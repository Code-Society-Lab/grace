"""
This module contains functions for working with logic operations and propositions
"""

from lib.discrete_maths.parsers import shunting_yard

OPERATION_BY_PRECEDENCES = {"=": 2, ">": 3, "v": 4, "^": 5, "~": 6}
"""= == iff, > == implies, v == or, ^ == and, ~ == not"""

def negation(a):
    return not a

def conjunction(a, b):
    return a and b

def disjunction(a, b):
    return a or b

def implies(a, b):
    return (not a) or b

def iff(a, b):
    return (a and b) or ((not a) and (not b))

def xor(a, b):
    return (a and (not b)) or ((not a) and b)

def nand(a, b):
    return not (a and b)

def nor(a, b):
    return not (a or b)

def xnor(a, b):
    return (not a and not b) or (a and b)

def is_balanced_proposition(proposition: str) -> bool:
    """Check if a proposition is balanced
    
    :param proposition: A proposition
    :type proposition: str
    """
    balance = 0
    for char in proposition:
        if char == '(':
            balance += 1
        elif char == ')':
            balance -= 1
        if balance < 0:
            return False
    
    return balance == 0

def is_well_formed_proposition(proposition: str) -> bool:
    """Check if a proposition is well-formed

    :param proposition: A proposition
    :type proposition: str
    """
    for i in range(len(proposition) - 1):
        if proposition[i] in ['v', '^', '>', '='] and proposition[i + 1] in ['v', '^', '>', '=']:
            return False
        if proposition[i].isalpha() and proposition[i + 1].isalpha():
            return False
        
    return True

def is_valid_proposition(proposition: str) -> bool:
    """Check if a proposition is valid

    :param proposition: A proposition
    :type proposition: str
    """
    if not proposition:
        raise SyntaxError("Empty proposition")

    for char in proposition:
        if char not in ['~', '(', ')', 'v', '^', '>', '=', ' ']:
            if not char.isalpha():
                raise ValueError("Invalid character in proposition: " + char)
    
    if not is_balanced_proposition(proposition):
        raise SyntaxError("Unbalanced proposition")
    
    if not is_well_formed_proposition(proposition):
        raise SyntaxError("Proposition is not well-formed")
    
    return True
    
def calculate_rpn_prop(reverse_polish_prop: list, variable_values: dict) -> bool:
    """Calculate the result of a proposition when in Reverse Polish Notation

    :param reverse_polish_prop: A proposition in rpn form
    :type reverse_polish_prop: list
    """
    
    stack = []

    for token in reverse_polish_prop:
        if token in variable_values.keys():
            stack.append(variable_values[token])
        elif token == "~":
            stack.append(negation(stack.pop()))
        elif token == "^":
            stack.append(conjunction(stack.pop(), stack.pop()))
        elif token == "v":
            stack.append(disjunction(stack.pop(), stack.pop()))
        elif token == ">":
            stack.append(implies(stack.pop(), stack.pop()))
        elif token == "=":
            stack.append(iff(stack.pop(), stack.pop()))
    
    return stack.pop()

def generate_values_for_variables(reverse_polish_prop: list) -> list:
    """Create a list of all the possible values for the proposition and calculate the result of the proposition for each combination
    
    :param reverse_polish_prop: A proposition in Reverse Polish Notation
    :type reverse_polish_prop: list
    """
    variable_list = []
    variable_count = 0
    for token in reverse_polish_prop:
        if token.isalpha() and token not in variable_list and token not in OPERATION_BY_PRECEDENCES.keys():
            variable_list.append(token)
            variable_count += 1

    combinations_list = []
    for i in range(2 ** variable_count):
        combination = []
        for j in range(variable_count):
            combination.append(bool(i & (1 << j)))
        combinations_list.append(combination)
    
    return combinations_list, variable_list

# Check if a proposition is a tautology
def is_prop_tautolgy(proposition: str) -> bool:
    # Sanity check
    if not is_valid_proposition(proposition):
        raise SyntaxError("Invalid proposition")

    proposition = proposition.replace(" ", "")
    rpn_tokenization = shunting_yard(proposition, OPERATION_BY_PRECEDENCES)

    combinations_list, variable_list = generate_values_for_variables(rpn_tokenization)

    # Calculate the result of the proposition for each combination and add the result to the list
    results = []
    for combination in combinations_list:
        variable_values = {}
        for i in range(len(variable_list)):
            variable_values[variable_list[i]] = combination[i]
        results.append(calculate_rpn_prop(rpn_tokenization, variable_values))

    # Check if all the results are true
    return all(results)

# Create a truth table from a proposition
def create_truth_table(proposition: str) -> str:
    # Sanity check
    if not is_valid_proposition(proposition):
        raise SyntaxError("Invalid proposition")
    
    truth_table = ""
    initial_proposition = proposition

    # Prepare the proposition
    proposition = proposition.replace(" ", "")
    rpn_tokenization = shunting_yard(proposition, OPERATION_BY_PRECEDENCES)
    
    combination_list, variable_list = generate_values_for_variables(rpn_tokenization)

    # Prepare the table
    for char in variable_list:
        truth_table += " " + char + " |"

    truth_table += " " + initial_proposition + "\n" + ("----" * len(variable_list) + "----") + "\n"

    # Create a list of all the possible values for the proposition and calculate the result of the proposition for each combination
    for combination in combination_list:
        variable_values = {}
        for i in range(len(variable_list)):
            variable_values[variable_list[i]] = combination[i]

        result = calculate_rpn_prop(rpn_tokenization, variable_values)

        # Add the result to the truth table text
        for i in range(len(variable_list)):
            truth_table += " "
            if variable_values[variable_list[i]]:
                truth_table += "1 |"
            else:
                truth_table += "0 |"
        if result:
            truth_table += " 1\n"
        else:
            truth_table += " 0\n"


    return truth_table