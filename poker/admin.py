import pprint
from django.contrib import admin
from django.contrib.sessions.models import Session
from .models import PokerSession, User


class PokerSessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return pprint.pformat(obj.get_decoded()).replace("\n", "<br>\n")
    _session_data.allow_tags=True
    list_display = ["session_key", "_session_data", "expire_date"]
    readonly_fields = ["_session_data"]
    exclude = ["session_data"]

admin.site.register(PokerSession)
admin.site.register(User)
admin.site.register(Session, PokerSessionAdmin)