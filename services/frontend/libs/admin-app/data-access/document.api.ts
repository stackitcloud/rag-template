import axios, { AxiosProgressEvent } from 'axios';
import { DocumentModel } from "../models/document.model.ts";

axios.defaults.baseURL = import.meta.env.VITE_ADMIN_URL + "/api";
  axios.defaults.auth = {
    username: import.meta.env.VITE_AUTH_USERNAME,
    password: import.meta.env.VITE_AUTH_PASSWORD
  };

// confluence configuration interface
export interface ConfluenceConfig {
  spaceKey?: string;
  cql?: string;
  token: string;
  url: string;
  maxPages?: number;
  name: string;
}

// sitemap configuration interface
export interface SitemapConfig {
  webPath: string;
  filterUrls: string;
  headerTemplate: string;
  name: string;
    parser?: 'docusaurus' | 'astro' | 'generic';
}

export class DocumentAPI {
    static async loadDocuments(): Promise<DocumentModel[]> {
        try {
            const response = await axios.get<DocumentModel[]>('/all_documents_status');
            return response.data;
        } catch (error) {
            this.handleError(error);
        }
    }

    static async uploadDocument(file: File, onUploadProgress: (progressEvent: AxiosProgressEvent) => void): Promise<null> {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post<null>('/upload_file', formData, {
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

    static async loadConfluence(config: ConfluenceConfig): Promise<void> {
        try {
            // convert config to list of key/value items for backend
            const payload: { key: string; value: string }[] = [
                { key: 'url', value: config.url.trim() },
                { key: 'token', value: config.token },
            ];

            const spaceKey = config.spaceKey?.trim();
            if (spaceKey) {
                payload.push({ key: 'space_key', value: spaceKey });
            }

            const cql = config.cql?.trim();
            if (cql) {
                payload.push({ key: 'cql', value: cql });
            }

            if (typeof config.maxPages === 'number') {
                payload.push({ key: 'max_pages', value: String(config.maxPages) });
            }
            // include required query parameters
            await axios.post<void>('/upload_source', payload, {
                params: { source_type: 'confluence', name: config.name }
            });
        } catch(error) {
            this.handleError(error);
        }
    }

    static async loadSitemap(config: SitemapConfig): Promise<void> {
        try {
            // convert config to list of key/value items for backend
            const payload = [
                { key: 'web_path', value: config.webPath }
            ];

            if (config.parser) {
                payload.push({ key: 'sitemap_parser', value: config.parser });
            }

            // add filter_urls only if provided
            if (config.filterUrls && config.filterUrls.trim()) {
                // Convert multiline string to array and filter out empty lines
                const filterUrlsArray = config.filterUrls
                    .split('\n')
                    .map(url => url.trim())
                    .filter(url => url.length > 0);

                if (filterUrlsArray.length > 0) {
                    payload.push({ key: 'filter_urls', value: JSON.stringify(filterUrlsArray) });
                }
            }

            // add header_template only if provided
            if (config.headerTemplate && config.headerTemplate.trim()) {
                try {
                    // Validate JSON format
                    JSON.parse(config.headerTemplate);
                    payload.push({ key: 'header_template', value: config.headerTemplate });
                } catch {
                    throw new Error('Header template must be valid JSON format');
                }
            }

            // include required query parameters
            await axios.post<void>('/upload_source', payload, {
                params: { source_type: 'sitemap', name: config.name }
            });
        } catch(error) {
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
