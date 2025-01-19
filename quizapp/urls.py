from django.urls import path
from .views import video_detail,videos_list, lesson_detail, lessons_list, login_view, teacher_dashboard_view, view_students_progress, list_submissions_view, mark_quiz_view, make_quiz_view, teacher_dashboard_view, view_quizzes_view, take_quiz_view, student_dashboard_view
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', login_view, name='login'),
    path('admin/', admin.site.urls),
    path('makequiz/', make_quiz_view, name='make_quiz'),
    path('', teacher_dashboard_view, name='teacher_dashboard'),
    path('view_quizzes/', view_quizzes_view, name='view_quizzes'),
    path('take_quiz/<int:quiz_id>/', take_quiz_view, name='take_quiz'),
    path('student_dashboard/', student_dashboard_view, name='student_dashboard'),
    path('mark_quiz/<int:submission_id>/', mark_quiz_view, name='mark_quiz'),
    path('list_submissions/', list_submissions_view, name='list_submissions'),
    path('view_students/', view_students_progress, name='view_students'), 
    path('teacher_dashboard/', teacher_dashboard_view, name='teacher_dashboard'),
    path('lessons/', lessons_list, name='lessons_list'),
    path('lessons/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('videos/', videos_list, name='videos_list'),
    path('videos/<int:video_id>/', video_detail, name='video_detail'),
]

