from django.contrib import admin
from .models import (
    Quiz,
    MultipleChoiceQuestion,
    ShortEssayQuestion,
    UserProfile,
    QuizSubmission,
    MultipleChoiceAnswer,
    ShortEssayAnswer,
    Marks,
    Lesson,
)
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from .models import Video


# Change Admin Titles
admin.site.site_header = "ثروة - لوحة التحكم"
admin.site.site_title = "ثروة - إدارة الموقع"
admin.site.index_title = "مرحبًا بكم في إدارة منصة ثروة"

# Customize the User and Group models in admin panel
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('معلومات شخصية'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('الأذونات'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('تواريخ مهمة'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    verbose_name = _("مجموعة")
    verbose_name_plural = _("المجموعات")

# Register custom models with translated verbose names
admin.site.register(UserProfile)
admin.site.register(Quiz)
admin.site.register(MultipleChoiceQuestion)
admin.site.register(ShortEssayQuestion)
admin.site.register(QuizSubmission)
admin.site.register(MultipleChoiceAnswer)
admin.site.register(ShortEssayAnswer)
admin.site.register(Marks)
admin.site.register(Lesson)
admin.site.register(Video)
