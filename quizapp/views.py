from django import forms
from django.forms import ModelForm, formset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import (
    Quiz, MultipleChoiceQuestion, ShortEssayQuestion,
    MultipleChoiceAnswer, ShortEssayAnswer, QuizSubmission, Marks, UserProfile , Video
)
from .forms import (
    QuizForm, MultipleChoiceQuestionForm, ShortEssayQuestionForm,
    ViewQuizzesForm, TakeQuizForm, MarkQuizForm
)
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, MultipleChoiceQuestion, ShortEssayQuestion, QuizSubmission, MultipleChoiceAnswer, ShortEssayAnswer
from .forms import TakeQuizForm

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User is authenticated, log them in
            login(request, user)
            
            # Redirect based on user type
            if user.userprofile.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif user.userprofile.user_type == 'student':
                return redirect('student_dashboard')
        else:
            # Authentication failed
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة")
            return redirect('login')

    # If GET request, just render the login page
    return render(request, 'login.html')

# View to handle quiz creation (teacher only)
from django.forms import formset_factory

from django.shortcuts import render, redirect
from .forms import QuizForm, MultipleChoiceQuestionForm, ShortEssayQuestionForm

from django.shortcuts import render, redirect

from django.forms import formset_factory
from .forms import QuizForm, MultipleChoiceQuestionForm, ShortEssayQuestionForm  # Correct import statement

@login_required(login_url='login')
def make_quiz_view(request):
    if request.user.userprofile.user_type != 'teacher':
        return redirect('student_dashboard')  # Redirect non-teachers to student dashboard

    # Create formsets for the multiple choice and essay questions
    MultipleChoiceFormSet = formset_factory(MultipleChoiceQuestionForm, extra=3)
    EssayFormSet = formset_factory(ShortEssayQuestionForm, extra=2)

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        mcq_formset = MultipleChoiceFormSet(request.POST, request.FILES, prefix='mcq')
        essay_formset = EssayFormSet(request.POST, request.FILES, prefix='essay')

        if quiz_form.is_valid() and mcq_formset.is_valid() and essay_formset.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()

            for mcq_form in mcq_formset:
                if mcq_form.cleaned_data:  # Save only if form contains data
                    mcq_question = mcq_form.save(commit=False)
                    mcq_question.quiz = quiz
                    mcq_question.save()

            for essay_form in essay_formset:
                if essay_form.cleaned_data:  # Save only if form contains data
                    essay_question = essay_form.save(commit=False)
                    essay_question.quiz = quiz
                    essay_question.save()

            return redirect('teacher_dashboard')
    else:
        quiz_form = QuizForm()
        mcq_formset = MultipleChoiceFormSet(prefix='mcq')
        essay_formset = EssayFormSet(prefix='essay')

    return render(request, 'makequiz.html', {
        'quiz_form': quiz_form,
        'mcq_formset': mcq_formset,
        'essay_formset': essay_formset,
    })


# Teacher Dashboard View
@login_required(login_url='login')
def teacher_dashboard_view(request):
    if request.user.userprofile.user_type != 'teacher':
        return redirect('student_dashboard')  # Redirect non-teachers to student dashboard

    quizzes = Quiz.objects.filter(created_by=request.user)
    submissions = QuizSubmission.objects.filter(quiz__created_by=request.user)

    return render(request, 'teacher_dashboard.html', {
        'quizzes': quizzes,
        'submissions': submissions,
    })

# View for students to see available quizzes
@login_required(login_url='login')
def view_quizzes_view(request):
    if request.user.userprofile.user_type != 'student':
        return redirect('teacher_dashboard')  # Redirect non-students to teacher dashboard

    if request.method == 'POST':
        form = ViewQuizzesForm(request.POST)
        if form.is_valid():
            selected_quiz = form.cleaned_data['quiz']
            return redirect('take_quiz', quiz_id=selected_quiz.id)
    else:
        form = ViewQuizzesForm()

    return render(request, 'view_quizzes.html', {
        'form': form,
    })

# Student Take Quiz View

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, MultipleChoiceQuestion, ShortEssayQuestion, QuizSubmission, MultipleChoiceAnswer, ShortEssayAnswer


