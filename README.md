# EV vs Combustão — Simulador de TCO

Mini produto em HTML + Tailwind + JavaScript puro para comparar custo total de propriedade (TCO) entre carro elétrico e combustão, pronto para deploy em GitHub Pages.

## Funcionalidades

- Simulação de TCO em **1, 5 e 10 anos**.
- Métricas: custo total EV/ICE, economia, payback, break-even mileage, ROI, CO₂ evitado.
- Inputs obrigatórios e avançados (seguro, manutenção, risco de troca de bateria).
- Sensibilidade com sliders para combustível, energia e quilometragem.
- IPVA por estado com incentivos locais (base JSON).
- Tarifa de energia por cidade/concessionária (base JSON).
- Busca opcional FIPE (API pública `parallelum.com.br`).
- Gráficos interativos com Chart.js.
- Interface mobile-first e dark mode.

## Estrutura

```txt
ev-vs-gas-calculator/
index.html
assets/
  css/style.css
  js/app.js
  js/calculator.js
  js/depreciation.js
  js/charts.js
  js/fipe.js
data/
  ipva_rates.json
  electricity_rates.json
  fuel_prices.json
  maintenance_costs.json
components/
  comparison-table.js
  charts.js
README.md
```

## Como rodar localmente

Como é estático, basta servir os arquivos por um servidor local:

```bash
python3 -m http.server 8080
```

Depois abra `http://localhost:8080`.

## Deploy no GitHub Pages

1. Faça push do repositório para GitHub.
2. Vá em **Settings → Pages**.
3. Em **Build and deployment**, selecione:
   - Source: **Deploy from a branch**
   - Branch: **main** (ou branch desejada), pasta **/** (root)
4. Salve e aguarde o link público ser gerado.

## Dados e integrações

- `data/*.json` contém bases estáticas editáveis.
- A integração FIPE é opcional e depende de disponibilidade do endpoint público.
- Para produção, recomenda-se pipeline de atualização automática para combustível/IPVA/tarifas.

## Próximas evoluções

- Landing pages SEO (ex.: `/byd-dolphin-vs-corolla`).
- Modo “Tesla vs Corolla” com presets.
- Quiz “Should I buy an EV?”.
- API de emissões mais detalhada e dados de recarga (OpenChargeMap).
