{{- define "adminFrontend.fullImageName" -}}
{{- if .Values.adminFrontend.image -}}
    {{- if .Values.adminFrontend.image.repository -}}
        {{- $repo := .Values.adminFrontend.image.repository -}}
        {{- $tag := default .Chart.AppVersion .Values.adminFrontend.image.tag -}}
        {{- $digest := default "" .Values.adminFrontend.image.digest -}}
        {{- if $digest -}}
            {{- printf "%s@%s" $repo $digest -}}
        {{- else -}}
            {{- printf "%s:%s" $repo $tag -}}
        {{- end -}}
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
