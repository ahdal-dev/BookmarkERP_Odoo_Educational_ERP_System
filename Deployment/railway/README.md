# Railway service networking: Odoo and API Gateway

The API Gateway logs `Odoo service-account auth failed: [Errno -2] Name or service not known` when the hostname in `ODOO_URL` cannot be resolved. This is a DNS/service-discovery problem, not an Odoo password problem. In Railway, container names such as `odoo` are not automatically valid DNS names across services; connect over Railway's private network using Odoo's private domain.

## Configure the API Gateway service

1. Deploy the API Gateway as a separate Railway service in the same Railway project **and environment** as Odoo. Use `api_gateway/fastapi_app/Dockerfile` as its Dockerfile (with the repository root as the build context), and expose port `8000`.
2. In the API Gateway service's Variables, set `ODOO_URL` to Odoo's private domain and port. Railway private DNS uses the format `<service-name>.railway.internal`. The most robust option is to use Railway's variable-reference picker to reference the Odoo service's `RAILWAY_PRIVATE_DOMAIN`:

   ```text
   ODOO_URL=http://${{Odoo.RAILWAY_PRIVATE_DOMAIN}}:8081
   ```

   Replace `Odoo` in the reference with the exact Railway service name if yours differs. Alternatively, set the hostname directly, for example `http://odoo.railway.internal:8081` if that is the private domain shown for your Odoo service. Odoo listens on port `8081` in `Deployment/railway/odoo-start.sh`.
3. Set `ODOO_DB`, `ODOO_USERNAME`, and `ODOO_PASSWORD` to the database and service-account credentials configured for Odoo. Also configure the API Gateway's required `JWT_SECRET_KEY` and its Redis settings as appropriate.
4. Redeploy the API Gateway after saving the variable. Confirm the startup logs show `Odoo connection verified on startup`. If DNS resolution still fails, verify both services are deployed in the same Railway project and environment, and verify the Odoo service's actual `RAILWAY_PRIVATE_DOMAIN` value in Railway. Do not use Odoo's public URL for private service-to-service traffic.

The Gateway's source default (`http://odoo:8081`) only works where the service is actually reachable under the hostname `odoo` (for example, a configured Docker network). It does not discover another Railway service automatically. Set `ODOO_URL` explicitly on Railway.

The repeated startup messages in the reported logs are expected when Uvicorn starts multiple worker processes: each worker runs the FastAPI lifespan and attempts its own Odoo connection. They are symptoms of the same invalid or unresolvable `ODOO_URL`, not independent Redis or Odoo authentication failures.

## What the log does and does not establish

`[Errno -2] Name or service not known` means DNS lookup of the configured host failed before HTTP could reach Odoo. It does not indicate invalid Odoo credentials. Once the hostname resolves, a later error may reveal a separate port, network-listening, database, or credential issue.

Railway project/environment variables and service deployments are configured in the Railway dashboard and are not stored in this repository. Therefore, repository review can confirm the expected Odoo port and Gateway defaults, but cannot verify the actual Railway service names, environment variables, deployments, private-domain value, or network membership without dashboard access or the resolved (non-secret) `ODOO_URL` host and service configuration.
