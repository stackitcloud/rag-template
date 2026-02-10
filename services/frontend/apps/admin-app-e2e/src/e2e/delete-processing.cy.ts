describe('Document deletion for processing state', () => {
  it('allows deleting processing documents', () => {
    cy.intercept('GET', '**/all_documents_status', [
      { name: 'doc-processing.pdf', status: 'PROCESSING' },
      { name: 'doc-ready.pdf', status: 'READY' }
    ]).as('getDocs');
    cy.intercept('DELETE', '**/delete_document/*', { statusCode: 200, body: {} }).as('deleteDocument');

    cy.visit('/documents');
    cy.wait('@getDocs');

    cy.get('#doc-processing.pdf').within(() => {
      cy.get('[data-testid="document-delete-btn"]').should('not.be.disabled').click();
    });

    cy.get('.modal-action-button--delete').click();

    cy.wait('@deleteDocument')
      .its('request.url')
      .should('include', 'doc-processing.pdf');
  });
});
