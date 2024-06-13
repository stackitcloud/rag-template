{{- define "configmap.name" -}}
{{- .Release.Name -}}-configmap
{{- end -}}

{{- define "fullimagename" -}}
{{- printf "%s/%s:%s" .Values.image.repository .Values.image.name (include "tagname" .) | trimSuffix ":" }}
{{- end -}}

{{- define "tagname" -}}
{{- default "" .Values.image.tag }}
{{- end -}}

{{- define "ingress.frontend.fullname" -}}
{{- .Release.Name -}}-frontend-ingress
{{- end -}}
