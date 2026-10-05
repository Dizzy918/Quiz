from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class AnswerOptionInlineFormSet(forms.BaseInlineFormSet):
    """Applies the four-options-one-correct rule while editing in the admin.

    The model cannot check it on its own here, because the inline rows are
    saved after the question itself.
    """

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        kept = [
            form
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE")
        ]

        if len(kept) != ChoiceQuestion.REQUIRED_OPTION_COUNT:
            raise ValidationError(
                "A choice question must have exactly "
                f"{ChoiceQuestion.REQUIRED_OPTION_COUNT} answer options, "
                f"got {len(kept)}."
            )

        correct = sum(1 for form in kept if form.cleaned_data.get("is_correct"))
        if correct != 1:
            raise ValidationError(
                "A choice question must have exactly one correct answer option, "
                f"got {correct}."
            )


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    formset = AnswerOptionInlineFormSet
    extra = 0
    min_num = ChoiceQuestion.REQUIRED_OPTION_COUNT
    max_num = ChoiceQuestion.REQUIRED_OPTION_COUNT


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category")
    list_filter = ("category",)
    search_fields = ("text",)
    inlines = [AnswerOptionInline]


@admin.register(NumericQuestion)
class NumericQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "correct_answer")
    list_filter = ("category",)
    search_fields = ("text",)
