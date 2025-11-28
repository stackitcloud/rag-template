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

{{- define "secret.langfuseRefName" -}}
{{- if .Values.backend.secrets.langfuse.publicKey.secretKeyRef.name -}}
{{- .Values.backend.secrets.langfuse.publicKey.secretKeyRef.name -}}
{{- else if .Values.backend.secrets.langfuse.secretKey.secretKeyRef.name -}}
{{- .Values.backend.secrets.langfuse.secretKey.secretKeyRef.name -}}
{{- else -}}
{{ template "secret.langfuseName" . }}
{{- end -}}
{{- end -}}

{{- define "secret.stackitVllmRefName" -}}
{{- if .Values.backend.secrets.stackitVllm.apiKey.secretKeyRef.name -}}
{{- .Values.backend.secrets.stackitVllm.apiKey.secretKeyRef.name -}}
{{- else -}}
{{ template "secret.stackitVllmName" . }}
{{- end -}}
{{- end -}}

{{- define "secret.stackitEmbedderRefName" -}}
{{- if .Values.backend.secrets.stackitEmbedder.apiKey.secretKeyRef.name -}}
{{- .Values.backend.secrets.stackitEmbedder.apiKey.secretKeyRef.name -}}
{{- else -}}
{{ template "secret.stackitEmbedderName" . }}
{{- end -}}
{{- end -}}

{{- define "secret.s3RefName" -}}
{{- if .Values.shared.secrets.s3.accessKey.secretKeyRef.name -}}
{{- .Values.shared.secrets.s3.accessKey.secretKeyRef.name -}}
{{- else if .Values.shared.secrets.s3.secretKey.secretKeyRef.name -}}
{{- .Values.shared.secrets.s3.secretKey.secretKeyRef.name -}}
{{- else -}}
{{ template "secret.s3Name" . }}
{{- end -}}
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
{{- $tag := default .Chart.AppVersion .Values.adminBackend.image.tag -}}
{{- printf "%s:%s" .Values.adminBackend.image.repository $tag | trimSuffix ":" }}
{{- end -}}

{{- define "extractor.fullImageName" -}}
{{- $tag := default .Chart.AppVersion .Values.extractor.image.tag -}}
{{- printf "%s:%s" .Values.extractor.image.repository $tag | trimSuffix ":" }}
{{- end -}}

{{- define "extractor.huggingfaceCacheDir" -}}
{{- default "/tmp/hf-cache" .Values.extractor.huggingfaceCacheDir -}}
{{- end -}}

{{- define "extractor.modelscopeCacheDir" -}}
{{- default "/var/modelscope" .Values.extractor.modelscopeCacheDir -}}
{{- end -}}

# ingress
{{- define "ingress.adminBackendFullname" -}}
{{- printf "%s-admin-backend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
