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
{{- $creds := dict "username" (default "" .Values.shared.secrets.basicAuth.user.value) "password" (default "" .Values.shared.secrets.basicAuth.password.value) -}}

{{- if and (eq (get $creds "username") "") .Values.shared.secrets.basicAuth.user.secretKeyRef.name }}
  {{- with lookup "v1" "Secret" .Release.Namespace .Values.shared.secrets.basicAuth.user.secretKeyRef.name }}
    {{- $key := default "BASIC_AUTH_USER" $.Values.shared.secrets.basicAuth.user.secretKeyRef.key }}
    {{- $raw := index .data $key | default "" }}
    {{- if ne $raw "" }}
      {{- $_ := set $creds "username" (b64dec $raw) }}
    {{- end }}
  {{- end }}
{{- end }}

{{- if and (eq (get $creds "password") "") .Values.shared.secrets.basicAuth.password.secretKeyRef.name }}
  {{- with lookup "v1" "Secret" .Release.Namespace .Values.shared.secrets.basicAuth.password.secretKeyRef.name }}
    {{- $key := default "BASIC_AUTH_PASSWORD" $.Values.shared.secrets.basicAuth.password.secretKeyRef.key }}
    {{- $raw := index .data $key | default "" }}
    {{- if ne $raw "" }}
      {{- $_ := set $creds "password" (b64dec $raw) }}
    {{- end }}
  {{- end }}
{{- end }}

{{- toYaml $creds -}}
{{- end -}}

{{/* Build data block for the basic auth secret from htpasswd value or username/password. */}}
{{- define "rag.basicAuthSecretData" -}}
{{- $creds := (include "rag.basicAuthCredentials" . | fromYaml) -}}
{{- $auth := dict "value" (default "" .Values.shared.secrets.basicAuth.auth.value) -}}
{{- if and (eq (get $auth "value") "") .Values.shared.secrets.basicAuth.auth.secretKeyRef.name }}
  {{- with lookup "v1" "Secret" .Release.Namespace .Values.shared.secrets.basicAuth.auth.secretKeyRef.name }}
    {{- $key := default "auth" $.Values.shared.secrets.basicAuth.auth.secretKeyRef.key }}
    {{- $raw := index .data $key | default "" }}
    {{- if $raw }}
      {{- $_ := set $auth "value" (b64dec $raw) }}
    {{- end }}
  {{- end }}
{{- end }}
{{- $providedAuth := get $auth "value" }}
{{- $fromSecretRef := or .Values.shared.secrets.basicAuth.user.secretKeyRef.name .Values.shared.secrets.basicAuth.password.secretKeyRef.name }}
{{- $data := dict -}}
{{- if $providedAuth }}
  {{- $_ := set $data "auth" ($providedAuth | b64enc) }}
{{- else if and $creds.username $creds.password }}
  {{- $_ := set $data "auth" (htpasswd $creds.username $creds.password | b64enc) }}
  {{- if $fromSecretRef }}
    {{- $_ := set $data "BASIC_AUTH_USER" ($creds.username | b64enc) }}
    {{- $_ := set $data "BASIC_AUTH_PASSWORD" ($creds.password | b64enc) }}
  {{- end }}
{{- end }}
{{- if gt (len $data) 0 }}
{{- toYaml $data -}}
{{- end }}
{{- end -}}
