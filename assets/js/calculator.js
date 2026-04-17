import { projectResaleValue, expectedBatteryCost } from './depreciation.js';

export function calculateTCO(inputs) {
  const years = Number(inputs.horizonYears);
  const annualKmAdjusted = Number(inputs.annualKm) * (1 + Number(inputs.kmVariationPct) / 100);
  const fuelPriceAdjusted = Number(inputs.fuelPrice) * (1 + Number(inputs.fuelIncreasePct) / 100);
  const energyPriceAdjusted = Number(inputs.energyPrice) * (1 + Number(inputs.energyIncreasePct) / 100);

  const evPurchase = Number(inputs.evPrice);
  const icePurchase = Number(inputs.icePrice);

  const evResale = projectResaleValue(evPurchase, years, inputs.depreciation.ev);
  const iceResale = projectResaleValue(icePurchase, years, inputs.depreciation.ice);

  const evEnergyCost = (annualKmAdjusted / Number(inputs.evEfficiency)) * energyPriceAdjusted * years;
  const iceFuelCost = (annualKmAdjusted / Number(inputs.iceEfficiency)) * fuelPriceAdjusted * years;

  const evIpva = evPurchase * Number(inputs.ipva.evRate) * years;
  const iceIpva = icePurchase * Number(inputs.ipva.iceRate) * years;

  const evInsurance = evPurchase * (Number(inputs.evInsurancePct) / 100) * years;
  const iceInsurance = icePurchase * (Number(inputs.iceInsurancePct) / 100) * years;

  const evMaintenance = Number(inputs.evMaintenanceAnnual) * years;
  const iceMaintenance = Number(inputs.iceMaintenanceAnnual) * years;

  const batteryRiskCost = expectedBatteryCost(
    Number(inputs.batteryReplacementCost),
    Number(inputs.batteryReplacementProbability) / 100,
    years
  );

  const evTotal = evPurchase - evResale + evEnergyCost + evIpva + evInsurance + evMaintenance + batteryRiskCost;
  const iceTotal = icePurchase - iceResale + iceFuelCost + iceIpva + iceInsurance + iceMaintenance;

  const savings = iceTotal - evTotal;
  const initialGap = evPurchase - icePurchase;
  const annualOperationalEV = evEnergyCost / years + evIpva / years + evInsurance / years + evMaintenance / years;
  const annualOperationalICE = iceFuelCost / years + iceIpva / years + iceInsurance / years + iceMaintenance / years;

  const annualOperationalSavings = annualOperationalICE - annualOperationalEV;
  const paybackYears = annualOperationalSavings > 0 ? initialGap / annualOperationalSavings : null;

  const breakEvenKm = annualOperationalSavings > 0
    ? (initialGap / annualOperationalSavings) * annualKmAdjusted
    : null;

  const roi = initialGap > 0 ? (savings / initialGap) * 100 : null;

  const co2AvoidedKg = ((annualKmAdjusted / Number(inputs.iceEfficiency)) * Number(inputs.co2.fuelKgPerL) -
    (annualKmAdjusted / Number(inputs.evEfficiency)) * Number(inputs.co2.gridKgPerKwh)) * years;

  return {
    years,
    totals: { ev: evTotal, ice: iceTotal, savings },
    paybackYears,
    breakEvenKm,
    roi,
    co2AvoidedKg,
    adjusted: {
      annualKmAdjusted,
      fuelPriceAdjusted,
      energyPriceAdjusted
    },
    breakdown: {
      ev: {
        compra: evPurchase,
        revenda: -evResale,
        energia: evEnergyCost,
        ipva: evIpva,
        seguro: evInsurance,
        manutencao: evMaintenance,
        bateria: batteryRiskCost
      },
      ice: {
        compra: icePurchase,
        revenda: -iceResale,
        combustivel: iceFuelCost,
        ipva: iceIpva,
        seguro: iceInsurance,
        manutencao: iceMaintenance
      }
    },
    annualSeries: buildAnnualSeries(inputs, years)
  };
}

function buildAnnualSeries(inputs, years) {
  const list = [];
  for (let year = 1; year <= years; year += 1) {
    const partialInputs = { ...inputs, horizonYears: year };
    const partial = calculateTCOWithoutSeries(partialInputs);
    list.push({ year, ev: partial.ev, ice: partial.ice });
  }
  return list;
}

function calculateTCOWithoutSeries(inputs) {
  const years = Number(inputs.horizonYears);
  const annualKmAdjusted = Number(inputs.annualKm) * (1 + Number(inputs.kmVariationPct) / 100);
  const fuelPriceAdjusted = Number(inputs.fuelPrice) * (1 + Number(inputs.fuelIncreasePct) / 100);
  const energyPriceAdjusted = Number(inputs.energyPrice) * (1 + Number(inputs.energyIncreasePct) / 100);

  const evPurchase = Number(inputs.evPrice);
  const icePurchase = Number(inputs.icePrice);

  const evResale = projectResaleValue(evPurchase, years, inputs.depreciation.ev);
  const iceResale = projectResaleValue(icePurchase, years, inputs.depreciation.ice);

  const evEnergyCost = (annualKmAdjusted / Number(inputs.evEfficiency)) * energyPriceAdjusted * years;
  const iceFuelCost = (annualKmAdjusted / Number(inputs.iceEfficiency)) * fuelPriceAdjusted * years;

  const evIpva = evPurchase * Number(inputs.ipva.evRate) * years;
  const iceIpva = icePurchase * Number(inputs.ipva.iceRate) * years;

  const evInsurance = evPurchase * (Number(inputs.evInsurancePct) / 100) * years;
  const iceInsurance = icePurchase * (Number(inputs.iceInsurancePct) / 100) * years;

  const evMaintenance = Number(inputs.evMaintenanceAnnual) * years;
  const iceMaintenance = Number(inputs.iceMaintenanceAnnual) * years;

  const batteryRiskCost = expectedBatteryCost(
    Number(inputs.batteryReplacementCost),
    Number(inputs.batteryReplacementProbability) / 100,
    years
  );

  return {
    ev: evPurchase - evResale + evEnergyCost + evIpva + evInsurance + evMaintenance + batteryRiskCost,
    ice: icePurchase - iceResale + iceFuelCost + iceIpva + iceInsurance + iceMaintenance
  };
}

export function formatBRL(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);
}
