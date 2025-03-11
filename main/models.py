# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    # Fields inherited: id, username, first_name, last_name, email, password, etc.
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseLevel(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="levels")
    name = models.CharField(max_length=50)  # e.g., "Beginner", "Intermediate", "Professional"
    order = models.IntegerField()

    def __str__(self):
        return f"{self.course.title} - {self.name}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class Video(models.Model):
    title = models.CharField(max_length=255)
    level = models.ForeignKey(CourseLevel, on_delete=models.CASCADE, related_name="videos")
    order = models.IntegerField()
    video_file = models.FileField(upload_to='videos/')

    def __str__(self):
        return f"{self.title} (Level: {self.level.name})"


class UserVideoProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="video_progress")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="progresses")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.video.title} - Completed: {self.is_completed}"


class Quiz(models.Model):
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, related_name="quizzes")
    level = models.ForeignKey(CourseLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name="quizzes")
    passing_score = models.IntegerField()
    order = models.IntegerField()

    def __str__(self):
        return f"Quiz {self.id} for {self.video or self.level}"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="answers")
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Answer: {self.answer_text[:50]} (Correct: {self.is_correct})"


class UserQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    score = models.IntegerField()
    passed = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Quiz {self.quiz.id} Attempt"


class LevelExam(models.Model):
    level = models.OneToOneField(CourseLevel, on_delete=models.CASCADE, related_name="exam")
    passing_score = models.IntegerField()

    def __str__(self):
        return f"Exam for {self.level}"


class ExamQuestion(models.Model):
    exam = models.ForeignKey(LevelExam, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return f"Exam Q{self.order}: {self.question_text[:50]}"


class ExamAnswer(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name="answers")
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Exam Answer: {self.answer_text[:50]} (Correct: {self.is_correct})"


class UserExamAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exam_attempts")
    exam = models.ForeignKey(LevelExam, on_delete=models.CASCADE, related_name="attempts")
    score = models.IntegerField()
    passed = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Exam for {self.exam.level.name} Attempt"


# models.py

class UserLevelProgress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="level_progress"
    )
    course_level = models.ForeignKey(
        CourseLevel, on_delete=models.CASCADE, related_name="user_progress"
    )
    progress = models.PositiveIntegerField(
        default=0,
        help_text="Progress percentage (0-100) manually set by admin"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course_level')

    def __str__(self):
        return f"{self.user.username} - {self.course_level.name}: {self.progress}%"
