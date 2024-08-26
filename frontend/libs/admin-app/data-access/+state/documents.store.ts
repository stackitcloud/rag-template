import {DocumentModel} from "../../models/document.model.ts";
import {UploadedDocument, mapToUploadDocument} from "../../models/uploaded-document.model";
import {defineStore} from 'pinia';
import {ref} from 'vue';
import {DocumentAPI} from "../document.api";
import {ErrorType} from "../../models/error-type";

export const useDocumentsStore = defineStore('chat', () => {
    const uploadedDocuments = ref<UploadedDocument[]>([]);
    const allDocuments = ref<DocumentModel[]>();
    const error = ref<ErrorType | null>(null);

    function updateUploadedDocumentData(documentId: string, data: Partial<UploadedDocument>) {
        const document = uploadedDocuments.value.find((d: UploadedDocument) => d.id === documentId);
        if(document) {
            Object.assign(document, data);
        }
    }

    async function uploadDocument(file: File) {
        const documentData = mapToUploadDocument(file);
        uploadedDocuments.value.push(documentData);

        try {
            await DocumentAPI.uploadDocument(file, (progress) => {
                updateUploadedDocumentData(documentData.id, {
                    total: progress.total,
                    progress: progress.loaded,
                    isProcessing: progress.total === progress.loaded
                });
            });

            updateUploadedDocumentData(documentData.id, {
                isCompleted: true
            });
        } catch(err) {
            updateUploadedDocumentData(documentData.id, {isFailed: true});
            console.error(err);
        }
    }

    const loadDocuments = async () => {
        try {
            const loadedDocuments = await DocumentAPI.loadDocuments();
            allDocuments.value = [...loadedDocuments.map(o => ({
                name: o.name,
                status: o.status
            } as DocumentModel))];
        } catch {
            error.value = "load";
        }
    };

    const uploadDocuments = async (files: File[]) => {
        try {
            const uploads = files.map(uploadDocument);
            await Promise.all(uploads);
            await new Promise((resolve) => setTimeout(resolve, 250)); // short delay for the user to see the progress
            await loadDocuments();
        } catch(err) {
            error.value = "upload";
            console.error(err);
        } finally {
            uploadedDocuments.value = uploadedDocuments.value.filter(o => o.isFailed);
        }
    };

    const deleteDocument = async (documentId: string) => {
        try {
            await DocumentAPI.deleteDocument(documentId);
            await loadDocuments();
        } catch(err) {
            error.value = "delete";
            console.error(err);
        }
    };

    const removeUploadedDocument = (documentId: string) => {
        uploadedDocuments.value = uploadedDocuments.value.filter(o => o.id !== documentId);
    };

    return {removeUploadedDocument, uploadDocuments, loadDocuments, deleteDocument, allDocuments, uploadedDocuments, error};
});
