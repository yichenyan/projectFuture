from django.shortcuts import render
from django.db import transaction
import xlrd
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from bokeh.io import show, output_notebook
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, NumeralTickFormatter, \
    LinearAxis, Range1d,LabelSet, ColumnDataSource, FixedTicker, Label, Legend
from bokeh.layouts import column
from numbers import Number
from math import pi

from .models import DartOpsReport
from .form import UploadOpsDataForm
#from .modelform import UploadFileModelForm


def UploadExcel(request):

    # 这个函数用于检查excel表单元格中的值是否是特殊字符，以及调整空值的数据类型，因为xlrd从表格中读出的值是遵循原始格式的
    def symbol_check(theValue):
        if isinstance(theValue,str) and theValue.strip() in ['-','']:  # 
            theValue = 0
        elif isinstance(theValue,int) and theValue in ['']:
            theValue = 0
        return theValue

    # 初始化表格的点睛之笔：request.Post or None, request.FILES or None
    myform = UploadOpsDataForm(request.POST or None, request.FILES or None)
    if myform.is_valid():
        uploaded_excel = request.FILES.get('myfile')  # myfile是form中定义的FileField的值，如果在template的template中即form中的name属性
        print(uploaded_excel)

        excel_type = uploaded_excel.name.split('.')[-1].strip()  # 读取一个excel文件的扩展名，xls还是xlsx等。。。
        if excel_type in ['xls']:
            excel_data = xlrd.open_workbook(filename=None, file_contents=uploaded_excel.read(), formatting_info=True)   # xls文件
            print('1')
            #print(excel_data.sheets())
        elif excel_type in ['xlsx']:
            excel_data = xlrd.open_workbook(filename=None, file_contents=uploaded_excel.read())
            #print(excel_data.sheets())
            print('2')
        else:
            print("Are you sure it is an EXCEL file?")
            excel_data = False

        sheet = excel_data.sheets()[0]  # wb里的第一个sheet
        rows = sheet.nrows  # 总行数
        cols = sheet.ncols  # 总列数
        header_count = 1  # 前几行是表头，不用导入数据库

        # 开始尝试将表格导入数据库
        try:
            with transaction.atomic():  #控制数据库事务交易
                # 读出excel表中的每一行数据变成row_values列表
                for row in range(header_count,rows):
                    print("This is row # {row} from the spreadsheet...".format(row=row))
                    row_values = sheet.row_values(row)  # row_values是一个列表
                    #print(row_values[1])

                    # 如果想插入的数据是空值，或在表中已经存在，则跳过这行 
                    target_data = row_values[9]  # 关注这个数据：flight_id
                    value_existed = DartOpsReport.objects.filter(flight_id = symbol_check(target_data))
                    if str(target_data).strip() == '' or value_existed.count():
                        print("This is not a valid record or it has existed in the database...")
                        continue

                    # 确认插入的数据不会重复后，将该行excel数据插入数据表中，其中的列来自于并同名与models，必须贴合实际excel中列的含义，避免excel格式变更带来的问题
                    DartOpsReport.objects.create(
                        operator = symbol_check(row_values[1]),
                        aircraft = symbol_check(row_values[2]),
                        aircraft_type = symbol_check(row_values[4]),
                        flight_type = symbol_check(row_values[5]),
                        antenna_type = symbol_check(row_values[6]),
                        xid = symbol_check(row_values[7]),
                        bc_gen = symbol_check(row_values[8]),
                        flight_id = symbol_check(row_values[9]),  # flight_id是表中必须唯一的
                        flight_num = symbol_check(row_values[10]),
                        excluded = symbol_check(row_values[11]),
                        exclusion_reason = symbol_check(row_values[12]),
                        departure_airport = symbol_check(row_values[13]),
                        arrival_airport = symbol_check(row_values[14]),
                        departure_time = symbol_check(row_values[15]),
                        arrival_time = symbol_check(row_values[16]),
                        flight_time = symbol_check(row_values[17]),
                        connected_sec = symbol_check(row_values[19]),
                        connected_sec_expected = symbol_check(row_values[21]),
                        avail_raw = symbol_check(row_values[23]),
                        avail_calibrated = symbol_check(row_values[24]),
                        latency = symbol_check(row_values[25]),
                        latency_std = symbol_check(row_values[26]),
                        packet_loss = symbol_check(row_values[27]),
                        packet_loss_std = symbol_check(row_values[28]),
                        beam_switch_count = symbol_check(row_values[29]),
                        beam_switch_average_sec = symbol_check(row_values[30]),
                        beam_switch_excluded_sec = symbol_check(row_values[32]),
                        kbpu = symbol_check(row_values[37]),
                        device_count = symbol_check(row_values[38])
                    )
            return render(request, 'upload/upload_success.html')  # 成功后返回成功页面

        except Exception as e:
            print("Something went wrong when importing excel data to the database...")
            print(e)
            myform = UploadOpsDataForm()

    template_name = 'upload/upload.html'
    content = {'form':myform}
    return render(request,template_name,content)

    

