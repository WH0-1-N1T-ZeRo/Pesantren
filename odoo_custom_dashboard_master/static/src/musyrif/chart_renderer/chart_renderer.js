/** @odoo-module */
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const {
  Component,
  onWillStart,
  useRef,
  onMounted,
  onWillUnmount,
  onWillUpdateProps,
} = owl;
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class MusyrifChartRenderer extends Component {
  static props = {
    type: { type: String },
    period: { type: String, optional: true },
    startDate: { type: String, optional: true },
    endDate: { type: String, optional: true },
  };

  setup() {
    this.chartRef = useRef("chart");
    this.areaChartRef = useRef("areaChart");
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.state = {
      chartData: { series: [], labels: [], stateIds: {} },
      uangSakuData: { dates: [], masuk: [], keluar: [] },
      selectedPeriod: this.props.period || "all",
      currentStartDate: this.props.startDate,
      currentEndDate: this.props.endDate,
      isLoading: false,
      totalPermissions: 0,
      isFiltered: !!(this.props.startDate && this.props.endDate),
    };
    this.refreshInterval = null;
    this.countdownInterval = null;
    this.areaChartInstance = null;
    this.countdownTime = 10;
    this.isCountingDown = false;

    if (this.props.startDate && this.props.endDate) {
      this.state.currentStartDate = this.props.startDate;
      this.state.currentEndDate = this.props.endDate;
    }

    onWillUpdateProps(async (nextProps) => {
      if (
        nextProps.startDate !== this.props.startDate ||
        nextProps.endDate !== this.props.endDate
      ) {
        this.state.currentStartDate = nextProps.startDate;
        this.state.currentEndDate = nextProps.endDate;
        this.state.isFiltered = !!(nextProps.startDate && nextProps.endDate);
        await this.fetchData(
          this.state.currentStartDate,
          this.state.currentEndDate
        );
        await this.fetchUangSakuData(
            this.state.currentStartDate,
            this.state.currentEndDate
          );
      }
    });

    onWillStart(async () => {
      await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
      await this.fetchData(
        this.state.currentStartDate,
        this.state.currentEndDate
      );
      await this.fetchUangSakuData(
        this.state.currentStartDate,
        this.state.currentEndDate
      );
    });

    onMounted(() => {
      this.renderChart();
      this.renderAreaChart();
      this.attachEventListeners();
    });

    onWillUnmount(() => {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
    });
  }

  cleanup() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
    if (this.areaChartInstance) {
        this.areaChartInstance.destroy();
        this.areaChartInstance = null;
      }
      this.clearIntervals();
    }

  toggleCountdown() {
    if (this.isCountingDown) {
      this.clearIntervals();
      document.getElementById("timerIcon").className = "fas fa-clock";
      document.getElementById("timerCountdown").textContent = "";
    } else {
      this.startCountdown();
      document.getElementById("timerIcon").className = "fas fa-stop";
    }
    this.isCountingDown = !this.isCountingDown;
  }

  startCountdown() {
    this.countdownTime = 10;
    this.updateCountdownDisplay();

    this.countdownInterval = setInterval(() => {
      this.countdownTime--;
      if (this.countdownTime < 0) {
        this.countdownTime = 10;
        this.refreshChart();
      }
      this.updateCountdownDisplay();
    }, 1000);
  }

  updateCountdownDisplay() {
    document.getElementById("timerCountdown").textContent = this.countdownTime;
  }

  async refreshChart() {
    const startDate = this.state.isFiltered
      ? this.state.currentStartDate
      : null;
    const endDate = this.state.isFiltered 
      ? this.state.currentEndDate 
      : null;

    try {
      // Fetch both datasets
      await Promise.all([
        this.fetchData(startDate, endDate),
        this.fetchUangSakuData(startDate, endDate)
      ]);

      // Update donut chart
      if (this.chartInstance) {
        this.chartInstance.updateOptions(
          {
            series: this.state.chartData.series,
            labels: this.state.chartData.labels,
          },
          true,
          true
        );
      }

      // Update area chart
      if (this.areaChartInstance) {
        const masuk = this.state.uangSakuData.masuk.map(value => Number(value) || 0);
        const keluar = this.state.uangSakuData.keluar.map(value => Number(value) || 0);
        
        this.areaChartInstance.updateOptions({
          series: [
            {
              name: "Uang Masuk",
              data: masuk,
            },
            {
              name: "Uang Keluar",
              data: keluar,
            },
          ],
          xaxis: {
            categories: this.state.uangSakuData.dates.map(date => this.formatDate(date)),
          }
        }, true, true);
      }
    } catch (error) {
      console.error("Error refreshing charts:", error);
    }
  }

  clearIntervals() {
    if (this.countdownInterval) clearInterval(this.countdownInterval);
    if (this.refreshInterval) clearInterval(this.refreshInterval);
  }

  attachEventListeners() {
    const timerButton = document.getElementById("timerButton");
    timerButton.addEventListener("click", this.toggleCountdown.bind(this));

    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');

    if (startDateInput && endDateInput) {
      startDateInput.addEventListener("change", () => this.handleDateFilter());
      endDateInput.addEventListener("change", () => this.handleDateFilter());
    }
  }

  async handleDateFilter() {
    this.clearIntervals();

    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');

    if (startDateInput && endDateInput) {
      const startDate = startDateInput.value;
      const endDate = endDateInput.value;

      if (startDate && endDate) {
        const formattedStartDate = this.formatDateToOdoo(startDate);
        const formattedEndDate = this.formatDateToOdoo(endDate);

        this.state.currentStartDate = formattedStartDate;
        this.state.currentEndDate = formattedEndDate;
        this.state.isFiltered = true;

        await this.fetchData(formattedStartDate, formattedEndDate);
        await this.fetchUangSakuData(formattedStartDate, formattedEndDate);
      }
    }

    if (this.isCountingDown) {
      this.startCountdown();
    }
  }

  formatDateToOdoo(dateString) {
    const date = new Date(dateString);
    return date.toISOString().split(".")[0] + "Z";
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    const months = [
      "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
      "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
    ];
    const day = String(date.getDate()).padStart(2, '0');
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    
    return `${day} ${month} ${year}`;
  }

  getStateColor(state) {
    const colorMap = {
      Draft: "#16a34a", // Warm orange for pending/draft#f59e0b
      Check: "#dc2626", // Blue for in review/check #3b82f6
      Approved: "#737373", // Green for approved
      Rejected: "#3b82f6", // Red for rejected
    };
    return colorMap[state] || "#cbd5e1"; // Default gray if state not found
  }

  getChartConfig() {
    // Get unique states and their corresponding colors
    const states = ["Draft", "Check", "Approved", "Rejected"];
    const colors = states.map((state) => this.getStateColor(state));

    return {
      chart: {
        type: "donut",
        height: 300,
        width: "100%",
        fontFamily: "Inter, sans-serif",
        background: "transparent",
        animations: {
          enabled: true,
          easing: "easeinout",
          speed: 800,
          animateGradually: {
            enabled: true,
            delay: 150,
          },
          dynamicAnimation: {
            enabled: true,
            speed: 350,
          },
        },
        events: {
          dataPointSelection: (event, chartContext, config) => {
            const dataPointIndex = config.dataPointIndex;
            if (dataPointIndex === -1) return;

            const selectedLabel = this.state.chartData.labels[dataPointIndex];
            const associatedIds = this.state.chartData.stateIds[selectedLabel];

            if (!associatedIds || associatedIds.length === 0) return;

            const actionConfig = {
              type: "ir.actions.act_window",
              target: "current",
              name: "Perijinan",
              res_model: "cdn.perijinan",
              view_mode: "list,form",
              views: [
                [false, "list"],
                [false, "form"],
              ],
              domain: [["id", "in", associatedIds]],
            };

            this.actionService.doAction(actionConfig);
          },
        },
      },
      series: [], // Will be populated with data
      labels: states.map((state) => this.getStateLabel(state)), // Use the mapped labels
      colors: colors, // Use our custom color array
      plotOptions: {
        pie: {
          donut: {
            size: "65%",
            height: 350,
            width: '100%', // Add explicit width
            labels: {
              show: true,
              name: {
                show: true,
                fontSize: "22px",
                fontFamily: "Inter, sans-serif",
                offsetY: -10,
                color: "#1f2937",
              },
              value: {
                show: true,
                fontSize: "16px",
                fontFamily: "Inter, sans-serif",
                color: "#1f2937",
                formatter: function (val) {
                  return `${val} Siswa`;
                },
              },
              total: {
                show: true,
                fontSize: "16px",
                fontFamily: "Inter, sans-serif",
                color: "#1f2937",
                label: "Total Siswa",
                formatter: function (w) {
                  return `${w.globals.seriesTotals.reduce(
                    (a, b) => a + b,
                    0
                  )} Siswa`;
                },
              },
            },
          },
        },
      },
      states: {
        hover: {
          filter: {
            type: "none",
          },
        },
        active: {
          filter: {
            type: "none",
          },
        },
      },
      stroke: {
        width: 0,
      },
      legend: {
        position: "top",
        horizontalAlign: "center",
        fontSize: "14px",
        fontFamily: "Inter, sans-serif",
        labels: {
          colors: "#1f2937",
        },
        markers: {
          width: 10,
          height: 10,
          radius: 6,
        },
        itemMargin: {
          horizontal: 15,
          vertical: 8,
        },
        onItemClick: {
          toggleDataSeries: false,
        },
        onItemHover: {
          highlightDataSeries: false,
        },
      },
      dataLabels: {
        enabled: false,
      },
      tooltip: {
        enabled: true,
        theme: "dark",
        style: {
          fontSize: "14px",
          fontFamily: "Inter, sans-serif",
        },
        y: {
          formatter: function (value) {
            return `${value} Siswa`;
          },
          title: {
            formatter: function (seriesName) {
              return seriesName;
            },
          },
        },
      },
      responsive: [
        {
          breakpoint: 480,
          options: {
            chart: {
              width: "100%",
            },
            legend: {
              position: "bottom",
            },
          },
        },
      ],
      noData: {
        text: "Tidak ada data",
        align: "center",
        verticalAlign: "middle",
        style: {
          color: "#1f2937",
          fontSize: "16px",
          fontFamily: "Inter",
        },
      },
    };
  }

  getAreaChartConfig() {
    const self = this;

    return {
        chart: {
            type: "area",
            height: 450,
            width: '100%',
            stacked: true,
            toolbar: {
                show: false,
            },
            zoom: {
                enabled: false,
            },
            events: {
                click: function(event, chartContext, config) {
                    // Validate click event data
                    if (!config || config.dataPointIndex === undefined || config.dataPointIndex < 0) {
                        console.warn('Invalid click event data');
                        return;
                    }

                    // Validate state data
                    if (!self.state.uangSakuData || !Array.isArray(self.state.uangSakuData.dates)) {
                        console.error('Invalid state data structure');
                        return;
                    }

                    try {
                        const selectedDate = self.state.uangSakuData.dates[config.dataPointIndex];
                        if (!selectedDate) {
                            console.warn('Selected date not found');
                            return;
                        }

                        // Create date range for the selected date
                        const startDate = new Date(selectedDate);
                        startDate.setHours(0, 0, 0, 0);
                        const endDate = new Date(selectedDate);
                        endDate.setHours(23, 59, 59, 999);

                        // Format dates for domain
                        const formattedStartDate = startDate.toISOString().split('.')[0];
                        const formattedEndDate = endDate.toISOString().split('.')[0];

                        // Determine transaction type based on series index
                        const transactionType = config.seriesIndex === 0 ? "masuk" : "keluar";

                        // Build domain query
                        const domain = [
                            ["tgl_transaksi", ">=", formattedStartDate],
                            ["tgl_transaksi", "<=", formattedEndDate],
                            ["jns_transaksi", "=", transactionType]
                        ];

                        // Execute action if service is available
                        if (!self.actionService) {
                            console.error('Action service not initialized');
                            return;
                        }

                        self.actionService.doAction({
                            type: 'ir.actions.act_window',
                            name: `Data Uang ${transactionType === 'masuk' ? 'Masuk' : 'Keluar'}`,
                            res_model: 'cdn.uang_saku',
                            view_mode: 'list,form',
                            views: [
                                [false, 'list'],
                                [false, 'form']
                            ],
                            target: 'current',
                            domain: domain,
                            context: { 
                                create: false,
                                search_default_group_by_tgl_transaksi: 1
                            },
                            flags: { 
                                actionViewsInitialized: true
                            }
                        }).catch(error => {
                            console.error('Failed to execute action:', error);
                        });
                    } catch (error) {
                        console.error('Error handling chart click:', error);
                    }
                }
            }
        },
        plotOptions: {
            area: {
                fillTo: 'end',
                opacity: 1,
                dataLabels: {
                    enabled: false
                }
            }
        },
        colors: ["#16a34a", "#dc2626"],
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: "smooth",
            width: 2
        },
        markers: {
            size: 6,
            strokeWidth: 2,
            fillOpacity: 1,
            strokeOpacity: 1,
            hover: {
                size: 8
            }
        },
        series: [
            {
                name: "Uang Masuk",
                data: self.state.uangSakuData?.masuk || []
            },
            {
                name: "Uang Keluar",
                data: self.state.uangSakuData?.keluar || []
            }
        ],
        xaxis: {
            type: "category",
            categories: (self.state.uangSakuData?.dates || []).map(date => 
                self.formatDate(date)
            ),
            labels: {
                rotate: 0,
                style: {
                    fontSize: '12px'
                }
            },
            tooltip: {
                enabled: true
            }
        },
        yaxis: {
            labels: {
                formatter: value => new Intl.NumberFormat("id-ID", {
                    style: "currency",
                    currency: "IDR",
                    minimumFractionDigits: 0
                }).format(value)
            }
        },
        tooltip: {
            shared: true,
            intersect: false,
            y: {
                formatter: value => new Intl.NumberFormat("id-ID", {
                    style: "currency",
                    currency: "IDR",
                    minimumFractionDigits: 0
                }).format(value)
            }
        },
        fill: {
            type: "gradient",
            gradient: {
                opacityFrom: 0.6,
                opacityTo: 0.3,
                stops: [0, 90, 100]
            }
        },
        legend: {
            position: "bottom",
            horizontalAlign: "center"
        },
        noData: {
            text: 'Tidak ada data',
            align: 'center',
            verticalAlign: 'middle',
            style: {
                color: '#1f2937',
                fontSize: '16px',
                fontFamily: 'Inter'
            }
        }
    };
}

  async fetchData(startDate = null, endDate = null, silent = false) {
    const domain = [
      ["musyrif_id", "ilike", session.partner_display_name],
      ["state", "not in", ["Return", "Permission"]],
    ];
    if (startDate) domain.push(["create_date", ">=", startDate]);
    if (endDate) domain.push(["create_date", "<=", endDate]);

    try {
      const data = await this.orm.call("cdn.perijinan", "search_read", [
        domain,
        ["state", "musyrif_id"],
      ]);

      if (!data || data.length === 0) {
        console.warn("No data found.");
        this.state.chartData = { series: [], labels: [], stateIds: {} }; // Reset chart data
        this.renderChart(); // Render chart ulang untuk memastikan noData ditampilkan
        return;
      }

      // Process data
      const stateGroups = {};
      const stateIds = {};
      data.forEach((record) => {
        const state = this.getStateLabel(record.state);
        if (!stateGroups[state]) {
          stateGroups[state] = 0;
          stateIds[state] = [];
        }
        stateGroups[state]++;
        stateIds[state].push(record.id);
      });

      this.state.chartData = {
        series: Object.values(stateGroups),
        labels: Object.keys(stateGroups),
        stateIds,
      };

      this.renderChart(); // Update chart setelah data berhasil di-fetch
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  }

  async fetchUangSakuData(startDate = null, endDate = null) {
    let domain = [
        ["musyrif_id", "ilike", session.partner_display_name],
    ];
    
    if (startDate) {
        const start = new Date(startDate);
        start.setHours(0, 0, 0, 0);
        domain.push(["tgl_transaksi", ">=", start.toISOString().split('.')[0]]);
    }
    
    if (endDate) {
        const end = new Date(endDate);
        end.setHours(23, 59, 59, 999);
        domain.push(["tgl_transaksi", "<=", end.toISOString().split('.')[0]]);
    }

    try {
        // Fetch all data regardless of state
        const data = await this.orm.call("cdn.uang_saku", "search_read", [
            domain,
            ["tgl_transaksi", "amount_in", "amount_out", "jns_transaksi", "state"],
        ]);

        if (!data || data.length === 0) {
            this.state.uangSakuData = { 
                dates: [], 
                masuk: [], 
                keluar: [],
                rawData: {} // Add raw data storage
            };
            
            if (this.areaChartInstance) {
                this.areaChartInstance.updateOptions({
                    series: [{
                        name: "Uang Masuk",
                        data: []
                    }, {
                        name: "Uang Keluar",
                        data: []
                    }],
                    xaxis: {
                        categories: []
                    }
                }, true, true);
            }
            return;
        }

        // Sort data by date
        data.sort((a, b) => new Date(a.tgl_transaksi) - new Date(b.tgl_transaksi));

        // Process data for area chart
        const processedData = data.reduce((acc, record) => {
            const date = new Date(record.tgl_transaksi).toISOString().split('T')[0];
            
            // Initialize date entry if it doesn't exist
            if (!acc.dates.includes(date)) {
                acc.dates.push(date);
                acc.masuk.push(0);
                acc.keluar.push(0);
                acc.rawData[date] = []; // Initialize array for raw data
            }
            
            // Store raw record data for click handling
            acc.rawData[date].push(record);
            
            // Process amounts regardless of state
            const index = acc.dates.indexOf(date);
            if (record.jns_transaksi === 'masuk' && record.amount_in) {
                acc.masuk[index] += Number(record.amount_in) || 0;
            }
            if (record.jns_transaksi === 'keluar' && record.amount_out) {
                acc.keluar[index] += Number(record.amount_out) || 0;
            }
            
            return acc;
        }, { 
            dates: [], 
            masuk: [], 
            keluar: [], 
            rawData: {} // Add raw data storage
        });

        this.state.uangSakuData = processedData;

        // Update chart with click handler
        if (this.areaChartInstance) {
            this.areaChartInstance.updateOptions({
                series: [
                    {
                        name: "Uang Masuk",
                        data: processedData.masuk,
                    },
                    {
                        name: "Uang Keluar",
                        data: processedData.keluar,
                    }
                ],
                xaxis: {
                    categories: processedData.dates.map(date => this.formatDate(date)),
                },
                chart: {
                    events: {
                        dataPointSelection: (event, chartContext, config) => {
                            const date = processedData.dates[config.dataPointIndex];
                            const records = processedData.rawData[date];
                            
                            // Handle the click event with all records for that date
                            this.handleChartPointClick(records);
                        }
                    }
                }
            }, true, true);
        }
    } catch (error) {
        console.error("Error fetching uang saku data:", error);
    }
}

handleChartPointClick(records) {
  if (!records || records.length === 0) return;
  
  // Update the state with all records
  this.state.selectedRecords = records.map(record => ({
      ...record,
      formattedDate: this.formatDate(record.tgl_transaksi),
      amount: record.jns_transaksi === 'masuk' ? record.amount_in : record.amount_out
  }));
  
  // If you're using a modal to display the records
  if (this.modalRef) {
      this.modalRef.show();
  }
  
  this.render();
}

  renderAreaChart() {
    if (!this.areaChartRef.el) return;

    if (this.areaChartInstance) {
      this.areaChartInstance.destroy();
    }

    // Ensure the container has dimensions
    this.areaChartRef.el.style.minHeight = "350px";
    this.areaChartRef.el.style.width = "100%";

    const config = this.getAreaChartConfig();
    
    // Add default dimensions if data is empty
    if (!this.state.uangSakuData.dates.length) {
      config.chart.height = 350;
      config.chart.width = '100%';
    }

    try {
      this.areaChartInstance = new ApexCharts(this.areaChartRef.el, config);
      this.areaChartInstance.render();
    } catch (error) {
      console.error("Error rendering area chart:", error);
    }
  }

  getStateLabel(state) {
    const stateMap = {
      Draft: "Pengajuan",
      Check: "Diperiksa",
      Approved: "Disetujui",
      Rejected: "Ditolak",
    };
    return stateMap[state] || state;
  }

  updateChart() {
    if (this.chartInstance) {
      this.chartInstance.updateOptions({
        xaxis: {
          categories: this.state.chartData.labels,
        },
        series: this.state.chartData.series,
      });
    }

    if (this.areaChartInstance) {
      this.chartInstance.updateOptions({
        xaxis: {
          categories: this.state.chartData.labels,
        },
        series: this.state.chartData.series,
      });
    }
  }

  renderAreaChart() {
    if (!this.areaChartRef.el) return;

    if (this.areaChartInstance) {
      this.areaChartInstance.destroy();
    }

    const config = this.getAreaChartConfig();

    try {
      this.areaChartInstance = new ApexCharts(this.areaChartRef.el, config);
      this.areaChartInstance.render();
    } catch (error) {
      console.error("Error rendering area chart:", error);
    }
  }

  renderChart() {
    if (!this.chartRef.el) return;

    // Hapus instance chart jika ada
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }

    const hasData = this.state.chartData.series.length > 0;

    const config = {
      ...this.getChartConfig(),
      series: hasData ? this.state.chartData.series : [],
      labels: hasData ? this.state.chartData.labels : [],
    };

    try {
      this.chartInstance = new ApexCharts(this.chartRef.el, config);
      this.chartInstance.render();

      // Jika tidak ada data, panggil fungsi noData
      if (!hasData) {
        this.chartInstance.updateOptions({
          noData: {
            text: "Tidak ada data",
            align: "center",
            verticalAlign: "middle",
            style: {
              color: "#1f2937",
              fontSize: "16px",
              fontFamily: "Inter",
            },
          },
        });
      }
    } catch (error) {
      console.error("Error rendering chart:", error);
    }
  }
}

MusyrifChartRenderer.template = "owl.MusyrifChartRenderer";
