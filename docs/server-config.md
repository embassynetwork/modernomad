
## Nginx

1. the default request entity size is 1M on Nginx. This can cause error 413
 "request entity too large." to fix this, add the following directive either in
 the specific site or installation-wide: `client_max_body_size 20M;`

2. redirect all requests to HTTPS. here is an example nginx config file. if you
 have an example config for apache, i am happy to include it. 


###### Example Nginx Config ######

	upstream modernomad {
		# nnnn is a local port for this app
		server 127.0.0.1:nnnn;
	}

	server {

	    # force everything through https
	    listen 80;
	    server_name example.com;
	    rewrite ^ https://$server_name$request_uri? permanent;
	}

	server {
	    listen 443;
	    ssl on;
	    ssl_certificate /srv/www/example.com/ssl/example-wildcard.crt;
	    ssl_certificate_key /srv/www/example.com/ssl/example-wildcard.key;

	    server_name example.com;
	    access_log /var/log/nginx/example_access.log;
	    error_log /var/log/nginx/example_error.log;


		location /static/ {
			autoindex on;
			# absolute path to the django admin directory (this example shows a typical path if you are using a virtual env)
			root /home/yourname/virtualenvs/virtual-env-name/lib/python2.7/site-packages/django/contrib/admin;
		}

		location / {
			# header unchanged
			proxy_set_header Host $http_host;

			# i have no idea what these mean :/
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Scheme $scheme;
			# to allow the path portion of the url to pass through to the
			# proxy server, ensure there is NO trailing slash after the
			# proxy upstream.
			proxy_pass http://modernomad;

			proxy_pass_header Server;
			proxy_redirect off;

	       }
	}

