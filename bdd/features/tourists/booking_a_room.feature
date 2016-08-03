Feature: Booking a room
  A tourist should be able to book a room for a short term stay
  at an embassy house as easily as possible. This is an important
  first introduction to the network for many people, and is also
  a major financial engine for the embassy network.

  Background:
    Given there is a location called "The Red Vic"
    And   "The Red Vic" has a room "Swanky Hostel" with 4 beds available
    And   "The Red Vic" has a room "Love Nest" with 1 bed available

  Scenario: A new tourist should be able to apply to book a bed
    Given a new site visitor is looking at options to stay at "The Red Vic"
    When  they want to say 60 days from now for 2 nights
    Then  ensure they are offered 2 rooms
    When  they ask to book a bed in "Swanky Hostel"
    Then  they should be asked to create a profile
    When  they create a valid profile
    Then  they should have a pending reservation
    And   the house admins get an email about a new pending reservation
