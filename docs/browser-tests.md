# Browser tests

We use [Cypress](https://www.cypress.io/) to test the high-level features of Modernomad in a browser. This checks that the frontend code and backend code all work together from the level of a user clicking around on the site.

Cypress needs to run on your local machine, not inside Chrome or a VM, because it has to start and control your browser.

First, install Cypress:

    $ npm install

Then, start it up: 

    npm run cypress:open

[The Cypress documentation has information on how to run and write tests.](https://docs.cypress.io/) The test cases are in `cypress/fixtures/`.

