const FIPE_BASE = 'https://parallelum.com.br/fipe/api/v1';

export async function fetchBrands(vehicleType = 'carros') {
  const res = await fetch(`${FIPE_BASE}/${vehicleType}/marcas`);
  if (!res.ok) throw new Error('Falha ao carregar marcas FIPE.');
  return res.json();
}

export async function fetchModels(vehicleType, brandCode) {
  const res = await fetch(`${FIPE_BASE}/${vehicleType}/marcas/${brandCode}/modelos`);
  if (!res.ok) throw new Error('Falha ao carregar modelos FIPE.');
  return res.json();
}

export async function fetchYears(vehicleType, brandCode, modelCode) {
  const res = await fetch(`${FIPE_BASE}/${vehicleType}/marcas/${brandCode}/modelos/${modelCode}/anos`);
  if (!res.ok) throw new Error('Falha ao carregar anos FIPE.');
  return res.json();
}

export async function fetchPrice(vehicleType, brandCode, modelCode, yearCode) {
  const res = await fetch(`${FIPE_BASE}/${vehicleType}/marcas/${brandCode}/modelos/${modelCode}/anos/${yearCode}`);
  if (!res.ok) throw new Error('Falha ao carregar preço FIPE.');
  return res.json();
}
