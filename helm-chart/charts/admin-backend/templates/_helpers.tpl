# secrets
{{- define "secret.s3.name" -}}
{{- .Release.Name -}}-s3-secret
{{- end -}}

{{- define "secret.alephalpha.name" -}}
{{- .Release.Name -}}-alephalpha-secret
{{- end -}}

{{- define "secret.langfuse.name" -}}
{{- .Release.Name -}}-langfuse-secret
{{- end -}}

{{- define "secret.stackit-myapi-llm.name" -}}
{{- .Release.Name -}}-stackit-myapi-llm-secret
{{- end -}}

{{- define "secret.usecase.name" -}}
{{- .Release.Name -}}-usecase-secret
{{- end -}}
# configmaps
{{- define "configmap.s3.name" -}}
{{- .Release.Name -}}-s3-configmap
{{- end -}}

{{- define "configmap.summarizer.name" -}}
{{- .Release.Name -}}-summarizer-configmap
{{- end -}}

{{- define "configmap.chunker.name" -}}
{{- .Release.Name -}}-chunker-configmap
{{- end -}}

{{- define "configmap.ollama.name" -}}
{{- .Release.Name -}}-ollama-configmap
{{- end -}}

{{- define "configmap.rag-class-types.name" -}}
{{- .Release.Name -}}-rag-class-types-configmap
{{- end -}}

{{- define "configmap.alephalpha.name" -}}
{{- .Release.Name -}}-alephalpha-configmap
{{- end -}}

{{- define "configmap.ragapi.name" -}}
{{- .Release.Name -}}-ragapi-configmap
{{- end -}}

{{- define "configmap.logging.name" -}}
{{- .Release.Name -}}-logging-configmap
{{- end -}}

{{- define "configmap.langfuse.name" -}}
{{- .Release.Name -}}-langfuse-configmap
{{- end -}}

{{- define "configmap.stackit-myapi-llm.name" -}}
{{- .Release.Name -}}-stackit-myapi-llm.configmap
{{- end -}}

{{- define "configmap.pdfextractor.name" -}}
{{- .Release.Name -}}-pdfextractor-configmap
{{- end -}}

{{- define "configmap.admin-backend.name" -}}
{{- .Release.Name -}}-admin-backend-configmap
{{- end -}}

{{- define "configmap.usecase.name" -}}
{{- .Release.Name -}}-usecase-configmap
{{- end -}}

{{- define "adminbackendfullimagename" -}}
{{- printf "%s/%s:%s" .Values.admin_backend.image.repository .Values.admin_backend.image.name .Values.admin_backend.image.tag | trimSuffix ":" }}
{{- end -}}

{{- define "extractorfullimagename" -}}
{{- printf "%s/%s:%s" .Values.extractor.image.repository .Values.extractor.image.name .Values.extractor.image.tag | trimSuffix ":" }}
{{- end -}}

# ingress
{{- define "ingress.admin-backend.fullname" -}}
{{- .Release.Name -}}-admin-backend-ingress
{{- end -}}

{{- define "secret.stackit-vllm.name" -}}
{{- .Release.Name -}}-stackit-vllm-secret
{{- end -}}

{{- define "configmap.stackit-vllm.name" -}}
{{- .Release.Name -}}-stackit-vllm-configmap
{{- end -}}
