# serializers.py
from rest_framework import serializers
from .models import Enrollment
from rest_framework import serializers
from .models import (
    Course, CourseLevel, Enrollment, Video, UserVideoProgress,
    Quiz, QuizQuestion, QuizAnswer, UserQuizAttempt,
    LevelExam, ExamQuestion, ExamAnswer, UserExamAttempt
)
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'created_at']


class CourseLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLevel
        fields = ['id', 'course', 'name', 'order']


# serializers.py
from .models import UserLevelProgress

class CourseLevelProgressSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = CourseLevel
        fields = ['id', 'course', 'name', 'order', 'progress_percentage']

    def get_progress_percentage(self, obj):
        user = self.context.get('request').user

        # First, check if there's a manual progress entry
        try:
            manual_progress = obj.user_progress.get(user=user)
            return manual_progress.progress
        except UserLevelProgress.DoesNotExist:
            pass

        # Fallback: compute progress based on quiz attempts.
        quizzes = obj.quizzes.all()
        total_quizzes = quizzes.count()
        if total_quizzes == 0:
            return 0
        completed = 0
        for quiz in quizzes:
            if quiz.attempts.filter(user=user, passed=True).exists():
                completed += 1
        percentage = int((completed / total_quizzes) * 100)
        return percentage


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'level', 'order', 'video_file']


class UserVideoProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVideoProgress
        fields = ['id', 'user', 'video', 'is_completed', 'completed_at']


class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ['id', 'answer_text', 'is_correct']


class QuizQuestionSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'order', 'answers']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'video', 'level', 'passing_score', 'order', 'questions']


class UserQuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizAttempt
        fields = '__all__'


class ExamAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAnswer
        fields = ['id', 'answer_text', 'is_correct']


class ExamQuestionSerializer(serializers.ModelSerializer):
    answers = ExamAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ExamQuestion
        fields = ['id', 'question_text', 'order', 'answers']


class LevelExamSerializer(serializers.ModelSerializer):
    questions = ExamQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = LevelExam
        fields = ['id', 'level', 'passing_score', 'questions']


class UserExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExamAttempt
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
