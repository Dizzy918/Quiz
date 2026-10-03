"""Small helpers so each test can build its own independent data."""

from django.contrib.auth import get_user_model

from games.models import Game, GamePlayer, Round, RoundAnswer
from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion

User = get_user_model()


def create_user(username):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="example-password",
    )


def create_game(created_by=None, **kwargs):
    return Game.objects.create(
        created_by=created_by or create_user("host"), **kwargs
    )


def create_player(game, user=None, player_order=1, **kwargs):
    return GamePlayer.objects.create(
        game=game,
        user=user or create_user(f"player{player_order}"),
        player_order=player_order,
        **kwargs,
    )


def create_choice_question(category=None, correct_index=0):
    category = category or Category.objects.create(name="География")
    question = ChoiceQuestion.objects.create(
        category=category, text="Коя е столицата на Австралия?"
    )
    for index in range(ChoiceQuestion.REQUIRED_OPTION_COUNT):
        AnswerOption.objects.create(
            question=question,
            text=f"Отговор {index + 1}",
            is_correct=index == correct_index,
        )
    return question


def create_numeric_question(category=None):
    category = category or Category.objects.create(name="Наука")
    return NumericQuestion.objects.create(
        category=category, text="Колко кръга има олимпийският символ?", correct_answer=5
    )


def create_choice_round(game, number=1, question=None, **kwargs):
    return Round.objects.create(
        game=game,
        number=number,
        question_type=Round.CHOICE,
        choice_question=question or create_choice_question(),
        **kwargs,
    )


def create_numeric_round(game, number=1, question=None, **kwargs):
    return Round.objects.create(
        game=game,
        number=number,
        question_type=Round.NUMERIC,
        numeric_question=question or create_numeric_question(),
        **kwargs,
    )


def create_choice_answer(round_, player, option=None, **kwargs):
    return RoundAnswer.objects.create(
        round=round_,
        player=player,
        selected_option=option or round_.choice_question.options.first(),
        **kwargs,
    )
