# Trust Game Demo Analysis

A Streamlit webapp that accesses the same database as the [Trust Game Demo](https://github.com/cosanlab/trust-game) allowing for quick real-time analysis and data viz

## Setting up for local development

1. `pip install -r requirements.txt` in your current or a new Python environment
2. From the firebase project console make sure to download a new service account key. 
3. Run `python key-to-toml.py`
4. Run `streamlit run app.py` and navigate to `localhost:8501` in your browser