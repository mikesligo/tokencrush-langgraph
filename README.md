## tokencrush-langraph

LangGraph module that wraps the TokenCrush `/v1/crush` API.

### Install (dev)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip build
pip install -e .
```

### Usage
```bash
export TOKENCRUSH_API_KEY="your-tokencrush-api-key"
python examples/simple_crush.py
```

### API
- `build_tokencrush_graph(api_key, base_url=None, fallback_to_input=False) -> CompiledGraph`
- `crush(api_key, prompt, base_url=None, fallback_to_input=False) -> dict`


