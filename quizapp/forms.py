from django import forms
from django.forms import ModelForm
from .models import Quiz, MultipleChoiceQuestion, ShortEssayQuestion
from django import forms
from django.forms import ModelForm
from .models import Quiz, MultipleChoiceQuestion, ShortEssayQuestion, MultipleChoiceAnswer, ShortEssayAnswer, QuizSubmission

# Form to create or edit a Quiz
class QuizForm(ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']

# Form for Multiple Choice Question
class MultipleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question_text', 'choice_1', 'choice_2', 'choice_3', 'correct_choice', 'url', 'image']

# Form for Short Essay Question
class ShortEssayQuestionForm(forms.ModelForm):
    class Meta:
        model = ShortEssayQuestion
        fields = ['question_text', 'url', 'image']


# Form for students to view and take quizzes
class ViewQuizzesForm(forms.Form):
    quiz = forms.ModelChoiceField(queryset=Quiz.objects.all(), label="اختر اختبارًا")

# Form for taking a quiz (both Multiple Choice and Short Essay Questions)
class TakeQuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        mcq_questions = kwargs.pop('mcq_questions')
        essay_questions = kwargs.pop('essay_questions')
        super(TakeQuizForm, self).__init__(*args, **kwargs)

        # Add multiple choice questions to the form
        for question in mcq_questions:
            field_name = f'mcq_{question.id}'
            choices = [
                (1, question.choice_1),
                (2, question.choice_2),
                (3, question.choice_3)
            ]
            self.fields[field_name] = forms.ChoiceField(
                label=question.question_text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )

        # Add short essay questions to the form
        for question in essay_questions:
            field_name = f'essay_{question.id}'
            self.fields[field_name] = forms.CharField(
                label=question.question_text,
                widget=forms.Textarea,
                required=True
            )
# Form for marking student submissions
class MarkQuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        essay_answers = kwargs.pop('essay_answers', [])
        super(MarkQuizForm, self).__init__(*args, **kwargs)

        # Create a form field for each essay answer
        for answer in essay_answers:
            field_name = f"essay_score_{answer.id}"
            self.fields[field_name] = forms.FloatField(
                label=f"الدرجة للسؤال: {answer.question.question_text}",
                min_value=0.0,
                max_value=2.0,
                required=True
            )