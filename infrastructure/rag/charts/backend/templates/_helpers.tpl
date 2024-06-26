# secrets
{{- define "secret.database.name" -}}
{{- .Release.Name -}}-database-secret
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
{{- define "configmap.public.name" -}}
{{- .Release.Name -}}-public-configmap
{{- end -}}

{{- define "configmap.database.name" -}}
{{- .Release.Name -}}-database-configmap
{{- end -}}

{{- define "configmap.ollama.name" -}}
{{- .Release.Name -}}-ollama-configmap
{{- end -}}

{{- define "configmap.rag-class-types.name" -}}
{{- .Release.Name -}}-rag-class-types-configmap
{{- end -}}

{{- define "configmap.retriever.name" -}}
{{- .Release.Name -}}-retriever-configmap
{{- end -}}

{{- define "configmap.alephalpha.name" -}}
{{- .Release.Name -}}-alephalpha-configmap
{{- end -}}

{{- define "configmap.langfuse.name" -}}
{{- .Release.Name -}}-langfuse-configmap
{{- end -}}

{{- define "configmap.errormessages.name" -}}
{{- .Release.Name -}}-errormessages-configmap
{{- end -}}

{{- define "configmap.stackit-myapi-llm.name" -}}
{{- .Release.Name -}}-stackit-myapi-llm.configmap
{{- end -}}

{{- define "configmap.usecase.name" -}}
{{- .Release.Name -}}-usecase-configmap
{{- end -}}

{{- define "fullimagename" -}}
{{- printf "%s/%s:%s" .Values.image.repository .Values.image.name .Values.image.tag | trimSuffix ":" }}
{{- end -}}

# ingress
{{- define "ingress.fullname" -}}
{{- .Release.Name -}}-backend-ingress
{{- end -}}
