// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

// https://github.com/cypress-io/cypress/issues/170
Cypress.Commands.add("uploadFile", (fileName, selector) => {
  cy.get(selector).then(subject => {
    cy.fixture(fileName).then(content => {
      Cypress.Blob.base64StringToBlob(content, "image/jpeg").then(blob => {
        const el = subject[0];
        const testFile = new File([blob], fileName);
        const dataTransfer = new DataTransfer();

        dataTransfer.items.add(testFile);
        el.files = dataTransfer.files;
      });
    });
  });
});

// https://docs.cypress.io/guides/getting-started/testing-your-app.html#Logging-in
// https://github.com/cypress-io/cypress-example-recipes/blob/master/examples/logging-in__csrf-tokens/cypress/integration/logging-in-csrf-tokens-spec.js
Cypress.Commands.add("login", (username, password) => {
  return cy
    .request("/people/login/")
    .its("body")
    .then(body => {
      const $html = Cypress.$(body);
      const csrf = $html.find("input[name=csrfmiddlewaretoken]").val();

      return cy
        .request({
          method: "POST",
          url: "/people/login/",
          form: true,
          followRedirect: false,
          body: {
            username: username,
            password: password,
            csrfmiddlewaretoken: csrf
          }
        })
        .then(resp => {
          // Redirect to home page = success
          expect(resp.status).to.eq(302);
        });
    });
});

// https://gist.github.com/mbrochh/460f6d4fce959791c8f947cb30bed6a7
Cypress.Commands.add("stripeCheckout", () => {
  // For some reason we need to wait a bit before getting iframe
  cy.wait(1000);
  return cy.get("iframe.stripe_checkout_app").then(function($iframe) {
    return $iframe.contents().find("body");
  });
});
