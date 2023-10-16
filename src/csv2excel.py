from xlsxwriter.workbook import Workbook
from src.file_format import load_csv
from pathlib import Path


def csv2excel(csv_file_path):
    csv_file_path = Path(csv_file_path).resolve()
    excel_file_path = (csv_file_path.parent / f'{csv_file_path.stem}.xlsx')
    print(excel_file_path)
    tables2excel([{
        'name': csv_file_path.stem,
        'table': load_csv(csv_file_path, converters=[])
    }], excel_file_path)


def tables2excel(table_info_list, excel_file_path):

    workbook = Workbook(str(excel_file_path))

    for table_info in table_info_list:
        table_name = table_info['name']
        table = table_info['table']
        headers = table_info.get('headers')

        if not headers:
            # TODO, use the csv header detector
            # TODO, the header detector is for any table format
            headers = table[0].keys()

        sheet = workbook.add_worksheet(table_name)

        for c_idx, header in enumerate(headers):
            sheet.write(0, c_idx, header)

        for r_idx, row in enumerate(table):
            for c_idx, header in enumerate(headers):
                value = row.get(header, '')

                value, cell_format = get_cell_format(value, workbook)

                if not cell_format:
                    sheet.write_string(r_idx + 1, c_idx, str(value))
                else:
                    sheet.write(r_idx + 1, c_idx, value, cell_format)

    workbook.close()


# TODO, detect format then convert, maybe using some regular expression
def get_cell_format(value, workbook):

    cell_format = workbook.add_format()

    try:
        float(value)
        cell_format.set_num_format('General')
        return float(value), cell_format
    except ValueError:
        pass

    if not value.endswith('%'):
        return value, None

    pcnt_number = value[:-1]

    # TODO seperate the num and pcnt, test if it's a percent column
    try:
        pcnt_number = float(pcnt_number)
        if pcnt_number >= 1:
            cell_format.set_num_format('0%')
        elif pcnt_number >= 0.1:
            cell_format.set_num_format('0.0%')
        else:
            cell_format.set_num_format('0.00%')
        return pcnt_number / 100, cell_format
    except ValueError:
        pass

    return value, None
