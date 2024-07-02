"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", view=views.SessionHomeView.as_view(), name="home"),
    path("create", view=views.SessionCreateView.as_view(), name="create"),
    path("join", view=views.SessionJoinView.as_view(), name="join"),
    path("possible_estimations", view=views.SessionPossibleEstimationsView.as_view(), name="possible_estimations"),
    path("possible_estimations_partial", view=views.SessionPossibleEstimationsPartialView.as_view(), name="possible_estimations_partial"),
    path("participants_list<str:public_identifier>", view=views.SessionParticipantsListView.as_view(), name="participants_list"),
    path("session/<str:public_identifier>", view=views.SessionOverViewView.as_view(), name="session_overview"),
    path("session/<str:public_identifier>/start_estimation", view=views.SessionStartEstimation.as_view(), name="start_estimation"),
    path("session/<str:public_identifier>/stop_estimation", view=views.SessionStopEstimation.as_view(), name="stop_estimation"),
    path("session/<str:public_identifier>/submit_estimation/<str:value>", view=views.SessionStopEstimation.as_view(), name="submit_estimation"),
]
