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

{{- define "secret.basicAuthName" -}}
{{- if .Values.shared.secrets.basicAuth.auth.secretKeyRef.name -}}
{{- .Values.shared.secrets.basicAuth.auth.secretKeyRef.name -}}
{{- else if .Values.shared.secrets.basicAuth.user.secretKeyRef.name -}}
{{- .Values.shared.secrets.basicAuth.user.secretKeyRef.name -}}
{{- else if .Values.shared.secrets.basicAuth.password.secretKeyRef.name -}}
{{- .Values.shared.secrets.basicAuth.password.secretKeyRef.name -}}
{{- else -}}
basic-auth
{{- end -}}
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

{{- define "secret.stackitEmbedderRefName" -}}
{{- if .Values.backend.secrets.stackitEmbedder.apiKey.secretKeyRef.name -}}
{{- .Values.backend.secrets.stackitEmbedder.apiKey.secretKeyRef.name -}}
{{- else -}}
{{ template "secret.stackitEmbedderName" . }}
{{- end -}}
{{- end -}}

{{- define "secret.stackitVllmRefName" -}}
{{- if .Values.backend.secrets.stackitVllm.apiKey.secretKeyRef.name -}}
{{- .Values.backend.secrets.stackitVllm.apiKey.secretKeyRef.name -}}
{{- else -}}
{{ template "secret.stackitVllmName" . }}
{{- end -}}
{{- end -}}

{{- define "secret.ragasRefName" -}}
{{- if .Values.backend.secrets.ragas.openaiApikey.secretKeyRef.name -}}
{{- .Values.backend.secrets.ragas.openaiApikey.secretKeyRef.name -}}
{{- else -}}
{{ template "secret.ragasName" . }}
{{- end -}}
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

{{- define "configmap.mcp" -}}
{{- printf "%s-mcp-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

# ingress
{{- define "backend.ingressFullName" -}}
{{- printf "%s-backend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "backend.fullImageName" -}}
{{- $tag := default .Chart.AppVersion .Values.backend.image.tag -}}
{{- printf "%s:%s" .Values.backend.image.repository $tag | trimSuffix ":" | trimSuffix "-" }}
{{- end -}}

{{- define "mcp.fullImageName" -}}
{{- $tag := default .Chart.AppVersion .Values.backend.mcp.image.tag -}}
{{- printf "%s:%s" .Values.backend.mcp.image.repository $tag | trimSuffix ":" | trimSuffix "-" }}
{{- end -}}


# Common ingress annotations for backend services
{{- define "backend.ingress.commonAnnotations" -}}
{{- if .Values.shared.config.basicAuth.enabled }}
nginx.ingress.kubernetes.io/auth-type: basic
nginx.ingress.kubernetes.io/auth-secret: {{ template "secret.basicAuthName" . }}
{{- end }}
nginx.ingress.kubernetes.io/proxy-body-size: "0"
nginx.ingress.kubernetes.io/proxy-read-timeout: "6000"
nginx.ingress.kubernetes.io/enable-cors: "true"
nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
nginx.ingress.kubernetes.io/proxy-send-timeout: "6000"
nginx.ingress.kubernetes.io/cors-max-age: "100"
nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
{{- if .Values.shared.config.tls.enabled }}
nginx.ingress.kubernetes.io/ssl-redirect: "true"
nginx.ingress.kubernetes.io/cors-allow-origin: "http://localhost:4200, https://{{ .Values.backend.ingress.host.name }}, https://admin.{{ .Values.backend.ingress.host.name }}"
{{- else }}
nginx.ingress.kubernetes.io/ssl-redirect: "false"
nginx.ingress.kubernetes.io/cors-allow-origin: "*"
{{- end }}
{{- end -}}

# Common ingress spec for backend services
{{- define "backend.ingress.commonSpec" -}}
{{- if .Values.shared.config.tls.enabled }}
tls:
  - hosts:
    - {{ .Values.shared.config.tls.host }}
    secretName: {{ .Values.shared.config.tls.secretName }}
{{- end }}
ingressClassName: nginx
{{- end -}}
