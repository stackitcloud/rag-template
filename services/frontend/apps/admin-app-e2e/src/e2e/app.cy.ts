describe('When the App is loaded', () => {
  it('should display the document view when visiting /', () => {
    cy.visit('/documents');
    cy.get('[data-testid="document-view"]').should('exist');
  });
});