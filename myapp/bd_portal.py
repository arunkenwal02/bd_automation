import random
import pandas as pd
from multiprocessing import Process
import sys
# from .db_con import engine
import warnings
import numpy as np
warnings.filterwarnings("ignore")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

django.setup()
from .models import *


def project_assumption(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        solar_gen = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', nrows=6, engine='openpyxl').T
        solar_gen.columns = ['solar_ehv_line_loss', 'solar_plant_availability', 'solar_grid_availability',
                             'ctu_loss', 'stu_loss', 'loss_at_load_end']
        solar_gen.fillna(0, inplace=True)
        solar_gen['version_id'] = param_id
        # solar_gen.to_sql('myapp_solar_assumptions', con=engine, if_exists='append', index=False)

        wind_gen = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=10, nrows=4,
                                 engine='openpyxl').T
        wind_gen.columns = ['ctu_loss', 'stu_loss', 'loss_at_load_end']
        wind_gen.fillna(0, inplace=True)
        wind_gen['version_id'] = param_id
        # wind_gen.to_sql('myapp_wind_assumptions', con=engine, if_exists='append', index=False)

        battery = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=17, nrows=8,
                                engine='openpyxl').T
        battery.columns = ["battery_capacity_power_rating", "battery_energy_rating", "roundtrip_loss_total",
                           "roundtrip_efficiency_charging_leg",
                           "roundtrip_efficiency_discharging_leg", "battery_discharge_depth",
                           "battery_other_losses", "usable_battery_energy_rating"]
        battery.fillna(0, inplace=True)
        battery['version_id'] = param_id
        # battery.to_sql('myapp_battery_assumptions', con=engine, if_exists='append', index=False)

        psp = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=29, nrows=9,
                            engine='openpyxl').T
        psp.columns = [
            "psp_turbine_capacity_power_rating", "psp_energy_rating",
            "roundtrip_efficiency_charging_leg", "roundtrip_efficiency_discharging_leg",
            "pump_capacity", "incident_power_threshold_perc_charging",
            "incident_power_threshold_mw_charging", "incident_power_threshold_perc_discharging",
            "incident_power_threshold_mw_discharging"
        ]
        psp.fillna(0, inplace=True)
        psp['version_id'] = param_id
        # psp.to_sql('myapp_psp_assumptions', con=engine, if_exists='append', index=False)

        plant_shutdown = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=42, nrows=4,
                                       engine='openpyxl').T
        plant_shutdown.columns = ["no_of_days", "month_of_shutdown", "shutdown_from_day_of_month",
                                  "shutdown_till_day_of_month"]
        plant_shutdown.fillna(0, inplace=True)
        plant_shutdown['version_id'] = param_id
        # plant_shutdown.to_sql('myapp_plant_shutdown', con=engine, if_exists='append', index=False)

        oper_inputs = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=50, nrows=3,
                                    engine='openpyxl').T
        oper_inputs.columns = ["elz_min_turndown", "elz_availability", "nh3_plant_availability"]
        oper_inputs.fillna(0, inplace=True)
        oper_inputs['version_id'] = param_id
        # oper_inputs.to_sql('myapp_operational_inputs', con=engine, if_exists='append', index=False)

        nh3_h2 = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=57,
                               engine='openpyxl').T
        nh3_h2.columns = ['nh3_h2_multiplier']
        nh3_h2.fillna(0, inplace=True)
        nh3_h2['version_id'] = param_id
        # nh3_h2.to_sql('myapp_nh3_h2_inputs', con=engine, if_exists='append', index=False)

    except Exception as e:
        error_dict['project_assumption'] = str(e)


