## Copilot / AI assistant notes for this repo

Purpose: quick orientation for code edits, tests and where business logic lives.

- **Project type**: Django app for mortgage/finance simulations (SAC, Price, consórcio, aluguel+investimento).

- **Two project roots**: there are two `manage.py` and `ImobCalc/settings.py` copies — one at repository root and one under `FI/`. Always confirm which `manage.py` / settings module your environment or CI uses before running commands or editing settings.

- **Quick dev commands** (choose the matching `manage.py`):
  - Run server: `python manage.py runserver` or `python FI/manage.py runserver`
  - Apply migrations: `python manage.py migrate`
  - Make migrations: `python manage.py makemigrations`
  - Run tests for the app: `python manage.py test simulacao`
  - Open Django shell for quick checks: `python manage.py shell`

- **No `requirements.txt` detected** in the repo root — verify the Python environment and install Django and other deps used by CI locally before running.

- **Core code / data-flow**
  - Input layer: `simulacao/forms.py` and `simulacao/wizard_forms.py` (user inputs, validation)
  - Controller / view: `simulacao/views.py` and `simulacao/wizard_views.py` (parse form, call calculation functions, prepare context)
  - Business logic: `simulacao/calculadora_financeira.py` — the authoritative location for calculations.
    - Key exported functions to call or test directly: `simular_financiamento_geral`, `calcular_price_sac`, `simular_consorcio`, `simular_aluguel_investimento`, `comparar_cenarios_e_formatar`.
    - Calculation functions accept numeric values (often as kwargs) and internally convert to `Decimal` — follow this pattern when adding numeric APIs.
  - Formatting utilities: `simulacao/formatacao.py` and local format helpers (e.g. `formatar_moeda_brl` inside `calculadora_financeira.py`).
  - Templates: see `simulacao/templates/simulacao/` (examples: `tabela_price.html`, `simulacao_sac.html`, `wizard_step.html`, `wizard_resultados.html`).

- **How to run and debug calculation logic quickly**
  - Use Django shell and import functions directly, e.g.:

    from simulacao.calculadora_financeira import simular_financiamento_geral
    simular_financiamento_geral('price', 300000, 7.0, 360)

  - Prefer unit-tests that call those functions directly rather than exercising full HTTP views for fast feedback.

- **Patterns & conventions**
  - Financial computations use `Decimal` for precision — ensure inputs are converted similarly when modifying or adding helpers.
  - Many functions accept `**kwargs` routing extra flags (e.g. FGTS handling) — follow existing argument names to avoid breaking callers from views.
  - Views call a single orchestrator (`comparar_cenarios_e_formatar`) which returns a context-ready, formatted result for templates. If adding outputs, keep the shape compatible with existing templates.

- **Testing and migrations**
  - Test module: `simulacao/tests.py` — add focused unit tests for pure-Python functions in `calculadora_financeira.py`.
  - DB: SQLite files exist at repo root (`db.sqlite3`) and under `FI/` — be intentional which DB file you use in local runs.

- **What to check before submitting changes**
  - Run `python manage.py test simulacao` after editing calculations.
  - If changing public API of calculation functions, update any callers in `views.py` and the template keys consumed by templates in `simulacao/templates/simulacao/`.
  - If touching settings, prefer editing the `ImobCalc/settings.py` that corresponds to the `manage.py` you run.

If any section is unclear or you'd like more examples (unit test snippets, common call signatures, or a short checklist for PR reviews), tell me which part to expand.
