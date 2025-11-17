{{- define "configmap.frontendName" -}}
{{- printf "%s-frontend-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "frontend.fullImageName" -}}
{{- $tag := default .Chart.AppVersion .Values.frontend.image.tag -}}
{{- printf "%s:%s" .Values.frontend.image.repository $tag | trimSuffix ":" -}}
{{- end -}}

{{- define "ingress.frontendFullname" -}}
{{- printf "%s-frontend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
