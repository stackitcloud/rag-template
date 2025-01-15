# secrets
{{- define "secret.databaseName" -}}
{{- printf "%s-database-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.langfuseName" -}}
{{- printf "%s-langfuse-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.stackitEmbedderName" -}}
{{- printf "%s-stackit-embedder-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.stackitVllmName" -}}
{{- printf "%s-stackit-vllm-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.ragasName" -}}
{{- printf "%s-stackit-ragas-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


# configmaps
{{- define "configmap.publicName" -}}
{{- printf "%s-public-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.databaseName" -}}
{{- printf "%s-database-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.loggingName" -}}
{{- printf "%s-logging-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.ollamaName" -}}
{{- printf "%s-ollama-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.ollamaEmbedderName" -}}
{{- printf "%s-ollama-embedder-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.fakeEmbedderName" -}}
{{- printf "%s-fake-embedder-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.ragClassTypesName" -}}
{{- printf "%s-rag-class-types-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.embedderClassTypesName" -}}
{{- printf "%s-embedder-class-types-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.retrieverName" -}}
{{- printf "%s-retriever-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.langfuseName" -}}
{{- printf "%s-langfuse-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.ragasName" -}}
{{- printf "%s-ragas-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.errorMessagesName" -}}
{{- printf "%s-error-messages-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.rerankerName" -}}
{{- printf "%s-reranker-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.stackitVllmName" -}}
{{- printf "%s-stackit-vllm-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.stackitEmbedderName" -}}
{{- printf "%s-stackit-embedder-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.chatHistoryName" -}}
{{- printf "%s-chat-history-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


# ingress
{{- define "backend.ingressFullName" -}}
{{- printf "%s-backend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "backend.fullImageName" -}}
{{- printf "%s/%s:%s" .Values.backend.image.repository .Values.backend.image.name .Values.backend.image.tag | trimSuffix ":" | trimSuffix "-" }}
{{- end -}}
