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

{{- define "configmap.retryDecoratorName" -}}
{{- printf "%s-retry-decorator-configmap" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "secret.usecaseName" -}}
{{- printf "%s-usecase-secret" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Resolve basic auth credentials from inline values or referenced secrets. */}}
{{- define "rag.basicAuthCredentials" -}}
{{- $creds := dict "username" (default "" .Values.shared.secrets.basicAuthUser.value) "password" (default "" .Values.shared.secrets.basicAuthPassword.value) -}}

{{- if and (eq (get $creds "username") "") .Values.shared.secrets.basicAuthUser.secretKeyRef.name }}
  {{- with lookup "v1" "Secret" .Release.Namespace .Values.shared.secrets.basicAuthUser.secretKeyRef.name }}
    {{- $key := default "BASIC_AUTH_USER" $.Values.shared.secrets.basicAuthUser.secretKeyRef.key }}
    {{- $raw := index .data $key | default "" }}
    {{- if ne $raw "" }}
      {{- $_ := set $creds "username" (b64dec $raw) }}
    {{- end }}
  {{- end }}
{{- end }}

{{- if and (eq (get $creds "password") "") .Values.shared.secrets.basicAuthPassword.secretKeyRef.name }}
  {{- with lookup "v1" "Secret" .Release.Namespace .Values.shared.secrets.basicAuthPassword.secretKeyRef.name }}
    {{- $key := default "BASIC_AUTH_PASSWORD" $.Values.shared.secrets.basicAuthPassword.secretKeyRef.key }}
    {{- $raw := index .data $key | default "" }}
    {{- if ne $raw "" }}
      {{- $_ := set $creds "password" (b64dec $raw) }}
    {{- end }}
  {{- end }}
{{- end }}

{{- toYaml $creds -}}
{{- end -}}
