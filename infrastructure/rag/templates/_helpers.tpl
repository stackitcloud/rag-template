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

{{- define "secret.basicAuthName" -}}
{{- $basicAuth := fromYaml (include "rag.secretConfig" .Values.backend.secrets.basicAuth) -}}
{{- default "basic-auth" (dig "secretKeyRef" "name" "" $basicAuth) -}}
{{- end -}}

{{- define "rag.secretConfig" -}}
{{- if kindIs "map" . }}{{ toYaml . }}{{- else }}{{ toYaml (dict "value" .) }}{{- end -}}
{{- end -}}

{{- define "rag.secretRefName" -}}
{{- $config := fromYaml (include "rag.secretConfig" .config) -}}
{{- default .defaultName (dig "secretKeyRef" "name" "" $config) -}}
{{- end -}}

{{- define "rag.secretRefKey" -}}
{{- $config := fromYaml (include "rag.secretConfig" .config) -}}
{{- default .defaultKey (dig "secretKeyRef" "key" "" $config) -}}
{{- end -}}

{{- define "rag.secretEnvVar" -}}
{{- $config := fromYaml (include "rag.secretConfig" .config) -}}
{{- $secretName := include "rag.secretRefName" (dict "config" $config "defaultName" .defaultName) -}}
{{- $secretKey := include "rag.secretRefKey" (dict "config" $config "defaultKey" .defaultKey) -}}
- name: {{ .name }}
  valueFrom:
    secretKeyRef:
      name: {{ $secretName }}
      key: {{ $secretKey }}
{{- end -}}

{{- define "rag.secretIsExternal" -}}
{{- $config := fromYaml (include "rag.secretConfig" .config) -}}
{{- ne "" (dig "secretKeyRef" "name" "" $config) -}}
{{- end -}}

{{- define "rag.secretValue" -}}
{{- $config := fromYaml (include "rag.secretConfig" .) -}}
{{- $config.value -}}
{{- end -}}
