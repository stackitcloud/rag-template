describe('Document deletion availability', () => {
  it('enables delete for documents in PROCESSING and READY', () => {
    cy.intercept('GET', '**/all_documents_status', [
      { name: 'doc-processing.pdf', status: 'PROCESSING' },
      { name: 'doc-ready.pdf', status: 'READY' },
    ]).as('docs');

    cy.visit('/documents');
    cy.wait('@docs');

    // Processing item should have enabled delete button
    cy.contains('h4', 'doc-processing.pdf')
      .parentsUntil('div')
      .parent()
      .find('[data-testid="document-delete-btn"]')
      .should('not.be.disabled');

    // Ready item should have enabled delete button
    cy.contains('h4', 'doc-ready.pdf')
      .parentsUntil('div')
      .parent()
      .find('[data-testid="document-delete-btn"]')
      .should('not.be.disabled');
  });
});
