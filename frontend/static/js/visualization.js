import Chart from 'chart.js/auto';

class SkinAnalysisVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.charts = {};
    }
    
    createSkinScoreChart(data) {
        const ctx = document.createElement('canvas');
        this.container.appendChild(ctx);
        
        this.charts.skinScore = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: '肤质评分',
                    data: data.scores,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    createMoistureOilChart(data) {
        const ctx = document.createElement('canvas');
        this.container.appendChild(ctx);
        
        this.charts.moistureOil = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: '水分含量',
                        data: data.moisture,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 1
                    },
                    {
                        label: '油脂含量',
                        data: data.oil,
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgb(255, 99, 132)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    createRadarChart(data) {
        const ctx = document.createElement('canvas');
        this.container.appendChild(ctx);
        
        this.charts.radar = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['水分', '油脂', '敏感度', '弹性', '光泽度'],
                datasets: [{
                    label: '当前状态',
                    data: [
                        data.moisture,
                        data.oil,
                        data.sensitivity,
                        data.elasticity,
                        data.brightness
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgb(54, 162, 235)',
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(54, 162, 235)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    createTrendChart(data) {
        const ctx = document.createElement('canvas');
        this.container.appendChild(ctx);
        
        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: '水分趋势',
                        data: data.moisture_trend,
                        borderColor: 'rgb(54, 162, 235)',
                        tension: 0.1
                    },
                    {
                        label: '油脂趋势',
                        data: data.oil_trend,
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1
                    },
                    {
                        label: '敏感度趋势',
                        data: data.sensitivity_trend,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    updateCharts(newData) {
        // 更新所有图表
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        
        this.charts = {};
        
        // 重新创建图表
        this.createSkinScoreChart(newData);
        this.createMoistureOilChart(newData);
        this.createRadarChart(newData);
        this.createTrendChart(newData);
    }
    
    createHeatmap(data) {
        const ctx = document.createElement('canvas');
        this.container.appendChild(ctx);
        
        this.charts.heatmap = new Chart(ctx, {
            type: 'heatmap',
            data: {
                datasets: [{
                    data: data.map(point => ({
                        x: point.x,
                        y: point.y,
                        v: point.value
                    })),
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgb(255, 99, 132)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom'
                    },
                    y: {
                        type: 'linear',
                        position: 'left'
                    }
                }
            }
        });
    }
    
    createComparisonChart(data) {
        const ctx = document.createElement('canvas');
        this.container.appendChild(ctx);
        
        this.charts.comparison = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['水分', '油脂', '敏感度', '弹性', '光泽度'],
                datasets: [
                    {
                        label: '当前状态',
                        data: data.current,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 1
                    },
                    {
                        label: '上次状态',
                        data: data.previous,
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgb(255, 99, 132)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}