def SlaReport(request):
    qs = OpsData.objects.all()
    template_name = 'sla/sla_report.html'
    content = {'sla',qs}
    return render(request,template_name,content)

# 定义2个将十进制和百分数相互转换的函数
def decimal2percent(v, precision='0.2'):  
    """Convert number to percentage string."""
    if isinstance(v, Number):
        return "{{:{}%}}".format(precision).format(v)
    else:
        raise TypeError("Numeric type required")

def percent2decimal(x):
    return float(x.strip('%'))/100



def create_detailed_plots(df):

    #color_avail_gen1 = '#005792'
    color_avail_gen1 = 'steelblue'
    #color_avail_gen3 = '#cf455c'
    color_avail_gen3 = 'seagreen'
    color_flight_count = '#fdb44b'

    airline_list = df.operator.unique().tolist()
    for airline in airline_list:
        sla_airline = df[df.operator == airline].pivot_table(index=['aircraft','bc_gen'],\
            values=["connected_sec","connected_sec_expected","flight_num","latency","packet_loss"],fill_value=0,\
            aggfunc={"connected_sec":np.sum,"connected_sec_expected":"sum","flight_num":'count',"latency":np.mean,"packet_loss":np.mean})
        
        sla_airline['Availability_decimal'] = sla_airline['connected_sec']/sla_airline['connected_sec_expected']
        sla_airline['Availability'] = sla_airline['Availability_decimal'].apply(decimal2percent)
        sla_airline['Operator'] = airline
        sla_report = pd.DataFrame(sla_airline.to_records())

        sla_report = sla_report.rename(index=str, columns={\
            #"operator": "Operator", \
            "aircraft": "Aircraft",\
            "bc_gen": "Gen",\
            "flight_num": "Flight_Count",\
            "connected_sec_expected": "SLA_Expected",\
            "connected_sec": "SLA_Actual",\
            "latency": "Latency",
            "packet_loss": "Packet_Loss"})

        sla_report_sorted = sla_report.sort_values('Availability_decimal',ascending=True)

        sla_report_Gen1 = sla_report_sorted[sla_report['Gen']=="GEN1"]
        sla_report_Gen3 = sla_report_sorted[sla_report['Gen']=="GEN3"]
        #print(sla_report_Gen1,sla_report_Gen3)
        
        plot_list = []
        # Convert dataframe column data to a list -- the tolist() function
        if sla_report_Gen1.empty == False:  # Gen1机队存在
            operator_list_gen1 = sla_report_Gen1['Operator'].tolist()
            aircraft_list_gen1 = sla_report_Gen1['Aircraft'].tolist()
            flight_count_gen1 = sla_report_Gen1['Flight_Count'].tolist()
            gen_list_gen1 = list(sla_report_Gen1['Gen'].tolist())
            avail_percent_list_gen1 = sla_report_Gen1['Availability'].tolist()
            avail_decimal_list_gen1 = sla_report_Gen1['Availability_decimal'].tolist()
            latency_list_gen1 = sla_report_Gen1['Latency'].tolist()
            packet_loss_list_gen1 = sla_report_Gen1['Packet_Loss'].tolist()
            
            p_gen1 = figure(x_range=aircraft_list_gen1,plot_height=300,plot_width=18*len(aircraft_list_gen1)+100,\
                title="{airline} Gen1 SLA Details".format(airline=airline))

            # 定义主轴(y轴)图形
            p_gen1.vbar(aircraft_list_gen1, top=avail_decimal_list_gen1,width=0.8,\
                fill_color=color_avail_gen1,line_color=color_avail_gen1,legend='FT Avail')
            # 定义主轴范围
            p_gen1.y_range = Range1d(start=int((min(avail_decimal_list_gen1))*10)/10, end=1)
            # 主轴标签改为百分比格式
            p_gen1.yaxis.formatter = NumeralTickFormatter(format="0%")
            # 定义主轴标签名
            #p_gen1.yaxis.axis_label = "Flight Time Availability"

            # 给主轴的每个数据点插入标签
            source = ColumnDataSource(data=dict(aircraft_list_gen1=aircraft_list_gen1, \
                avail_decimal_list_gen1=avail_decimal_list_gen1, \
                avail_percent_list_gen1=avail_percent_list_gen1,\
                flight_count_gen1=flight_count_gen1))

            label_avail = LabelSet(x='aircraft_list_gen1', y='avail_decimal_list_gen1',\
                text='avail_percent_list_gen1',\
                source=source,\
                render_mode='canvas',\
                text_font_size='6pt',angle=pi/2,text_color='white',\
                x_offset=4, y_offset=-30)

            p_gen1.add_layout(label_avail)

            # 给副轴数据点插入标签，还没搞懂。。。
            """
            label_flight_count = LabelSet(x='aircraft_list_gen1', y='flight_count_gen1',\
                text='flight_count_gen1',\
                source=source,\
                render_mode='css',\
                text_font_size='6pt',text_color=color_flight_count,\
                x_offset=4, y_offset=-30
                )
            """

            
            # 定义多个副轴(y轴)的名字和范围
            p_gen1.extra_y_ranges = {"Flight_Count": Range1d(start=0, end=200),\
                "Latency": Range1d(start=500, end=1500),
                "Packet_Loss": Range1d(start=0, end=10)}
            # 定义各副轴的图形和标签
            p_gen1.circle(aircraft_list_gen1,flight_count_gen1,color='darkgray',y_range_name="Flight_Count",legend='Flight Count')
            p_gen1.square(aircraft_list_gen1,latency_list_gen1,color='gold',y_range_name="Latency",legend='Latency')
            p_gen1.x(aircraft_list_gen1,packet_loss_list_gen1,color='black',y_range_name="Packet_Loss",legend='Packet Loss')

            # 将副轴加入现有图表中
            #p_gen1.add_layout(LinearAxis(y_range_name="Flight_Count",axis_label='Flight Count'), 'right')


            # 主轴副轴标签字体设置
            p_gen1.yaxis.axis_label_text_font_style = "bold"
            
            # x轴文字标签旋转
            p_gen1.xaxis.major_label_orientation = 1
            # x轴取消网格线
            p_gen1.xgrid.grid_line_color = None

            # 设置legend
            p_gen1.legend.orientation = "horizontal"
            p_gen1.legend.location = "top_left"
            p_gen1.legend.label_text_font_size = "6pt"
            p_gen1.legend.border_line_alpha = 0.5


            plot_list.append(p_gen1)

        if sla_report_Gen3.empty == False:  # Gen3机队存在
            operator_list_gen3 = sla_report_Gen3['Operator'].tolist()
            aircraft_list_gen3 = sla_report_Gen3['Aircraft'].tolist()
            flight_count_gen3 = sla_report_Gen3['Flight_Count'].tolist()
            gen_list_gen3 = list(sla_report_Gen3['Gen'].tolist())
            avail_percent_list_gen3 = sla_report_Gen3['Availability'].tolist()
            avail_decimal_list_gen3 = sla_report_Gen3['Availability_decimal'].tolist()
            latency_list_gen3 = sla_report_Gen3['Latency'].tolist()
            packet_loss_list_gen3 = sla_report_Gen3['Packet_Loss'].tolist()
            #print(aircraft_list_gen3)

            p_gen3 = figure(x_range=aircraft_list_gen3,plot_height=300,plot_width=18*len(aircraft_list_gen3)+100,\
                title="{airline} Gen3 SLA Details".format(airline=airline))

            # 定义主轴(y轴)图形
            p_gen3.vbar(aircraft_list_gen3, top=avail_decimal_list_gen3,width=0.8,fill_color=color_avail_gen3,line_color=color_avail_gen3,legend='Availability')
            # 定义主轴范围
            p_gen3.y_range = Range1d(start=int((min(avail_decimal_list_gen3))*10)/10, end=1)
            # 主轴标签改为百分比格式
            p_gen3.yaxis.formatter = NumeralTickFormatter(format="0%")
            # 定义主轴标签名
            #p_gen3.yaxis.axis_label = "Flight Time Availability"

            # 给主轴的每个数据点插入标签
            source = ColumnDataSource(data=dict(aircraft_list_gen3=aircraft_list_gen3, \
                avail_decimal_list_gen3=avail_decimal_list_gen3, \
                avail_percent_list_gen3=avail_percent_list_gen3,\
                flight_count_gen3=flight_count_gen3))

            label_avail = LabelSet(x='aircraft_list_gen3', y='avail_decimal_list_gen3',\
                text='avail_percent_list_gen3',\
                source=source,\
                render_mode='canvas',\
                text_font_size='6pt',angle=pi/2,text_color='white',\
                x_offset=4, y_offset=-30)

            p_gen3.add_layout(label_avail)
            

            # 定义多个副轴(y轴)的名字和范围
            p_gen3.extra_y_ranges = {"Flight_Count": Range1d(start=0, end=200),\
                "Latency": Range1d(start=500, end=1500),
                "Packet_Loss": Range1d(start=0, end=10)}
            # 定义各副轴的图形和标签
            p_gen3.circle(aircraft_list_gen3,flight_count_gen3,color='darkgray',y_range_name="Flight_Count",legend='Flight Count')
            p_gen3.square(aircraft_list_gen3,latency_list_gen3,color='gold',y_range_name="Latency",legend='Latency')
            p_gen3.x(aircraft_list_gen3,packet_loss_list_gen3,color='black',y_range_name="Packet_Loss",legend='Packet Loss')

            # 将副轴加入现有图表中
            #p_gen3.add_layout(LinearAxis(y_range_name="Flight_Count",axis_label='Flight Count'), 'right')
            #p_gen3.add_layout(LinearAxis(y_range_name="Flight_Count"), 'right')


            # 主轴副轴标签字体设置
            p_gen3.yaxis.axis_label_text_font_style = "bold"
            # x轴文字标签旋转
            p_gen3.xaxis.major_label_orientation = 1
            # x轴取消网格线
            p_gen3.xgrid.grid_line_color = None

            # 设置legend
            p_gen3.legend.orientation = "horizontal"
            p_gen3.legend.location = "bottom_right"
            p_gen3.legend.label_text_font_size = "6pt"
            p_gen3.legend.border_line_alpha = 0.5

            plot_list.append(p_gen3)

        
        return column(plot_list)
        
        break


