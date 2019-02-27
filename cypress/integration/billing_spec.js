/// <reference types="Cypress" />

describe("Billing", function() {
  it("works when adding credit card to profile", function() {
    cy.login("pixel", "password");
    cy.visit("/people/pixel/");

    cy.contains("Add Credit Card").click();

    cy.stripeCheckout().then(function($body) {
      cy.wrap($body)
        .find("input:eq(0)")
        .type("pixel@example.com");
      cy.wrap($body)
        .find("input:eq(1)")
        .type("4242424242424242");
      cy.wrap($body)
        .find("input:eq(2)")
        .type("1222");
      cy.wrap($body)
        .find("input:eq(3)")
        .type("123")
        .type("{enter}");
    });

    cy.contains("Your card has been saved.");
    cy.contains("Delete saved card (**4242)").click();
    cy.contains("Card deleted.");
    cy.contains("Add Credit Card");
  });
});
