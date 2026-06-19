# Odoo Backend Refactoring Guide — Bookmark Academic ERP

This document outlines the required backend changes to decouple the Odoo modules from the custom XML-based frontend, now replaced by the Bookmark React application.

> [!CAUTION]
> These changes are **irreversible** once applied to a production database. Always back up your database before proceeding.

---

## 1. Uninstall & Delete `edu_mang_website` Module

The `edu_mang_website` module contains the XML dashboards and custom login page that the React frontend replaces entirely.

### Step 1: Uninstall from Odoo

```python
# Via Odoo Shell (python odoo-bin shell -d edu_demo_new)
module = env['ir.module.module'].search([('name', '=', 'edu_mang_website')])
if module and module.state == 'installed':
    module.button_immediate_uninstall()
    env.cr.commit()
    print("edu_mang_website uninstalled successfully")
```

Or via Odoo Admin UI: **Settings → Apps → Search "Educational ERP Website Portal" → Uninstall**

### Step 2: Remove Files

Delete the entire module directory:

```bash
rm -rf addons/edu_mangment/edu_mang_website/
```

**Files deleted:**
- `views/login_templates.xml` — Custom Odoo login page
- `views/dashboard_templates.xml` — Student/Officer/Admin XML dashboards
- `controllers/main.py` — `/web/login` override + `/edu/login` route
- `controllers/dashboards.py` — Dashboard route controllers
- `static/src/css/dashboard.css` — Dashboard styles

### Step 3: Update Dependent Modules

`edu_portal_gateway` depends on `edu_mang_website` indirectly. Check its `__manifest__.py` dependencies and remove `edu_mang_website` if listed. Currently `edu_portal_gateway` depends on:
- `edu_mang_auth` ✅ (keep)
- `edu_mang_admission` ✅ (keep)
- `edu_mang_petition` ✅ (keep)
- `custom_registration` ✅ (keep)

No direct dependency on `edu_mang_website` — safe to delete.

---

## 2. Detach Custom Login from Odoo Web

The `edu_mang_website` controller overrides `/web/login` (line 74 of `controllers/main.py`) to redirect all logins to the custom page. After uninstalling `edu_mang_website`, Odoo's native `/web/login` will be restored automatically.

### Verify Native Login Works

After uninstalling, verify that:
1. `http://localhost:8069/web/login` shows the standard Odoo login form
2. Admin users can still log into the native Odoo backend

### Keep `edu_mang_auth` JSON APIs

The pure auth controller at `addons/edu_mangment/edu_mang_auth/controllers/auth.py` provides these JSON API endpoints that the React frontend uses via the API Gateway:

| Endpoint | Purpose |
|---|---|
| `/edu/api/session` | Check session status |
| `/edu/api/user_roles` | Get user roles |
| `/edu/api/logout` | Logout user |

These do **NOT** depend on the website module — keep them intact.

---

## 3. New FastAPI Gateway Endpoints

Add these endpoints to `api_gateway/fastapi_app/main.py`:

### 3.1 Login Endpoint (Odoo Session → JWT)

```python
class LoginRequest(BaseModel):
    login: str
    password: str
    db: str = "edu_demo_new"

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """
    Authenticate via Odoo session, then issue a JWT token.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            auth_url = f"{ODOO_URL}/web/session/authenticate"
            payload = {
                "jsonrpc": "2.0",
                "params": {
                    "db": request.db,
                    "login": request.login,
                    "password": request.password,
                }
            }
            response = await client.post(auth_url, json=payload)
            result = response.json()
            
            if "result" in result and result["result"].get("uid"):
                uid = result["result"]["uid"]
                user_name = result["result"].get("name", request.login)
                
                # Issue JWT
                jwt_payload = {
                    "user_id": uid,
                    "username": request.login,
                    "email": request.login,
                    "role": "admin",  # Determine from Odoo groups
                    "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
                }
                token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
                
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user_id": uid,
                    "user_name": user_name,
                    "expires_in": JWT_EXPIRATION_HOURS * 3600,
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")
```

### 3.2 Session Check Endpoint

```python
@app.get("/api/v1/auth/session")
async def check_session(
    user: TokenData = Depends(RBACChecker([
        UserRole.PROSPECTIVE_STUDENT,
        UserRole.ADMISSION_STAFF,
        UserRole.ADMIN,
        UserRole.SYSTEM
    ]))
):
    """Validate current JWT token and return user info."""
    return {
        "valid": True,
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
    }
```

### 3.3 Module Management Endpoints

