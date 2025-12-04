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
  {{- $secret := lookup "v1" "Secret" .Release.Namespace .Values.shared.secrets.basicAuthUser.secretKeyRef.name }}
  {{- if not $secret }}
    {{- fail (printf "Secret %q not found in namespace %q for shared.secrets.basicAuthUser.secretKeyRef" .Values.shared.secrets.basicAuthUser.secretKeyRef.name .Release.Namespace) }}
  {{- end }}
  {{- if not $secret.data }}
    {{- fail (printf "Secret %q has no data field" .Values.shared.secrets.basicAuthUser.secretKeyRef.name) }}
  {{- end }}
  {{- $key := default "BASIC_AUTH_USER" .Values.shared.secrets.basicAuthUser.secretKeyRef.key }}
  {{- $raw := index $secret.data $key | default "" }}
  {{- if eq $raw "" }}
    {{- fail (printf "Key %q not found in secret %q for shared.secrets.basicAuthUser.secretKeyRef" $key .Values.shared.secrets.basicAuthUser.secretKeyRef.name) }}
  {{- end }}
  {{- $_ := set $creds "username" (b64dec $raw) }}
{{- end }}

{{- if and (eq (get $creds "password") "") .Values.shared.secrets.basicAuthPassword.secretKeyRef.name }}
  {{- $secret := lookup "v1" "Secret" .Release.Namespace .Values.shared.secrets.basicAuthPassword.secretKeyRef.name }}
  {{- if not $secret }}
    {{- fail (printf "Secret %q not found in namespace %q for shared.secrets.basicAuthPassword.secretKeyRef" .Values.shared.secrets.basicAuthPassword.secretKeyRef.name .Release.Namespace) }}
  {{- end }}
  {{- if not $secret.data }}
    {{- fail (printf "Secret %q has no data field" .Values.shared.secrets.basicAuthPassword.secretKeyRef.name) }}
  {{- end }}
  {{- $key := default "BASIC_AUTH_PASSWORD" .Values.shared.secrets.basicAuthPassword.secretKeyRef.key }}
  {{- $raw := index $secret.data $key | default "" }}
  {{- if eq $raw "" }}
    {{- fail (printf "Key %q not found in secret %q for shared.secrets.basicAuthPassword.secretKeyRef" $key .Values.shared.secrets.basicAuthPassword.secretKeyRef.name) }}
  {{- end }}
  {{- $_ := set $creds "password" (b64dec $raw) }}
{{- end }}

{{- toYaml $creds -}}
{{- end -}}
