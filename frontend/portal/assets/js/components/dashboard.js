/* ============================================
   Dashboard Component
   ============================================ */

/**
 * Render dashboard report
 * @param {object} data - Dashboard report data
 */
function renderDashboardReport(data) {
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    
    let html = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">${data.company_name || 'Company'} - Dashboard</h2>
            
            <!-- Summary Stats -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px;">
                <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px;">
                    <div style="font-size: 14px; opacity: 0.9;">Total Transactions</div>
                    <div style="font-size: 32px; font-weight: 600; margin-top: 10px;">${(data.stats && data.stats.total_transactions) ? data.stats.total_transactions.toLocaleString() : 0}</div>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 8px;">
                    <div style="font-size: 14px; opacity: 0.9;">Total Parties</div>
                    <div style="font-size: 32px; font-weight: 600; margin-top: 10px;">${(data.stats && data.stats.total_parties) ? data.stats.total_parties.toLocaleString() : 0}</div>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 8px;">
                    <div style="font-size: 14px; opacity: 0.9;">Net Balance</div>
                    <div style="font-size: 32px; font-weight: 600; margin-top: 10px;">${formatCurrency((data.stats && data.stats.net_balance) ? data.stats.net_balance : 0)}</div>
                </div>
            </div>
            
            <!-- Sales Summary Cards -->
            ${data.sales ? `
            <div style="margin-bottom: 30px;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">💰 Sales Metrics (FY ${data.sales.financial_year || 'N/A'})</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
                    <div style="padding: 20px; background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; opacity: 0.9;">Total Sales Amount</div>
                        <div style="font-size: 28px; font-weight: 600; margin-top: 10px;">${formatCurrency(data.sales.total_sales_amount || 0)}</div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">Sales + GST</div>
                    </div>
                    <div style="padding: 20px; background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; opacity: 0.9;">Total Sales Count</div>
                        <div style="font-size: 28px; font-weight: 600; margin-top: 10px;">${(data.sales.total_sales_count || 0).toLocaleString()}</div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">Invoices</div>
                    </div>
                    <div style="padding: 20px; background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; opacity: 0.9;">Avg Sales per Transaction</div>
                        <div style="font-size: 28px; font-weight: 600; margin-top: 10px;">${formatCurrency(data.sales.avg_sales_per_transaction || 0)}</div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">Per Invoice</div>
                    </div>
                    <div style="padding: 20px; background: linear-gradient(135deg, ${(data.sales.sales_growth_percent || 0) >= 0 ? '#e74c3c 0%, #c0392b 100%' : '#e67e22 0%, #d35400 100%'}); color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="font-size: 14px; opacity: 0.9;">Sales Growth</div>
                        <div style="font-size: 28px; font-weight: 600; margin-top: 10px;">
                            ${(data.sales.sales_growth_percent || 0) >= 0 ? '↑' : '↓'} ${Math.abs(data.sales.sales_growth_percent || 0).toFixed(1)}%
                        </div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">vs Previous FY</div>
                    </div>
                </div>
            </div>
            ` : ''}
            
            <!-- Monthly Sales Trend Chart -->
            ${data.sales && data.monthly_sales_trend && data.monthly_sales_trend.length > 0 ? `
            <div style="margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">📈 Monthly Sales Trend</h3>
                <div style="position: relative; height: 400px;">
                    <canvas id="monthlySalesChart"></canvas>
                </div>
            </div>
            ` : ''}
            
            <!-- Top Sales Customers Table -->
            ${data.top_sales_customers && data.top_sales_customers.length > 0 ? `
            <div style="margin-bottom: 30px; padding: 20px; background: #ecf0f1; border-radius: 8px;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">🏆 Top 10 Sales Customers</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #34495e; color: white;">
                                <th style="padding: 12px; text-align: center;">Rank</th>
                                <th style="padding: 12px; text-align: left;">Customer Name</th>
                                <th style="padding: 12px; text-align: right;">Total Sales</th>
                                <th style="padding: 12px; text-align: center;">Invoices</th>
                                <th style="padding: 12px; text-align: right;">Avg Invoice</th>
                                <th style="padding: 12px; text-align: right;">% of Total</th>
                            </tr>
                        </thead>
                        <tbody>
            ${data.top_sales_customers.map((customer, idx) => {
                const percentOfTotal = data.sales && data.sales.total_sales_amount > 0 
                    ? ((customer.total_sales / data.sales.total_sales_amount) * 100).toFixed(1)
                    : '0.0';
                return `
                            <tr style="border-bottom: 1px solid #bdc3c7;">
                                <td style="padding: 10px; text-align: center; font-weight: 600; color: #3498db;">${idx + 1}</td>
                                <td style="padding: 10px; font-weight: 600;">${customer.customer_name || '-'}</td>
                                <td style="padding: 10px; text-align: right; color: #27ae60; font-weight: 600;">${formatCurrency(customer.total_sales || 0)}</td>
                                <td style="padding: 10px; text-align: center;">${(customer.invoice_count || 0).toLocaleString()}</td>
                                <td style="padding: 10px; text-align: right; color: #7f8c8d;">${formatCurrency(customer.avg_invoice_value || 0)}</td>
                                <td style="padding: 10px; text-align: right; color: #3498db; font-weight: 600;">${percentOfTotal}%</td>
                            </tr>
                `;
            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            ` : ''}
            
            <!-- Additional Charts: Sales by Customer and Sales Distribution -->
            ${data.top_sales_customers && data.top_sales_customers.length > 0 && data.sales ? `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <!-- Sales by Customer (Bar Chart) -->
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">📊 Sales by Customer (Top 10)</h3>
                    <div style="position: relative; height: 350px;">
                        <canvas id="salesByCustomerChart"></canvas>
                    </div>
                </div>
                
                <!-- Sales Distribution (Pie Chart) -->
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">🥧 Sales Distribution</h3>
                    <div style="position: relative; height: 350px;">
                        <canvas id="salesDistributionChart"></canvas>
                    </div>
                </div>
            </div>
            ` : ''}
            
            <!-- Top Debtors and Creditors -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div style="padding: 20px; background: #ecf0f1; border-radius: 8px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">Top 10 Debtors</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #34495e; color: white;">
                                <th style="padding: 8px; text-align: left;">Party</th>
                                <th style="padding: 8px; text-align: right;">Balance</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Check if top_debtors array exists
    if (data.top_debtors && Array.isArray(data.top_debtors)) {
        data.top_debtors.forEach((debtor, idx) => {
            html += `
                <tr style="border-bottom: 1px solid #bdc3c7;">
                    <td style="padding: 8px;">${idx + 1}. ${debtor.party_name || '-'}</td>
                    <td style="padding: 8px; text-align: right; color: #27ae60; font-weight: 600;">${formatCurrency(debtor.balance || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="2" style="text-align: center; padding: 10px; color: #7f8c8d;">No debtors found</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
                <div style="padding: 20px; background: #ecf0f1; border-radius: 8px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">Top 10 Creditors</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #34495e; color: white;">
                                <th style="padding: 8px; text-align: left;">Party</th>
                                <th style="padding: 8px; text-align: right;">Balance</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Check if top_creditors array exists
    if (data.top_creditors && Array.isArray(data.top_creditors)) {
        data.top_creditors.forEach((creditor, idx) => {
            html += `
                <tr style="border-bottom: 1px solid #bdc3c7;">
                    <td style="padding: 8px;">${idx + 1}. ${creditor.party_name || '-'}</td>
                    <td style="padding: 8px; text-align: right; color: #e74c3c; font-weight: 600;">${formatCurrency(creditor.balance || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="2" style="text-align: center; padding: 10px; color: #7f8c8d;">No creditors found</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Voucher Type Summary -->
            <div style="margin-bottom: 30px;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">Voucher Type Summary</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #34495e; color: white;">
                                <th style="padding: 12px; text-align: left;">Voucher Type</th>
                                <th style="padding: 12px; text-align: right;">Count</th>
                                <th style="padding: 12px; text-align: right;">Total Debit</th>
                                <th style="padding: 12px; text-align: right;">Total Credit</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Check if voucher_types array exists
    if (data.voucher_types && Array.isArray(data.voucher_types)) {
        data.voucher_types.forEach(vt => {
            html += `
                <tr style="border-bottom: 1px solid #ecf0f1;">
                    <td style="padding: 10px;">${vt.type || '-'}</td>
                    <td style="padding: 10px; text-align: right;">${vt.count || 0}</td>
                    <td style="padding: 10px; text-align: right; color: #27ae60;">${formatCurrency(vt.debit || 0)}</td>
                    <td style="padding: 10px; text-align: right; color: #e74c3c;">${formatCurrency(vt.credit || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="4" style="text-align: center; padding: 10px; color: #7f8c8d;">No voucher types found</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    
    // Render Monthly Sales Trend Chart using Chart.js
    if (data.sales && data.monthly_sales_trend && data.monthly_sales_trend.length > 0 && typeof Chart !== 'undefined') {
        const ctx = document.getElementById('monthlySalesChart');
        if (ctx) {
            const labels = data.monthly_sales_trend.map(item => item.month_name);
            const salesData = data.monthly_sales_trend.map(item => item.sales_amount);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Sales Amount',
                        data: salesData,
                        borderColor: 'rgb(39, 174, 96)',
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: 'rgb(39, 174, 96)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                },
                                color: '#2c3e50'
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return 'Sales: ' + formatCurrency(context.parsed.y);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1000000) {
                                        return '₹' + (value / 1000000).toFixed(1) + 'M';
                                    } else if (value >= 1000) {
                                        return '₹' + (value / 1000).toFixed(1) + 'K';
                                    }
                                    return '₹' + value;
                                },
                                font: {
                                    size: 12
                                },
                                color: '#7f8c8d'
                            },
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                font: {
                                    size: 12
                                },
                                color: '#7f8c8d'
                            },
                            grid: {
                                display: false
                            }
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        }
    }
    
    // Render Sales by Customer Bar Chart
    if (data.top_sales_customers && data.top_sales_customers.length > 0 && typeof Chart !== 'undefined') {
        const ctxBar = document.getElementById('salesByCustomerChart');
        if (ctxBar) {
            // Show top 10 customers
            const topCustomers = data.top_sales_customers.slice(0, 10);
            const customerLabels = topCustomers.map(c => {
                // Truncate long names
                const name = c.customer_name || 'Unknown';
                return name.length > 20 ? name.substring(0, 20) + '...' : name;
            });
            const customerSales = topCustomers.map(c => c.total_sales);
            
            new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: customerLabels,
                    datasets: [{
                        label: 'Sales Amount',
                        data: customerSales,
                        backgroundColor: [
                            'rgba(39, 174, 96, 0.8)',
                            'rgba(52, 152, 219, 0.8)',
                            'rgba(155, 89, 182, 0.8)',
                            'rgba(241, 196, 15, 0.8)',
                            'rgba(230, 126, 34, 0.8)',
                            'rgba(231, 76, 60, 0.8)',
                            'rgba(46, 204, 113, 0.8)',
                            'rgba(26, 188, 156, 0.8)',
                            'rgba(52, 73, 94, 0.8)',
                            'rgba(149, 165, 166, 0.8)'
                        ],
                        borderColor: [
                            'rgb(39, 174, 96)',
                            'rgb(52, 152, 219)',
                            'rgb(155, 89, 182)',
                            'rgb(241, 196, 15)',
                            'rgb(230, 126, 34)',
                            'rgb(231, 76, 60)',
                            'rgb(46, 204, 113)',
                            'rgb(26, 188, 156)',
                            'rgb(52, 73, 94)',
                            'rgb(149, 165, 166)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y', // Horizontal bar chart
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Sales: ' + formatCurrency(context.parsed.x);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1000000) {
                                        return '₹' + (value / 1000000).toFixed(1) + 'M';
                                    } else if (value >= 1000) {
                                        return '₹' + (value / 1000).toFixed(1) + 'K';
                                    }
                                    return '₹' + value;
                                },
                                font: {
                                    size: 11
                                },
                                color: '#7f8c8d'
                            },
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        y: {
                            ticks: {
                                font: {
                                    size: 11
                                },
                                color: '#7f8c8d'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Render Sales Distribution Pie Chart
    if (data.top_sales_customers && data.top_sales_customers.length > 0 && data.sales && typeof Chart !== 'undefined') {
        const ctxPie = document.getElementById('salesDistributionChart');
        if (ctxPie) {
            // Top 5 customers + Others
            const top5 = data.top_sales_customers.slice(0, 5);
            const top5Total = top5.reduce((sum, c) => sum + (c.total_sales || 0), 0);
            const othersTotal = (data.sales.total_sales_amount || 0) - top5Total;
            
            const pieLabels = [...top5.map(c => {
                const name = c.customer_name || 'Unknown';
                return name.length > 15 ? name.substring(0, 15) + '...' : name;
            }), 'Others'];
            const pieData = [...top5.map(c => c.total_sales || 0), othersTotal];
            
            new Chart(ctxPie, {
                type: 'pie',
                data: {
                    labels: pieLabels,
                    datasets: [{
                        data: pieData,
                        backgroundColor: [
                            'rgba(39, 174, 96, 0.8)',
                            'rgba(52, 152, 219, 0.8)',
                            'rgba(155, 89, 182, 0.8)',
                            'rgba(241, 196, 15, 0.8)',
                            'rgba(230, 126, 34, 0.8)',
                            'rgba(149, 165, 166, 0.8)'
                        ],
                        borderColor: [
                            'rgb(39, 174, 96)',
                            'rgb(52, 152, 219)',
                            'rgb(155, 89, 182)',
                            'rgb(241, 196, 15)',
                            'rgb(230, 126, 34)',
                            'rgb(149, 165, 166)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    size: 12
                                },
                                color: '#2c3e50',
                                padding: 15,
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {
                                        return data.labels.map((label, i) => {
                                            const value = data.datasets[0].data[i];
                                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            return {
                                                text: `${label} (${percentage}%)`,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                strokeStyle: data.datasets[0].borderColor[i],
                                                lineWidth: data.datasets[0].borderWidth,
                                                hidden: false,
                                                index: i
                                            };
                                        });
                                    }
                                    return [];
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
}

