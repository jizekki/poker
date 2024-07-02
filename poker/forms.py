from django import forms
from .models import PokerSession
from django.core.exceptions import ValidationError


def validate_identifier(value):
    if PokerSession.objects.filter(public_identifier=value).count() == 0:
        raise ValidationError(f"{value} is not a valid session ID")
    
class SessionJoinForm(forms.Form):
    public_identifier = forms.CharField(
        required=True,
        min_length=3,
        max_length=8,
        widget=forms.TextInput(attrs={"placeholder": "Session ID", "class": "input input-bordered"}),
        validators=[validate_identifier],
    )

    username = forms.CharField(
        required=True,
        min_length=3,
        max_length=8,
        widget=forms.TextInput(attrs={"placeholder": "Username (trigramme)", "class": "input input-bordered"}),
    )
