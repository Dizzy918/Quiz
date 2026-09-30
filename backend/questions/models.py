from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BaseQuestion(models.Model):
    """Fields shared by every kind of question."""

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    text = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.text


class ChoiceQuestion(BaseQuestion):
    """A question with exactly four options, exactly one of them correct."""

    REQUIRED_OPTION_COUNT = 4

    def clean(self):
        super().clean()
        if self.pk is None:
            # Options are attached after the question is saved.
            return

        options = list(self.options.all())
        errors = {}

        if len(options) != self.REQUIRED_OPTION_COUNT:
            errors["options"] = [
                f"A choice question must have exactly "
                f"{self.REQUIRED_OPTION_COUNT} answer options, got {len(options)}."
            ]

        correct_count = sum(1 for option in options if option.is_correct)
        if correct_count != 1:
            errors.setdefault("options", []).append(
                f"A choice question must have exactly one correct answer option, "
                f"got {correct_count}."
            )

        if errors:
            raise ValidationError(errors)


class NumericQuestion(BaseQuestion):
    correct_answer = models.IntegerField()


class AnswerOption(models.Model):
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
