import axios, { AxiosProgressEvent } from 'axios';
import { DocumentModel } from "../models/document.model.ts";

axios.defaults.baseURL = import.meta.env.VITE_ADMIN_URL + "/api";
axios.defaults.auth = {
    username: import.meta.env.VITE_AUTH_USERNAME,
    password: import.meta.env.VITE_AUTH_PASSWORD
};

export class DocumentAPI {
    static async loadDocuments(): Promise<string[]> {
        try {
            const response = await axios.get<string[]>('/all_documents');
            return response.data;
        } catch (error) {
            this.handleError(error);
        }
    }

    static async uploadDocument(file: File, onUploadProgress: (progressEvent: AxiosProgressEvent) => void): Promise<DocumentModel> {
        try {
            const formData = new FormData();
            formData.append('body', file);

            const response = await axios.post<DocumentModel>('/upload_documents', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                onUploadProgress
            });

            return response.data;
        } catch (error) {
            this.handleError(error);
        }
    }

    static async deleteDocument(documentId: string): Promise<void> {
        try {
            await axios.delete<void>(`/delete_document/${documentId}`);
        } catch (error) {
            this.handleError(error);
        }
    }

    static async getDocumentReference(id: string): Promise<Blob> {
        try {
            const response = await axios.get(`/document_reference/${id}`, {
                responseType: 'blob'
            });
            return response.data;
        } catch (error) {
            this.handleError(error);
        }
    }

    private static handleError(error: any): never {
        if (axios.isAxiosError(error)) {
            console.error('Axios error:', error.response?.data || error.message);
        } else {
            console.error('Unexpected error:', error);
        }
        throw error;
    }
}
