import random # random.randint(a, b) Return a random integer N such that a <= N <= b.

class DiceError(Exception):
    pass

# Verify the input is a string, remove any whitespace, check it has only characters from the permissible set then pass to calculate method
def roll(raw_data):
    if type(raw_data) is not str:
        raise DiceError('Roll: Input must be in string form (got: ' + str(type(raw_data)) + ')')

    formated_data = raw_data.lower().replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
    for char in formated_data:
        if char not in '0123456789d+-*/()':
            raise DiceError('Roll: Invalid character/s in input string \''+ raw_data + '\'')
    while True:
        #print formated_data
        new_data = formated_data.replace('--', '+')
        if formated_data != new_data:
            formated_data = new_data
            continue
        new_data = formated_data.replace('++', '+')
        if formated_data != new_data:
           formated_data = new_data
           continue
        new_data = formated_data.replace('-+-', '+')
        if formated_data != new_data:
            formated_data = new_data
            continue
        new_data = formated_data.replace('+-', '-').replace('-+', '-')
        if formated_data != new_data:
            formated_data = new_data
            continue
        break
    #print formated_data

    total = (__calculate(formated_data))
    print  raw_data + ' = ' + str(total[0]) + ' (' + str(total[1]) + ')'
    return total


# Return the evaluated experession and an ordered list of the results of each individual dice roll
def __calculate(raw_data):
    # Strip matched sets of parentheses from start/end of input string
    while len(raw_data) >= 2 and raw_data[0] + raw_data[-1] == '()':
        raw_data = raw_data[1:-1]
    total = None
    roll_results = []
    stop = False

    # Immediately return if input is a single literal number or dice term
    # Check for a literal number
    try:
        total = int(raw_data)
    except:
        pass
    else:
        stop = True
    # Check for a single dice term: '(int)'d'(int)'.
    try:
        split_list = raw_data.split('d')
        if len(split_list) !=2:
            raise Exception
        if split_list[0] is '':
            quantity = 1
        else:
            quantity = int(split_list[0])
        die_type = int(split_list[1])
        if die_type <= 0:
            raise DiceError('Invalid dice descriptor \'' + raw_data +'\'')
    except(DiceError):
        raise
    except:
        pass
    else:
        total = 0
        for i in range(quantity):
            # A standard d10 is a special case - 0-9 not 1-10 as expected
            result = random.randint(1 if die_type != 10 else 0, die_type if die_type != 10 else 9)
            total += result
            roll_results += [result]

        stop = True


    # find the lowest precedence operator and return the appropriate combination of the evaluated values of the operands
    paren_depth = 0 # current level within parenthses
    sweep2 = False # looking for + during the first sweep and *, / in the second

    while not stop:
        # Read the string backwards to find lowest precedence operator first
        for i in  [len(raw_data) - x - 1 for x in range(0, len(raw_data))]:
            char = raw_data[i]
            if char == ')':
                paren_depth += 1
            elif char == '(':
                paren_depth -= 1
            elif paren_depth == 0 and char in ('+-' * (not sweep2)) + ('*/' * sweep2):
                # Recursively evaluate the operands of the operator found.
                operand1 = __calculate(raw_data[:i])
                operand2 = __calculate(raw_data[i+1:])
                roll_results += (operand1[1] + operand2[1])
                operand1, operand2 = operand1[0], operand2[0]
                if char == '+':
                    total = operand1 + operand2
                elif char == '-':
                    total = operand1 - operand2
                elif char == '*':
                    total = operand1 * operand2
                elif char == '/':
                    total = operand1 // operand2

                stop = True
            if stop: 
                break
        if paren_depth != 0:
            raise DiceError('Bad Formatting: unmatched parentheses in input string "' + raw_data + '"')
        stop |= sweep2 # don't change stop if it is already True
        sweep2 = not sweep2

    if total is not None:
        return (total, roll_results) 
    else:
        raise DiceError('Bad Formatting in input string "' + raw_data + '"') # total never got assigned an int value 

#######################################
## TESTING
#######################################