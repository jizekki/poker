import queue

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.http import HttpResponse
from django.views.generic import TemplateView, View, FormView
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import PokerSession, UserRole, User, Estimation, PossibleEstimation, UserStatus
from .forms import SessionJoinForm


class SessionHomeView(TemplateView):
    template_name = "poker/home.html"

class SessionCreateView(View):
    def get(self, request, *args, **kwargs):
        # create a new PokerSession
        identifier = PokerSession.generate_public_identifier()
        poker_session = PokerSession.objects.create(public_identifier=identifier)

        # check if user already exists or else create one
        user_slug = request.session.get("user_slug", None)
        if user_slug is not None:
            try:
                user = User.objects.get(slug=user_slug)
                user.session_id = poker_session
            except ObjectDoesNotExist:
                user = User.objects.create(role=UserRole.ORGANIZER, username="organizer", session_id=poker_session)
        else:
            user = User.objects.create(role=UserRole.ORGANIZER, username="organizer", session_id=poker_session)

        request.session["user_slug"] = user.slug

        return redirect(to="poker:session_overview", public_identifier=poker_session.public_identifier)

class SessionOverViewView(View):
    def get(self, request, public_identifier, *args, **kwargs):
        # check if user already exists or else create one
        user_slug = request.session.get("user_slug", None)
        if user_slug is not None:
            try:
                user = User.objects.get(slug=user_slug)
                if user.session_id.public_identifier == public_identifier:
                    context = {
                        "object": user.session_id,
                    }
                    return render(request, "poker/started_session.html", context=context)
            except ObjectDoesNotExist:
                pass
        return HttpResponse("Error")


class SessionParticipantsListView(View):
    def get(self, request, public_identifier, *args, **kwargs):
        # check if user already exists or else create one
        user_slug = request.session.get("user_slug", None)
        if user_slug is not None:
            try:
                user = User.objects.get(slug=user_slug)
                if user.session_id.public_identifier == public_identifier:
                    context = {
                        "session": user.session_id,
                        "users": User.objects.filter(session_id=user.session_id, role=UserRole.PARTICIPANT),
                    }
                    return render(request, "poker/participants_list.html", context=context)
            except ObjectDoesNotExist:
                pass
        return HttpResponse("Error")

class SessionJoinView(FormView):
    form_class = SessionJoinForm
    template_name = "poker/join.html"

    def form_valid(self, form):
        print("form valid")
        public_identifier = form.cleaned_data["public_identifier"]
        username = form.cleaned_data["username"]
        try:
            poker_session = PokerSession.objects.get(public_identifier=public_identifier)

            # TODO check first to make sure user is not already created
            # create a new user
            user = User.objects.create(username=username, session_id=poker_session, role=UserRole.PARTICIPANT)

            self.request.session["user_slug"] = user.slug

            async_to_sync(get_channel_layer().group_send)(
                # TODO change chat room name
                "chat_RoomName",
                {
                    "type": "participant.update",
                    "content": None,
                }
            )

            return redirect(to=reverse("poker:possible_estimations"))

        except (ObjectDoesNotExist, FieldError):
            print("No such poker session")
            return render(self.request, "poker/join.html")

    def form_invalid(self, form):
        print("form invalid")
        context = self.get_context_data(form=form)
        return render(self.request, "poker/join.html", context=context)


class SessionPossibleEstimationsView(TemplateView):
    def get_template_names(self):
        return ["poker/estimations.html"]


class SessionPossibleEstimationsPartialView(TemplateView):
    def get_template_names(self):
        return ["poker/partial_estimations.html"]

    def get_context_data(self, **kwargs):
        context = super(SessionPossibleEstimationsPartialView, self).get_context_data(**kwargs)
        context["possible_estimations"] = ["0", "1/2", "1", "2", "3", "5", "8", "13", "21", "34", "55", "89", "144"]
        slug = self.request.session.get("user_slug", None)
        if slug is not None:
            try:
                user = User.objects.get(slug=slug)
                context["object"] = user.session_id
            except ObjectDoesNotExist:
                # TODO do something
                pass

        return context


class SessionStartEstimation(View):
    def get(self, request, public_identifier, *args, **kwargs):
        slug = self.request.session.get("user_slug", None)
        if slug is not None:
            try:
                user = User.objects.get(slug=slug)
                if user.session_id.public_identifier != public_identifier:
                    # TODO handle error
                    pass
                user.session_id.start_estimation()
                async_to_sync(get_channel_layer().group_send)(
                    # TODO change chat room name
                    "chat_RoomName",
                    {
                        "type": "organizer.isEstimationRunningChanged",
                        "content": None
                    }
                )
                context = {
                    "object": user.session_id
                }
                return render(self.request, "poker/start_and_stop_estimation.html", context=context)
            except ObjectDoesNotExist:
                # TODO do something
                pass

class SessionStopEstimation(View):
    def get(self, request, public_identifier, *args, **kwargs):
        slug = self.request.session.get("user_slug", None)
        if slug is not None:
            try:
                user = User.objects.get(slug=slug)
                if user.session_id.public_identifier != public_identifier:
                    # TODO handle error
                    pass
                user.session_id.stop_estimation()
                async_to_sync(get_channel_layer().group_send)(
                    # TODO change chat room name
                    "chat_RoomName",
                    {
                        "type": "organizer.isEstimationRunningChanged",
                        "content": None
                    }
                )
                context = {
                    "object": user.session_id
                }
                return render(request, "poker/start_and_stop_estimation.html", context=context)
            except ObjectDoesNotExist:
                # TODO do something
                pass

class SessionSubmitEstimation(View):
    def post(self, request, public_identifier, value, *args, **kwargs):
        slug = self.request.session.get("user_slug", None)
        if slug is not None:
            try:
                user = User.objects.get(slug=slug)
                if user.session_id.public_identifier != public_identifier:
                    # TODO handle error
                    pass

                possible_estimation = PossibleEstimation.objects.get(value=value)

                Estimation.objects.create(user_id=user, possible_estimation_id=possible_estimation, index=user.session_id.current_index)
                user.status = UserStatus.ESTIMATION_SUBMITTED
                user.save()

                async_to_sync(get_channel_layer().group_send)(
                    # TODO change chat room name
                    "chat_RoomName",
                    {
                        "type": "participant.update",
                        "content": None
                    }
                )
                context = {
                    "object": user.session_id
                }
                return render(request, "poker/start_and_stop_estimation.html", context=context)
            except ObjectDoesNotExist:
                # TODO do something
                pass