def create_overview_plot(df):

    # 2. 用pandas对进行data cleaning
    df_overview = df.pivot_table(index=["operator"],\
        values=["connected_sec","connected_sec_expected","flight_num"],fill_value=0,\
        aggfunc={"connected_sec":np.sum,"connected_sec_expected":"sum","flight_num":'count'})
    
    df_overview['Availability_decimal'] = df_overview['connected_sec']/df_overview['connected_sec_expected']
    df_overview['Availability'] = df_overview['Availability_decimal'].apply(decimal2percent)

    # 将透视表转换回普通表格 -- to_records() function
    sla_report = pd.DataFrame(df_overview.to_records())

    # Rename the columns to easily understandable names
    sla_report = sla_report.rename(index=str, columns={
        "operator": "Operator", \
        "flight_num": "Flight_Count",\
        "connected_sec_expected": "SLA_Expected",\
        "connected_sec": "SLA_Actual",\
        "SLA_Actual": "SLA_Actual",\
        "SLA_Expected": "SLA_Expected"
        })
    print(sla_report)

    # Convert dataframe column data to a list -- the tolist() function
    operator_list = sla_report['Operator'].tolist()
    flight_count = sla_report['Flight_Count'].tolist()
    avail_percent_list = sla_report['Availability'].tolist()
    avail_decimal_list = sla_report['Availability_decimal'].tolist()

    # Start Bokeh plotting!!!
    p = figure(x_range=operator_list, plot_height = 500, title="SLA Overview")
    p.vbar(operator_list, top=avail_decimal_list,width=1.5,line_width=200)

    #p.xgrid.grid_line_color = None
    p.y_range.start = 0

    #show(p)
    return p


