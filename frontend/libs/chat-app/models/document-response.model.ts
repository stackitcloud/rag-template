export interface DocumentResponseMetadataModel {
  key: string;
  value: object | [] | string;  // TODO: handle nested json-text values correctly
}

export interface DocumentResponseModel {
  metadata: DocumentResponseMetadataModel[],
  content: string
}
