let evolutionChart;
let breakdownChart;

export function renderCharts(result) {
  renderEvolution(result);
  renderBreakdown(result);
}

function renderEvolution(result) {
  const ctx = document.getElementById('costEvolutionChart');
  if (evolutionChart) evolutionChart.destroy();

  evolutionChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: result.annualSeries.map(item => `Ano ${item.year}`),
      datasets: [
        {
          label: 'EV',
          data: result.annualSeries.map(item => item.ev),
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34,197,94,0.2)',
          tension: 0.35
        },
        {
          label: 'Combustão',
          data: result.annualSeries.map(item => item.ice),
          borderColor: '#f97316',
          backgroundColor: 'rgba(249,115,22,0.2)',
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: 'Evolução acumulada de custos' }
      }
    }
  });
}

function renderBreakdown(result) {
  const ctx = document.getElementById('costBreakdownChart');
  if (breakdownChart) breakdownChart.destroy();

  breakdownChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Energia/Combustível', 'IPVA', 'Seguro', 'Manutenção', 'Bateria (risco)'],
      datasets: [
        {
          label: 'EV',
          data: [
            result.breakdown.ev.energia,
            result.breakdown.ev.ipva,
            result.breakdown.ev.seguro,
            result.breakdown.ev.manutencao,
            result.breakdown.ev.bateria
          ],
          backgroundColor: '#22c55e'
        },
        {
          label: 'Combustão',
          data: [
            result.breakdown.ice.combustivel,
            result.breakdown.ice.ipva,
            result.breakdown.ice.seguro,
            result.breakdown.ice.manutencao,
            0
          ],
          backgroundColor: '#f97316'
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: 'Breakdown de custos no horizonte' }
      }
    }
  });
}
