from calendar import HTMLCalendar
from datetime import date

from django.utils.html import conditional_escape as esc

class GuestCalendar(HTMLCalendar):
	def __init__(self, reservations, year, month):
		#self.formatmonth(year, month)
	 	self.year, self.month = year, month
		super(GuestCalendar, self).__init__()
		self.reservations = self.group_by_day(reservations)

	def formatday(self, day, weekday):
		if day != 0:
			cssclass = self.cssclasses[weekday]
			if date.today() == date(self.year, self.month, day):
				cssclass += ' today'
				today = True
			else:
				today = False
			if day in self.reservations:
				cssclass += ' filled'
				body = ['<ul>']
				num_today = len(self.reservations[day])
				num_private = 0
				num_shared = 0
				for reservation in self.reservations[day]:
					room_type = None 
					if reservation.room.name == "Ada Lovelace Hostel":
						num_shared += 1
						room_type = "S"
					else:
						num_private += 1
						room_type = "P"
					body.append('<li id="res%d-cal-item">' %reservation.id)
					body.append('<a href="#reservation%d">' % reservation.id)
					body.append(esc("%s (%s)" % (reservation.user.first_name.title(), room_type)))
					body.append('</a>')
					if reservation.arrive.day == day:
						body.append('<em> (Arrive)</em>') 					
					if reservation.depart.day == day:
						body.append('<em> (Depart)</em>') 					
					body.append('</li>')
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
				if r.arrive <= the_day and r.depart >= the_day:
					today_reservations.append(r)
			if len(today_reservations) > 0:
				guests_by_day[day] = today_reservations
		return guests_by_day

	def day_cell(self, cssclass, body):
		return '<td class="%s">%s</td>' % (cssclass, body)

