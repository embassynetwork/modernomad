from calendar import HTMLCalendar
from datetime import date, timedelta
from core.models import Reservation, Room

from django.utils.html import conditional_escape as esc

class GuestCalendar(HTMLCalendar):
	def __init__(self, reservations, year, month, location):
		#self.formatmonth(year, month)
	 	self.year, self.month = year, month
		super(GuestCalendar, self).__init__()
		self.reservations = self.group_by_day(reservations)
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
			if day in self.reservations:
				body = ['<ul>']
				num_today = len(self.reservations[day])
				num_private = 0
				num_shared = 0
				this_date = date(self.year, self.month, day)
				any_availability = Room.objects.free(this_date, tomorrow, self.location)
				print this_date
				print tomorrow
				print any_availability
				if not any_availability:
					cssclass += ' full-today'
				for reservation in self.reservations[day]:
					if reservation.room.shared:
						num_shared += 1
						room_type = "S"
					else:
						num_private += 1
						room_type = "P"

					body.append('<li id="res%d-cal-item">' %reservation.id)
					if reservation.is_apprived():
						body.append('<a href="#reservation%d" class="greyed-out">' % reservation.id)
					else:
						body.append('<a href="#reservation%d">' % reservation.id)
					body.append(esc("%s (%s)" % (reservation.user.first_name.title(), room_type)))
					body.append('</a>')
					if reservation.arrive.day == day:
						body.append('<em> (Arrive)</em>') 					
					if reservation.depart == tomorrow:
						body.append('<em> (Last night)</em>')					
					body.append('</li>')
					body.append('</span>')
				body.append('</ul>')
				body.append("<span class='cal-day-total'>total %d (P: %d/S: %d)</span>" % (num_today, num_private, num_shared))
				return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
			return self.day_cell(cssclass, day)
		return self.day_cell('noday', '&nbsp;')

	def group_by_day(self, reservations):
		''' create a dictionary of day: items key-value pairs, where items is
		a list of all reservations that intersect this day. '''
		
		next_month = (self.month+1) % 12 
		if next_month == 0: next_month = 12
		if next_month < self.month:
			next_months_year = self.year + 1
		else: next_months_year = self.year
		days = (date(next_months_year, next_month, 1) - date(self.year, self.month, 1)).days 

		guests_by_day = {}
		for day in range(1,days+1):
			today_reservations = []
			the_day = date(self.year, self.month, day)
			for r in reservations:
				# only check that r.depart is strictly greater than the_day,
				# since people don't need a bed on the day they leave.
				if r.arrive <= the_day and r.depart > the_day:
					today_reservations.append(r)
			if len(today_reservations) > 0:
				guests_by_day[day] = today_reservations
		return guests_by_day

	def day_cell(self, cssclass, body):
		return '<td class="%s">%s</td>' % (cssclass, body)

