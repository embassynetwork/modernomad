from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from gather.models import Event, EventAdminGroup, EventSeries, Location

class EventAdmin(admin.ModelAdmin):
    model = Event

class EventAdminGroupAdmin(admin.ModelAdmin):
    model = EventAdminGroup

class EventSeriesAdmin(admin.ModelAdmin):
    model = EventSeries

class LocationAdmin(admin.ModelAdmin):
    model = Location

admin.site.register(Event, EventAdmin)
admin.site.register(EventAdminGroup, EventAdminGroupAdmin)
admin.site.register(EventSeries, EventSeriesAdmin)
admin.site.register(Location, LocationAdmin)
