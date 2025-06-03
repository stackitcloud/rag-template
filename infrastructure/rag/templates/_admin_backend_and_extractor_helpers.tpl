# secrets
{{- define "secret.s3Name" -}}
{{- printf "%s-s3-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.langfuseName" -}}
{{- printf "%s-langfuse-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.usecaseName" -}}
{{- printf "%s-usecase-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.stackitVllmName" -}}
{{- printf "%s-stackit-vllm-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

# configmaps
{{- define "configmap.s3Name" -}}
{{- printf "%s-s3-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.keyValueStoreName" -}}
{{- printf "%s-key-value-store-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.summarizerName" -}}
{{- printf "%s-summarizer-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.chunkerName" -}}
{{- printf "%s-chunker-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.ollamaName" -}}
{{- printf "%s-ollama-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.ragClassTypesName" -}}
{{- printf "%s-rag-class-types-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.ragapiName" -}}
{{- printf "%s-ragapi-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.loggingName" -}}
{{- printf "%s-logging-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.langfuseName" -}}
{{- printf "%s-langfuse-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.pdfextractorName" -}}
{{- printf "%s-pdfextractor-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.adminBackendName" -}}
{{- printf "%s-admin-backend-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.usecaseName" -}}
{{- printf "%s-usecase-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.stackitVllmName" -}}
{{- printf "%s-stackit-vllm-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "configmap.sourceUploaderName" -}}
{{- printf "%s-source-uploader-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

# image
{{- define "adminBackend.fullImageName" -}}
{{- printf "%s/%s:%s" .Values.adminBackend.image.repository .Values.adminBackend.image.name .Values.adminBackend.image.tag | trimSuffix ":" }}
{{- end -}}

{{- define "extractor.fullImageName" -}}
{{- printf "%s/%s:%s" .Values.extractor.image.repository .Values.extractor.image.name .Values.extractor.image.tag | trimSuffix ":" }}
{{- end -}}

# ingress
{{- define "ingress.adminBackendFullname" -}}
{{- printf "%s-admin-backend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
