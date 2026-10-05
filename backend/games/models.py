from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from questions.models import AnswerOption, ChoiceQuestion, NumericQuestion


class Game(models.Model):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (WAITING, "Waiting"),
        (IN_PROGRESS, "In Progress"),
        (FINISHED, "Finished"),
        (CANCELLED, "Cancelled"),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_games",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Game {self.pk} ({self.status})"


class GamePlayer(models.Model):
    """A single user taking part in a single game."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="game_players",
    )
    player_order = models.PositiveSmallIntegerField()
    score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["player_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["game", "user"], name="unique_user_per_game"
            ),
            models.UniqueConstraint(
                fields=["game", "player_order"], name="unique_player_order_per_game"
            ),
        ]

    def __str__(self):
        return f"{self.user} in game {self.game_id}"


class Round(models.Model):
    """One round of a game, played with exactly one question.

    ``question_type`` says which of the two question columns is in use. It
    repeats what the filled column already implies, but it is what the game
    reads to know which kind of answer to expect, so the two can never be
    allowed to drift: ``round_has_exactly_one_question`` below rejects any
    row where the type and the filled column disagree, and ``clean`` reports
    the same thing with a readable message.
    """

    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    EVALUATED = "evaluated"

    ROUND_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (OPEN, "Open"),
        (CLOSED, "Closed"),
        (EVALUATED, "Evaluated"),
    ]

    CHOICE = "choice"
    NUMERIC = "numeric"

    QUESTION_TYPE_CHOICES = [
        (CHOICE, "Choice"),
        (NUMERIC, "Numeric"),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, choices=ROUND_STATUS_CHOICES, default=PENDING
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    choice_question = models.ForeignKey(
        ChoiceQuestion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rounds",
    )
    numeric_question = models.ForeignKey(
        NumericQuestion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rounds",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                fields=["game", "number"], name="unique_round_number_per_game"
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        question_type="choice",
                        choice_question__isnull=False,
                        numeric_question__isnull=True,
                    )
                    | Q(
                        question_type="numeric",
                        numeric_question__isnull=False,
                        choice_question__isnull=True,
                    )
                ),
                name="round_has_exactly_one_question",
            ),
        ]

    def __str__(self):
        return f"Round {self.number} of game {self.game_id}"

    @property
    def question(self):
        """The one question this round is played with."""
        return (
            self.choice_question
            if self.question_type == self.CHOICE
            else self.numeric_question
        )

    def clean(self):
        super().clean()
        if self.question_type == self.CHOICE and self.choice_question_id is None:
            raise ValidationError(
                {"choice_question": ["A choice round needs a choice question."]}
            )
        if self.question_type == self.NUMERIC and self.numeric_question_id is None:
            raise ValidationError(
                {"numeric_question": ["A numeric round needs a numeric question."]}
            )
        if self.question_type == self.CHOICE and self.numeric_question_id is not None:
            raise ValidationError(
                {"numeric_question": ["A choice round cannot hold a numeric question."]}
            )
        if self.question_type == self.NUMERIC and self.choice_question_id is not None:
            raise ValidationError(
                {"choice_question": ["A numeric round cannot hold a choice question."]}
            )


class RoundAnswer(models.Model):
    """One player's answer in one round."""

    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="answers")
    player = models.ForeignKey(
        GamePlayer, on_delete=models.CASCADE, related_name="answers"
    )
    selected_option = models.ForeignKey(
        AnswerOption,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="round_answers",
    )
    numeric_value = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_awarded = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["round", "player"]
        constraints = [
            models.UniqueConstraint(
                fields=["round", "player"], name="unique_answer_per_player_per_round"
            ),
            models.CheckConstraint(
                condition=(
                    Q(selected_option__isnull=False, numeric_value__isnull=True)
                    | Q(selected_option__isnull=True, numeric_value__isnull=False)
                ),
                name="round_answer_has_exactly_one_value",
            ),
        ]

    def __str__(self):
        return f"Answer of {self.player_id} in round {self.round_id}"

    def clean(self):
        super().clean()
        if self.round_id and self.player_id:
            if self.round.game_id != self.player.game_id:
                raise ValidationError(
                    {"player": ["The player does not take part in this game."]}
                )

            if (
                self.round.question_type == Round.CHOICE
                and self.selected_option_id is None
            ):
                raise ValidationError(
                    {"selected_option": ["A choice round expects a selected option."]}
                )
            if (
                self.round.question_type == Round.NUMERIC
                and self.numeric_value is None
            ):
                raise ValidationError(
                    {"numeric_value": ["A numeric round expects a numeric value."]}
                )
