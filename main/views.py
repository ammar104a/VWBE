# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    Course, CourseLevel, Enrollment, Video, UserVideoProgress,
    Quiz, UserQuizAttempt, LevelExam, UserExamAttempt
)
from .serializers import (
    CourseSerializer, CourseLevelProgressSerializer, VideoSerializer,
    EnrollmentSerializer, QuizSerializer, LevelExamSerializer
)

from rest_framework.permissions import IsAuthenticated

# ----- Course APIs -----

# GET /api/courses/
class CourseListAPIView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


# POST /api/courses/<course_id>/enroll/
class EnrollCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            return Response({"detail": "Already enrolled."}, status=status.HTTP_400_BAD_REQUEST)
        enrollment = Enrollment.objects.create(user=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# GET /api/courses/<course_id>/levels/
class CourseLevelsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        # Ensure the user is enrolled before accessing levels.
        if not Enrollment.objects.filter(user=request.user, course=course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        levels = course.levels.all().order_by('order')
        serializer = CourseLevelProgressSerializer(levels, many=True, context={'request': request})
        return Response(serializer.data)


# GET /api/levels/<level_id>/videos/
class LevelVideosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, level_id):
        level = get_object_or_404(CourseLevel, id=level_id)
        # Check if the user is enrolled in the course of this level.
        if not Enrollment.objects.filter(user=request.user, course=level.course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        videos = level.videos.all().order_by('order')
        # Determine locked/unlocked status based on sequential completion.
        data = []
        previous_completed = True  # For the first video, we assume it’s unlocked.
        first_video_order = videos.first().order if videos.exists() else None
        for video in videos:
            # Check if the video has been completed.
            progress = UserVideoProgress.objects.filter(user=request.user, video=video, is_completed=True).exists()
            # If it is not the first video, lock it if the previous video was not completed.
            is_locked = False
            if video.order != first_video_order and not previous_completed:
                is_locked = True
            # Update the flag for sequential unlocking.
            if not progress:
                previous_completed = False
            video_data = VideoSerializer(video).data
            video_data['is_locked'] = is_locked
            data.append(video_data)
        return Response(data)


# GET /api/videos/<video_id>/
class VideoDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        if not Enrollment.objects.filter(user=request.user, course=video.level.course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        serializer = VideoSerializer(video)
        return Response(serializer.data)


# POST /api/videos/<video_id>/complete/
class CompleteVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        if not Enrollment.objects.filter(user=request.user, course=video.level.course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        progress, created = UserVideoProgress.objects.get_or_create(user=request.user, video=video)
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return Response({"detail": "Video marked as completed."})


# ----- Quiz APIs -----

# GET /api/quizzes/<quiz_id>/
class QuizDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        # Determine the related course from quiz.video or quiz.level.
        course = quiz.video.level.course if quiz.video else (quiz.level.course if quiz.level else None)
        if course and not Enrollment.objects.filter(user=request.user, course=course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)


# POST /api/quizzes/<quiz_id>/submit/
class SubmitQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        course = quiz.video.level.course if quiz.video else (quiz.level.course if quiz.level else None)
        if course and not Enrollment.objects.filter(user=request.user, course=course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        answers = request.data.get('answers', [])
        total_questions = quiz.questions.count()
        correct_count = 0
        # Expecting data like: {"answers": [{"question_id": X, "answer_id": Y}, ...]}
        for ans in answers:
            question_id = ans.get('question_id')
            answer_id = ans.get('answer_id')
            try:
                question = quiz.questions.get(id=question_id)
                answer = question.answers.get(id=answer_id)
                if answer.is_correct:
                    correct_count += 1
            except Exception as e:
                continue
        score = int((correct_count / total_questions) * 100) if total_questions else 0
        passed = score >= quiz.passing_score
        UserQuizAttempt.objects.create(user=request.user, quiz=quiz, score=score, passed=passed)
        return Response({"score": score, "passed": passed})


# ----- Exam APIs -----

# GET /api/levels/<level_id>/exam/
class LevelExamDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, level_id):
        level = get_object_or_404(CourseLevel, id=level_id)
        if not Enrollment.objects.filter(user=request.user, course=level.course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        exam = get_object_or_404(LevelExam, level=level)
        serializer = LevelExamSerializer(exam)
        return Response(serializer.data)


# POST /api/levels/<level_id>/exam/submit/
class SubmitExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, level_id):
        level = get_object_or_404(CourseLevel, id=level_id)
        if not Enrollment.objects.filter(user=request.user, course=level.course).exists():
            return Response({"detail": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        exam = get_object_or_404(LevelExam, level=level)
        answers = request.data.get('answers', [])
        total_questions = exam.questions.count()
        correct_count = 0
        # Expecting data like: {"answers": [{"question_id": X, "answer_id": Y}, ...]}
        for ans in answers:
            question_id = ans.get('question_id')
            answer_id = ans.get('answer_id')
            try:
                question = exam.questions.get(id=question_id)
                answer = question.answers.get(id=answer_id)
                if answer.is_correct:
                    correct_count += 1
            except Exception as e:
                continue
        score = int((correct_count / total_questions) * 100) if total_questions else 0
        passed = score >= exam.passing_score
        UserExamAttempt.objects.create(user=request.user, exam=exam, score=score, passed=passed)
        # Unlock the next level if the exam is passed.
        if passed:
            next_level = CourseLevel.objects.filter(course=level.course, order__gt=level.order).order_by('order').first()
            if next_level:
                message = f"Exam passed. Next level unlocked: {next_level.name}."
            else:
                message = "Exam passed. You have completed the course."
        else:
            message = "Exam failed."
        return Response({"score": score, "passed": passed, "message": message})
