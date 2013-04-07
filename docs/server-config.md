
## Nginx

1. the default request entity size is 1M on Nginx. This can cause error 413 "request entity too large." to fix this, add the following directive either in the specific site or installation-wide:
`client_max_body_size 20M;`

