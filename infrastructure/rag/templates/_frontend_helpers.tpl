{{- define "configmap.frontendName" -}}
{{- printf "%s-frontend-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "frontend.fullImageName" -}}
{{- $repo := .Values.frontend.image.repository -}}
{{- $tag := default .Chart.AppVersion .Values.frontend.image.tag -}}
{{- $digest := default "" .Values.frontend.image.digest -}}
{{- if $digest -}}
{{- printf "%s@%s" $repo $digest -}}
{{- else -}}
{{- printf "%s:%s" $repo $tag -}}
{{- end -}}
{{- end -}}

{{- define "ingress.frontendFullname" -}}
{{- printf "%s-frontend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
