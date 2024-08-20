{{- define "configmap.name" -}}
{{- .Release.Name -}}-frontend-configmap
{{- end -}}

{{- define "tagname" -}}
{{- default "" .Values.image.tag }}
{{- end -}}


{{- define "fullimagename" -}}
{{- if .Values.image -}}
    {{- if .Values.image.repository -}}
        {{- printf "%s/%s:%s" .Values.image.repository .Values.image.name (include "tagname" .) | trimSuffix ":" }}
    {{- else -}}
        {{ required "A valid .Values.image.repository entry required!" . }}
    {{- end -}}
{{- else -}}
    {{ required "A valid .Values.image entry required!" . }}
{{- end -}}
{{- end -}}

{{- define "ingress.adminfrontend.fullname" -}}
{{- .Release.Name -}}-adminfrontend-ingress
{{- end -}}
