import axios, { AxiosProgressEvent } from "axios";
import { DocumentModel } from "../models/document.model";
import { newUid } from "@shared/utils";

// Mock data
const mockDocuments: DocumentModel[] = [
  { name: "Annual-Report-2023.pdf", status: "READY" },
  { name: "Product-Specifications.docx", status: "READY" },
  { name: "Financial-Summary-Q2.pdf", status: "PROCESSING" },
  { name: "Meeting-Notes.docx", status: "READY" },
  { name: "Technical-Documentation.pdf", status: "READY" },
  { name: "Project-Proposal.pptx", status: "UPLOADING" },
  { name: "Customer-Survey-Results.xml", status: "ERROR" },
];

// Mock implementation with the same interface as the real DocumentAPI
export class MockDocumentAPI {
  static async loadDocuments(): Promise<DocumentModel[]> {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 500));
    return [...mockDocuments];
  }

  static async uploadDocument(
    file: File,
    onUploadProgress: (progressEvent: AxiosProgressEvent) => void,
  ): Promise<null> {
    // Simulate upload progress
    const total = file.size;
    const steps = 10;

    for (let i = 1; i <= steps; i++) {
      await new Promise((resolve) => setTimeout(resolve, 300));
      onUploadProgress({
        loaded: Math.floor(total * (i / steps)),
        total,
      } as AxiosProgressEvent);
    }

    // Add the uploaded document to our mock list
    mockDocuments.push({ name: file.name, status: "PROCESSING" });

    // After a delay, mark it as ready
    setTimeout(() => {
      const doc = mockDocuments.find((d) => d.name === file.name);
      if (doc) doc.status = "READY";
    }, 2000);

    return null;
  }

  static async loadConfluence(): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Add some mock Confluence documents
    mockDocuments.push(
      { name: `Confluence-Doc-${newUid()}.pdf`, status: "PROCESSING" },
      { name: `Confluence-Doc-${newUid()}.pdf`, status: "PROCESSING" },
    );

    // Mark them as ready after delay
    setTimeout(() => {
      mockDocuments.forEach((doc) => {
        if (doc.name.startsWith("Confluence-Doc-")) {
          doc.status = "READY";
        }
      });
    }, 1500);
  }

  static async deleteDocument(documentId: string): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const index = mockDocuments.findIndex((d) => d.name === documentId);
    if (index !== -1) {
      mockDocuments.splice(index, 1);
    }
  }
}
