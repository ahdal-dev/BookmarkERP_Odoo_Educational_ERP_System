# Railway service networking: Odoo and API Gateway

The API Gateway logs `Odoo service-account auth failed: [Errno -2] Name or service not known` when its `ODOO_URL` hostname cannot be resolved. This is a DNS/service-discovery problem, not an Odoo password problem. In Railway, container names such as `odoo` are not automatically valid DNS names across services; the services must communicate over Railway's private network using Odoo's private domain.

## Configure the API Gateway service

1. Deploy the API Gateway as a separate Railway service in the same Railway project and environment as Odoo. Use `api_gateway/fastapi_app/Dockerfile` as its Dockerfile (with the repository root as the build context), and expose port `8000`.
2. In the API Gateway service's Variables, set `ODOO_URL` to Odoo's private domain and port. Prefer Railway's variable-reference picker to reference the Odoo service's `RAILWAY_PRIVATE_DOMAIN`, so renaming or changing its private domain does not leave a stale hostname:

   ```text
   ODOO_URL=http://${{Odoo.RAILWAY_PRIVATE_DOMAIN}}:8081
   ```

   Replace `Odoo` in the reference with the exact Railway service name if yours differs. Odoo listens on port `8081` in `Deployment/railway/odoo-start.sh`.
3. Set `ODOO_DB`, `ODOO_USERNAME`, and `ODOO_PASSWORD` to the database and service-account credentials configured for Odoo. Also configure the API Gateway's required `JWT_SECRET_KEY` and its Redis settings as appropriate.
4. Redeploy the API Gateway after saving the variable. Confirm the startup logs show `Odoo connection verified on startup`. If DNS resolution still fails, verify both services are in the same Railway project and environment and inspect the resolved Odoo private domain in Railway; do not use Odoo's public URL for private service-to-service traffic.

The Gateway's source defaults (`http://odoo:8081`) are for deployments where the service is actually reachable under the hostname `odoo` (for example, a configured container network). They do not discover another Railway service automatically. Set `ODOO_URL` explicitly on Railway.

The repeated startup messages in the reported logs are expected when Uvicorn starts multiple worker processes: each worker runs the FastAPI lifespan and attempts its own Odoo connection. They are symptoms of the same invalid/unresolvable `ODOO_URL`, not independent Redis or Odoo authentication failures.
