{{- define "rag.dockerconfigjson" -}}
{{- $username := .Values.shared.imagePullSecret.auths.username -}}
{{- $password := .Values.shared.imagePullSecret.auths.pat -}}
{{- $auth := printf "%s:%s" $username $password | b64enc -}}
{{- $dockerconfigjson := dict "auths" (dict .Values.shared.imagePullSecret.auths.registry (dict "username" $username "password" $password "email" .Values.shared.imagePullSecret.auths.email "auth" $auth)) | toJson -}}
{{- print $dockerconfigjson | b64enc -}}
{{- end -}}

{{- define "configmap.usecaseName" -}}
{{- printf "%s-usecase-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.usecaseName" -}}
{{- printf "%s-usecase-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
