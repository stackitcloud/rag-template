import { DocumentResponseModel } from "./document-response.model";

export interface ChatDocumentModel {
    index: number;
    messageId: string;
    name: string;
    chunk: string;
    url: string;
}

export const mapToChatDocuments = (startIncrementId: number, documents: DocumentResponseModel[], messageId: string) => documents.map((o, index) => ({
    index: startIncrementId + index,
    messageId,
    ...o
}) as ChatDocumentModel);