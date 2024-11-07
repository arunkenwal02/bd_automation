import random

import pandas as pd
from multiprocessing import Process
from .db_con import engine
import warnings

warnings.filterwarnings("ignore")


def project_assumption(excel_file, param_id, error_dict):
    try:
        xlsx = pd.ExcelFile(excel_file)
        solar_gen = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', nrows=6, engine='openpyxl').T
        solar_gen.columns = ['solar_ehv_line_loss', 'solar_plant_availability', 'solar_grid_availability',
                             'ctu_loss', 'stu_loss', 'loss_at_load_end']
        solar_gen.fillna(0, inplace=True)
        solar_gen['version_id'] = param_id
        solar_gen.to_sql('myapp_solar_assumptions', con=engine, if_exists='append', index=False)

        wind_gen = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=10, nrows=4,
                                 engine='openpyxl').T
        wind_gen.columns = ['ctu_loss', 'stu_loss', 'loss_at_load_end']
        wind_gen.fillna(0, inplace=True)
        wind_gen['version_id'] = param_id
        wind_gen.to_sql('myapp_wind_assumptions', con=engine, if_exists='append', index=False)

        battery = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=17, nrows=8,
                                engine='openpyxl').T
        battery.columns = ["battery_capacity_power_rating", "battery_energy_rating", "roundtrip_loss_total",
                           "roundtrip_efficiency_charging_leg",
                           "roundtrip_efficiency_discharging_leg", "battery_discharge_depth",
                           "battery_other_losses", "usable_battery_energy_rating"]
        battery.fillna(0, inplace=True)
        battery['version_id'] = param_id
        battery.to_sql('myapp_battery_assumptions', con=engine, if_exists='append', index=False)

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
        psp.to_sql('myapp_psp_assumptions', con=engine, if_exists='append', index=False)

        plant_shutdown = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=42, nrows=4,
                                       engine='openpyxl').T
        plant_shutdown.columns = ["no_of_days", "month_of_shutdown", "shutdown_from_day_of_month",
                                  "shutdown_till_day_of_month"]
        plant_shutdown.fillna(0, inplace=True)
        plant_shutdown['version_id'] = param_id
        plant_shutdown.to_sql('myapp_plant_shutdown', con=engine, if_exists='append', index=False)

        oper_inputs = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=50, nrows=3,
                                    engine='openpyxl').T
        oper_inputs.columns = ["elz_min_turndown", "elz_availability", "nh3_plant_availability"]
        oper_inputs.fillna(0, inplace=True)
        oper_inputs['version_id'] = param_id
        oper_inputs.to_sql('myapp_operational_inputs', con=engine, if_exists='append', index=False)

        nh3_h2 = pd.read_excel(xlsx, sheet_name='Project Assumptions', usecols='C', skiprows=57,
                               engine='openpyxl').T
        nh3_h2.columns = ['nh3_h2_multiplier']
        nh3_h2.fillna(0, inplace=True)
        nh3_h2['version_id'] = param_id
        nh3_h2.to_sql('myapp_nh3_h2_inputs', con=engine, if_exists='append', index=False)

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
        electrolyzer.to_sql('myapp_electrolyzer', con=engine, if_exists='append', index=False)

        construction_costing = pd.read_excel(xlsx, sheet_name='Required Data', usecols='A:C', skiprows=17, nrows=6,
                                             engine='openpyxl')
        construction_costing.columns = ["capex", "uom", "value"]
        construction_costing.fillna(0, inplace=True)
        construction_costing['version_id'] = param_id
        construction_costing.to_sql('myapp_constructioncosting', con=engine, if_exists='append', index=False)

        operational_costing = pd.read_excel(xlsx, sheet_name='Required Data', usecols='A:C', skiprows=28, nrows=8,
                                            engine='openpyxl')
        operational_costing.columns = ["npv_of_opex", "uom", "value"]
        operational_costing.fillna(0, inplace=True)
        operational_costing['version_id'] = param_id
        operational_costing.to_sql('myapp_operationalcosting', con=engine, if_exists='append', index=False)

        nh3_plant = pd.read_excel(xlsx, sheet_name='Required Data', usecols='A:C', skiprows=41, engine='openpyxl')
        nh3_plant.columns = ['nh3_tpd', 'nh3_power_requirement_mw', 'capex_usd_mn']
        nh3_plant.fillna(0, inplace=True)
        nh3_plant['version_id'] = param_id
        nh3_plant.to_sql('myapp_nh3_plant', con=engine, if_exists='append', index=False)

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
        solar_gen_inputs.to_sql('myapp_solarprofile', con=engine, if_exists='append', index=False)

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
        wind_gen.to_sql('myapp_windprofile', con=engine, if_exists='append', index=False)

    except Exception as e:
        error_dict['wind_profile'] = str(e)


def output(x, n, other_id):
    solar_values = pd.DataFrame({
        'solar_value': [random.uniform(0, 50) for _ in range(x)],
        'otherattribute_id': other_id
    })
    wind_values = pd.DataFrame({
        'wind_value': [random.uniform(0, 50) for _ in range(n)],
        'otherattribute_id': other_id
    })
    solar_values.to_sql('myapp_solaroutput', con=engine, if_exists='append', index=False)
    wind_values.to_sql('myapp_windoutput', con=engine, if_exists='append', index=False)
    return solar_values['solar_value'], wind_values['wind_value']


