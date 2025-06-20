import { defineStore } from "pinia";
import { ref } from "vue";
import { DocumentModel } from "../../models/document.model.ts";
import { ErrorType } from "../../models/error-type";
import { UploadedDocument, mapToUploadDocument } from "../../models/uploaded-document.model";
import { ConfluenceConfig, DocumentAPI, SitemapConfig } from "../document.api";

export const useDocumentsStore = defineStore('chat', () => {
  const uploadedDocuments = ref<UploadedDocument[]>([]);
  const allDocuments = ref<DocumentModel[]>();
  const error = ref<ErrorType | null>(null);
  const isLoadingConfluence = ref(false);
  const isLoadingSitemap = ref(false);


  const uploadedDocuments = ref<UploadedDocument[]>([]);
  const allDocuments = ref<DocumentModel[]>();
  const error = ref<ErrorType | null>(null);
  const isLoadingConfluence = ref(false);

  function updateUploadedDocumentData(
    documentId: string,
    data: Partial<UploadedDocument>,
  ) {
    const document = uploadedDocuments.value.find(
      (d: UploadedDocument) => d.id === documentId,
    );
    if (document) {
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
          isProcessing: progress.total === progress.loaded,
        });
      });

      updateUploadedDocumentData(documentData.id, {
        isCompleted: true,
      });
    } catch (err) {
      updateUploadedDocumentData(documentData.id, { isFailed: true });
      console.error(err);
    }
  }

  const loadDocuments = async () => {
    try {
      const loadedDocuments = await DocumentAPI.loadDocuments();
      allDocuments.value = [
        ...loadedDocuments.map(
          (o) =>
            ({
              name: o.name,
              status: o.status,
            }) as DocumentModel,
        ),
      ];
    } catch {
      error.value = "load";
    }
  };

    const loadConfluence = async (config: ConfluenceConfig) => {
      isLoadingConfluence.value = true;
      error.value = null;
      try {
        // provide confluence configuration from frontend
        await DocumentAPI.loadConfluence(config);
        await loadDocuments(); // Refresh the document list after uploading
      } catch(err) {
        if (err.response && err.response.status === 501) {
          error.value = "confluence_not_configured";
          console.error("Confluence loader is not configured.");
        } else if (err.response && err.response.status === 423) {
          error.value = "confluence_locked";
          console.error("Confluence loader returned a warning.");
        } else {
          error.value = "confluence";
          console.error(err);
        }
      } finally {
        isLoadingConfluence.value = false;
      }
    } finally {
      isLoadingConfluence.value = false;
    }
  };

    const loadSitemap = async (config: SitemapConfig) => {
      isLoadingSitemap.value = true;
      error.value = null;
      try {
        // provide sitemap configuration from frontend
        await DocumentAPI.loadSitemap(config);
        await loadDocuments(); // Refresh the document list after uploading
      } catch(err) {
        if (err.response && err.response.status === 501) {
          error.value = "sitemap_not_configured";
          console.error("Sitemap loader is not configured.");
        } else if (err.response && err.response.status === 423) {
          error.value = "sitemap_locked";
          console.error("Sitemap loader returned a warning.");
        } else {
          error.value = "sitemap";
          console.error(err);
        }
      } finally {
        isLoadingSitemap.value = false;
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
    } catch (err) {
      error.value = "delete";
      console.error(err);
    }
  };

  const removeUploadedDocument = (documentId: string) => {
    uploadedDocuments.value = uploadedDocuments.value.filter(
      (o) => o.id !== documentId,
    );
  };


  return {removeUploadedDocument, uploadDocuments, loadDocuments, deleteDocument, loadConfluence, loadSitemap, allDocuments, uploadedDocuments, error, isLoadingSitemap};

});
