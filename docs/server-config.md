
## Nginx

1. the default request entity size is 1M on Nginx. This can cause error 413 "request entity too large." to fix this, add the following directive either in the specific site or installation-wide:
`client_max_body_size 20M;`

2. i currently set up the server to redirect all requests to HTTPS. you could
also do it only for the pages that support credit card data insertion but i
just use it for the whole site. 

