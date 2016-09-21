# Administering Bookings

under /manage/bookings/ there are custom management pages for house admins. 

- management pages
- emailing users
- comps
- canceling
- when a user is emailed about their booking from the management page, the 'last cont

to get to the built-in admin interface, visit /admin and log in with an administrative user. 

Groups: Residents and House Admins

- add a user as a resident or a house admin in the django admin interface. 
- if you want them to be able to log into the django admin pages, enable 'staff' status. this is useful if you want them to be able to create email templates, rooms, or do advanced booking administration. 
- a user marked as a resident will show up on the 'community' page. 
- a user marked as a house_admin will a) receive booking requests notifications by email, b) be able to administer bookings on the `/manage` pages. (this may cause them to get a lot of email). 

