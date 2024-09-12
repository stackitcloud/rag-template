import { DocumentResponseModel } from "./document-response.model";

export interface ChatDocumentModel {
    index: number;
    messageId: string;
    name: string;
    chunk: string;
    url: string;
}

export const mapToChatDocuments = (startIncrementId: number, documents: DocumentResponseModel[], messageId: string) => documents.map((doc, index) => ({
  index: startIncrementId + index,
  messageId: messageId,
  name: (doc.metadata.find(meta => (meta.key === "title" || meta.key === "document"))?.value as string).replace(/^"+|"+$/g, '') || "",  // TODO: handle nested json-text values correctly
  chunk: doc.content,
  url: (doc.metadata.find(meta => meta.key === "document_url")?.value as string).replace(/^"+|"+$/g, '') || ""  // TODO: handle nested json-text values correctly
}) as ChatDocumentModel);
