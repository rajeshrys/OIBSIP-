// Retail Sales Analytics Dashboard Logic

let charts = {};

document.addEventListener('DOMContentLoaded', () => {
    initFilters();
    loadDashboardData();
    loadTransactions();
});

function initFilters() {
    const filterIds = ['filterCategory', 'filterGender', 'filterAgeGroup', 'filterYear'];
    filterIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => {
                loadDashboardData();
            });
        }
    });

    const resetBtn = document.getElementById('resetFiltersBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            document.getElementById('filterCategory').value = 'All';
            document.getElementById('filterGender').value = 'All';
            document.getElementById('filterAgeGroup').value = 'All';
            document.getElementById('filterYear').value = '0';
            loadDashboardData();
        });
    }
}

function getFilterParams() {
    const category = document.getElementById('filterCategory')?.value || 'All';
    const gender = document.getElementById('filterGender')?.value || 'All';
    const ageGroup = document.getElementById('filterAgeGroup')?.value || 'All';
    const year = document.getElementById('filterYear')?.value || '0';

    const params = new URLSearchParams();
    if (category !== 'All') params.append('category', category);
    if (gender !== 'All') params.append('gender', gender);
    if (ageGroup !== 'All') params.append('age_group', ageGroup);
    if (year !== '0') params.append('year', year);

    return params.toString();
}

async function loadDashboardData() {
    const queryString = getFilterParams();
    const query = queryString ? `?${queryString}` : '';

    try {
        await Promise.all([
            fetchKPIs(query),
            fetchTrends(query),
            fetchCategories(query),
            fetchDemographics(query),
            fetchTopProducts(query),
            fetchDiscountInsight()
        ]);
    } catch (err) {
        console.error("Error loading dashboard metrics:", err);
    }
}

// 1. Fetch KPIs
async function fetchKPIs(query) {
    const res = await fetch(`/api/kpis${query}`);
    const data = await res.json();

    document.getElementById('kpiRevenue').textContent = `$${data.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('kpiProfit').textContent = `$${data.total_profit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('kpiMargin').textContent = `Avg Margin: ${data.average_profit_margin}%`;
    document.getElementById('kpiOrders').textContent = data.total_orders.toLocaleString();
    document.getElementById('kpiUnits').textContent = `Units Sold: ${data.total_units_sold.toLocaleString()}`;
    document.getElementById('kpiAOV').textContent = `$${data.average_order_value.toFixed(2)}`;
    document.getElementById('kpiDiscount').textContent = `Avg Discount: ${data.average_discount_pct}%`;
}

// 2. Fetch Trends
async function fetchTrends(query) {
    const res = await fetch(`/api/trends${query}`);
    const data = await res.json();

    renderMonthlyTrendChart(data.monthly);
    renderQuarterlyTrendChart(data.quarterly);
}

function renderMonthlyTrendChart(monthly) {
    const ctx = document.getElementById('monthlyTrendChart').getContext('2d');
    if (charts.monthly) charts.monthly.destroy();

    charts.monthly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthly.labels,
            datasets: [
                {
                    label: 'Net Revenue ($)',
                    data: monthly.revenue,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.35,
                    yAxisID: 'y'
                },
                {
                    label: 'Order Volume',
                    data: monthly.orders,
                    type: 'bar',
                    backgroundColor: 'rgba(245, 158, 11, 0.3)',
                    borderColor: '#F59E0B',
                    borderWidth: 1,
                    borderRadius: 4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { labels: { color: '#9CA3AF' } }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9CA3AF', maxRotation: 45 }
                },
                y: {
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#3B82F6',
                        callback: val => `$${val >= 1000 ? (val/1000).toFixed(0) + 'k' : val}`
                    }
                },
                y1: {
                    position: 'right',
                    grid: { display: false },
                    ticks: { color: '#F59E0B' }
                }
            }
        }
    });
}

function renderQuarterlyTrendChart(quarterly) {
    const ctx = document.getElementById('quarterlyTrendChart').getContext('2d');
    if (charts.quarterly) charts.quarterly.destroy();

    charts.quarterly = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: quarterly.labels,
            datasets: [
                {
                    label: 'Net Revenue ($)',
                    data: quarterly.revenue,
                    backgroundColor: '#2563EB',
                    borderRadius: 6
                },
                {
                    label: 'Operating Profit ($)',
                    data: quarterly.profit,
                    backgroundColor: '#10B981',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#9CA3AF' } }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#9CA3AF' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#9CA3AF',
                        callback: val => `$${val >= 1000 ? (val/1000).toFixed(0) + 'k' : val}`
                    }
                }
            }
        }
    });
}

