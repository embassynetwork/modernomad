Feature: Booking a room
  A tourist should be able to book a room for a short term stay
  at an embassy house as easily as possible. This is an important
  first introduction to the network for many people, and is also
  a major financial engine for the embassy network.

  Background:
    Given there is a house called "The Red Vic"
    And   "The Red Vic" has a room "Swanky Hostel" with 4 beds available
    And   "The Red Vic" has a room "Love Nest" with 1 bed available

  Scenario: A new tourist should be able to apply to book a bed
    Given a new site visitor is looking at options to stay at "The Red Vic"
    And   they want to say from the 1st - 3rd of next month
    Then  ensure they are offered "Swanky Hostel" and "Love Nest" rooms
    When  they ask to book a bed in "Swanky Hostel"
    Then  something good should happen
