import random
import decimal
import time


def check_answer(correct_answer, input_answer):
    return True if input_answer == correct_answer else False


def update_score(difficulty, bool_right, current_score):
    """updates the score

    Args:
        current_score (int): 
        question_difficulty (str): 
        input_answer (str): typed answer
        correct_answer (str): correct answer

    Returns:
        int: updated score
    """
    add_score = {'easy': 1,
                 'medium': 2,
                 'difficult': 3}

    deduct_score = {'easy': 3,
                    'medium': 1,
                    'difficult': 2}
    if bool_right:
        current_score += add_score[difficulty]
    else:
        current_score -= deduct_score[difficulty]
    return current_score


def generate_random_number(numrange, have_decimals):
    """generates a random number x where a <= x <= b
        the number could contain decimals or is an int
    Args:
        numrange (list): number range to select random number from [a, b]
        have_decimals (int): bool in the form of 0 or 1

    Returns:
        int / decimal: random number
    """
    l_bound, u_bound = numrange[0], numrange[1]
    decimals = 0
    number = None
    if have_decimals:
        decimals = random.randint(1, 3)
        divisor = 10 ** decimals
        number = decimal.Decimal(random.randint(l_bound, u_bound))/divisor
    else:
        number = random.randint(l_bound, u_bound)
    return number


def get_numrange(operation, difficulty, have_decimals):
    """get the number range from which to pick a random number

    Args:
        operation (str): arithmetic operation
        difficulty (str): difficulty
        have_decimals (int/bool): boolean for whether if the 
            random number should contain decimals

    Returns:
        list: [a, b] list that contains low & high of range
    """
    if operation == '+' or operation == '-':
        if have_decimals:
            numranges = {'medium': [[1, 99], [1, 99]],
                         'difficult': [[100, 1000], [100, 1000]]}
        else:
            numranges = {'easy': [[10, 200], [10, 200]],
                         'medium': [[1000, 10000], [1000, 10000]],
                         'difficult': [[10000, 100000], [10000, 100000]]}
    else:
        if have_decimals:
            numranges = {'medium': [[1, 20], [1, 10]],
                         'difficult': [[100, 1000], [0, 100]]}
        else:
            numranges = {'easy': [[1, 99], [1, 9]],
                         'medium': [[10, 99], [10, 20]],
                         'difficult': [[100, 1000], [50, 200]]}
    ranges = numranges[difficulty]
    return ranges[0], ranges[1]


def select_random_difficulty():
    """randomly selects a difficulty

    Returns:
        str: difficulty
    """
    difficulties = {1: 'easy',
                    2: 'medium',
                    3: 'difficult'}
    return difficulties[random.randint(1, 3)]


def select_random_operation():
    """randomly selects an arithmetic operation

    Returns:
        str: arithmetic operation
    """
    operations = ['+', '-', '*', '/']
    return operations[random.randint(2, 3)]


def get_question_type():
    """gathers basic features of the question to be generated

    Returns:
        [string, string, int/bool]: [arithmetic operation, difficulty, 0/1]
    """
    operation = select_random_operation()
    difficulty = select_random_difficulty()
    have_decimals = random.randint(0, 1)
    return operation, difficulty, have_decimals


def generate_question(force_difficulty=None):
    """randomly generates an arithmetic question

    Args:
        force_difficulty (str, optional): option to force the difficulty to easy. 
            Defaults to None.

    Returns:
        [str, str, str]: the question, the correct answer, and the difficulty 
            of the question
    """

    # instead of using only one range of numbers for generation,
    operation, difficulty, have_decimals = get_question_type()

    if force_difficulty:
        difficulty = force_difficulty

    # only medium and difficult questions should have decimals
    if difficulty == 'easy' and have_decimals:
        return generate_question(force_difficulty)

    # get the random numbers
    num1range, num2range = get_numrange(operation, difficulty, have_decimals)
    num1 = generate_random_number(
        num1range, have_decimals)
    num2 = generate_random_number(
        num2range, have_decimals)

    # get the number string
    if operation == '+':
        correct_answer = num1 + num2
    elif operation == '-':
        correct_answer = num1 - num2
    elif operation == '*':
        correct_answer = num1 * num2
    else:
        correct_answer = num1
        num1 = num1 * num2

    question = f'{num1} {operation} {num2}'
    correct_answer = str(correct_answer)
    return question, correct_answer, difficulty


def ask_game_settings():
    is_easy_only = input('Easy Only? ')
    if is_easy_only:
        is_easy_only = 'easy'
    minutes = int(input('How Many Minutes Do You Wish to Play For? '))
    return is_easy_only, minutes


def practice():
    """

    Args:
        minutes (int, optional): [number of minutes for practice]. Defaults to 2.
        is_easy_only ([type], optional): [force questions' difficulty to be easy]. Defaults to None.

    Returns:
        int: total score
    """
    is_easy_only, minutes = ask_game_settings()
    score = 0
    total_rights, total_wrongs = 0, 0
    start_time = time.time()
    total_seconds = minutes * 60
    while True:
        question, correct_answer, difficulty = generate_question(is_easy_only)
        print(f'Question: {question}')
        input_answer = input('Answer: ')

        if time.time() - start_time > total_seconds:
            print(f'{minutes} Minutes Passed, Total Score: {score}')
            break

        bool_right = check_answer(correct_answer, input_answer)
        if not bool_right:
            print(
                f'Inputted Answer was Wrong, Correct Answer is: {correct_answer}')
        score = update_score(difficulty, bool_right, score)


if __name__ == '__main__':
    practice()