def requrired_data(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        electrolyzer = pd.read_excel(xlsx, sheet_name='Required Data', usecols='A:C', skiprows=1, nrows=12,
                                     engine='openpyxl')
        electrolyzer.columns = ['lower_end_range_elz_loading', 'specific_power_actual_generation_kwh_per_kg_h2',
                                'ac_dc_conversion_losses_perc']
        electrolyzer.fillna(0, inplace=True)
        electrolyzer['version_id'] = param_id
        print(electrolyzer)
        electrolyzer_objects = [
            Electrolyzer(
                lower_end_range_elz_loading=row['lower_end_range_elz_loading'],
                specific_power_actual_generation_kwh_per_kg_h2=row['specific_power_actual_generation_kwh_per_kg_h2'],
                ac_dc_conversion_losses_perc=row['ac_dc_conversion_losses_perc'],
                version_id=row['version_id']
            )
            for index, row in electrolyzer.iterrows()
        ]

        # Bulk create the records
        Electrolyzer.objects.bulk_create(electrolyzer_objects)

        print("Electrolyzer Bulk create completed successfully!")
        # electrolyzer.to_sql('myapp_electrolyzer', con=engine, if_exists='append', index=False)

        construction_costing = pd.read_excel(xlsx, sheet_name='Required Data', usecols='A:C', skiprows=17, nrows=13,
                                             engine='openpyxl')
        construction_costing.columns = ["capex", "uom", "value"]

        construction_costing['value'] = construction_costing['value'].replace('-', None)
        construction_costing.fillna(0, inplace=True)

        construction_costing['version_id'] = param_id
        print(construction_costing)
        construction_costing_objects = [
            ConstructionCosting(
                capex=row['capex'],
                uom=row['uom'],
                value=row['value'],
                version_id=row['version_id']
            )
            for index, row in construction_costing.iterrows()
        ]

        # Bulk create the records
        ConstructionCosting.objects.bulk_create(construction_costing_objects)

        print("ConstructionCosting Bulk create completed successfully!")
        # construction_costing.to_sql('myapp_constructioncosting', con=engine, if_exists='append', index=False)

        operational_costing = pd.read_excel(xlsx, sheet_name='Required Data', usecols='A:C', skiprows=34, nrows=16,
                                            engine='openpyxl')
        operational_costing.columns = ["npv_of_opex", "uom", "value"]
        operational_costing['value'] = operational_costing['value'].replace('-', None)

        operational_costing.fillna(0, inplace=True)
        operational_costing['version_id'] = param_id
        print(operational_costing)
        operational_costing_objects = [
            OperationalCosting(
                npv_of_opex=row['npv_of_opex'],
                uom=row['uom'],
                value=row['value'],
                version_id=row['version_id']
            )
            for index, row in operational_costing.iterrows()
        ]

        OperationalCosting.objects.bulk_create(operational_costing_objects)

        print("OperationalCosting Bulk create completed successfully!")
        # operational_costing.to_sql('myapp_operationalcosting', con=engine, if_exists='append', index=False)

        nh3_plant = pd.read_excel(xlsx, sheet_name='Required Data', usecols='A:D', skiprows=54, engine='openpyxl')
        nh3_plant.columns = ['nh3_tpd', 'nh3_power_requirement_mw', 'capex_usd_mn', 'capex_inr_mn']
        nh3_plant.fillna(0, inplace=True)
        nh3_plant['version_id'] = param_id
        print(nh3_plant)
        nh3_plant_objects = [
            NH3_Plant(
                nh3_tpd=row['nh3_tpd'],
                nh3_power_requirement_mw=row['nh3_power_requirement_mw'],
                capex_usd_mn=row['capex_usd_mn'],
                capex_inr_mn=row['capex_inr_mn'],
                version_id=row['version_id']
            )
            for index, row in nh3_plant.iterrows()
        ]

        NH3_Plant.objects.bulk_create(nh3_plant_objects)

        print("NH3_Plant Bulk create completed successfully!")
        # nh3_plant.to_sql('myapp_nh3_plant', con=engine, if_exists='append', index=False)

    except Exception as e:
        error_dict['required_data'] = str(e)


def solar_profile(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        solar_gen_inputs = pd.read_excel(xlsx, sheet_name='Solar Profile', skiprows=4, engine='openpyxl')
        solar_gen_inputs = solar_gen_inputs.melt(
            id_vars=['Day of year', 'Time'],
            value_vars=solar_gen_inputs.columns[5:-1],
            var_name='Unit',
            value_name='Generation Value'
        )

        solar_gen_inputs['Unit'] = solar_gen_inputs['Unit'].str.extract(r'(\d+)').astype(int)
        solar_gen_inputs['Generation Value'].fillna(0, inplace=True)
        solar_gen_inputs.columns = ['day_of_year', 'time', 'unit', 'generation_value']
        cuf_val = pd.read_excel(xlsx, sheet_name='Solar Profile', nrows=1, engine='openpyxl')
        cuf = pd.DataFrame()
        cuf['cuf'] = cuf_val.iloc[:, 5:-1].T.reset_index(drop=True).fillna(0)
        cuf['unit'] = cuf.index + 1
        solar_gen_inputs = solar_gen_inputs.merge(cuf, on='unit')
        solar_gen_inputs['version_id'] = param_id
        # solar_gen_inputs.to_sql('myapp_solarprofile', con=engine, if_exists='append', index=False)
        return

    except Exception as e:
        error_dict['solar_profile'] = str(e)


def wind_profile(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        wind_gen = pd.read_excel(xlsx, sheet_name='Wind Profile', skiprows=6, engine='openpyxl')
        wind_gen = wind_gen.melt(id_vars=['Day of year', 'Time'], value_vars=wind_gen.columns[5:-1], var_name='Unit',
                                 value_name='Generation Value')
        wind_gen['Generation Value'].fillna(0, inplace=True)
        wind_gen['Unit'] = wind_gen['Unit'].str.extract(r'(\d+)').astype(int)
        wind_gen.columns = ['day_of_year', 'time', 'unit', 'generation_value']
        wind_cuf = pd.read_excel(xlsx, sheet_name='Wind Profile', skiprows=1, nrows=3,
                                 engine='openpyxl')
        wind_cuf = wind_cuf.iloc[:, 5:-1].T.reset_index(drop=True).fillna(0)
        wind_cuf.columns = ['cuf', 'mw_per_turbine']
        wind_cuf['unit'] = wind_cuf.index + 1
        wind_gen = wind_gen.merge(wind_cuf, on='unit')
        wind_gen['version_id'] = param_id
        # wind_gen.to_sql('myapp_windprofile', con=engine, if_exists='append', index=False)

    except Exception as e:
        error_dict['wind_profile'] = str(e)


def output(x, n, other_id):
    solar_values = pd.DataFrame({
        'solar_value': np.round(np.random.uniform(100,200, x), 3),
        'otherattribute_id': other_id
    })
    wind_values = pd.DataFrame({
        'wind_value': np.round(np.random.uniform(100,200, n), 3),
        'otherattribute_id': other_id
    })
    solar_objects = [
        SolarOutput(solar_value=row['solar_value'], otherattribute_id=row['otherattribute_id'])
        for _, row in solar_values.iterrows()
    ]

    # Create WindValues instances from the dataframe
    wind_objects = [
        WindOutput(wind_value=row['wind_value'], otherattribute_id=row['otherattribute_id'])
        for _, row in wind_values.iterrows()
    ]

    # Bulk create the objects in the database
    SolarOutput.objects.bulk_create(solar_objects)
    WindOutput.objects.bulk_create(wind_objects)
    # solar_values.to_sql('myapp_solaroutput', con=engine, if_exists='append', index=False)
    # wind_values.to_sql('myapp_windoutput', con=engine, if_exists='append', index=False)
    return solar_values['solar_value'], wind_values['wind_value']


def project_assump(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        prjct_asmption = pd.read_excel(xlsx, sheet_name='Project Assumptions')
        current_group = prjct_asmption.columns[0]
        prjct_asmption.insert(0, 'group', ' ')

        prjct_asmption.rename(
            columns={'Solar Generation Assumptions': 'parameter', 'Unnamed: 1': 'unit', 'Unnamed: 2': 'para_value'},
            inplace=True)

        for index, row in prjct_asmption.iterrows():
            if pd.notna(row['parameter']) and 'Assumptions' in row['parameter'] or row[
                'parameter'] == 'Plant Shutdown' or row['parameter'] == 'Operational Inputs' or row[
                'parameter'] == 'NH3-H2 Inputs':
                current_group = row['parameter']

            prjct_asmption.loc[index, 'group'] = current_group
        prjct_asmption = prjct_asmption.dropna(subset=['unit', 'para_value'], how='all').reset_index(drop=True)
        prjct_asmption['version_id'] = param_id
        prjct_asmption.fillna(0.0, inplace=True)
        prjct_asmption_instance = [
            ProjectAssumption(
                parameter=row['parameter'],
                unit=row['unit'],
                para_value=row['para_value'],
                group=row['group'],
                version_id=row['version_id']
            ) for idx, row in prjct_asmption.iterrows()
        ]
        ProjectAssumption.objects.bulk_create(prjct_asmption_instance)
        print("ProjectAssumption Bulk insert successful.")
        # prjct_asmption.to_sql('myapp_projectassumption', con=engine, if_exists='append', index=False)
        return

    except Exception as e:
        error_dict['project_assump'] = str(e)


def solarprofile(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        solar_gen_inputs = pd.read_excel(xlsx, sheet_name='Solar Profile', skiprows=4, engine='openpyxl')
        solar_gen_inputs = solar_gen_inputs.iloc[:, :-1]
        solar_gen_inputs.columns = ['date', 'day_of_year', 'day_of_month', 'month', 'time', 'unit_solar1',
                                    'unit_solar2',
                                    'unit_solar3', 'unit_solar4', 'unit_solar5']
        solar_gen_inputs['version_id'] = param_id
        solar_gen_inputs.fillna(0.0, inplace=True)
        solar_gen_input_instances = [
            Solar_Profile(
                date=row['date'],
                day_of_year=row['day_of_year'],
                day_of_month=row['day_of_month'],
                month=row['month'],
                time=row['time'],
                unit_solar1=row['unit_solar1'],
                unit_solar2=row['unit_solar2'],
                unit_solar3=row['unit_solar3'],
                unit_solar4=row['unit_solar4'],
                unit_solar5=row['unit_solar5'],
                version_id=row['version_id']
            ) for idx, row in solar_gen_inputs.iterrows()
        ]
        Solar_Profile.objects.bulk_create(solar_gen_input_instances)
        print("Solar_Profile Bulk insert successful.")
        # solar_gen_inputs.to_sql('myapp_solar_profile', con=engine, if_exists='append', index=False)

    except Exception as err:
        error_dict['error'] = f"{type(err).__name__} was raised: {err} Error on line " + format(
            sys.exc_info()[-1].tb_lineno)


def windprofile(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        wind_gen_inputs = pd.read_excel(xlsx, sheet_name='Wind Profile', skiprows=6, engine='openpyxl')
        wind_gen_inputs = wind_gen_inputs.iloc[:, :-1]
        wind_gen_inputs.columns = ['date', 'day_of_year', 'day_of_month', 'month', 'time', 'unit_wind1',
                                   'unit_wind2', 'unit_wind3', 'unit_wind4', 'unit_wind5']
        wind_gen_inputs['version_id'] = param_id
        wind_gen_inputs.fillna(0.0, inplace=True)
        # wind_gen_inputs.to_sql('myapp_wind_profile', con=engine, if_exists='append', index=False)
        wind_gen_input_instances = [
            Wind_Profile(
                date=row['date'],
                day_of_year=row['day_of_year'],
                day_of_month=row['day_of_month'],
                month=row['month'],
                time=row['time'],
                unit_wind1=row['unit_wind1'],
                unit_wind2=row['unit_wind2'],
                unit_wind3=row['unit_wind3'],
                unit_wind4=row['unit_wind4'],
                unit_wind5=row['unit_wind5'],
                version_id=row['version_id']
            )
            for index, row in wind_gen_inputs.iterrows()
        ]

        Wind_Profile.objects.bulk_create(wind_gen_input_instances)
        print("Wind_Profile Bulk insert successful.")

    except Exception as err:
        error_dict['error'] = f"{type(err).__name__} was raised: {err} Error on line " + format(
            sys.exc_info()[-1].tb_lineno)





def main_func(param_id, error_dict):
    try:
        solar_profile = pd.DataFrame(Solar_Profile.objects.filter(version=param_id).values())
        wind_profile = pd.DataFrame(Wind_Profile.objects.filter(version=param_id).values())
        project_assump = pd.DataFrame(ProjectAssumption.objects.filter(version=param_id).values())
        sec_ac_dc_losses = pd.DataFrame(Electrolyzer.objects.filter(version=param_id).values())
        nh3_tpd_power_capex = pd.DataFrame(NH3_Plant.objects.filter(version=param_id).values())
        oper_cost = pd.DataFrame(OperationalCosting.objects.filter(version=param_id).values())
        oper_cost.rename(columns={'npv_of_opex': 'parameter'}, inplace=True)
        const_cost = pd.DataFrame(ConstructionCosting.objects.filter(version=param_id).values())
        const_cost.rename(columns={'capex': 'parameter'}, inplace=True)
        cost_data = pd.concat([const_cost, oper_cost], ignore_index=True)

        solar_ehv = project_assump.iloc[0, 4]
        solar_plant_avail = project_assump.iloc[1, 4]
        solar_grid_avail = project_assump.iloc[2, 4]
        solar_ctu = project_assump.iloc[3, 4]
        solar_stu = project_assump.iloc[4, 4]
        solar_load_end = project_assump.iloc[5, 4]
        wind_ctu = project_assump.iloc[6, 4]
        wind_stu = project_assump.iloc[7, 4]
        wind_load_end = project_assump.iloc[8, 4]
        battery_power_rating = 0  # to be opt
        battery_hrs = project_assump.iloc[10, 4]
        battery_energy_rating = battery_power_rating * battery_hrs
        battery_total_rtc = project_assump.iloc[12, 4]
        battery_rtc_charging_leg = project_assump.iloc[13, 4]
        battery_rtc_discharging_leg = project_assump.iloc[14, 4]
        battery_dod = project_assump.iloc[15, 4]
        battery_other_loss = project_assump.iloc[16, 4]
        battery_useable_energy_rating = project_assump.iloc[17, 4]
        shutdown_days = project_assump.iloc[27, 4]
        shutdown_month = project_assump.iloc[28, 4]
        shutdown_start_day = project_assump.iloc[29, 4]
        shutdown_end_day = project_assump.iloc[30, 4]

        elz_min_turndown = project_assump.iloc[31, 4]
        elz_avail = project_assump.iloc[32, 4]
        nh3_avail = project_assump.iloc[33, 4]
        nh3_h2_multiplier = project_assump.iloc[34, 4]
        solar1_capex = cost_data.iloc[0, 3]
        solar2_capex = cost_data.iloc[1, 3]
        solar3_capex = cost_data.iloc[2, 3]
        solar4_capex = cost_data.iloc[3, 3]
        solar5_capex = cost_data.iloc[4, 3]
        wind1_capex = cost_data.iloc[5, 3]
        wind2_capex = cost_data.iloc[6, 3]
        wind3_capex = cost_data.iloc[7, 3]
        wind4_capex = cost_data.iloc[8, 3]
        wind5_capex = cost_data.iloc[9, 3]
        battery_capex = cost_data.iloc[10, 3]
        elz_capex = cost_data.iloc[11, 3]
        ghs_capex = wind1_capex = cost_data.iloc[12, 3]

        solar1_opex = cost_data.iloc[13, 3]
        solar2_opex = cost_data.iloc[14, 3]
        solar3_opex = cost_data.iloc[15, 3]
        solar4_opex = cost_data.iloc[16, 3]
        solar5_opex = cost_data.iloc[17, 3]
        wind1_opex = cost_data.iloc[18, 3]
        wind2_opex = cost_data.iloc[19, 3]
        wind3_opex = cost_data.iloc[20, 3]
        wind4_opex = cost_data.iloc[21, 3]
        wind5_opex = cost_data.iloc[22, 3]
        battery_opex = cost_data.iloc[23, 3]
        psp_opex = cost_data.iloc[24, 3]
        elz_opex = cost_data.iloc[25, 3]
        nh3_opex = cost_data.iloc[26, 3]
        iex_sale_cost = cost_data.iloc[27, 3]
        iex_purchase_cost = cost_data.iloc[28, 3]


    except Exception as err:
        error_dict['error'] = f"{type(err).__name__} was raised: {err} Error on line " + format(
            sys.exc_info()[-1].tb_lineno)
