{{- define "rag.ingress.fullname" -}}
{{- .Release.Name -}}-ingress
{{- end -}}

{{- define "rag.dockerconfigjson" -}}
{{- $username := .Values.registry.auths.crIo.username -}}
{{- $password := .Values.registry.auths.crIo.pat -}}
{{- $auth := printf "%s:%s" $username $password | b64enc -}}
{{- $dockerconfigjson := dict "auths" (dict .Values.registry.name (dict "username" $username "password" $password "email" .Values.registry.auths.crIo.email "auth" $auth)) | toJson -}}
{{- print $dockerconfigjson | b64enc -}}
{{- end -}}
