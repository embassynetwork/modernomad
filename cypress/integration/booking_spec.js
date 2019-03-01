/// <reference types="Cypress" />
const randomstring = require("randomstring");

describe("Booking a room", function() {
  it("works for the full happy path: existing logged in user, adding card, approved by admin, refunded", function() {
    cy.login("pixel", "password");
    cy.visit("/");
    cy.contains("Embassy SF").click();
    cy.contains("View all rooms").click();
    cy.contains("Ada Lovelace").click({ force: true });

    // Fill in booking form
    cy.get("input[name=arrive]").focus();
    // Pick next month so all the dates are available
    cy.get(".react-datepicker__navigation--next").click({ force: true });
    cy.get("[aria-label=day-13]").click({ force: true });
    // Force de-select first date picker. For some reason immediately selecting second date
    // picker causes first not to close.
    cy.get("#network-footer").click("topLeft");
    cy.get("input[name=depart]").focus();
    cy.get("[aria-label=day-16]").click({ force: true });
    cy.get("[name=purpose]").type("Work.");
    cy.contains("Request to Book").click();

    cy.contains("Your booking was submitted.");

    // Fill in credit card form
    cy.get("[data-stripe=number").type("4242424242424242");
    cy.get("[data-stripe=cvc").type("123");
    cy.get("[data-stripe=exp-month").type("12");
    cy.get("[data-stripe=exp-year").type("22");
    cy.contains("Add Card").click();

    cy.contains("Your card has been saved.");

    // Approve booking
    cy.login("embassysfadmin", "password");
    cy.visit("/locations/embassysf/manage/bookings/");
    // The booking we want is the only one by pixel
    cy.contains("Pixel")
      .parent()
      .parent()
      .find("a")
      .first()
      .click();
    cy.contains("Charge the user's card").click();

    // Dismiss email dialog
    // TODO: emails
    cy.get("#emailModal")
      .find(".close")
      .click();

    cy.contains("This booking is confirmed and paid.");

    // Refund
    cy.get("[href='#booking-manage-edit']").click();
    cy.contains("Cancel This Booking").click();
    cy.contains("Yes, Cancel").click();
    cy.contains("The booking has been cancelled.").click();
  });

  it("shows an error when credit card is declined when added", function() {
    cy.login("pixel", "password");
    cy.visit("/locations/embassysf/stay/");

    cy.contains("Ada Lovelace").click({ force: true });

    // Fill in booking form
    cy.get("input[name=arrive]").focus();
    // Pick next month so all the dates are available
    cy.get(".react-datepicker__navigation--next").click({ force: true });
    cy.get("[aria-label=day-13]").click({ force: true });
    // Force de-select first date picker. For some reason immediately selecting second date
    // picker causes first not to close.
    cy.get("#network-footer").click("topLeft");
    cy.get("input[name=depart]").focus();
    cy.get("[aria-label=day-16]").click({ force: true });
    cy.get("[name=purpose]").type("Work.");
    cy.contains("Request to Book").click();

    cy.contains("Your booking was submitted.");

    // Fill in credit card form
    // https://stripe.com/docs/testing#cards-responses
    cy.get("[data-stripe=number").type("4000000000000002");
    cy.get("[data-stripe=cvc").type("123");
    cy.get("[data-stripe=exp-month").type("12");
    cy.get("[data-stripe=exp-year").type("22");
    cy.contains("Add Card").click();

    cy.contains("Your card was declined.");
  });

  it("shows an error when credit card is declined at approval", function() {
    cy.login("pixel", "password");
    cy.visit("/locations/embassysf/stay/");

    cy.contains("Ada Lovelace").click({ force: true });

    // Fill in booking form
    cy.get("input[name=arrive]").focus();
    // Pick next month so all the dates are available
    cy.get(".react-datepicker__navigation--next").click({ force: true });
    cy.get("[aria-label=day-13]").click({ force: true });
    // Force de-select first date picker. For some reason immediately selecting second date
    // picker causes first not to close.
    cy.get("#network-footer").click("topLeft");
    cy.get("input[name=depart]").focus();
    cy.get("[aria-label=day-16]").click({ force: true });
    cy.get("[name=purpose]").type("Work.");
    cy.contains("Request to Book").click();

    cy.contains("Your booking was submitted.");

    // Fill in credit card form
    // https://stripe.com/docs/testing#cards-responses
    cy.get("[data-stripe=number").type("4000000000000341");
    cy.get("[data-stripe=cvc").type("123");
    cy.get("[data-stripe=exp-month").type("12");
    cy.get("[data-stripe=exp-year").type("22");
    cy.contains("Add Card").click();

    cy.contains("Your card has been saved.");

    // Approve booking
    cy.login("embassysfadmin", "password");
    cy.visit("/locations/embassysf/manage/bookings/");
    // The booking we want is the only one by pixel
    cy.contains("Pixel")
      .parent()
      .parent()
      .find("a")
      .first()
      .click();
    cy.contains("Charge the user's card").click();

    cy.contains("The card was declined");
    cy.contains("Charge the user's card"); // button to charge still exists, so it hasn't been marked as paid
  });

  it("works for a new user", function() {
    cy.visit("/");
    cy.contains("Embassy SF").click();
    cy.contains("View all rooms").click();
    cy.contains("Ada Lovelace").click({ force: true });

    cy.get("input[name=arrive]").focus();
    // Pick next month so all the dates are available
    cy.get(".react-datepicker__navigation--next").click({ force: true });
    cy.get("[aria-label=day-13]").click({ force: true });
    // Force de-select first date picker. For some reason immediately selecting second date
    // picker causes first not to close.
    cy.get("#network-footer").click("topLeft");
    cy.get("input[name=depart]").focus();
    cy.get("[aria-label=day-16]").click({ force: true });
    cy.get("[name=purpose]").type("Work.");
    cy.contains("Request to Book").click();

    cy.get("[name=bio]").type("I am a robot.");
    cy.get("[name=projects]").type("Kill all humans.");
    cy.get("[name=sharing]").type("I can do your math homework.");
    cy.get("[name=discussion]").type("Is AI risk overrated?");
    cy.get("[name=first_name]").type("Bot");
    cy.get("[name=last_name]").type("McBotface");
    cy.get("[name=referral]").type("Pixel");
    cy.get("[name=city]").type("Chapek 9");
    cy.get("[name=email]").type(`${randomstring.generate(10)}@example.com`);
    cy.get("[name=password1]").type("password");
    cy.get("[name=password2]").type("password");

    cy.uploadFile("profile.png", "input[name=image");

    cy.contains("Submit").click();

    cy.contains("Your booking has been submitted.");
  });

  it("works for an existing logged out user", function() {
    cy.visit("/");
    cy.contains("Embassy SF").click();
    cy.contains("View all rooms").click();
    cy.contains("Ada Lovelace").click({ force: true });

    cy.get("input[name=arrive]").focus();
    // Pick next month so all the dates are available
    cy.get(".react-datepicker__navigation--next").click({ force: true });
    cy.get("[aria-label=day-13]").click({ force: true });
    // Force de-select first date picker. For some reason immediately selecting second date
    // picker causes first not to close.
    cy.get("#network-footer").click("topLeft");
    cy.get("input[name=depart]").focus();
    cy.get("[aria-label=day-16]").click({ force: true });
    cy.get("[name=purpose]").type("Work.");
    cy.contains("Request to Book").click();

    cy.contains("log in").click();
    cy.get("[name=username]").type("pixel");
    cy.get("[name=password]").type("password");
    cy.get("button[type=submit]").click();

    cy.contains("Your booking has been submitted.");
  });
});