def BokehChart(request):
    """此函数对数据表进行data cleaning"""
    # 1. 连接数据库并去除表中所有内容
    # 2. 用pandas对进行data cleaning

    # 1. 连接数据库并去除表中所有内容
    db_name = 'sladb'
    table_name = 'dart_ops_report'
    col_name = "*"
    db_engine = 'mysql'
    driver = 'pymysql'
    db_login = 'root:noway.man'
    db_server = 'localhost:3306'
    db_charset = 'utf8mb4'

    
    db_conn = '{db_engine}+{driver}://{db_login}@{db_server}/{db_name}?charset={db_charset}'\
        .format(db_engine=db_engine,driver=driver,db_login=db_login,\
        db_server=db_server,db_name=db_name,db_charset=db_charset)

    conn = create_engine(db_conn)
    sql = 'select {col_name} from {db_name}.{table_name};'\
        .format(col_name=col_name,db_name=db_name,table_name=table_name)

    df = pd.read_sql(sql,conn)
    #df.to_csv('OpsData.csv',index=False)

    # 只对没有被exclud的数据进行处理
    df_excluded = df.loc[df['excluded'] == 1]
    df = df.loc[df['excluded'] == 0]
    #print(df.head())


    sla_overview_plot = create_overview_plot(df)
    sla_detailled_plots = create_detailed_plots(df)

    script, div = components(sla_detailled_plots)
    template_name = 'sla/sla_report.html'
    content = {
        'script':script,
        'div':div
    }

    return render(request,template_name,content)

    


