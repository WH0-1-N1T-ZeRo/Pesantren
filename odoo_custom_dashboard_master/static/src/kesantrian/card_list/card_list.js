/** @odoo-module **/
import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PelanggaranCardList extends Component {
    static props = {
        startDate: { type: String, optional: true },
        endDate: { type: String, optional: true }
    };

    setup() {
        this.orm = useService('orm');
        this.actionService = useService('action');
        this.state = {
            pelanggarans: [],
            isLoading: true,
            hasData: false,
            currentStartDate: this.props.startDate,
            currentEndDate: this.props.endDate
        };

        onWillStart(async () => {
            await this.fetchPelanggaranSantri();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.startDate !== this.props.startDate || 
                nextProps.endDate !== this.props.endDate) {
                this.state.currentStartDate = nextProps.startDate;
                this.state.currentEndDate = nextProps.endDate;
                await this.fetchPelanggaranSantri();
            }
        });
    }

    async onPelanggaranRowClick(pelanggaran) {
        try {
            const pelanggaranRecord = await this.orm.searchRead(
                'cdn.pelanggaran', 
                [
                    ['siswa_id.name', '=', pelanggaran.student_name],
                    ['tgl_pelanggaran', '=', this.formatDateForSearch(pelanggaran.tanggal)],
                    ['pelanggaran_id.name', '=', pelanggaran.pelanggaran_name],
                    ['poin', '=', pelanggaran.points]
                ], 
                ['id', 'name']
            );
    
            if (pelanggaranRecord.length > 0) {

                this.actionService.doAction({
                    type: 'ir.actions.act_window',
                    res_model: 'cdn.pelanggaran',
                    res_id: pelanggaranRecord[0].id,
                    views: [[false, 'form']],
                    target: 'current'
                });
            } else {
                console.warn("No matching pelanggaran record found");
            }
        } catch (error) {
            console.error("Error navigating to pelanggaran record:", error);
        }
    }
    formatDateForSearch(dateStr) {
        if (!dateStr) return null;
        const [day, month, year] = dateStr.split('/');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }
    
    async fetchPelanggaranSantri() {
        try {
            this.state.isLoading = true;

            const filterDomain = [
                ['state', '=', 'approved'],
                ['poin', '>', 0]
            ];

            if (this.state.currentStartDate) {
                filterDomain.push(['tgl_pelanggaran', '>=', this.state.currentStartDate]);
            }
            if (this.state.currentEndDate) {
                filterDomain.push(['tgl_pelanggaran', '<=', this.state.currentEndDate]);
            }

            const pelanggaranRecords = await this.orm.searchRead(
                'cdn.pelanggaran',
                filterDomain,
                [
                    'siswa_id',
                    'pelanggaran_id',
                    'kategori',
                    'poin',
                    'tgl_pelanggaran',
                    'kelas_id',
                    'deskripsi'
                ],
                { 
                    order: 'create_date DESC, poin DESC'
                }
            );

            if (!pelanggaranRecords || pelanggaranRecords.length === 0) {
                this.state.hasData = false;
                this.state.pelanggarans = [];
                return;
            }

            const studentIds = [...new Set(pelanggaranRecords.map(p => p.siswa_id[0]))];
            const students = await this.orm.searchRead(
                'cdn.siswa',
                [['id', 'in', studentIds]],
                ['id', 'name', 'ruang_kelas_id']
            );
           
            const studentMap = new Map(students.map(s => [s.id, s]));

            this.state.pelanggarans = pelanggaranRecords
                .map(p => {
                    const pelanggaran = {
                        student_name: studentMap.get(p.siswa_id[0])?.name || "N/A",
                        pelanggaran_name: p.pelanggaran_id[1] || "N/A",
                        kategori: p.kategori || "N/A",
                        points: p.poin || 0,
                        tanggal: this.formatDate(p.tgl_pelanggaran),
                        kelas: p.kelas_id ? p.kelas_id[1] : "N/A",
                        deskripsi: p.deskripsi || ""
                    };
                    
                    pelanggaran.onClick = () => this.onPelanggaranRowClick(pelanggaran);
                    return pelanggaran;
                })
                .sort((a, b) => new Date(b.tanggal) - new Date(a.tanggal))
                .slice(0, 10);

            this.state.hasData = this.state.pelanggarans.length > 0;

        } catch (error) {
            console.error("Error fetching pelanggaran data:", error);
            this.state.pelanggarans = [];
            this.state.hasData = false;
        } finally {
            this.state.isLoading = false;
        }
    }

    formatDate(dateStr) {
        if (!dateStr) return "N/A";
        const date = new Date(dateStr);
        return date.toLocaleDateString('id-ID', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
}

PelanggaranCardList.template = 'owl.PelanggaranCardList';

export class TahfidzCardList extends Component {
    static props = {
        startDate: { type: String, optional: true },
        endDate: { type: String, optional: true }
    };

    setup() {
        this.orm = useService('orm');
        this.actionService = useService('action');
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

    async onTahfidzRowClick(tahfidz) {
        try {
            const tahfidzRecord = await this.orm.searchRead(
                'cdn.tahfidz_quran', 
                [
                    ['siswa_id.name', '=', tahfidz.name],
                    ['jml_baris', '=', tahfidz.total_baris]
                ], 
                ['id']
            );
    
            if (tahfidzRecord.length > 0) {

                this.actionService.doAction({
                    type: 'ir.actions.act_window',
                    res_model: 'cdn.tahfidz_quran',
                    res_id: tahfidzRecord[0].id,
                    views: [[false, 'form']],
                    target: 'current'
                });
            }
        } catch (error) {
            console.error("Error navigating to tahfidz record:", error);
        }
    }

    async fetchTahfidzTertinggi() {
        try {
            this.state.isLoading = true;
    
            const filterDomain = [
                ['state', '=', 'done'],
                ['siswa_id', '!=', false],
                ['jml_baris', '>', 0]
            ];
    
            if (this.state.currentStartDate) {
                filterDomain.push(['tanggal', '>=', this.state.currentStartDate]);
            }
            if (this.state.currentEndDate) {
                filterDomain.push(['tanggal', '<=', this.state.currentEndDate]);
            }
    
            const tahfidzRecords = await this.orm.searchRead(
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
    
            if (!tahfidzRecords || tahfidzRecords.length === 0) {
                this.state.hasData = false;
                this.state.topTahfidz = [];
                return;
            }
    
            const studentTahfidz = {};
            tahfidzRecords.forEach(record => {
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
    
            let sortedData = Object.entries(studentTahfidz)
                .map(([name, data]) => ({
                    name: name,
                    total_baris: data.jml_baris,
                    kelas: data.kelas
                }))
                .sort((a, b) => b.total_baris - a.total_baris)
                .slice(0, 10);
    
            this.state.topTahfidz = sortedData.map((item, index) => {
                const tahfidz = {
                    number: index + 1,
                    ...item
                };
                
                tahfidz.onClick = () => this.onTahfidzRowClick(tahfidz);
                return tahfidz;
            });
    
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

TahfidzCardList.template = 'owl.TahfidzCardList';