```python
@app.get("/api/v1/admin/modules")
async def list_modules(
    user: TokenData = Depends(RBACChecker([UserRole.ADMIN, UserRole.SYSTEM]))
):
    """List available Odoo modules."""
    await odoo_client.authenticate()
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "ir.module.module",
                "method": "search_read",
                "args": [[["state", "in", ["installed", "uninstalled"]]]],
                "kwargs": {
                    "fields": ["name", "shortdesc", "state", "summary"],
                    "limit": 200,
                }
            }
        }
        response = await client.post(f"{ODOO_URL}/web/dataset/call_kw", json=payload)
        return response.json().get("result", [])


class InstallModuleRequest(BaseModel):
    module_name: str

@app.post("/api/v1/admin/modules/install")
async def install_module(
    request: InstallModuleRequest,
    user: TokenData = Depends(RBACChecker([UserRole.ADMIN, UserRole.SYSTEM]))
):
    """Install an Odoo module by technical name."""
    await odoo_client.authenticate()
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Find the module
        search_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "ir.module.module",
                "method": "search_read",
                "args": [[["name", "=", request.module_name]]],
                "kwargs": {"fields": ["id", "state"], "limit": 1}
            }
        }
        search_resp = await client.post(f"{ODOO_URL}/web/dataset/call_kw", json=search_payload)
        modules = search_resp.json().get("result", [])
        
        if not modules:
            raise HTTPException(status_code=404, detail=f"Module '{request.module_name}' not found")
        
        module = modules[0]
        if module["state"] == "installed":
            return {"success": True, "message": f"Module '{request.module_name}' is already installed"}
        
        # Install the module
        install_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "ir.module.module",
                "method": "button_immediate_install",
                "args": [[module["id"]]],
                "kwargs": {}
            }
        }
        await client.post(f"{ODOO_URL}/web/dataset/call_kw", json=install_payload)
        return {"success": True, "message": f"Module '{request.module_name}' installed successfully"}
```

---

## 4. Fallback Backend Views

Ensure all custom modules have native Odoo tree/form views for backend administration.

### Module View Status

| Module | Has Backend Views? | Action Needed |
|---|---|---|
| `edu_mang_auth` | ❌ No views (security groups only) | Create basic group management views |
| `edu_mang_admission` | ✅ `admission_views.xml` | None |
| `edu_mang_petition` | ✅ `petition_views.xml` + menus | None |
| `custom_registration` | ⚠️ Has website templates, no backend views | Add tree/form views for admin |
| `edu_portal_gateway` | ⚠️ Has portal templates, no model views | Verify menu accessibility |

### 4.1 Add Backend Views for `custom_registration`

Create `addons/edu_mangment/custom_registration/views/backend_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Course Tree View -->
    <record id="view_course_tree" model="ir.ui.view">
        <field name="name">course.tree</field>
        <field name="model">registration.course</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="code"/>
                <field name="instructor_id"/>
                <field name="seats_available"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

    <!-- Course Form View -->
    <record id="view_course_form" model="ir.ui.view">
        <field name="name">course.form</field>
        <field name="model">registration.course</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="code"/>
                        </group>
                        <group>
                            <field name="instructor_id"/>
                            <field name="seats_available"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Menu and Action -->
    <record id="action_course" model="ir.actions.act_window">
        <field name="name">Courses</field>
        <field name="res_model">registration.course</field>
        <field name="view_mode">tree,form</field>
    </record>

    <menuitem id="menu_registration_root" name="Registration" sequence="30"/>
    <menuitem id="menu_courses" name="Courses" parent="menu_registration_root" action="action_course"/>
</odoo>
```

Then add this to the `data` list in `custom_registration/__manifest__.py`.

---

## 5. CORS Configuration

Update the FastAPI CORS middleware in `api_gateway/fastapi_app/main.py` to allow the React dev server:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",       # Alternative dev port
        "https://your-production-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6. Docker Compose Update

Add the React frontend as a new service in `api_gateway/docker-compose.yml`:

```yaml
  # React Frontend
  frontend:
    build:
      context: ../bookmark-frontend
      dockerfile: Dockerfile
    container_name: edu_erp_frontend
    restart: unless-stopped
    ports:
      - "3001:80"
    networks:
      - frontend
    depends_on:
      - nginx
    labels:
      - "com.edu-erp.service=react-frontend"
      - "com.edu-erp.layer=frontend"
```

Create `bookmark-frontend/Dockerfile` for production:

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Summary Checklist

- [ ] Back up database
- [ ] Uninstall `edu_mang_website` module from Odoo
- [ ] Delete `addons/edu_mangment/edu_mang_website/` directory
- [ ] Verify native Odoo login at `/web/login` works
- [ ] Add new auth/modules endpoints to FastAPI gateway
- [ ] Update CORS origins in FastAPI
- [ ] Add backend views for `custom_registration`
- [ ] Verify all modules are accessible from native Odoo backend
- [ ] Deploy React frontend
- [ ] Test end-to-end: React Login → JWT → Dashboard → Backend link
