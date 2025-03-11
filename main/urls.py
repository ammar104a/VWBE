# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    CourseListAPIView,
    EnrollCourseAPIView,
    CourseLevelsAPIView,
    LevelVideosAPIView,
    VideoDetailAPIView,
    CompleteVideoAPIView,
    QuizDetailAPIView,
    SubmitQuizAPIView,
    LevelExamDetailAPIView,
    SubmitExamAPIView,
)

urlpatterns = [
    # Course endpoints
    path('api/courses/', CourseListAPIView.as_view(), name='course-list'),
    path('api/courses/<int:course_id>/enroll/', EnrollCourseAPIView.as_view(), name='course-enroll'),
    path('api/courses/<int:course_id>/levels/', CourseLevelsAPIView.as_view(), name='course-levels'),

    # Video endpoints
    path('api/levels/<int:level_id>/videos/', LevelVideosAPIView.as_view(), name='level-videos'),
    path('api/videos/<int:video_id>/', VideoDetailAPIView.as_view(), name='video-detail'),
    path('api/videos/<int:video_id>/complete/', CompleteVideoAPIView.as_view(), name='video-complete'),

    # Quiz endpoints
    path('api/quizzes/<int:quiz_id>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('api/quizzes/<int:quiz_id>/submit/', SubmitQuizAPIView.as_view(), name='quiz-submit'),

    # Exam endpoints
    path('api/levels/<int:level_id>/exam/', LevelExamDetailAPIView.as_view(), name='exam-detail'),
    path('api/levels/<int:level_id>/exam/submit/', SubmitExamAPIView.as_view(), name='exam-submit'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
