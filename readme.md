Modernomad is guest, event and community management software for coliving
houses and other experimental living arrangements focused on openness,
collaboration and participation. 

Modernomad is licensed under the [Affero General Public License](agpl-3.0.txt),
which is like the GPL but *requires* you provide access to the source code for
any modified versions that are running publicly (among other things). The
[intent](http://www.gnu.org/licenses/why-affero-gpl.html) is to make sure that
anyone improving the software makes those improvements available to others, as
we have to them. 

Docs are linked to below, with additional docs also to be found in the `docs` directory. 

Interested in contributing? We use [Pivotal
Tracker](https://www.pivotaltracker.com/s/projects/883046) for our tickets, and
[Github issues](https://github.com/jessykate/modernomad/issues?state=open)
associated with this repository for new problems, bug reports and suggestions.
[Read more about contributing](docs/contributing.md).

<img src="static/img/agplv3-88x31.png" />

## About 
Modernomad is designed to integrate guests, residents and a broader community
around a colivng house. Although a large portion of the functionality revolves
around managing guests, the underlying ethos is one in which the reservation is
the beginning of a shared experience and participation in a community. If you
are just looking for reservation software, you could probably use this but you
might be better off with something like
[CheckFront](http://www.checkfront.com/) which seems to integrate nicely with
custom sites, or even [AirBnB](http://airbnb.com). 

Main Features:

- Accept reservation requests online
- Full profile system for guests and residents
- Guests can edit and delete reservations online, create multiple reservations
  associated wth their account. 
- Define rooms with default rate and privacy settings (specify if guests or
  only admins can book it)
- Set custom rate or comp for reservations on case-by-case basis
- Ability to take credit card payments on the site using stripe
- Issue invoices and receipts by email
- Guest and resident profiles 
- Separate groups for residents and house admins
- Automated email workflow around new reservation requests - email house admins
  With new requests, email guest with approval or confirmation info (house
  Access, rules, general info, etc.)
- Calendar view of reservations 
- 'Today' view of residents and guests at the house "today"
- Occupancy view for admins showing breakdown of income, paid status and guests
  Stats on a month-by-month basis. 

### Pre-requisites, system dependencies and environment setup intructions:
see [Environment Setup](docs/environment-setup.md)

### First-time Setup
see [How to Run](docs/how-to-run.md)

### Configuration
see [Configuration](docs/configuration.md)
