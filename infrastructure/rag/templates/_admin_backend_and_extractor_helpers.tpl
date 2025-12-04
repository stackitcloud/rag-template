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

{{- define "secret.keyValueStoreName" -}}
{{- printf "%s-key-value-store-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

# key value store credentials helper
{{- define "keyValueStore.credentials" -}}
{{- $result := dict "username" "" "password" "" "usernameSecretName" "" "usernameSecretKey" "" "passwordSecretName" "" "passwordSecretKey" "" -}}
{{- $defaultUsernameKey := "USECASE_KEYVALUE_USERNAME" -}}
{{- $defaultPasswordKey := "USECASE_KEYVALUE_PASSWORD" -}}

{{- if .Values.adminBackend.secrets.keyValueStore.username.secretKeyRef.name }}
{{- $_ := set $result "usernameSecretName" .Values.adminBackend.secrets.keyValueStore.username.secretKeyRef.name -}}
{{- $_ := set $result "usernameSecretKey" (default $defaultUsernameKey .Values.adminBackend.secrets.keyValueStore.username.secretKeyRef.key) -}}
{{- else if .Values.adminBackend.secrets.keyValueStore.username.value }}
{{- $_ := set $result "username" .Values.adminBackend.secrets.keyValueStore.username.value -}}
{{- end }}

{{- if .Values.adminBackend.secrets.keyValueStore.password.secretKeyRef.name }}
{{- $_ := set $result "passwordSecretName" .Values.adminBackend.secrets.keyValueStore.password.secretKeyRef.name -}}
{{- $_ := set $result "passwordSecretKey" (default $defaultPasswordKey .Values.adminBackend.secrets.keyValueStore.password.secretKeyRef.key) -}}
{{- else if .Values.adminBackend.secrets.keyValueStore.password.value }}
{{- $_ := set $result "password" .Values.adminBackend.secrets.keyValueStore.password.value -}}
{{- else if .Values.keydb.existingSecret }}
{{- $_ := set $result "passwordSecretName" .Values.keydb.existingSecret -}}
{{- $_ := set $result "passwordSecretKey" (default "password" .Values.keydb.existingSecretPasswordKey) -}}
{{- else if .Values.keydb.password }}
{{- $_ := set $result "password" .Values.keydb.password -}}
{{- end }}

{{- if and (not (get $result "username")) (not (get $result "usernameSecretName")) (or (get $result "password") (get $result "passwordSecretName")) }}
{{- $_ := set $result "username" (default "default" .Values.keydb.auth.username) -}}
{{- end }}

{{- toYaml $result -}}
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
