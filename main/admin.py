# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Course, CourseLevel, Enrollment, Video, UserVideoProgress,
    Quiz, QuizQuestion, QuizAnswer, UserQuizAttempt,
    LevelExam, ExamQuestion, ExamAnswer, UserExamAttempt
)


# -----------------------------------------------------------
# Custom UserAdmin for our custom User model.
# -----------------------------------------------------------
class UserAdmin(BaseUserAdmin):
    # Make 'created_at' read-only since it's non-editable (auto_now_add)
    readonly_fields = ('created_at',)

    # Remove 'created_at' from the fieldsets so it won't be treated as an editable field.
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'profile_photo', 'address', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')  # 'created_at' is intentionally excluded here.
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


# Register the custom User model with our custom admin.
admin.site.register(User, UserAdmin)


# -----------------------------------------------------------
# Course Admin
# -----------------------------------------------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


# -----------------------------------------------------------
# CourseLevel Admin
# -----------------------------------------------------------
@admin.register(CourseLevel)
class CourseLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'name', 'order')
    search_fields = ('name', 'course__title')
    list_filter = ('course', 'name')
    ordering = ('course', 'order')


# -----------------------------------------------------------
# Enrollment Admin
# -----------------------------------------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('course', 'user')
    ordering = ('-enrolled_at',)


# -----------------------------------------------------------
# Video Admin
# -----------------------------------------------------------
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'order')
    search_fields = ('title', 'level__name')
    list_filter = ('level',)
    ordering = ('level', 'order')


# -----------------------------------------------------------
# UserVideoProgress Admin
# -----------------------------------------------------------
@admin.register(UserVideoProgress)
class UserVideoProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'is_completed', 'completed_at')
    search_fields = ('user__username', 'video__title')
    list_filter = ('is_completed', 'user')
    ordering = ('user', 'video')


# -----------------------------------------------------------
# Inlines for Quiz-related models.
# -----------------------------------------------------------
class QuizAnswerInline(admin.TabularInline):
    """
    Inline admin for QuizAnswer.
    Allows adding/editing answers directly on the QuizQuestion page.
    """
    model = QuizAnswer
    extra = 1


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'order', 'question_text')
    search_fields = ('question_text',)
    list_filter = ('quiz',)
    ordering = ('quiz', 'order')
    inlines = [QuizAnswerInline]


class QuizQuestionInline(admin.TabularInline):
    """
    Inline admin for QuizQuestion.
    This is used in the Quiz admin page.
    """
    model = QuizQuestion
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'level', 'passing_score', 'order')
    search_fields = ('video__title', 'level__name')
    list_filter = ('video', 'level')
    ordering = ('order',)
    inlines = [QuizQuestionInline]


# -----------------------------------------------------------
# UserQuizAttempt Admin
# -----------------------------------------------------------
@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'score', 'passed', 'attempted_at')
    search_fields = ('user__username',)
    list_filter = ('passed', 'quiz', 'user')
    ordering = ('-attempted_at',)


# -----------------------------------------------------------
# Inlines for Exam-related models.
# -----------------------------------------------------------
class ExamAnswerInline(admin.TabularInline):
    """
    Inline admin for ExamAnswer.
    Allows managing answers for an exam question.
    """
    model = ExamAnswer
    extra = 1


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'order', 'question_text')
    search_fields = ('question_text',)
    list_filter = ('exam',)
    ordering = ('exam', 'order')
    inlines = [ExamAnswerInline]


class ExamQuestionInline(admin.TabularInline):
    """
    Inline admin for ExamQuestion.
    Used in the LevelExam admin to manage exam questions directly.
    """
    model = ExamQuestion
    extra = 1


@admin.register(LevelExam)
class LevelExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'level', 'passing_score')
    search_fields = ('level__name',)
    list_filter = ('level',)
    ordering = ('level',)
    inlines = [ExamQuestionInline]


# -----------------------------------------------------------
# UserExamAttempt Admin
# -----------------------------------------------------------
@admin.register(UserExamAttempt)
class UserExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'exam', 'score', 'passed', 'attempted_at')
    search_fields = ('user__username', 'exam__level__name')
    list_filter = ('passed', 'exam', 'user')
    ordering = ('-attempted_at',)


# admin.py
from django.contrib import admin
from .models import UserLevelProgress

@admin.register(UserLevelProgress)
class UserLevelProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course_level', 'progress', 'updated_at')
    search_fields = ('user__username', 'course_level__name')
