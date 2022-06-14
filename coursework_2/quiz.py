from flask_login import current_user

# Variables
current_question = {}
score = 0
question_count = 0
available_questions = []
used_hint = False
correct = False

# Constants



def start_quiz():
    return


def get_next_question():
    return


def update_score(score, correct, used_hint):
    if correct:
        score = score + 2
    if used_hint:
        score = score - 1
    return score