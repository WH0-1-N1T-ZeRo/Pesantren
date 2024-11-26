from asyncio.log import logger
from odoo import api, fields, models


class ReportPenilaianAkhir(models.AbstractModel):
    _name   = 'report.pesantren_guru.penilaian_akhir'
    _inherit = 'report.report_xlsx.abstract'

    def filter(self,function,lists):
        return [x for x in lists if function(x)]
    def get_value(self,model,fields,i=0):
        if isinstance(model,models.Model):
            if len(fields) == i:
                return getattr(model,'name')
            else:
                return self.get_value(getattr(model,fields[i]),fields,i+1)
        if len(fields) == i:
            return model
        if len(fields)>i:
            return self.get_value(getattr(model,fields[i]),fields,i+1)
        return  getattr(model,fields[i])
    # TODO : loop direction
    def generate_cells(self,row,coll,cells_expr,model_tree):
        cells = []
        i = row
        for j,expr in enumerate(cells_expr):
             # * make sure expr has expr_value
            if expr[4]:
                if isinstance(expr[4],int):
                    cells.append((
                        i+1,j+coll,
                        i+1,j+coll,
                        expr[4]
                    ))
                elif len(expr[4].split('.')) < 2:
                    cells.append((
                        i+1,j+coll,
                        i+1,j+coll,
                        expr[4]
                    ))
                else:
                    expr_model = expr[4][0:(expr[4].find(expr[4].split('.')[-1])-1)]

                    # * find model in model_tree that match current expr_model
                    model = self.filter(lambda v: type(v).__name__ == expr_model,model_tree)

                    # * group expr[5] (field,val)
                    if expr[5]:
                        model = self.filter(lambda v:self.get_value(v,expr[5][0].split('.')) == expr[5][1],model)
                    # TODO : do something if no model found [done]
                    if model:
                        model = model[0]

                        cells.append((
                            i+1,j+coll,
                            i+1,j+coll,
                            self.get_value(model,[expr[4].split('.')[-1]])
                        ))
                    else:
                        cells.append((
                            i+1,j+coll,
                            i+1,j+coll,
                            '-'
                        ))
                        
            else:
                cells.append((
                    i+1,j+coll,
                    i+1,j+coll,
                    ''
                ))
        return cells

        
    def generate_xlsx_report(self,workbook,data,PenilaianAkhir):
        final_cells = []
        # columns (column final name, column name in odoo, group(column name in odoo, value))
        """
            TODO : make cells writer


            * cells_expr (
            *     row_from,
            *     col_from,
            *     row_to,
            *     col_to,
            *     expr_value,
            *     group
            *)
            * cells (
            *     row_from,
            *     col_from,
            *     row_to,
            *     col_to,
            *     value,
            *) 

            * main_model

            * process
            - loop generate cells, will define list variable to store main model and its sub model
            - and execute generate_cells method
            - method generate_cells(current_row,cells_expr,model_tree) this method generate cells from cells expression


        """
        cells_expr = [
            (2,0,2,0,'increament',0),
            (2,1,2,1,'cdn.penilaian_akhir.siswa_id',0),
            (2,2,2,2,0,0),
            (2,3,2,3,'cdn.penilaian_akhir.nis',0),
            (2,4,2,4,'cdn.penilaian_akhir.semester',0),
            (2,5,2,5,'cdn.penilaian_akhir.tahunajaran_id',0)
        ]
        MataPelajaran = self.env['cdn.mata_pelajaran'].search([], order='id asc')
        columns_nilai = [
            ('N.Kog','cdn.penilaian_akhir_lines.nilai1'),
            ('P.Kog','cdn.penilaian_akhir_lines.predikat1'),
            ('N.Psi','cdn.penilaian_akhir_lines.nilai2'),
            ('P.Psi','cdn.penilaian_akhir_lines.predikat2'),
            ('Religius','cdn.penilaian_akhir_lines.aspek1'),
            ('Etika','cdn.penilaian_akhir_lines.aspek2'),
            ('Kejujuran','cdn.penilaian_akhir_lines.aspek3'),
            ('Kepedulian','cdn.penilaian_akhir_lines.aspek4'),
            ('Kedisiplinan','cdn.penilaian_akhir_lines.aspek5'),
            ('Kemandirian','cdn.penilaian_akhir_lines.aspek6')
        ]
        # write header data siswa
        for i,header in enumerate(['No','Name','Program','NIS','Semester','Tahun Ajaran']):
            final_cells.append((
                0,i,
                0,i,
                header
            ))
        # write header nilai and expression for data nilai 
        for mapel in MataPelajaran:
            for cn in columns_nilai:
                lc = max(x[1] for x in cells_expr ) # last col
                lch = max(x[1] for x in final_cells) # last col header
                cells_expr.append((2,lc+1,2,lc+1,cn[1],('mapel_id.kode',mapel.kode)))
                final_cells.append((
                    0,lch+1,
                    0,lch+1,
                    '{} {}'.format(mapel.kode,cn[0])
                ))
        
        columns_ekstra = [
            ('Nama','cdn.penilaian_ekstrakulikuler.name'),
            ('Nilai','cdn.penilaian_ekstrakulikuler.nilai'),
            ('Predikat','cdn.penilaian_ekstrakulikuler.predikat'),
        ]

        save_points = []
        save_points.append(max(x[1] for x in final_cells))
        # write header ekstrakulikuler
        for ekstra in columns_ekstra:
            lch = max(x[1] for x in final_cells) # last col header
            final_cells.append((
                0,lch + 1,
                0,lch + 1,
                '{} Ekstra Wajib'.format(ekstra[0])
            ))
        save_points.append(max(x[1] for x in final_cells))
        save_points.append(max(x[1] for x in final_cells))
        for i in range(1,3):
            for ekstra in columns_ekstra:
                lch = max(x[1] for x in final_cells) # last col header
                final_cells.append((
                    0,lch + 1,
                    0,lch + 1,
                    '{} Ekstra Pilihan {}'.format(ekstra[0],i)
                ))
        save_points.append(max(x[1] for x in final_cells))
        column_organisasi = [
            ('Nama Organisasi','name'),
            ('Posisi Organisasi','position')
        ]
        save_points.append(max(x[1] for x in final_cells))
        # write header oraganisasi
        for i in range(1,4):
            for c in column_organisasi:
                lch = max(x[1] for x in final_cells) # last col header
                final_cells.append((
                    0,lch + 1,
                    0,lch + 1,
                    '{} {}'.format(c[0],i)
                ))
        save_points.append(max(x[1] for x in final_cells))

        column_absensi = [
            ('Jml Sakit','Sakit'),
            ('Jml Ijin','Ijin'),
            ('Jml Alpha','Alpha')
        ]
        save_points.append(max(x[1] for x in final_cells))
        for c in column_absensi:
            lch = max(x[1] for x in final_cells) # last col header
            final_cells.append((
                0,lch + 1,
                0,lch + 1,
                c[0]
            ))
        save_points.append(max(x[1] for x in final_cells))

        final_cells.append((
            0, save_points[7] + 1,
            0, save_points[7] + 1,
            'Catatan Wali Kelas'
        ))
        
        for z,pa in enumerate(PenilaianAkhir):
            ekstra_wajib = [x for x in pa.ekstrakulikuler_ids if x.is_wajib == True]
            ekstra = [x for x in pa.ekstrakulikuler_ids if x.is_wajib == False]

            for i in range(len(columns_ekstra)):
                fields = ['name','nilai','predikat']
                final_cells.append((
                    2 + z, save_points[0] + i +1,
                    2 + z, save_points[0] + i + 1,
                    ekstra_wajib[0][fields[i]]
                ))
            save_point = 0
            for j,e in enumerate(ekstra):
                for i in range(len(columns_ekstra)):
                    fields = ['name','nilai','predikat']
                    final_cells.append((
                        2 + z, save_points[2] + i+1 +(j*len(fields)),
                        2 + z, save_points[2] + i+1 +(j*len(fields)),
                        e[fields[i]]
                    ))
                    save_point = save_points[2] + i+1 +(j*len(fields))
            if (save_points[3] - save_point) > 0:
                for i in range(save_points[3]-save_point):
                    final_cells.append((
                        2 + z, save_point + i +1,
                        2 + z, save_point + i + 1,
                        '-'
                    ))
            
            for i,org in enumerate(pa.organisasi_ids):
                for j,c in enumerate(column_organisasi):
                    final_cells.append((
                        2 + z, save_points[4] + j+1 +(i*len(column_organisasi)),
                        2 + z, save_points[4] + j+1 +(i*len(column_organisasi)),
                        org[c[1]]
                    ))
                    save_point = save_points[4] + j +1 +(i*len(column_organisasi))
            if (save_points[5] - save_point) > 0:
                for i in range(save_points[5]-save_point):
                    final_cells.append((
                        2 + z, save_point + i + 1,
                        2 + z, save_point + i + 1,
                        '-'
                    ))
        
            AbsensiSiswaLine = self.env['cdn.absensi_siswa_lines'].search([('siswa_id','=',pa.siswa_id.id)])
            absensi = {
                'Sakit' : 0,
                'Ijin' : 0, 
                'Alpha' : 0
            }
            for absen in AbsensiSiswaLine:
                absensi[absen.kehadiran] += 1
            for i,a in enumerate(column_absensi):
                final_cells.append((
                    2 + z, save_points[6] + i + 1,
                    2 + z, save_points[6] + i + 1,
                    absensi[a[1]]
                ))

            final_cells.append((
                2 + z, save_points[7] + 1,
                2 + z, save_points[7] + 1,
                ''
            ))

        for i,pa in enumerate(PenilaianAkhir): # * loop generate cells
            model_tree = []
            # cdn.penilaian_akhir
            model_tree.append(pa)
            logger.info(model_tree)
            # cdn.penilaian_akhir_lines
            for lines in pa.penilaianakhir_ids:
                model_tree.append(lines)
            cells = self.generate_cells(i+1,0,cells_expr,model_tree)
            final_cells.extend(cells)



        ws = workbook.add_worksheet('test')
        ws.set_zoom(70)
        ws.freeze_panes(0, 2 )
        ws.set_column('A:A',4)
        ws.set_column('B:B',24)
        ws.set_column('C:F',13)
        # palettes
        colors = [
            '#d9e1f2', #blue
            '#ffc000', #yellow
            '#f4b084', #red
        ]
        colors2 = [
            '#dbdbdb', #Header Nama
            '#ffd966', #Yellow for No(header,value) Nama(Value)
            '#ffd966', #Yellow for Program
            '#bdd7ee', #blue NIS
            '#f4b084', #red Semester
            '#ffd966', #yellow Tahun Ajaran
        ]

        for c in final_cells:
            bg_color = 'white'
            if c[1] == 0 or c[1] == 1:
                bg_color = colors2[1]
            if c[0] == 0 and c[1] == 1:
                bg_color = colors2[0]
            if c[1] > 1 and c[1] < 6:
                bg_color = colors2[c[1]]
            if c[1] > 5:
                bg_color = colors[( (c[1]-5) // 11 ) % 3]
            
            # TODO : merge range
            proops = {
                'font_color':'black',
                'font_size':11,
                'font_name':'calibri',
                'bold':c[0]==0,
                'bg_color':bg_color,
                'align':'center',
                'valign':'vcenter',
                'border':1,
                'border_color':'black',
                'text_wrap':1
            }

            val = len(set().union(x[0] for x in final_cells if x[0] < c[0])) if c[4] == 'increament' else c[4]
            if c[0]==0: #merge header
                ws.merge_range(c[0],c[1],(c[0]+1),c[1],val,workbook.add_format(proops))
            else:
                ws.write(c[0],c[1],val,workbook.add_format(proops))

        # Grade / Predikat
        Predikat = self.env['cdn.predikat'].search([])
        r = max(x[0] for x in final_cells) + 2 # initial row
        c = 3
        predikat_cells = []
        for i,predikat in enumerate(Predikat):
            cells_expr = [
                (r,c,r,c,'cdn.predikat_lines.name',0),
                (r,c+1,r,c+1,'cdn.predikat_lines.min_nilai',0),
                (r,c+2,r,c+2,'cdn.predikat_lines.max_nilai',0),
            ]
            predikat_cells.append((
                r,c+(i*4),
                r,c+(i*4)+2,
                predikat.name
            ))
            for j,header in enumerate(['Pred','Min','Max']):
                predikat_cells.append((
                    r+1,c+(4*i)+j,
                    r+1,c+(i*4)+j,
                    header
                ))
            for j,line in enumerate(predikat.predikat_ids):
                predikat_cells.extend(self.generate_cells(r+j+1,c+(4*i),cells_expr,[line]))

        for cell in predikat_cells:
            bg_color = 'red' if cell[0]==r else colors[1]
            proops = {
                'font_color':'black',
                'font_size':11,
                'font_name':'calibri',
                'bold':cell[0]<=r+1,
                'bg_color':bg_color,
                'align':'center',
                'valign':'vcenter',
                'border':1,
                'border_color':'black',
                'text_wrap':1
            }
            if cell[0] != cell[2] or cell[1] != cell[3]:
                ws.merge_range(*cell,workbook.add_format(proops))
            else:
                ws.write(cell[0],cell[1],cell[4],workbook.add_format(proops))