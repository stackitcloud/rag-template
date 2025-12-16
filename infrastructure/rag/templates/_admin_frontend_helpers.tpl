{{- define "adminFrontend.fullImageName" -}}
{{- if .Values.adminFrontend.image -}}
    {{- if .Values.adminFrontend.image.repository -}}
        {{- $tag := default .Chart.AppVersion .Values.adminFrontend.image.tag -}}
        {{- printf "%s:%s" .Values.adminFrontend.image.repository $tag | trimSuffix ":" }}
    {{- else -}}
        {{ required "A valid .Values.adminFrontend.image.repository entry required!" . }}
    {{- end -}}
{{- else -}}
    {{ required "A valid .Values.adminFrontend.image entry required!" . }}
{{- end -}}
{{- end -}}

{{- define "ingress.adminFrontendFullname" -}}
{{- printf "%s-admin-frontend-ingress" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
