{{- define "configmap.frontendName" -}}
{{- printf "%s-frontend-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "frontend.fullImageName" -}}
{{- printf "%s/%s:%s" .Values.frontend.image.repository .Values.frontend.image.name .Values.frontend.image.tag | trimSuffix ":" -}}
{{- end -}}

{{- define "ingress.frontendFullname" -}}
{{- printf "%s-frontend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
