describe('When the App is loaded', () => {
  it('should display the document view when visiting /', () => {
    cy.visit('/documents');
    cy.get('[data-testid="document-view"]').should('exist');
  });

  it('should enable delete for processing and ready documents', () => {
    // Stub the backend response for documents
    cy.intercept('GET', '**/all_documents_status', [
      { name: 'Doc-A.pdf', status: 'PROCESSING' },
      { name: 'Doc-B.pdf', status: 'READY' }
    ]).as('getDocs');

    cy.visit('/documents');
    cy.wait('@getDocs');

    // The list renders items with id equal to document name
    cy.get('#Doc-A.pdf').within(() => {
      cy.get('[data-testid="document-delete-btn"]').should('not.be.disabled');
    });

    cy.get('#Doc-B.pdf').within(() => {
      cy.get('[data-testid="document-delete-btn"]').should('not.be.disabled');
    });
  });
});