// 3. Fetch Categories
async function fetchCategories(query) {
    const res = await fetch(`/api/categories${query}`);
    const data = await res.json();

    const ctx = document.getElementById('categoryChart').getContext('2d');
    if (charts.category) charts.category.destroy();

    charts.category = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Net Revenue ($)',
                    data: data.revenue,
                    backgroundColor: '#6366F1',
                    borderRadius: 6
                },
                {
                    label: 'Profit ($)',
                    data: data.profit,
                    backgroundColor: '#10B981',
                    borderRadius: 6
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#9CA3AF' } }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#9CA3AF',
                        callback: val => `$${val >= 1000 ? (val/1000).toFixed(0) + 'k' : val}`
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#9CA3AF', font: { weight: 600 } }
                }
            }
        }
    });
}

// 4. Fetch Demographics
async function fetchDemographics(query) {
    const res = await fetch(`/api/demographics${query}`);
    const data = await res.json();

    // Age Groups
    const ctxAge = document.getElementById('ageGroupChart').getContext('2d');
    if (charts.ageGroup) charts.ageGroup.destroy();

    charts.ageGroup = new Chart(ctxAge, {
        type: 'bar',
        data: {
            labels: data.age_groups.labels,
            datasets: [
                {
                    label: 'Revenue ($)',
                    data: data.age_groups.revenue,
                    backgroundColor: [
                        '#3B82F6',
                        '#2563EB',
                        '#1D4ED8',
                        '#1E3A8A'
                    ],
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#9CA3AF' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#9CA3AF',
                        callback: val => `$${val >= 1000 ? (val/1000).toFixed(0) + 'k' : val}`
                    }
                }
            }
        }
    });

    // Gender Donut
    const ctxGen = document.getElementById('genderChart').getContext('2d');
    if (charts.gender) charts.gender.destroy();

    charts.gender = new Chart(ctxGen, {
        type: 'doughnut',
        data: {
            labels: data.gender.labels,
            datasets: [
                {
                    data: data.gender.orders,
                    backgroundColor: ['#EC4899', '#3B82F6', '#9CA3AF'],
                    borderColor: '#111827',
                    borderWidth: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#9CA3AF', padding: 15 }
                }
            },
            cutout: '70%'
        }
    });
}

// 5. Fetch Top Products
async function fetchTopProducts(query) {
    const res = await fetch(`/api/products${query}`);
    const data = await res.json();

    const ctx = document.getElementById('topProductsChart').getContext('2d');
    if (charts.products) charts.products.destroy();

    charts.products = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Net Revenue ($)',
                    data: data.revenue,
                    backgroundColor: '#0D9488',
                    borderRadius: 6
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#9CA3AF',
                        callback: val => `$${val >= 1000 ? (val/1000).toFixed(0) + 'k' : val}`
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#9CA3AF' }
                }
            }
        }
    });
}

// 6. Fetch Non-Obvious Insight
async function fetchDiscountInsight() {
    const res = await fetch('/api/discounts');
    const data = await res.json();

    const ctx = document.getElementById('discountInsightChart').getContext('2d');
    if (charts.discount) charts.discount.destroy();

    charts.discount = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Average Profit ($)',
                    data: data.avg_profit,
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    tension: 0.3,
                    yAxisID: 'y'
                },
                {
                    label: 'Avg Units per Order',
                    data: data.avg_quantity,
                    borderColor: '#3B82F6',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    tension: 0.1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#9CA3AF' } }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9CA3AF' }
                },
                y: {
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#EF4444',
                        callback: val => `$${val}`
                    },
                    title: { display: true, text: 'Avg Profit ($)', color: '#EF4444' }
                },
                y1: {
                    position: 'right',
                    grid: { display: false },
                    ticks: { color: '#3B82F6', stepSize: 0.2 },
                    title: { display: true, text: 'Basket Quantity', color: '#3B82F6' },
                    min: 1.0,
                    max: 2.2
                }
            }
        }
    });
}

// 7. Load Recent Transactions Table
async function loadTransactions() {
    const res = await fetch('/api/transactions?limit=30');
    const data = await res.json();
    const tbody = document.getElementById('tableBody');

    if (!tbody || !data.transactions) return;

    tbody.innerHTML = '';
    data.transactions.forEach(t => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><code>${t.id}</code></td>
            <td>${t.date}</td>
            <td>${t.customer}</td>
            <td><small>${t.gender}, ${t.age}y</small></td>
            <td><strong>${t.category}</strong><br><small class="text-secondary">${t.product}</small></td>
            <td>${t.quantity}</td>
            <td>$${t.unit_price.toFixed(2)}</td>
            <td><span class="badge ${t.discount === '0%' ? 'info-badge' : 'live-badge'}">${t.discount}</span></td>
            <td><strong>$${t.net_amount.toFixed(2)}</strong></td>
            <td class="text-success">$${t.profit.toFixed(2)}</td>
            <td><small>${t.payment}</small></td>
        `;
        tbody.appendChild(row);
    });
}
