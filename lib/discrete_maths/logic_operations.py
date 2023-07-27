# Classical logic operations library

from lib.parsers import shunting_yard

# Operator Precedence Dictionary - = == iff, > == implies, v == or, ^ == and, ~ == not
OP_PRECIDENCE = {"=": 2, ">": 3, "v": 4, "^": 5, "~": 6}

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

# Check if a proposition is balanced
def is_balanced_proposition(proposition: str) -> bool:
    balance = 0
    for char in proposition:
        if char == '(':
            balance += 1
        elif char == ')':
            balance -= 1
        if balance < 0:
            return False
    
    return balance == 0

# Check if a proposition is well-formed - no 2 consecutive operators or variables
def is_well_formed_proposition(proposition: str) -> bool:
    for i in range(len(proposition) - 1):
        if proposition[i] in ['v', '^', '>', '='] and proposition[i + 1] in ['v', '^', '>', '=']:
            return False
        if proposition[i].isalpha() and proposition[i + 1].isalpha():
            return False
        
    return True

# Check if a proposition is valid
def is_valid_proposition(proposition: str) -> bool:
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
    
# Calculate the result of a proposition given a set of variable values and an RPN version of the proposition
def calculate_rpn_prop(rpn: list, variable_values: dict) -> bool:
    stack = []

    for token in rpn:
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

# Create a list of lists of all the possible values for the variables in the rpn proposition
def create_variable_values(rpn: list) -> list:
    variable_list = []
    variable_count = 0
    for token in rpn:
        if token.isalpha() and token not in variable_list and token not in OP_PRECIDENCE.keys():
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
    rpn_tokenization = shunting_yard(proposition, OP_PRECIDENCE)

    combinations_list, variable_list = create_variable_values(rpn_tokenization)

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
    rpn_tokenization = shunting_yard(proposition, OP_PRECIDENCE)
    
    combination_list, variable_list = create_variable_values(rpn_tokenization)

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