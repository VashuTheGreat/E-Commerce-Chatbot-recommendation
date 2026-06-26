# Build Frontend From FastAPI Routes

Load the skill:

fastapi_frontend

Your task:

1. Analyze the FastAPI project.

2. Find all APIRouter instances.

3. Find all routes.

4. Identify:

   * GET endpoints
   * POST endpoints
   * PUT endpoints
   * DELETE endpoints

5. Determine which routes require UI pages.

6. Create:

```text
templates/
static/js/constants.js
static/js/api.js
page specific js files
```

7. Store all API URLs inside:

```javascript
API_ENDPOINTS
```

8. Never hardcode URLs.

9. Use TailwindCSS.

10. Avoid inline JavaScript.

11. Create maintainable FastAPI + Jinja2 frontend.

12. Reuse components when possible.

13. For every generated page provide:

* HTML template
* Required JS file
* Required API functions
* Required constants

14. Before generating code provide a short implementation plan.

Analyze the entire repository before generating code.
