# Solenis – Reporte pH Descarga (Streamlit)

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud (GRATIS)

1. Sube este proyecto a un repositorio de **GitHub**
2. Ve a **share.streamlit.io** e inicia sesión con GitHub
3. Haz clic en **"New app"**
4. Selecciona tu repositorio, rama `main` y archivo `app.py`
5. En **"Advanced settings → Secrets"** agrega:
   ```toml
   SUPABASE_URL = "https://tu-proyecto.supabase.co"
   SUPABASE_KEY = "tu-anon-key"
   ```
6. Haz clic en **Deploy** — en 2 minutos está en línea con URL pública

## Estructura
```
solenis_streamlit/
├── app.py                  # App principal
├── solenis_logo.png        # Logo Solenis
├── requirements.txt        # Dependencias
└── .streamlit/
    └── secrets.toml        # Credenciales (NO subir a GitHub)
```

## ⚠️ Importante
- Agrega `.streamlit/secrets.toml` a tu `.gitignore` para no exponer credenciales
- Las credenciales en Streamlit Cloud se configuran desde la interfaz web, no desde el archivo
