# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Point the server domain to localhost
GF_SERVER_DOMAIN=localhost

# Set Grafana know server URL
GF_SERVER_ROOT_URL=https://${domain_name}

# Session policies
GF_SESSION_COOKIE_SECURE=true
GF_SESSION_COOKIE_SAMESITE=lax

# Disable internal username/password authentication
GF_AUTH_BASIC_ENABLED=false

# Disable basic auth login form
GF_AUTH_DISABLE_LOGIN_FORM=true

# Cognito OAuth settings

# Enable OAuth
GF_AUTH_GENERIC_OAUTH_ENABLED=true

# Oauth service name
GF_AUTH_GENERIC_OAUTH_ENABLED_NAME=Cognito

# Allow Oauth sign-up (Grafana can add authorized users to the internal database)
GF_AUTH_GENERIC_OAUTH_ALLOW_SIGN_UP=true

# App client ID/Secret
GF_AUTH_GENERIC_OAUTH_CLIENT_ID=${client_id}
GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET=${client_secret}

# Information scope
GF_AUTH_GENERIC_OAUTH_SCOPES=email profile aws.cognito.signin.user.admin openid

# AWS Cognito OAuth endpoints
GF_AUTH_GENERIC_OAUTH_AUTH_URL=https://${user_pool_domain}.auth.${region}.amazoncognito.com/oauth2/authorize
GF_AUTH_GENERIC_OAUTH_TOKEN_URL=https://${user_pool_domain}.auth.${region}.amazoncognito.com/oauth2/token
GF_AUTH_GENERIC_OAUTH_API_URL=https://${user_pool_domain}.auth.${region}.amazoncognito.com/oauth2/userInfo


GF_AUTH_GENERIC_OAUTH_ROLE_ATTRIBUTE_PATH=(\"cognito:groups\" | contains([*], 'Admin') && 'Admin' || 'Viewer')

# Logout callback to redirect signout from Grafana to AWS Cognito OAuth signout
GF_AUTH_SIGNOUT_REDIRECT_URL=https://${user_pool_domain}.auth.${region}.amazoncognito.com/logout?client_id=${client_id}&logout_uri=https://${domain_name}/login
