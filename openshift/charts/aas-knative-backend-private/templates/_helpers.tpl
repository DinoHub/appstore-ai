# Create a secret with the credentials for the private registry
{{- define "imagePullSecret" }}
{{- printf "{\"auths\": {\"%s\": {\"auth\": \"%s\"}}}" .Values.imageCredentials.registry (printf "%s:%s" .Values.imageCredentials.username .Values.imageCredentials.password | b64enc) | b64enc }}
{{- end }}

{{- define "baseImagePullSecret" }}
{{- printf "{\"auths\": {\"%s\": {\"auth\": \"%s\"}}}" .Values.baseImageCredentials.registry (printf "%s:%s" .Values.baseImageCredentials.username .Values.baseImageCredentials.password | b64enc) | b64enc }}
{{- end }}
