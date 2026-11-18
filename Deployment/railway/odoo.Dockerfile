# Odoo 19 with the project's custom addons, for Railway.
# Build context: repository root. Set RAILWAY_DOCKERFILE_PATH=Deployment/railway/odoo.Dockerfile
FROM odoo:19.0
USER root
COPY addons/edu_mangment /mnt/extra-addons/edu_mangment
COPY addons/open_edu_cat /mnt/extra-addons/open_edu_cat
COPY Deployment/railway/odoo-start.sh /usr/local/bin/odoo-start.sh
RUN chmod +x /usr/local/bin/odoo-start.sh && chown -R odoo:odoo /mnt/extra-addons
USER odoo
ENTRYPOINT ["/usr/local/bin/odoo-start.sh"]
