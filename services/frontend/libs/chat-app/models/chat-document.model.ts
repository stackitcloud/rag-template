import { DocumentResponseModel } from "./document-response.model";

export interface ChatDocumentModel {
  index: number;
  messageId: string;
  name: string;
  chunk: string;
  url: string;
}

export const mapToChatDocuments = (startIncrementId: number, documents: DocumentResponseModel[], messageId: string) => documents.map((doc, index) => {
  const getMetadataValue = (key: string): string => {
    const metaItem = doc.metadata.find(meta => meta.key === key);
    return metaItem ? (metaItem.value as string).replace(/^"+|"+$/g, '') : '';
  };

  const name = getMetadataValue('title') || getMetadataValue('document') || '?';
  const url = getMetadataValue('document_url');
  return {
    index: startIncrementId + index,
    messageId: messageId,
    name: name,
    chunk: doc.page_content,
    url: url
  } as ChatDocumentModel;
});
