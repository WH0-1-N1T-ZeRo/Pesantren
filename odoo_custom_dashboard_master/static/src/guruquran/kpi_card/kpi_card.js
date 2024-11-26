/** @odoo-module **/
const { Component, onWillStart, onMounted, onWillUpdateProps, onWillUnmount } = owl;
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session"; 

export class GuruquranKpiCard extends Component {
    setup() {
        this.orm = useService('orm');
        this.actionService = useService('action');

        this.state = {
            kpiData: [],
            animations: {},
            currentStartDate: this.props.startDate,
            currentEndDate: this.props.endDate,
            isFiltered: false
        };

        // Countdown related properties
        this.countdownInterval = null;
        this.countdownTime = 10;
        this.isCountingDown = false;

        // Set default dates if not provided
        const today = new Date();
        const firstDayOfYear = new Date(today.getFullYear(), 0, 1);
        
        this.defaultStartDate = firstDayOfYear.toISOString().split('T')[0];
        this.defaultEndDate = today.toISOString().split('T')[0];

        if (this.props.startDate && this.props.endDate) {
            this.state.isFiltered = true;
        }

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                this.state.isFiltered = !!(nextProps.startDate && nextProps.endDate);
                await this.fetchData();
            }
        });

        onMounted(() => {
            const timerButton = document.getElementById("timerButton");
            if (timerButton) {
                timerButton.addEventListener("click", () => this.handleTimerClick());
            }
            this.startKpiAnimations();
        });

        onWillStart(async () => {
        try {
            await this.fetchData(
                this.state.currentStartDate || this.defaultStartDate,
                this.state.currentEndDate || this.defaultEndDate
            );
        } catch (error) {
            console.error("Failed to fetch KPI data:", error);
        }
        });

        onWillUnmount(() => {
            this.cleanup();
            const timerButton = document.getElementById("timerButton");
            if (timerButton) {
                timerButton.removeEventListener("click", () => this.handleTimerClick());
            }
        });
    }

    handleTimerClick() {
        if (this.isCountingDown) {
            this.stopCountdown();
        } else {
            this.startCountdown();
        }
        this.isCountingDown = !this.isCountingDown;
    }

    startCountdown() {
        this.countdownTime = 10;
        this.updateTimerUI();
        this.countdownInterval = setInterval(() => {
            this.countdownTime--;
            if (this.countdownTime < 0) {
                this.countdownTime = 10;
                this.refreshData();
            }
            this.updateTimerUI();
        }, 1000);
    }

    stopCountdown() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        this.updateTimerUI(true);
    }

    updateTimerUI(stopped = false) {
        const timerIcon = document.getElementById("timerIcon");
        const timerCountdown = document.getElementById("timerCountdown");
        
        if (timerIcon) {
            timerIcon.className = stopped ? "fas fa-stopwatch" : "fas fa-stop d-none";
        }
        if (timerCountdown) {
            timerCountdown.textContent = stopped ? "" : this.countdownTime;
        }
    }

    cleanup() {
        this.stopCountdown();
        Object.values(this.state.animations).forEach(animationId => {
            cancelAnimationFrame(animationId);
        });
        this.state.animations = {};
    }

    startKpiAnimations() {
        this.state.kpiData.forEach((kpi, index) => {
            const countElement = document.getElementById(`counter-${index}`);
            if (countElement) {
                this.animateNumber(countElement, 0, kpi.value);
            }
        });
    }

    animateNumber(element, start, end, duration = 500) {
        if (!element) return;
        
        const range = end - start;
        const minFrame = 16;
        const steps = Math.max(Math.floor(duration / minFrame), 1);
        const increment = range / steps;
        let current = start;
        let step = 0;

        const animationKey = element.id;
        if (this.state.animations[animationKey]) {
            cancelAnimationFrame(this.state.animations[animationKey]);
        }

        const animate = () => {
            step++;
            current += increment;
            
            if (step <= steps) {
                element.textContent = Math.round(current).toLocaleString();
                this.state.animations[animationKey] = requestAnimationFrame(animate);
            } else {
                element.textContent = Math.round(end).toLocaleString();
                delete this.state.animations[animationKey];
            }
        };

        this.state.animations[animationKey] = requestAnimationFrame(animate);
    }

    async fetchData() {
        try {
            const startDate = this.state.currentStartDate || this.defaultStartDate;
            const endDate = this.state.currentEndDate || this.defaultEndDate;
    
            const dateDomain = [
                ['name', '>=', startDate],
                ['name', '<=', endDate],
                ['state', 'in', ['Proses', 'Done']],
                ["penanggung_jawab_id","ilike",session.partner_display_name]
            ];
    
            // Fetch data for Tahfidz and Tahsin
            const [tahfidzData, tahsinData] = await Promise.all([
                this.orm.call(
                    'cdn.absen_tahfidz_quran',
                    'search_read',
                    [dateDomain],
                    {
                        fields: ['name', 'absen_ids'],
                        context: this.env.context
                    }
                ),
                this.orm.call(
                    'cdn.absen_tahsin_quran',
                    'search_read',
                    [dateDomain],
                    {
                        fields: ['name', 'absen_ids'],
                        context: this.env.context
                    }
                )
            ]);
    
            // Extract absen IDs safely
            const tahfidzAbsenIds = tahfidzData?.flatMap(t => t.absen_ids) || [];
            const tahsinAbsenIds = tahsinData?.flatMap(t => t.absen_ids) || [];
    
            // Fetch Alpa counts if absen IDs are available
            let tahfidzAlpaCount = 0;
            let tahsinAlpaCount = 0;
    
            if (tahfidzAbsenIds.length > 0) {
                tahfidzAlpaCount = await this.orm.call(
                    'cdn.absen_tahfidz_quran_line',
                    'search_count',
                    [[
                        ['id', 'in', tahfidzAbsenIds],
                        ['kehadiran', '=', 'Alpa']
                    ]],
                    { context: this.env.context }
                );
            }
    
            if (tahsinAbsenIds.length > 0) {
                tahsinAlpaCount = await this.orm.call(
                    'cdn.absen_tahsin_quran_line',
                    'search_count',
                    [[
                        ['id', 'in', tahsinAbsenIds],
                        ['kehadiran', '=', 'Alpa']
                    ]],
                    { context: this.env.context }
                );
            }
    
            // Update KPI data
            this.state.kpiData = [
                {
                    name: 'Absen Tahfidz',
                    value: tahfidzData?.length || 0,
                    icon: 'fa-book-open',
                    color: '#00e396',
                    res_model: 'cdn.absen_tahfidz_quran',
                    domain: dateDomain,
                },
                {
                    name: 'Santri Tahfidz Alpa',
                    value: tahfidzAlpaCount,
                    icon: 'fa-calendar-times',
                    color: '#00e396',
                    res_model: 'cdn.absen_tahfidz_quran_line',
                    domain: tahfidzAbsenIds.length > 0 ? [
                        ['id', 'in', tahfidzAbsenIds],
                        ['kehadiran', '=', 'Alpa']
                    ] : [['id', '=', -1]], // Impossible domain when no data
                },
                {
                    name: 'Absen Tahsin',
                    value: tahsinData?.length || 0,
                    icon: 'fa-book-open',
                    color: '#00e396',
                    res_model: 'cdn.absen_tahsin_quran',
                    domain: dateDomain,
                },
                {
                    name: 'Santri Tahsin Alpa',
                    value: tahsinAlpaCount,
                    icon: 'fa-calendar-times',
                    color: '#00e396',
                    res_model: 'cdn.absen_tahsin_quran_line',
                    domain: tahsinAbsenIds.length > 0 ? [
                        ['id', 'in', tahsinAbsenIds],
                        ['kehadiran', '=', 'Alpa']
                    ] : [['id', '=', -1]], // Impossible domain when no data
                },
            ];
    
            // Start animations if there is any valid KPI value
            if (this.state.kpiData.some(kpi => kpi.value >= 0)) {
                this.startKpiAnimations();
            }
    
        } catch (error) {
            console.error('Error in fetchData:', error);
            // Reset KPI data to 0 on error
            this.state.kpiData = [
                { name: 'Absen Tahfidz', value: 0 },
                { name: 'Santri Tahfidz Alpa', value: 0 },
                { name: 'Absen Tahsin', value: 0 },
                { name: 'Santri Tahsin Alpa', value: 0 },
            ];
        }
    }
    

    async refreshData() {
        const startDate = this.state.isFiltered ? this.state.currentStartDate : this.defaultStartDate;
        const endDate = this.state.isFiltered ? this.state.currentEndDate : this.defaultEndDate;
        await this.fetchData(startDate, endDate);
    }

    attachEventListeners() {
        // Attach existing listeners
        const kpiCards = document.querySelectorAll('.kpi-card');
        kpiCards.forEach(card => {
            card.addEventListener('click', (evt) => {
                this.handleKpiCardClick(evt);
            });
        });

        // Add timer button listener
        const timerButton = document.getElementById("kpiTimerButton");
        if (timerButton) {
            timerButton.addEventListener("click", this.toggleCountdown.bind(this));
        }
    }

    handleKpiCardClick(evt) {
        const cardName = evt.currentTarget.dataset.name;
        const cardData = this.state.kpiData.find(kpi => kpi.name === cardName);

        if (cardData) {
            const { res_model, domain } = cardData;

            this.actionService.doAction({
                name: cardName,
                type: 'ir.actions.act_window',
                res_model: res_model,
                view_mode: 'list,form',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',
                domain: domain,
            });
        }
    }
}

GuruquranKpiCard.template = "owl.GuruquranKpiCard";

GuruquranKpiCard.props = {
    startDate: { type: String, optional: true },
    endDate: { type: String, optional: true },
};