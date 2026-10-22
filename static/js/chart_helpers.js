/*
 * static/js/chart_helpers.js
 * Shared helpers for the Chart.js doughnut charts:
 *   - percentLabels : draws the percentage on every slice
 *   - percentTooltip: tooltip shows "label: count (xx.x%)"
 *   - linkSlices(urls): makes slices clickable (opens urls[sliceIndex])
 *   - PALETTE       : enough distinct colours for all disease classes
 */
(function (global) {
    const PALETTE = [
        '#2e7d32', '#c62828', '#1565c0', '#ef6c00', '#6a1b9a', '#00897b',
        '#ad1457', '#5d4037', '#546e7a', '#9e9d24', '#00acc1'
    ];

    // Sum of the slices that are currently visible (legend items can be toggled off)
    function visibleTotal(chart) {
        const data = chart.data.datasets[0].data;
        return data.reduce((sum, v, i) => sum + (chart.getDataVisibility(i) ? v : 0), 0);
    }

    function fmtPercent(value, total) {
        if (!total) return '0%';
        const pct = (value * 100) / total;
        return (Math.round(pct * 10) / 10) + '%';   // 33.3%, 50%, 4.2%
    }

    const percentLabels = {
        id: 'percentLabels',
        afterDatasetsDraw(chart) {
            const total = visibleTotal(chart);
            if (!total) return;
            const ctx = chart.ctx;
            const values = chart.data.datasets[0].data;
            chart.getDatasetMeta(0).data.forEach((arc, i) => {
                if (!chart.getDataVisibility(i) || !values[i]) return;
                if ((values[i] * 100) / total < 4) return;      // too thin to fit text
                const pos = arc.tooltipPosition();
                ctx.save();
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 12px sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.shadowColor = 'rgba(0,0,0,0.5)';
                ctx.shadowBlur = 3;
                ctx.fillText(fmtPercent(values[i], total), pos.x, pos.y);
                ctx.restore();
            });
        }
    };

    const percentTooltip = {
        callbacks: {
            label(item) {
                const total = visibleTotal(item.chart);
                return ' ' + item.label + ': ' + item.parsed + ' (' + fmtPercent(item.parsed, total) + ')';
            }
        }
    };

    // Chart options that make each slice a link to urls[index]
    function linkSlices(urls) {
        return {
            onClick(evt, elements) {
                if (elements.length && urls[elements[0].index]) {
                    window.location.href = urls[elements[0].index];
                }
            },
            onHover(evt, elements) {
                evt.native.target.style.cursor = elements.length ? 'pointer' : 'default';
            }
        };
    }

    global.ChartHelpers = { PALETTE, percentLabels, percentTooltip, linkSlices };
})(window);
