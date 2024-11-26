/** @odoo-module **/
import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class GuruquranTahsinCardList extends Component {
    static props = {
        startDate: { type: String, optional: true },
        endDate: { type: String, optional: true }
    };

    setup() {
        this.orm = useService('orm');
        this.state = {
            tahsinData: [],
            isLoading: true,
            hasData: false,
            currentStartDate: this.props.startDate,
            currentEndDate: this.props.endDate,
        };

        onWillStart(async () => {
            await this.fetchTahsinData();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                await this.fetchTahsinData();
            }
        });
    }

    async fetchTahsinData() {
        try {
            this.state.isLoading = true;
    
            const filterDomain = [
                ['state', '=', 'done'],
                ["penanggung_jawab_id", "ilike", session.partner_display_name]
            ];
    
            if (this.state.currentStartDate) {
                filterDomain.push(['tanggal', '>=', this.state.currentStartDate]);
            }
            if (this.state.currentEndDate) {
                filterDomain.push(['tanggal', '<=', this.state.currentEndDate]);
            }
    
            const tahsinData = await this.orm.searchRead(
                'cdn.tahsin_quran',
                filterDomain,
                [
                    'tanggal',
                    'siswa_id',
                    'buku_tahsin_id',
                    'jilid_tahsin_id',
                    'halaman_tahsin',
                    'state'
                ],
                { order: 'tanggal desc' }
            );
    
            if (!tahsinData || tahsinData.length === 0) {
                this.state.hasData = false;
                this.state.tahsinData = [];
                return;
            }
    
            // Process and structure the data
            const processedData = tahsinData.map(record => ({
                student_name: record.siswa_id[1],
                date: record.tanggal,
                book: record.buku_tahsin_id ? record.buku_tahsin_id[1] : 'N/A',
                volume: record.jilid_tahsin_id ? record.jilid_tahsin_id[1] : 'N/A',
                page: record.halaman_tahsin || 'N/A'
            }));

            // Group by student and get their latest entry
            const studentLatestEntries = {};
            processedData.forEach(record => {
                const studentName = record.student_name;
                if (!studentLatestEntries[studentName] || 
                    new Date(record.date) > new Date(studentLatestEntries[studentName].date)) {
                    studentLatestEntries[studentName] = record;
                }
            });
    
            // Convert to array and sort by date (most recent first)
            this.state.tahsinData = Object.values(studentLatestEntries)
                .sort((a, b) => new Date(b.date) - new Date(a.date))
                .map((item, index) => ({
                    number: index + 1,
                    ...item
                }));
    
            this.state.hasData = this.state.tahsinData.length > 0;
    
        } catch (error) {
            console.error("Error fetching tahsin data:", error);
            this.state.tahsinData = [];
            this.state.hasData = false;
        } finally {
            this.state.isLoading = false;
        }
    }
}

GuruquranTahsinCardList.template = 'owl.GuruquranTahsinCardList';

export class GuruquranTahfidzCardList extends Component {
    static props = {
        startDate: { type: String, optional: true },
        endDate: { type: String, optional: true }
    };

    setup() {
        this.orm = useService('orm');
        this.state = {
            topTahfidz: [],
            isLoading: true,
            hasData: false,
            currentStartDate: this.props.startDate,
            currentEndDate: this.props.endDate
        };

        onWillStart(async () => {
            await this.fetchTahfidzTertinggi();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                await this.fetchTahfidzTertinggi();
            }
        });
    }

    async fetchTahfidzTertinggi() {
        try {
            this.state.isLoading = true;
    
            const filterDomain = [
                ['state', '=', 'done'],
                ['siswa_id', '!=', false],
                ['jml_baris', '>', 0],
                ["penanggung_jawab_id", "ilike", session.partner_display_name]
            ];
    
            if (this.state.currentStartDate) {
                filterDomain.push(['tanggal', '>=', this.state.currentStartDate]);
            }
            if (this.state.currentEndDate) {
                filterDomain.push(['tanggal', '<=', this.state.currentEndDate]);
            }
    
            const tahfidzData = await this.orm.searchRead(
                'cdn.tahfidz_quran',
                filterDomain,
                [
                    'siswa_id',
                    'halaqoh_id',
                    'jml_baris',
                    'state',
                    'tanggal'
                ],
                { order: 'jml_baris desc' }
            );
    
            if (!tahfidzData || tahfidzData.length === 0) {
                this.state.hasData = false;
                this.state.topTahfidz = [];
                return;
            }
    
            // Group by student name and get their highest jml_baris
            const studentTahfidz = {};
            tahfidzData.forEach(record => {
                if (record.jml_baris > 0) {
                    const studentName = record.siswa_id[1];
                    if (!studentTahfidz[studentName] || studentTahfidz[studentName].jml_baris < record.jml_baris) {
                        studentTahfidz[studentName] = {
                            student_name: studentName,
                            jml_baris: record.jml_baris,
                            kelas: record.halaqoh_id ? record.halaqoh_id[1] : "N/A"
                        };
                    }
                }
            });
    
            // Convert to array, sort by jml_baris, and apply sequential numbering
            let sortedData = Object.entries(studentTahfidz)
                .map(([name, data]) => ({
                    name: name,
                    total_baris: data.jml_baris,
                    kelas: data.kelas
                }))
                .sort((a, b) => b.total_baris - a.total_baris)
                .slice(0, 5);
    
            // Apply sequential numbering after sorting
            this.state.topTahfidz = sortedData.map((item, index) => ({
                number: index + 1,
                ...item
            }));
    
            this.state.hasData = this.state.topTahfidz.length > 0;
    
        } catch (error) {
            console.error("Error fetching tahfidz data:", error);
            this.state.topTahfidz = [];
            this.state.hasData = false;
        } finally {
            this.state.isLoading = false;
        }
    }
}

GuruquranTahfidzCardList.template = 'owl.GuruquranTahfidzCardList';