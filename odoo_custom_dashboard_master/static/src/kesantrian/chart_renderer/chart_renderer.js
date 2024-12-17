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

  export class ChartRenderer extends Component {
    static props = {
      type: { type: String },
      period: { type: String, optional: true },
      startDate: { type: String, optional: true },
      endDate: { type: String, optional: true },
    };

    setup() {
      this.chartRef = useRef("chart");
      this.chart2Ref = useRef("chart2");
      this.donutChartRef = useRef("donutChart"); 
      this.donutChart2Ref = useRef("donutChart2");
      this.loadingOverlayRef = useRef("loadingOverlay");
      this.orm = useService("orm");
      this.actionService = useService("action");
      this.state = {
        chartData: { series: [], labels: [] },
        chartData2: { series: [], labels: [] },
        donutChartData: { series: [], labels: [] },
        donutChartData2: { series: [], labels: [] }, 
        selectedPeriod: this.props.period || "all",
        currentStartDate: this.props.startDate,
        currentEndDate: this.props.endDate,
      };
      this.chartInstance = null;
      this.chart2Instance = null;
      this.donutChartInstance = null; 
      this.donutChart2Instance = null; 
      this.countdownInterval = null;
      this.countdownTime = 10;
      this.isCountingDown = false;

      if (this.props.startDate && this.props.endDate) {
        this.state.isFiltered = true;
      }

      onWillUpdateProps(async (nextProps) => {
        if (
          nextProps.startDate !== this.props.startDate ||
          nextProps.endDate !== this.props.endDate
        ) {
          this.showLoading();
          try {
            this.state.currentStartDate = nextProps.startDate;
            this.state.currentEndDate = nextProps.endDate;
            this.state.isFiltered = !!(nextProps.startDate && nextProps.endDate);
  
          await Promise.all([
          await this.fetchAttendanceData(
            this.state.currentStartDate,
            this.state.currentEndDate
          ),
          await this.fetchTahsinAttendanceData(
            this.state.currentStartDate,
            this.state.currentEndDate
          )
        ]);
      } catch (error) {
        console.error("Error updating props:", error);
      } finally {
        this.hideLoading();
      }
    }
  });

      onWillStart(async () => {
        this.showLoading();
        try {
        await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
        await Promise.all([
        await this.fetchAttendanceData(
          this.state.currentStartDate,
          this.state.currentEndDate
        ),
        await this.fetchTahsinAttendanceData(
          this.state.currentStartDate,
          this.state.currentEndDate
        )
      ]);
    } catch (error) {
      console.error("Error in initial data fetch:", error);
    } finally {
      this.hideLoading();
    }
  });

      onMounted(() => {
        this.renderChart();
        this.renderChart2();
        this.renderDonutChart(); 
        this.renderDonutChart2(); 
        this.attachEventListeners();
      });

      onWillUnmount(() => {
        this.cleanup();
      });
    }
    
  showLoading() {
    // Create loading overlay if it doesn't exist
    if (!this.loadingOverlay) {
      this.loadingOverlay = document.createElement('div');
      this.loadingOverlay.innerHTML = `
        <div class="musyrif-loading-overlay" style="
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.3);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
        ">
          <div class="loading-spinner">
            <i class="fas fa-sync-alt fa-spin fa-3x text-white"></i>
          </div>
        </div>
      `;
      document.body.appendChild(this.loadingOverlay);
    }
        // Ensure loading overlay is visible
        if (this.loadingOverlay) {
          this.loadingOverlay.style.display = 'flex';
        }
        
        this.state.isLoading = true;
      }

      hideLoading() {
        // Hide loading overlay
        if (this.loadingOverlay) {
          this.loadingOverlay.style.display = 'none';
        }
        
        this.state.isLoading = false;
      }


    cleanup() {
      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
      if (this.chart2Instance) {
        this.chart2Instance.destroy();
        this.chart2Instance = null;
      }
      if (this.donutChartInstance) { 
        this.donutChartInstance.destroy();
        this.donutChartInstance = null;
      }
      if (this.donutChart2Instance) { 
        this.donutChart2Instance.destroy();
        this.donutChart2Instance = null;
      }
      this.clearIntervals();
    }

    setPeriod(period) {
      this.state.selectedPeriod = period;
      this.fetchAttendanceData();
    }

    toggleCountdown() {
      if (this.isCountingDown) {
        this.clearIntervals();
        document.getElementById("timerIcon").className = "fas fa-stopwatch";
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
      this.showLoading();

      const startDate = this.state.isFiltered
        ? this.state.currentStartDate
        : null;
      const endDate = this.state.isFiltered ? this.state.currentEndDate : null;
      
    try {
      await Promise.all([
        await this.fetchAttendanceData(startDate, endDate),
        await this.fetchTahsinAttendanceData(startDate, endDate)
      ]);
    
      if (this.chartInstance) {
        this.chartInstance.updateOptions(
          {
            series: this.state.chartData.series,
            xaxis: {
              categories: this.state.chartData.labels,
            },
          },
          true,  
          true   
        );
      }

      if (this.chart2Instance) {
        this.chart2Instance.updateOptions(
          {
            series: this.state.chartData2.series,
            xaxis: {
              categories: this.state.chartData2.labels,
            },
          },
          true,  
          true  
        );
      }
    
      if (this.donutChartInstance) {
        this.donutChartInstance.updateOptions(
          {
            labels: this.state.donutChartData.labels,
            series: this.state.donutChartData.series,
        },
          true,
          true
        );
      }

      if (this.donutChart2Instance) {
        this.donutChart2Instance.updateOptions(
          {
            labels: this.state.donutChartData2.labels,
            series: this.state.donutChartData2.series,
        },
          true,
          true
        );
      }
    } catch (error) {
      console.error("Error refreshing charts:", error);
    } finally {
      this.hideLoading();
    }
  }

    clearIntervals() {
      if (this.countdownInterval) clearInterval(this.countdownInterval);
    }

    attachEventListeners() {
      const timerButton = document.getElementById("timerButton");
      if (timerButton) {
        const timerButton = document.getElementById("timerButton");
        timerButton.addEventListener("click", this.toggleCountdown.bind(this));
      }

      
      const startDateInput = document.querySelector('input[name="start_date"]');
      const endDateInput = document.querySelector('input[name="end_date"]');

      if (startDateInput && endDateInput) {
        startDateInput.addEventListener("change", () => this.handleDateFilter());
        endDateInput.addEventListener("change", () => this.handleDateFilter());
      }
    }

    async handleDateFilter() {
      this.clearIntervals(); 
      this.showLoading();
  
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

            try {
              await Promise.all([         
                await this.fetchAttendanceData(formattedStartDate, formattedEndDate),
                await this.fetchTahsinAttendanceData(formattedStartDate, formattedEndDate)
              ]);
            } catch (error) {
              console.error("Error in date filter:", error);
            } finally {
              this.hideLoading();
            }
          }
        }
    
        if (this.isCountingDown) {
          this.startCountdown();
        }
      }
  

    formatDateToDisplay(date) {
      if (!date) return '';
      
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
        'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'
      ];
      
      const dateObj = typeof date === 'string' ? new Date(date) : date;
      
      const day = String(dateObj.getDate()).padStart(2, '0');
      const month = months[dateObj.getMonth()];
      const year = dateObj.getFullYear();
    
      return `${day} ${month} ${year}`;
    }

    formatDateToOdoo(dateString) {
      const date = new Date(dateString);
      return date.toISOString().split(".")[0] + "Z";
    }

    updateChart() {
      if (this.chartInstance) {
        this.chartInstance.updateOptions(
          {
            xaxis: {
              categories: this.state.chartData.labels,
            },
            series: this.state.chartData.series,
          },
          false,
          true
        );
      }

      if (this.chart2Instance) {
        this.chart2Instance.updateOptions(
          {
            xaxis: {
              categories: this.state.chartData2.labels,
            },
            series: this.state.chartData2.series,
          },
          false,
          true
        );
      }

      if (this.donutChartInstance) {
        this.donutChartInstance.updateOptions({
          labels: this.state.donutChartData.labels,
          series: this.state.donutChartData.series,
        });
      }

      if (this.donutChart2Instance) {
        this.donutChart2Instance.updateOptions({
          labels: this.state.donutChartData2.labels,
          series: this.state.donutChartData2.series,
        });
      }
    }

    async fetchAttendanceData(startDate = null, endDate = null) {
      if (!startDate && !endDate) {
        endDate = new Date();
        startDate = new Date();
        startDate.setDate(startDate.getDate() - 6);
    
        startDate = startDate.toISOString().split("T")[0];
        endDate = endDate.toISOString().split("T")[0];
      } else {

        startDate = new Date(startDate).toISOString().split("T")[0];
        endDate = new Date(endDate).toISOString().split("T")[0];
      }
    
      const domain = [
        ["tanggal", ">=", startDate],
        ["tanggal", "<=", endDate],
      ];
    
      try {
        const data = await this.orm.call(
          "cdn.absen_tahfidz_quran_line",
          "search_read",
          [domain, ["name", "halaqoh_id", "tanggal", "kehadiran"]]
        );
        
        const groupedData = {};
        const halaqohSet = new Set();
        const attendanceStatus = {};
    
        data.forEach((record) => {
          const halaqohName = record.halaqoh_id[1];
          halaqohSet.add(halaqohName);
          if (!groupedData[halaqohName]) {
            groupedData[halaqohName] = {
              count: 0,
              associated_ids: []
            };
          }
          groupedData[halaqohName].count += 1;
          groupedData[halaqohName].associated_ids.push(record.id);
    
          const status = record.kehadiran || 'Tidak Ada Status';
          attendanceStatus[status] = (attendanceStatus[status] || 0) + 1;
        });
    
        const halaqohs = Array.from(halaqohSet).sort();
    
        
        this.state.chartData = {
          labels: ["Total"],
          series: halaqohs.map((halaqoh) => ({
            name: halaqoh,
            data: [groupedData[halaqoh].count],
            associated_ids: [groupedData[halaqoh].associated_ids]
          })),
        };
    
        
        this.state.donutChartData = {
          labels: Object.keys(attendanceStatus),
          series: Object.values(attendanceStatus),
        };
    
        
        this.state.currentViewRange = {
          startDate,
          endDate,
        };
    
        
        this.renderChart();
        this.renderDonutChart();
    
      } catch (error) {
        console.error("Error fetching attendance data:", error);
        this.state.chartData = { series: [], labels: [] };
        this.state.donutChartData = { series: [], labels: [] };
        this.state.currentViewRange = null;
      }
    }

    async fetchTahsinAttendanceData(startDate = null, endDate = null) {
      
      if (!startDate && !endDate) {
        endDate = new Date();
        startDate = new Date();
        startDate.setDate(startDate.getDate() - 6);
    
        startDate = startDate.toISOString().split("T")[0];
        endDate = endDate.toISOString().split("T")[0];
      } else {
        startDate = new Date(startDate).toISOString().split("T")[0];
        endDate = new Date(endDate).toISOString().split("T")[0];
      }
    
      const domain = [
        ["tanggal", ">=", startDate],
        ["tanggal", "<=", endDate],
      ];
    
      try {
        const data = await this.orm.call(
          "cdn.absen_tahsin_quran_line",
          "search_read",
          [domain, ["name", "halaqoh_id", "tanggal", "kehadiran", "nis"]]
        );
    
        
        const groupedData = {};
        const halaqohSet = new Set();
        const attendanceStatus = {};
    
        data.forEach((record) => {
          const halaqohName = record.halaqoh_id[1];
          halaqohSet.add(halaqohName);
          
          if (!groupedData[halaqohName]) {
            groupedData[halaqohName] = {
              count: 0,
              associated_ids: []
            };
          }
          groupedData[halaqohName].count += 1;
          groupedData[halaqohName].associated_ids.push(record.id);
    
          const status = record.kehadiran || 'Tidak Ada Status';
          attendanceStatus[status] = (attendanceStatus[status] || 0) + 1;
        });
    
        const halaqohs = Array.from(halaqohSet).sort();
    
        
        this.state.chartData2 = {
          labels: ["Total"],
          series: halaqohs.map((halaqoh) => ({
            name: halaqoh,
            data: [groupedData[halaqoh].count],
            associated_ids: [groupedData[halaqoh].associated_ids]
          })),
        };
    
        
        this.state.donutChartData2 = {
          labels: Object.keys(attendanceStatus),
          series: Object.values(attendanceStatus),
        };
    
        
        this.state.currentViewRangeTahsin = {
          startDate,
          endDate,
        };
    
        
        this.renderChart2();
        this.renderDonutChart2();
    
      } catch (error) {
        console.error("Error fetching Tahsin attendance data:", error);
        this.state.chartData2 = { series: [], labels: [] };
        this.state.donutChartData2 = { series: [], labels: [] };
        this.state.currentViewRangeTahsin = null;
      }
    }

    isCustomDateRange() {
      if (!this.state.currentViewRange) return false;

      const today = new Date();
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 6);

      const currentStartDate = new Date(this.state.currentViewRange.startDate);
      const currentEndDate = new Date(this.state.currentViewRange.endDate);

      return !(
        currentStartDate.toISOString().split("T")[0] ===
          weekAgo.toISOString().split("T")[0] &&
        currentEndDate.toISOString().split("T")[0] ===
          today.toISOString().split("T")[0]
      );
    }

    getChartConfig() {
      const barColors = [
        "#16a34a", 
        "#0891b2", 
        "#22c55e", 
        "#06b6d4", 
        "#15803d", 
        "#0e7490", 
        "#86efac", 
        "#67e8f9", 
        "#166534", 
        "#155e75", 
      ];

      const baseConfig = {
        chart: {
          type: "bar",
          height: 450,
          stacked: false,
          toolbar: {
            show: false,
            tools: {
              download: true,
              selection: false,
              zoom: true,
              zoomin: true,
              zoomout: true,
              pan: true,
            },
          },
          animations: {
            enabled: true,
            easing: "easeinout",
            speed: 800,
          },
          events: {
            dataPointSelection: (event, chartContext, config) =>
              this.onChartClick(event, chartContext, config),
          },
          hover: {
            mode: null
          }
        },
        colors: barColors,
        title: {
          text: '',
          align: "center",
          style: {
            fontSize: "18px",
            fontWeight: "600",
            fontFamily: "Inter, sans-serif",
          },
        },
        legend: {
          position: "bottom",
        },
        xaxis: {
          type: "category",
          categories: this.state.chartData.labels,
          labels: {
            style: {
              fontSize: "12px",
              fontFamily: "Inter, sans-serif",
            },
            rotate: -45,
            formatter: function (value) {
              return value.length > 15 ? value.substring(0, 15) + "..." : value;
            },
          },
        },
        dataLabels: {
          enabled: false,
          formatter: function (val) {
            return Math.round(val);
          },
          style: {
            fontSize: "12px",
            colors: ["#304758"],
          },
          offsetY: -20,
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: "55%",
            endingShape: "flat",
            borderRadius: 4,
            dataLabels: {
              position: "top",
            },
            groupPadding: 0.3,
            hover: {
              enabled: false
            }
          }
        },
        stroke: {
          width: 2,
          colors: ["transparent"],
        },
        yaxis: {
          title: {
            text: "",
            style: {
              fontSize: "14px",
              fontFamily: "Inter, sans-serif",
            },
          },
          labels: {
            formatter: function (val) {
              return Math.round(val);
            },
          },
        },
        tooltip: {
          shared: true,
          intersect: false,
          y: {
            formatter: function (val) {
              return Math.round(val);
            },
          },
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

      return baseConfig;
    }

    getDonutChartConfig() {
      return {
        chart: {
          type: 'pie',
          height: 355,
          toolbar: {
            show: false
          },
          animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800,
            animateGradually: {
                enabled: true,
                delay: 150
            },
            dynamicAnimation: {
                enabled: true,
                speed: 350
            }
        },
        events: {
          dataPointSelection: (event, chartContext, config) =>
            this.onPieClick(event, chartContext, config),
        },
        },
        title: {
          text: '',
          align: 'center',
          style: {
            fontSize: '18px',
            fontWeight: '600',
            fontFamily: 'Inter, sans-serif',
          },
        },
        legend: {
          position: 'top',
          horizontalAlign: 'center',
        },
        dataLabels: {
          enabled: false,
        },
        colors: [
          "#16a34a", 
          "#0891b2", 
          "#22c55e", 
          "#06b6d4", 
          "#15803d", 
          "#0e7490", 
          "#86efac", 
          "#67e8f9", 
          "#166534", 
          "#155e75", 
        ],
        labels: this.state.donutChartData.labels,
        series: this.state.donutChartData.series,
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 300
            },
            legend: {
              position: 'top'
            }
          }
        }],
        tooltip: {
          y: {
            formatter: function(value) {
              return value + ' orang';
            }
          }
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

    getChartConfig2() {
      const barColors = [
        "#16a34a", 
        "#0891b2", 
        "#22c55e", 
        "#06b6d4", 
        "#15803d", 
        "#0e7490", 
        "#86efac", 
        "#67e8f9", 
        "#166534", 
        "#155e75", 
      ];
    
      const baseConfig = {
        chart: {
          type: "bar",
          height: 450,
          stacked: false,
          toolbar: {
            show: false,
            tools: {
              download: true,
              selection: false,
              zoom: true,
              zoomin: true,
              zoomout: true,
              pan: true,
            },
          },
          animations: {
            enabled: true,
            easing: "easeinout",
            speed: 800,
          },
          events: {
            dataPointSelection: (event, chartContext, config) =>
              this.onChartClick2(event, chartContext, config),
          },
        },
        colors: barColors,
        title: {
          text: '',
          align: "center",
          style: {
            fontSize: "18px",
            fontWeight: "600",
            fontFamily: "Inter, sans-serif",
          },
        },
        legend: {
          position: "bottom",
        },
        xaxis: {
          type: "category",
          categories: this.state.chartData2.labels,
          labels: {
            style: {
              fontSize: "12px",
              fontFamily: "Inter, sans-serif",
            },
            rotate: -45,
            formatter: function (value) {
              return value.length > 15 ? value.substring(0, 15) + "..." : value;
            },
          },
        },
        dataLabels: {
          enabled: true,
          formatter: function (val) {
            return Math.round(val);
          },
          style: {
            fontSize: "12px",
            colors: ["#304758"],
          },
          offsetY: -20,
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: "55%",
            endingShape: "flat",
            borderRadius: 4,
            dataLabels: {
              position: "top",
            },
            groupPadding: 0.3,
          },
        },
        stroke: {
          width: 2,
          colors: ["transparent"],
        },
        yaxis: {
          title: {
            text: "",
            style: {
              fontSize: "14px",
              fontFamily: "Inter, sans-serif",
            },
          },
          labels: {
            formatter: function (val) {
              return Math.round(val);
            },
          },
        },
        tooltip: {
          shared: true,
          intersect: false,
          y: {
            formatter: function (val) {
              return Math.round(val);
            },
          },
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
    
      return baseConfig;
    }
    
    
    getDonutChartConfig2() {
      return {
        chart: {
          type: 'pie',
          height: 355,
          toolbar: {
            show: false
          },
          animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800,
            animateGradually: {
              enabled: true,
              delay: 150
            },
            dynamicAnimation: {
              enabled: true,
              speed: 350
            }
          },
          events: {
            dataPointSelection: (event, chartContext, config) =>
              this.onPieClick2(event, chartContext, config),
          },
        },
        title: {
          text: '',
          align: 'center',
          style: {
            fontSize: '18px',
            fontWeight: '600',
            fontFamily: 'Inter, sans-serif',
          },
        },
        legend: {
          position: 'top',
          horizontalAlign: 'center',
        },
        dataLabels: {
          enabled: false,
        },
        colors: [
          "#16a34a", 
          "#0891b2", 
          "#22c55e", 
          "#06b6d4", 
          "#15803d", 
          "#0e7490", 
          "#86efac", 
          "#67e8f9", 
          "#166534", 
          "#155e75", 
        ],
        labels: this.state.donutChartData2.labels,
        series: this.state.donutChartData2.series,
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 300
            },
            legend: {
              position: 'top'
            }
          }
        }],
        tooltip: {
          y: {
            formatter: function(value) {
              return value + ' orang';
            }
          }
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
    
    
    renderDonutChart2() {
      if (!this.donutChart2Ref.el) return;
    
      if (this.donutChartInstance2) {
        this.donutChartInstance2.destroy();
        this.donutChartInstance2 = null;
      }
    
      this.donutChart2Ref.el.innerHTML = "";
    
      const config = this.getDonutChartConfig2();
    
      try {
        this.donutChartInstance2 = new ApexCharts(this.donutChart2Ref.el, config);
        this.donutChartInstance2.render();
      } catch (error) {
        console.error("Error rendering Tahsin pie chart:", error);
      }
    }
    
    
    renderChart2() {
      if (!this.chart2Ref.el) return;
    
      if (this.chartInstance2) {
        this.chartInstance2.destroy();
        this.chartInstance2 = null;
      }
    
      this.chart2Ref.el.innerHTML = "";
    
      const config = {
        ...this.getChartConfig2(),
        series: this.state.chartData2.series,
      };
    
      try {
        this.chartInstance2 = new ApexCharts(this.chart2Ref.el, config);
        this.chartInstance2.render();
      } catch (error) {
        console.error("Error rendering Tahsin chart:", error);
      }
    }

    renderDonutChart() {
      if (!this.donutChartRef.el) return;

      if (this.donutChartInstance) {
        this.donutChartInstance.destroy();
        this.donutChartInstance = null;
      }

      this.donutChartRef.el.innerHTML = "";

      const config = this.getDonutChartConfig();

      try {
        this.donutChartInstance = new ApexCharts(this.donutChartRef.el, config);
        this.donutChartInstance.render();
      } catch (error) {
        console.error("Error rendering pie chart:", error);
      }
    }

    onPieClick(event, chartContext, config) {
      const dataPointIndex = config.dataPointIndex;
  
      if (dataPointIndex === -1) return;
  
      const selectedStatus = this.state.donutChartData.labels[dataPointIndex];
      const domain = [
        ["kehadiran", "=", selectedStatus],
      ];
  
      
      if (this.state.currentViewRange) {
        domain.push(
          ["tanggal", ">=", this.state.currentViewRange.startDate],
          ["tanggal", "<=", this.state.currentViewRange.endDate]
        );
      }
  
      const actionConfig = {
        type: "ir.actions.act_window",
        target: "current",
        name: `Absen Tahfidz - ${selectedStatus}`,
        res_model: "cdn.absen_tahfidz_quran_line",
        view_mode: "list,form",
        views: [
          [false, "list"],
          [false, "form"],
        ],
        domain: domain,
      };
  
      this.actionService.doAction(actionConfig);
    }

    onChartClick(event, chartContext, config) {
      const dataPointIndex = config.dataPointIndex;
      const seriesIndex = config.seriesIndex;

      if (dataPointIndex === -1) return;

      const associatedIds =
        this.state.chartData.series[seriesIndex].associated_ids[dataPointIndex];
      if (!associatedIds || associatedIds.length === 0) return;

      const actionConfig = {
        type: "ir.actions.act_window",
        target: "current",
        name: "Absen Tahfidz",
        res_model: "cdn.absen_tahfidz_quran_line",
        view_mode: "list,form",
        views: [
          [false, "list"],
          [false, "form"],
        ],
        domain: [["id", "in", associatedIds]],
      };

      this.actionService.doAction(actionConfig);
    }

    onChartClick2(event, chartContext, config) {
      const dataPointIndex = config.dataPointIndex;
      const seriesIndex = config.seriesIndex;
    
      if (dataPointIndex === -1) return;
    
      const associatedIds =
        this.state.chartData2.series[seriesIndex].associated_ids[dataPointIndex];
      if (!associatedIds || associatedIds.length === 0) return;
    
      const actionConfig = {
        type: "ir.actions.act_window",
        target: "current",
        name: "Absen Tahsin",
        res_model: "cdn.absen_tahsin_quran_line",
        view_mode: "list,form",
        views: [
          [false, "list"],
          [false, "form"],
        ],
        domain: [["id", "in", associatedIds]],
      };
    
      this.actionService.doAction(actionConfig);
    }
    
    
    onPieClick2(event, chartContext, config) {
      const dataPointIndex = config.dataPointIndex;
    
      if (dataPointIndex === -1) return;
    
      const selectedStatus = this.state.donutChartData2.labels[dataPointIndex];
      const domain = [
        ["kehadiran", "=", selectedStatus],
      ];
    
      
      if (this.state.currentViewRangeTahsin) {
        domain.push(
          ["tanggal", ">=", this.state.currentViewRangeTahsin.startDate],
          ["tanggal", "<=", this.state.currentViewRangeTahsin.endDate]
        );
      }
    
      const actionConfig = {
        type: "ir.actions.act_window",
        target: "current",
        name: `Absen Tahsin - ${selectedStatus}`,
        res_model: "cdn.absen_tahsin_quran_line",
        view_mode: "list,form",
        views: [
          [false, "list"],
          [false, "form"],
        ],
        domain: domain,
      };
    
      this.actionService.doAction(actionConfig);
    }

    renderChart() {
      if (!this.chartRef.el) return;

      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }

      this.chartRef.el.innerHTML = "";

      const config = {
        ...this.getChartConfig(),
        series: this.state.chartData.series,
      };

      try {
        this.chartInstance = new ApexCharts(this.chartRef.el, config);
        this.chartInstance.render();
      } catch (error) {
        console.error("Error rendering chart:", error);
      }
    }
  }

  ChartRenderer.template = "owl.ChartRenderer";
