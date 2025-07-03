{{- define "adminFrontend.fullImageName" -}}
{{- if .Values.adminFrontend.image -}}
    {{- if .Values.adminFrontend.image.repository -}}
        {{- printf "%s/%s:%s" .Values.adminFrontend.image.repository .Values.adminFrontend.image.name .Values.adminFrontend.image.tag | trimSuffix ":" }}
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
