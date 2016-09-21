from calendar import HTMLCalendar
from datetime import date, timedelta
from core.models import Booking, Resource

from django.utils.html import conditional_escape as esc


class GuestCalendar(HTMLCalendar):
    def __init__(self, bookings, year, month, location):
        # self.formatmonth(year, month)
        self.year, self.month = year, month
        super(GuestCalendar, self).__init__()
        self.bookings = self.group_by_day(bookings)
        self.location = location

    def formatday(self, day, weekday):
        if day != 0:
            tomorrow = date(self.year, self.month, day) + timedelta(days=1)
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
                today = True
            else:
                today = False
            if day in self.bookings:
                body = ['<ul>']
                num_today = len(self.bookings[day])
                this_date = date(self.year, self.month, day)
                any_availability = self.location.rooms_free(this_date, tomorrow)
                if not any_availability:
                    cssclass += ' full-today'
                for booking in self.bookings[day]:
                    body.append('<li id="res%d-cal-item">' % booking.id)
                    if booking.is_approved():
                        body.append('<a href="#booking%d" class="greyed-out">' % booking.id)
                    else:
                        body.append('<a href="#booking%d">' % booking.id)
                    body.append(esc("%s (%s)" % (booking.user.first_name.title(), booking.resource.name)))
                    body.append('</a>')
                    if booking.arrive.day == day:
                        body.append('<em> (Arrive)</em>')
                    if booking.depart == tomorrow:
                        body.append('<em> (Last night)</em>')
                    body.append('</li>')
                    body.append('</span>')
                body.append('</ul>')
                body.append("<span class='cal-day-total'>total %d</span>" % (num_today))
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def group_by_day(self, bookings):
        ''' create a dictionary of day: items key-value pairs, where items is
        a list of all bookings that intersect this day. '''

        next_month = (self.month+1) % 12
        if next_month == 0:
            next_month = 12
        if next_month < self.month:
            next_months_year = self.year + 1
        else:
            next_months_year = self.year
        days = (date(next_months_year, next_month, 1) - date(self.year, self.month, 1)).days

        guests_by_day = {}
        for day in range(1, days+1):
            today_bookings = []
            the_day = date(self.year, self.month, day)
            for r in bookings:
                # only check that r.depart is strictly greater than the_day,
                # since people don't need a bed on the day they leave.
                if r.arrive <= the_day and r.depart > the_day:
                    today_bookings.append(r)
            if len(today_bookings) > 0:
                guests_by_day[day] = today_bookings
        return guests_by_day

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)
