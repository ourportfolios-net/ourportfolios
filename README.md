# **OurPortfolios**

SAP (Stock Analysis Platform) to help investors build their investment portfolios and developers build their work portfolios.

Check OurPortfolios out at [ourportfolios-lime-moon.reflex.run](https://ourportfolios-lime-moon.reflex.run)

---

### Running the frontend locally

This project uses **[uv](https://docs.astral.sh/uv)** for dependency and package management.

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/#pypi).

2. **Install all dependencies:**

   ```bash
   uv sync
   ```

3. [A PostgreSQL Database URI](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS) should then be provided through a `.env` file. Duplicate the `.env.template` file and paste your own Database URI. The database should then be reproducable with

   ```bash
   uv run python ourportfolios/utils/database/create_schema.py
   ```

   The database should then be populated with `add_ticker()` placed in the same file. Use a notebook or add it right below `create_schema.py` as well. For example, adding `FPT` to the database would look like this:

   ```python
   add_ticker("FPT", company_sync_engine, schema_name="tickers2"
   ```

4. **The Webapp should then be accessible with**
   ```bash
   uv run reflex run
   ```

---

### Credits

This project is maintained and owned by [Dank,](https://www.linkedin.com/in/hmdank) alongside with the help of [Phuc](https://github.com/Sevastopol12) and [Dang.](https://github.com/Vmoi-777) Feel free to contact us for anything, including bug reports, ideas for future features, or just somebody to talk to :DD
