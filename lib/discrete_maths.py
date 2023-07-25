# Operator Precedence Dictionary
OP_PRECIDENCE = {"=": 2, ">": 3, "v": 4, "^": 5, "~": 6}

class DiscreteMaths():
    # Constructor
    def __init__(self):
        pass
    # Check if a proposition is valid
    def __is_valid_proposition(self, proposition: str) -> bool:
        # Check if the proposition is empty
        if not proposition:
            print("Failed: Empty proposition")
            return False

        # Check if the proposition is valid - ~ == not, v == or, ^ == and, > == implies, = == iff
        for char in proposition:
            if char not in ['~', '(', ')', 'v', '^', '>', '=', ' ']:
                if not char.isalpha():
                    print(f"Failed: Invalid character {char}")
                    return False
        
        # Check if the proposition is balanced
        if not self.__is_balanced_proposition(proposition):
            print("Failed: Unbalanced proposition")
            return False
        
        # Check if the proposition is well-formed
        if not self.__is_well_formed_proposition(proposition):
            print("Failed: Proposition is not well-formed")
            return False
        
        # Return true if the proposition is valid
        return True

    # Check if a proposition is balanced
    def __is_balanced_proposition(self, proposition: str) -> bool:
        # Check if the proposition is balanced
        balance = 0
        for char in proposition:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            if balance < 0:
                return False
        
        # Return true if the proposition is balanced
        return balance == 0
    
    # Check if a proposition is well-formed - Might need to be extended
    def __is_well_formed_proposition(self, proposition: str) -> bool:
        # Check if the proposition is well-formed (i.e. there are no 2 consecutive operators)
        for i in range(len(proposition) - 1):
            if proposition[i] in ['v', '^', '>', '='] and proposition[i + 1] in ['v', '^', '>', '=']:
                return False
            
        # Return true if the proposition is well-formed
        return True

    # ~ == not
    def __negation(self, p): # Not
        return not p
    
    # v == or
    def __conjunction(self, p, q): # And
        return p and q
    
    # ^ == and
    def __disjunction(self, p, q): # Or
        return p or q
    
    # > == implies
    def __conditional(self, p, q): # Implies
        return not p or q
    
    # = == iff
    def __biconditional(self, p, q): # Iff
        return p == q

    # Shunting Yard Algorithm - https://en.wikipedia.org/wiki/Shunting_yard_algorithm
    def __ShuntingYard(self, prop: str) -> str:
        output_queue = []
        operator_stack = []

        for token in prop:
            if token in OP_PRECIDENCE.keys():
                if operator_stack and operator_stack[-1] != "(" and OP_PRECIDENCE[operator_stack[-1]] == OP_PRECIDENCE[token]:
                    output_queue.append(operator_stack.pop())
                    operator_stack.append(token)
                    continue
                while operator_stack and operator_stack[-1] != "(" and OP_PRECIDENCE[operator_stack[-1]] > OP_PRECIDENCE[token]:
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

    # Calculate the result of a proposition given a set of variable values and an RPN version of the proposition
    def __calculate_RPN(self, RPN: list, variable_values: dict) -> bool:
        # Temporary stack
        stack = []

        # Go through each token in the RPN proposition
        for token in RPN:
            # If the token is a variable, add it to the stack
            if token in variable_values.keys():
                stack.append(variable_values[token])
            # If the token is an operator, calculate the result of the operation using the values in the stack and add it to the stack
            elif token == "~":
                stack.append(self.__negation(stack.pop()))
            elif token == "^":
                stack.append(self.__conjunction(stack.pop(), stack.pop()))
            elif token == "v":
                stack.append(self.__disjunction(stack.pop(), stack.pop()))
            elif token == ">":
                stack.append(self.__conditional(stack.pop(), stack.pop()))
            elif token == "=":
                stack.append(self.__biconditional(stack.pop(), stack.pop()))
        
        # return the result of the proposition
        return stack.pop()

    # Create a truth table from a proposition
    def create_truth_table(self, proposition: str) -> str:
         # Check if the proposition is valid
        if not self.__is_valid_proposition(proposition):
            return "Invalid proposition."
        # truth table text
        truth_table = ""
        initial_proposition = proposition
        # remove spaces from the proposition
        proposition = proposition.replace(" ", "")
        # Run it through the shunting yard algorithm
        RPN = self.__ShuntingYard(proposition)

        # Get all the variables in the proposition + add to truth table text
        variables = []
        for char in proposition:
            if char.isalpha() and char not in variables and char not in ['v', '^', '>', '=', '~']:
                truth_table += " " + char + " |"
                variables.append(char)

        # Add the proposition to the truth table text
        truth_table += " " + initial_proposition + "\n"
        # Add the line under the variables
        for i in range(len(variables)):
            truth_table += "----"
        truth_table += "----\n"
        
        # Get all combinations of true and false for the variables and have them be true or false
        combinations = []
        for i in range(2 ** len(variables)):
            combination = []
            for j in range(len(variables)):
                combination.append(bool(i & (1 << j)))
            combinations.append(combination)

        # Create a list of all the possible values for the proposition and calculate the result of the proposition for each combination
        results = []
        for value in combinations:
            # Create a dictionary of the variables and their values
            variable_values = {}
            for i in range(len(variables)):
                variable_values[variables[i]] = value[i]

            
            # Calculate the result of the proposition
            result = self.__calculate_RPN(RPN, variable_values)

            # Add the result to the truth table text
            for i in range(len(variables)):
                truth_table += " "
                if variable_values[variables[i]]:
                    truth_table += "1 |"
                else:
                    truth_table += "0 |"
            if result:
                truth_table += " 1\n"
            else:
                truth_table += " 0\n"

            results.append(result)


        return truth_table