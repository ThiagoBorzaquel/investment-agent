import { formatBRL } from '../assets/js/calculator.js';

export function renderComparisonTable(result) {
  const host = document.getElementById('comparison-table');
  const rows = [
    ['Compra', result.breakdown.ev.compra, result.breakdown.ice.compra],
    ['Revenda projetada', result.breakdown.ev.revenda, result.breakdown.ice.revenda],
    ['Energia / Combustível', result.breakdown.ev.energia, result.breakdown.ice.combustivel],
    ['IPVA', result.breakdown.ev.ipva, result.breakdown.ice.ipva],
    ['Seguro', result.breakdown.ev.seguro, result.breakdown.ice.seguro],
    ['Manutenção', result.breakdown.ev.manutencao, result.breakdown.ice.manutencao],
    ['Bateria (risco)', result.breakdown.ev.bateria, 0],
    ['TOTAL', result.totals.ev, result.totals.ice]
  ];

  host.innerHTML = `
    <div class="overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead>
          <tr class="text-left border-b border-slate-300 dark:border-slate-700">
            <th class="py-2 pr-4">Categoria</th>
            <th class="py-2 pr-4">EV</th>
            <th class="py-2 pr-4">Combustão</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map(([name, ev, ice]) => `
            <tr class="border-b border-slate-200/60 dark:border-slate-700/40">
              <td class="py-2 pr-4 font-medium">${name}</td>
              <td class="py-2 pr-4">${formatBRL(ev)}</td>
              <td class="py-2 pr-4">${formatBRL(ice)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}
