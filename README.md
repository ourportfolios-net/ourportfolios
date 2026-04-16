# **OurPortfolios**

SAP (Stock Analysis Platform) to help investors build their investment portfolios and developers build their work portfolios.

Check OurPortfolios out at [ourportfolios.net](https://ourportfolios.net)

---

### Running the frontend locally

This project uses **[uv](https://docs.astral.sh/uv)** for dependency and package management.

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/#pypi).

2. **Install all dependencies:**

   ```bash
   uv sync
   ```

3. [A PostgreSQL Database URI](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS) should then be provided through a `.env` file. Duplicate the `.env.template` file and paste your own Database URI.

   **If using a connection pooler** (e.g. Supabase Transaction Pooler, pgbouncer), use the **transaction mode** endpoint and run the following SQL once on your database:

   ```sql
   ALTER ROLE postgres SET jit = off;
   ALTER ROLE postgres SET statement_timeout = '20s';
   ```

   These must be set at the role level because pgbouncer resets session state between transactions. For more details, see [Properly connecting with a database on serverless](https://activeno.de/blog/2025-06/properly-connecting-with-a-database-on-serverless/).

   The schema can then be created and kept up to date with Alembic:

   ```bash
   uv run alembic upgrade head
   ```

4. **The Webapp should then be accessible with**
   ```bash
   uv run reflex run
   ```

---

### Credits

This project is maintained and owned by [Dank,](https://www.linkedin.com/in/hmdank) alongside with the help of [Phuc](https://github.com/Sevastopol12) and [Dang.](https://github.com/Vmoi-777) Feel free to contact us for anything, including bug reports, ideas for future features, or just somebody to talk to :DD
