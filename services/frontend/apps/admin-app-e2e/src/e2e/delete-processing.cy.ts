describe('Document deletion guarded by processing state', () => {
  it('disables delete for processing documents and enables for ready ones', () => {
    cy.intercept('GET', '**/all_documents_status', [
      { name: 'doc-processing.pdf', status: 'PROCESSING' },
      { name: 'doc-ready.pdf', status: 'READY' }
    ]).as('getDocs');

    cy.visit('/documents');
    cy.wait('@getDocs');

    // Find the list items by their id (DocumentContainer sets :id to document.name)
    cy.get('#doc-processing.pdf').within(() => {
      cy.get('[data-testid="document-delete-btn"]').should('be.disabled');
    });

    cy.get('#doc-ready.pdf').within(() => {
      cy.get('[data-testid="document-delete-btn"]').should('not.be.disabled');
    });
  });
});
