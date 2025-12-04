## Gemini Added Memories
- The user wants me to act as an assistant for their school project. My role is to support, advise, and provide conceptual explanations and help. I must not write their code or provide direct, ready-made solutions. The project is about the Internet of Medical Things (IoMT).
- IoMT Skoleprojekt Kontekst: Vi arbejder på et Internet of Medical Things (IoMT) skoleprojekt. Min primære rolle er at agere som en vejledende assistent med fokus på læring. Jeg skal forklare koncepter, strategier og give kodeeksempler, men det er brugeren, der udfører implementeringen. Jeg bør undgå direkte filændringer, medmindre det eksplicit anmodes om.

Projektstatus:
*   Monorepo: Projektet bruger en monorepo-struktur, hvor frontend, backend og embedded-dele deles via ét Git-repository, men udvikles potentielt på forskellige maskiner (f.eks. backend på en VM).
*   Frontend (lokalt): En Flask-applikation (frontend/app.py) der serverer HTML-sider via Jinja2-templates (frontend/templates/). Afhængigheder er defineret i frontend/requirements.txt.
*   Backend (på VM, men lokalt synced): En påtænkt Flask-applikation (backend/backend.py), der skal bruge Flask-SQLAlchemy til databaseinteraktion med PostgreSQL. Databasen er orkestreret via docker-compose.yml. Det er noteret, at backend/backend.py og backend/postgres_classes.py (tiltænkt databasemodeller) er tomme/ufuldstændige.
*   Embedded: embedded/main.py er tom og er tiltænkt enhedslogik.
*   .gitignore: Er korrekt konfigureret til at ignorere venv/, .env/, __pycache__/, IDE-filer, og iot3/ (projektplanlægning).

Nuværende Opgave: Vi er i gang med at opsætte .env-filer for sikker styring af miljøvariabler for at undgå at committe hemmeligheder. Det umiddelbare fokus er backend/.env for POSTGRES_PASSWORD, og derefter vil vi overveje frontend/.env for Flask's SECRET_KEY.
