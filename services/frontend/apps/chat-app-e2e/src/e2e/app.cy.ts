describe('When the App is loaded', () => {
  it('should display the chat view', () => {
    cy.visit('/');
    cy.get('[data-testid="chat-view"]').should('exist');
  });
});