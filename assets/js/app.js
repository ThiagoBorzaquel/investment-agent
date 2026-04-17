import { calculateTCO, formatBRL } from './calculator.js';
import { renderCharts } from './charts.js';
import { renderComparisonTable } from '../../components/comparison-table.js';
import { fetchBrands, fetchModels, fetchYears, fetchPrice } from './fipe.js';

const form = document.getElementById('tco-form');
const stateSelect = document.getElementById('state-select');
const resultsGrid = document.getElementById('results-grid');

const fuelAdjust = document.getElementById('fuel-adjust');
const energyAdjust = document.getElementById('energy-adjust');
const kmAdjust = document.getElementById('km-adjust');

const fuelLabel = document.getElementById('fuel-adjust-label');
const energyLabel = document.getElementById('energy-adjust-label');
const kmLabel = document.getElementById('km-adjust-label');

const themeToggle = document.getElementById('theme-toggle');

const fipeType = document.getElementById('fipeType');
const fipeBrand = document.getElementById('fipeBrand');
const fipeModel = document.getElementById('fipeModel');
const fipeOutput = document.getElementById('fipe-output');
const fipeButton = document.getElementById('fetch-fipe');

let ipvaRates = {};
let electricityRates = [];

init();

async function init() {
  await Promise.all([loadIpva(), loadElectricity(), populateFipeBrands()]);
  wireUi();
  runCalculation();
}

function wireUi() {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    runCalculation();
  });

  [fuelAdjust, energyAdjust, kmAdjust].forEach((slider) => {
    slider.addEventListener('input', () => {
      fuelLabel.textContent = `${fuelAdjust.value}%`;
      energyLabel.textContent = `${energyAdjust.value}%`;
      kmLabel.textContent = `${kmAdjust.value}%`;
      runCalculation();
    });
  });

  stateSelect.addEventListener('change', applyStateDefaults);

  themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
  });

  fipeType.addEventListener('change', populateFipeBrands);
  fipeBrand.addEventListener('change', populateFipeModels);
  fipeButton.addEventListener('click', applyFipePrice);
}

async function loadIpva() {
  ipvaRates = await fetch('./data/ipva_rates.json').then(r => r.json());
  const states = Object.keys(ipvaRates);
  stateSelect.innerHTML = states.map(uf => `<option value="${uf}">${uf} - ${ipvaRates[uf].stateName}</option>`).join('');
  stateSelect.value = 'SP';
}

async function loadElectricity() {
  electricityRates = await fetch('./data/electricity_rates.json').then(r => r.json());
  applyStateDefaults();
}

function applyStateDefaults() {
  const stateInfo = ipvaRates[stateSelect.value];
  if (!stateInfo) return;

  const energyInput = form.elements.energyPrice;
  const city = form.elements.city.value.trim().toLowerCase();
  const selectedRate = electricityRates.find(item => item.uf === stateSelect.value && item.city.toLowerCase() === city)
    || electricityRates.find(item => item.uf === stateSelect.value);

  if (selectedRate) {
    energyInput.value = selectedRate.rate;
  }
}

function getFormData() {
  const formData = new FormData(form);
  const raw = Object.fromEntries(formData.entries());
  const stateInfo = ipvaRates[raw.state] || { ipva_ice: 0.04, ipva_ev: 0.02, incentive: '' };

  return {
    ...raw,
    ipva: {
      evRate: stateInfo.ipva_ev,
      iceRate: stateInfo.ipva_ice,
      incentive: stateInfo.incentive
    },
    depreciation: {
      ev: { 1: 0.83, 5: 0.56, 10: 0.33 },
      ice: { 1: 0.86, 5: 0.52, 10: 0.29 }
    },
    co2: {
      fuelKgPerL: 2.31,
      gridKgPerKwh: 0.08
    }
  };
}

function runCalculation() {
  const inputs = getFormData();
  const result = calculateTCO(inputs);

  const metrics = [
    { title: 'Custo total EV', value: formatBRL(result.totals.ev) },
    { title: 'Custo total combustão', value: formatBRL(result.totals.ice) },
    { title: 'Economia EV', value: formatBRL(result.totals.savings) },
    { title: 'Payback', value: result.paybackYears ? `${result.paybackYears.toFixed(1)} anos` : 'Sem payback no cenário' },
    { title: 'Break-even mileage', value: result.breakEvenKm ? `${Math.round(result.breakEvenKm).toLocaleString('pt-BR')} km` : 'N/A' },
    { title: 'ROI diferença inicial', value: result.roi ? `${result.roi.toFixed(1)}%` : 'N/A' },
    { title: 'CO₂ evitado', value: `${(result.co2AvoidedKg / 1000).toFixed(2)} t` },
    { title: 'Incentivo estadual', value: inputs.ipva.incentive || 'Sem incentivo registrado' }
  ];

  resultsGrid.innerHTML = metrics.map(metric => `
    <div class="metric-card">
      <p class="metric-title">${metric.title}</p>
      <p class="metric-value">${metric.value}</p>
    </div>
  `).join('');

  renderComparisonTable(result, inputs);
  renderCharts(result);
}

async function populateFipeBrands() {
  const type = fipeType.value;
  try {
    const brands = await fetchBrands(type);
    fipeBrand.innerHTML = brands.map(item => `<option value="${item.codigo}">${item.nome}</option>`).join('');
    await populateFipeModels();
  } catch (error) {
    fipeOutput.textContent = `Erro FIPE: ${error.message}`;
  }
}

async function populateFipeModels() {
  const type = fipeType.value;
  try {
    const payload = await fetchModels(type, fipeBrand.value);
    fipeModel.innerHTML = payload.modelos.slice(0, 80).map(item => `<option value="${item.codigo}">${item.nome}</option>`).join('');
  } catch (error) {
    fipeOutput.textContent = `Erro FIPE: ${error.message}`;
  }
}

async function applyFipePrice() {
  const type = fipeType.value;
  try {
    const years = await fetchYears(type, fipeBrand.value, fipeModel.value);
    const year = years.find(y => y.codigo.includes('2024')) || years[0];
    const info = await fetchPrice(type, fipeBrand.value, fipeModel.value, year.codigo);

    fipeOutput.textContent = `FIPE ${info.Marca} ${info.Modelo} (${info.AnoModelo}): ${info.Valor}. Use como referência para preço de compra/revenda.`;
  } catch (error) {
    fipeOutput.textContent = `Erro FIPE: ${error.message}`;
  }
}
