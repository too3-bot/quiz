from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.db import models
from tinymce.models import HTMLField
from django.urls import reverse

# UserProfile to extend User model to differentiate between teachers and students
class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('teacher', 'معلم'),
        ('student', 'طالب'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name='نوع المستخدم')

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

    class Meta:
        verbose_name = "الملف الشخصي للمستخدم"
        verbose_name_plural = "ملفات المستخدمين الشخصية"

# Model for Quiz
class Quiz(models.Model):
    title = models.CharField(max_length=255, verbose_name='عنوان الاختبار')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='أنشأه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "اختبار"
        verbose_name_plural = "الاختبارات"


# Multiple Choice Question Model
class MultipleChoiceQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='mc_questions', verbose_name='الاختبار')
    question_text = models.TextField(verbose_name='نص السؤال')
    choice_1 = models.CharField(max_length=255, verbose_name='الخيار 1')
    choice_2 = models.CharField(max_length=255, verbose_name='الخيار 2')
    choice_3 = models.CharField(max_length=255, verbose_name='الخيار 3')
    correct_choice = models.PositiveSmallIntegerField(choices=((1, 'الخيار 1'), (2, 'الخيار 2'), (3, 'الخيار 3')), verbose_name='الخيار الصحيح')
    url = models.URLField(max_length=200, blank=True, null=True, verbose_name='رابط اختياري')
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True, verbose_name='صورة اختيارية')

    def __str__(self):
        return f"{self.quiz.title} - {self.question_text}"

    class Meta:
        verbose_name = "سؤال اختيار متعدد"
        verbose_name_plural = "أسئلة الاختيار المتعدد"

# Short Essay Question Model
class ShortEssayQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='essay_questions', verbose_name='الاختبار')
    question_text = models.TextField(verbose_name='نص السؤال')
    url = models.URLField(max_length=200, blank=True, null=True, verbose_name='رابط اختياري')
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True, verbose_name='صورة اختيارية')

    def __str__(self):
        return f"{self.quiz.title} - {self.question_text}"

    class Meta:
        verbose_name = "سؤال مقالي"
        verbose_name_plural = "أسئلة مقالية"

# Model for Student's Quiz Submission
class QuizSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='الطالب')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name='الاختبار')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التقديم')
    total_score = models.FloatField(default=0.0, verbose_name='الدرجة الكلية')

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

    class Meta:
        verbose_name = "تقديم اختبار"
        verbose_name_plural = "تقديمات الاختبارات"

# Model for Student's Answer for Multiple Choice Question
class MultipleChoiceAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='mc_answers', verbose_name='تقديم الاختبار')
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE, verbose_name='السؤال')
    selected_choice = models.PositiveSmallIntegerField(choices=((1, 'الخيار 1'), (2, 'الخيار 2'), (3, 'الخيار 3')), verbose_name='الخيار المحدد')
    score = models.FloatField(default=0.0, verbose_name='الدرجة')

    def __str__(self):
        return f"{self.submission.student.username} - {self.question.quiz.title} - {self.question.question_text}"

    class Meta:
        verbose_name = "إجابة اختيار متعدد"
        verbose_name_plural = "إجابات الاختيار المتعدد"

# Model for Student's Answer for Short Essay Question
class ShortEssayAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='essay_answers', verbose_name='تقديم الاختبار')
    question = models.ForeignKey(ShortEssayQuestion, on_delete=models.CASCADE, verbose_name='السؤال')
    answer_text = models.TextField(verbose_name='نص الإجابة')
    score = models.FloatField(default=0.0, verbose_name='الدرجة')

    def __str__(self):
        return f"{self.submission.student.username} - {self.question.quiz.title} - {self.question.question_text}"

    class Meta:
        verbose_name = "إجابة سؤال مقالي"
        verbose_name_plural = "إجابات الأسئلة المقالية"

# Model for Marks
class Marks(models.Model):
    submission = models.OneToOneField('QuizSubmission', on_delete=models.CASCADE, related_name='marks', verbose_name='تقديم الاختبار')
    total_marks = models.FloatField(default=0.0, verbose_name='الدرجات الكلية')
    grader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_by', verbose_name='المصحح')
    graded_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التصحيح')

    def __str__(self):
        return f"درجات {self.submission.student.username} - {self.submission.quiz.title}: {self.total_marks}"

    class Meta:
        verbose_name = "درجة"
        verbose_name_plural = "الدرجات"



class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان الدرس')
    background_image = models.ImageField(upload_to='lessons/backgrounds/', blank=True, null=True, verbose_name='صورة الخلفية')
    content = HTMLField(verbose_name='المحتوى', null=True)
    quiz_url = models.URLField(max_length=200, blank=True, null=True, verbose_name='رابط الاختبار')  # حقل URL لرابط الاختبار

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "الدروس"


class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان الفيديو')
    youtube_id = models.CharField(max_length=10000, verbose_name='معرف فيديو يوتيوب')
    description = models.TextField(blank=True, null=True, verbose_name='وصف الفيديو')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('video_detail', kwargs={'video_id': self.pk})

    class Meta:
        verbose_name = "فيديو"
        verbose_name_plural = "فيديوهات"