@login_required
def take_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    # Ensure that only students can take the quiz
    if request.user.userprofile.user_type != 'student':
        return redirect('teacher_dashboard')

    mcq_questions = MultipleChoiceQuestion.objects.filter(quiz=quiz)
    essay_questions = ShortEssayQuestion.objects.filter(quiz=quiz)

    if request.method == 'POST':
        # Create a new submission instance
        submission = QuizSubmission.objects.create(student=request.user, quiz=quiz)

        # Save Multiple Choice Answers
        for question in mcq_questions:
            selected_choice = request.POST.get(f'mcq_{question.id}')
            if selected_choice is not None:
                correct = question.correct_choice == int(selected_choice)
                score = 2.0 if correct else 0.0
                MultipleChoiceAnswer.objects.create(
                    submission=submission,
                    question=question,
                    selected_choice=selected_choice,
                    score=score
                )

        # Save Short Essay Answers
        for question in essay_questions:
            answer_text = request.POST.get(f'essay_{question.id}')
            if answer_text is not None:
                ShortEssayAnswer.objects.create(
                    submission=submission,
                    question=question,
                    answer_text=answer_text,
                    score=0.0  # Initial score is zero; to be graded by teacher later
                )

        return redirect('student_dashboard')

    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'mcq_questions': mcq_questions,
        'essay_questions': essay_questions,
    })

# Student Dashboard View
@login_required(login_url='login')
def student_dashboard_view(request):
    if request.user.userprofile.user_type != 'student':
        return redirect('teacher_dashboard')  # Redirect non-students to teacher dashboard

    available_quizzes = Quiz.objects.all()
    completed_submissions = QuizSubmission.objects.filter(student=request.user).select_related('quiz', 'marks')
    completed_quiz_ids = [submission.quiz.id for submission in completed_submissions]

    return render(request, 'student_dashboard.html', {
        'available_quizzes': available_quizzes,
        'completed_quiz_ids': completed_quiz_ids,
        'completed_submissions': completed_submissions,
    })



# Teacher's Mark Quiz View
@login_required(login_url='login')
def mark_quiz_view(request, submission_id):
    try:
        submission = QuizSubmission.objects.get(pk=submission_id)
    except QuizSubmission.DoesNotExist:
        return redirect('teacher_dashboard')

    if request.user.userprofile.user_type != 'teacher':
        return redirect('student_dashboard')

    mcq_answers = MultipleChoiceAnswer.objects.filter(submission=submission)
    essay_answers = ShortEssayAnswer.objects.filter(submission=submission)

    if request.method == 'POST':
        total_score = 0.0

        # Manually grade Multiple Choice Answers
        for answer in mcq_answers:
            score = float(request.POST.get(f"mcq_score_{answer.id}", 0))
            answer.score = score
            answer.save()
            total_score += score

        # Manually grade Essay Answers
        for answer in essay_answers:
            score = float(request.POST.get(f"essay_score_{answer.id}", 0))
            answer.score = score
            answer.save()
            total_score += score

        marks, created = Marks.objects.get_or_create(submission=submission)
        marks.total_marks = total_score
        marks.grader = request.user
        marks.save()

        return redirect('teacher_dashboard')

    return render(request, 'mark_quiz.html', {
        'submission': submission,
        'mcq_answers': mcq_answers,
        'essay_answers': essay_answers,
    })

# View Submissions (for Teacher)
@login_required(login_url='login')
def list_submissions_view(request):
    if request.user.userprofile.user_type != 'teacher':
        return redirect('student_dashboard')  # Redirect non-teachers to student dashboard
    
    submissions = QuizSubmission.objects.all()

    return render(request, 'list_submissions.html', {
        'submissions': submissions,
    })

# View Students Progress (for Teacher)
@login_required(login_url='login')
def view_students_progress(request):
    if request.user.userprofile.user_type != 'teacher':
        return redirect('student_dashboard')

    submissions = QuizSubmission.objects.all().select_related('student', 'quiz', 'marks')

    return render(request, 'viewstudents.html', {
        'submissions': submissions,
    })







from django.shortcuts import render, get_object_or_404
from .models import Lesson

# View function for the lessons grid page
def lessons_list(request):
    lessons = Lesson.objects.all()
    context = {
        'lessons': lessons,
    }
    return render(request, 'lessons_list.html', context)

# View function for the lesson detail page
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    context = {
        'lesson': lesson,
    }
    return render(request, 'lesson_detail.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Video

def videos_list(request):
    videos = Video.objects.all()
    return render(request, 'videos_list.html', {'videos': videos})

def video_detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return render(request, 'video_detail.html', {'video': video})