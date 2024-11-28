import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.animation import FuncAnimation
from scipy.optimize import minimize
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import warnings
import matplotlib.ticker as mtick
import math
from matplotlib.animation import FuncAnimation
import warnings

warnings.filterwarnings("ignore")
import datetime
from collections import Counter
from datetime import datetime
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date
from pyxirr import xirr
from scipy.optimize import brentq
import re

start_time = time.time()

inputs_xlsx = pd.ExcelFile("filnal_inputs_file.xlsx")

#### sheets ####
main_sheet = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet').fillna(0)
macro_tab = pd.read_excel(inputs_xlsx, sheet_name='For Macro Tab').fillna('')
opex_sheet = pd.read_excel(inputs_xlsx, sheet_name='For OpEx').fillna('')
cap_supply_sheet = pd.read_excel(inputs_xlsx, sheet_name='For Capacity Supply').fillna('')
rev_input = pd.read_excel(inputs_xlsx, sheet_name='For Revenue').fillna('')
krishnapur_env = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet').fillna('')
lender_fee_input = pd.read_excel(inputs_xlsx, sheet_name='For Lender Fees').fillna(' ')
lender_fee_flag = pd.read_excel(inputs_xlsx, sheet_name='Flags').fillna(' ')
interest = pd.read_excel(inputs_xlsx, sheet_name='For Debt Sch.').fillna('')
depre_sheet = pd.read_excel(inputs_xlsx, sheet_name='For Depreciation').fillna(" ")
h2_sheet = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_GH2')
flag = pd.read_excel(inputs_xlsx, sheet_name='Flags').fillna('').T
banking_inputs = pd.read_excel(inputs_xlsx, sheet_name='Banking Inputs').fillna(" ")
battery_inputs = pd.read_excel(inputs_xlsx, sheet_name='Battery Inputs').fillna(0)
psp_inputs = pd.read_excel(inputs_xlsx, sheet_name='PSP Inputs').fillna(" ")
gen_profile = pd.read_excel(inputs_xlsx, sheet_name='Generation Profile').fillna(" ")
slr_cst_sheet = pd.read_excel(inputs_xlsx, sheet_name='Solar Cost Sheet').fillna(0)
wnd_cst_sheet1 = pd.read_excel(inputs_xlsx, sheet_name="Wind Cost Sheet_S1").fillna(0)
wnd_cst_sheet2 = pd.read_excel(inputs_xlsx, sheet_name='Wind Cost Sheet_S2').fillna(0)

#### replacement capex & Depre new ####
main_sheet = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet')
main_sheet_gh2 = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_GH2')
main_sheet_nh3 = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_NH3')
bat_sheet = pd.read_excel(inputs_xlsx, sheet_name='Battery Inputs')
depre_sheet = pd.read_excel(inputs_xlsx, sheet_name='For Depreciation')

main_sheet_1 = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet', usecols=[1, 3], header=None)
main_sheet_1 = main_sheet_1.dropna().reset_index(drop=True)
main_sheet_1.columns = range(main_sheet_1.shape[1])

main_sheet_gh2_colb = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_GH2', usecols=[1, 3], header=None)
main_sheet_nh3_colb = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_NH3', usecols=[1, 3], header=None)
main_sheet_nh3_colg = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_NH3', usecols=[6, 8], header=None)
main_sheet_nh3_colg = main_sheet_nh3_colg.dropna().reset_index(drop=True).drop(3)
main_sheet_nh3_colg.columns = range(main_sheet_nh3_colg.shape[1])

main_sheet_gh2_new = pd.concat([main_sheet_gh2_colb, main_sheet_nh3_colb], ignore_index=True)
main_sheet_gh2_new.columns = range(main_sheet_gh2_new.shape[1])

main_sheet_gh2_nh3 = pd.concat([main_sheet_gh2_new, main_sheet_nh3_colg], ignore_index=True)

input_sheet = pd.concat([main_sheet_1, main_sheet_gh2_nh3], ignore_index=True)

input_sheet = input_sheet.dropna().reset_index(drop=True)

input_sheet[0] = input_sheet[0].str.lower().str.split(' ').str.join('_').str.replace(r'[-.&()%/]', '',
                                                                                     regex=True).str.replace(r'\s+', '',
                                                                                                             regex=True)  # .str.replace('.', '').str.replace('&', '').str.replace(r'\(|\)', '', regex=True).str.strip()
# Define the stop words
stop_words = {'of', 'on', 'the', 'for', 'and', 'in', 'to', 'with', 'at'}


class input:
    pass

    # Create an instance of the class


input = input()

for input_name, input_value in zip(input_sheet[0], input_sheet[1]):
    input_name = '_'.join([part for part in re.split(r'[_\s]+', input_name) if part.lower() not in stop_words])
    setattr(input, input_name, input_value)

main_sheet_gh2 = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_GH2')
main_sheet_nh3 = pd.read_excel(inputs_xlsx, sheet_name='Main Sheet_NH3')


pd.options.display.max_rows = None
pd.options.display.max_columns = None

#### banking inputs
banking_perc = banking_inputs.iloc[1, 3]
banking_loss = banking_inputs.iloc[2, 3]
ists_losses = banking_inputs.iloc[2, 3]  ###########chweck if its banking loss
banking_drawal_per_unit_charges = banking_inputs.iloc[4, 3]
banking_drawal_per_unit_charges_escalation = banking_inputs.iloc[5, 3]
aditnl_c1_wdrwl_unit_chrges = banking_inputs.iloc[7, 3]
aditnl_c4_wdrwl_unit_chrges = banking_inputs.iloc[10, 3]
aditnl_c5_wdrwl_unit_chrges = banking_inputs.iloc[13, 3]
additional_peak_pwr_wthdrwl_unt_chrgs_c1 = banking_inputs.iloc[8, 3]
additional_peak_pwr_wthdrwl_unt_chrgs_c4 = banking_inputs.iloc[11, 3]
additional_peak_pwr_wthdrwl_unt_chrgs_c5 = banking_inputs.iloc[14, 3]

### battery inputs
btry_other_losses = battery_inputs.iloc[7, 3]
rnd_trp_losses = battery_inputs.iloc[4, 3]
batt_depth_dschrge = battery_inputs.iloc[6, 3]
btry_cap = battery_inputs.iloc[1, 3]
charg_dischrg_cycle = battery_inputs.iloc[2, 3]
batt_capex_cost_ip = battery_inputs.iloc[9, 3]
annual_maintenance_chrgs = battery_inputs.iloc[10, 3]
batt_capex_phasing = battery_inputs.iloc[13, 3:].reset_index(drop=True)
bat_repl_chrgs = bat_sheet.iloc[17, 3]
bat_enrg_rtng = bat_sheet.iloc[3, 3]
bat_inflation_perc = bat_sheet.iloc[18, 3]
annual_maintenance_chrgs = battery_inputs.iloc[10, 3]
battery_op_flag = battery_inputs.iloc[0, 3]
bat_escalation = battery_inputs.iloc[11, 3]

### PSP inputs
charging_discharing_cycle = psp_inputs.iloc[2, 3]
roundtrip_ists_losses = psp_inputs.iloc[4, 3]
strage_rntl_cst_pr_yr = psp_inputs.iloc[9, 3]
psp_op_flag = psp_inputs.iloc[0, 3]

# inputs : solar per mw and wind per mw cost
s_cpx_cst = float(main_sheet.iloc[13, 3])  # solar cost
w_cpx_cst = float(main_sheet.iloc[14, 3])  # wind cost

# other inputs
roi = main_sheet.iloc[21, 3]  # rate of interest
debt_per = main_sheet.iloc[22, 3]  # debvt percentage
equ_per = main_sheet.iloc[23, 3]  # equity percentage
up_equ_per = main_sheet.iloc[24, 3]  # up equity percentage

# main sheet
ex_rate = main_sheet.iloc[42, 3]
csr_per = main_sheet.iloc[37, 3]
p1_phasing = main_sheet.iloc[46, 3:].reset_index(drop=True)
p2_phasing = main_sheet.iloc[47, 3:].reset_index(drop=True)
p3_phasing = main_sheet.iloc[48, 3:].reset_index(drop=True)
p4_phasing = main_sheet.iloc[49, 3:].reset_index(drop=True)
p4_phasing = main_sheet.iloc[20, 3:].reset_index(drop=True)
p5_phasing = main_sheet.iloc[44, 3:].reset_index(drop=True)

## Main Sheet_GH2
el_avail = main_sheet_gh2.iloc[20, 3]
el_stk_lf = main_sheet_gh2.iloc[26, 3]
el_repl_cpx_1 = main_sheet_gh2.iloc[27, 3]
el_repl_cpx_2 = main_sheet_gh2.iloc[28, 3]
gh2_inflsn = main_sheet_gh2.iloc[36, 3]
gh2_plnt_lf = main_sheet_gh2.iloc[37, 3]
bop = main_sheet_gh2.iloc[1, 3]
max_depre_val = main_sheet_gh2.iloc[38, 3]
electrolyzer_capacity = main_sheet_gh2.columns[6]
GHS_capacity = main_sheet_gh2.columns[9]

## Main Sheet_NH3 Inputs
nh3_inflsn = main_sheet_nh3.iloc[22, 3]
nh3_plnt_lf = main_sheet_nh3.iloc[21, 3]

# macro_tab
iex_sale_price = macro_tab.iloc[8, 5]
degradation_rates = macro_tab.iloc[1:, 1]

# inputs from opex
iex_pur_price = opex_sheet.iloc[0, 3]
DSM_penalties_wind = opex_sheet.iloc[4:9, 7].tolist()
##########LCOE MAKE THIS AS PER INPUTS SHEET FROM MAIN SHEET
# lcoe = opex_sheet.iloc[5,3]
wind_switch = main_sheet.iloc[2, 3]
DSM_penalties_solar = opex_sheet.iloc[11:16, 7].tolist()
solar_switch = main_sheet.iloc[1, 3]

# wind onm
free_period = opex_sheet.iloc[48, 3]
no_yrs_lockin = opex_sheet.iloc[50, 3]
onm_cost_lockin = opex_sheet.iloc[51, 3]
escalation_lockin = opex_sheet.iloc[52, 3]
onm_cost_self = opex_sheet.iloc[55, 3]  # onm cost self post lockin period
escalation_self = opex_sheet.iloc[56, 3]
wind_switch = main_sheet.iloc[2, 3]
bop_cost = opex_sheet.iloc[59, 3]
bop_escalation = opex_sheet.iloc[60, 3]
ctu_cost = opex_sheet.iloc[62, 3]
ctu_escalation = opex_sheet.iloc[63, 3]
emp_salary_wind = opex_sheet.iloc[65, 3]
sgil_escalation = opex_sheet.iloc[66, 3]
GP_taxes_wind = opex_sheet.iloc[68, 3]
wind_insurance = opex_sheet.iloc[72, 3]
escalation_insu = opex_sheet.iloc[73, 3]
button_wind1 = krishnapur_env.iloc[5][3:4].item()

# opex sheet inputs

# wind inputs
iex_pur_price = opex_sheet.iloc[0, 3]
DSM_penalties_wind = opex_sheet.iloc[4:9, 7].tolist()
# lcoe = opex_sheet.iloc[5, 3]
no_yrs_lockin = opex_sheet.iloc[50, 3]
onm_cost_lockin = opex_sheet.iloc[51, 3]
escalation_lockin = opex_sheet.iloc[52, 3]
onm_cost_self = opex_sheet.iloc[55, 3]  # onm cost self post lockin period
escalation_self = opex_sheet.iloc[56, 3]
bop_cost = opex_sheet.iloc[59, 3]
bop_escalation = opex_sheet.iloc[60, 3]
ctu_cost = opex_sheet.iloc[62, 3]
ctu_escalation = opex_sheet.iloc[63, 3]
emp_salary_wind = opex_sheet.iloc[65, 3]
sgil_escalation = opex_sheet.iloc[66, 3]
gp_taxes_wind = opex_sheet.iloc[68, 3]
wind_insurance = opex_sheet.iloc[72, 3]
escalation_insu = opex_sheet.iloc[73, 3]
envi_land_req = opex_sheet.iloc[83, 3]
sany_land_req = opex_sheet.iloc[83, 3]
envi_fst_instlment = opex_sheet.iloc[76, 3]
envi_scnd_instlment = opex_sheet.iloc[78, 3]
sany_fst_instlment = opex_sheet.iloc[76, 3]
sany_scnd_instlment = opex_sheet.iloc[78, 3]
first_instlmnt_yr = opex_sheet.iloc[75, 3]
scnd_instlmnt_yr = opex_sheet.iloc[77, 3]
upfront_duration = opex_sheet.iloc[84, 3]
land_lease_charges = opex_sheet.iloc[80, 3]
hanam_escalation = opex_sheet.iloc[81, 3]

# solar onm
onm_cost = opex_sheet.iloc[12, 3]
annual_escalation = opex_sheet.iloc[13, 3]
solar_switch = main_sheet.iloc[1, 3]
ctu_bay_charges = opex_sheet.iloc[14, 3]
escalation_rate_ctu = opex_sheet.iloc[15, 3]
land_lease_carges_pa = opex_sheet.iloc[18, 3]
land_required = opex_sheet.iloc[19, 3]
land_lease_escalation = opex_sheet.iloc[20, 3]
after_every_n_years = opex_sheet.iloc[21, 3]
cost_replacement = opex_sheet.iloc[24, 3]
inverter_switch = opex_sheet.iloc[23, 3]
bird_diverter_maintenance = opex_sheet.iloc[33, 3]
bird_diverter_amc_escalation = opex_sheet.iloc[34, 3]
escalation_years = opex_sheet.iloc[35, 3]
free_period_bird_div = opex_sheet.iloc[32, 3]
free_period_inv_amc = opex_sheet.iloc[27, 3]
inverter_annual_maintenance = opex_sheet.iloc[28, 3]
inverter_amc_escalation = opex_sheet.iloc[29, 3]
escalation_applicable = opex_sheet.iloc[30, 3]
aug_s_cap_exp = opex_sheet.iloc[42, 3]
free_period_land = opex_sheet.iloc[37, 3]
land_tax_charges_raj = opex_sheet.iloc[38, 3]
ists_charges = opex_sheet.iloc[40, 3]
insurance_solar = opex_sheet.iloc[44, 3]
escalation_insur = opex_sheet.iloc[45, 3]

# solar sheet cost
tl_length = slr_cst_sheet.iloc[38, 14]

ed_chrgs = main_sheet.iloc[53, 3]

# For Depreciation
max_dep_value = depre_sheet.iloc[2, 3]
book_dep_rate = depre_sheet.iloc[3, 3]
tax_rate_slm = depre_sheet.iloc[10, 3]
tax_rate_wdv = depre_sheet.iloc[15, 3]

## For Depreciation Sheet
bk_depre_rt_gh2 = depre_sheet.iloc[30, 3]
bk_depre_rt_btry = depre_sheet.iloc[22, 3]
wdv_rt_gh2 = depre_sheet.iloc[31, 3]
wdv_rt_btry = depre_sheet.iloc[26, 3]
# solar overloading
s_ovrld = main_sheet.iloc[45, 3]

# construction period
t_cnstrucn_perd = main_sheet.iloc[10, 3]
exh_rate = slr_cst_sheet.iloc[0, 3]
fwd_premium = slr_cst_sheet.iloc[1, 3]
Hedging_p_modules = slr_cst_sheet.iloc[2, 3]
eff_exh_rate = slr_cst_sheet.iloc[3, 3]

# A.  module cost
module_prce = slr_cst_sheet.iloc[7, 3]
non_usd_m_prce = slr_cst_sheet.iloc[8, 3]
# module testing
m_testing = slr_cst_sheet.iloc[11, 3]
# logistics
m_logistcs = slr_cst_sheet.iloc[14, 3]

# breakage contingency
m_breakage_conti = slr_cst_sheet.iloc[16, 3]

# LC cost for module procurement
lc_cst_module_pcmnt = slr_cst_sheet.iloc[18, 3]

# B. Land Cost
lnd_req_pr_mwp = slr_cst_sheet.iloc[21, 3]
ttl_land_cst = slr_cst_sheet.iloc[22, 3]
bkrage_cst = slr_cst_sheet.iloc[23, 3]

# C. Turn key BOS
turnky_bos_cst = slr_cst_sheet.iloc[26, 3]
gst = slr_cst_sheet.iloc[27, 3]
# D. Split Scope BOS
bos_till_33kv_mms = slr_cst_sheet.iloc[31, 3]

pss_input = slr_cst_sheet.iloc[32, 3]
equi_cst_robo_clng = slr_cst_sheet.iloc[33, 3]
bos_gst_cst = slr_cst_sheet.iloc[34, 3]
bos_cst = slr_cst_sheet.iloc[35, 3]

# E. External Evacuation System
ehv_line_cost = slr_cst_sheet.iloc[38, 3]

# F. Due Diligence Expense
thrd_party_rsrce_asmnt = slr_cst_sheet.iloc[41, 3]
thrd_party_lf_stdy = slr_cst_sheet.iloc[42, 3]
thrd_party_esia = slr_cst_sheet.iloc[43, 3]
title_srch = slr_cst_sheet.iloc[44, 3]
soil_tst_cntr_srvy = slr_cst_sheet.iloc[45, 3]
markting_exp = slr_cst_sheet.iloc[46, 3]
otr_than_bg_cst = slr_cst_sheet.iloc[51, 14]

# app_chrgs = slr_cst_sheet.iloc[49, 3]
stge_connec_approvl = slr_cst_sheet.iloc[51, 3]
conn_bnk_gua_chrgs = slr_cst_sheet.iloc[52, 3]
gna_app = slr_cst_sheet.iloc[53, 3]
rldc_reg_chrgs = slr_cst_sheet.iloc[55, 3]
conn_modeling = slr_cst_sheet.iloc[56, 3]
remote_end_mtr_tst = slr_cst_sheet.iloc[57, 3]
plant_end_mtr_tst = slr_cst_sheet.iloc[58, 3]
sna_reg = slr_cst_sheet.iloc[60, 3]

# H. Construction Expenses
insurnce = slr_cst_sheet.iloc[63, 3]
pd_exp = slr_cst_sheet.iloc[64, 3]
crtcal_tools_req_cod = slr_cst_sheet.iloc[65, 3]

# I. Land Diligence
na_convn_state_gdlines = slr_cst_sheet.iloc[68, 3]
land_due_gdlines = slr_cst_sheet.iloc[69, 3]

# J. ETS Diligence
site_topo_ttl_stion = slr_cst_sheet.iloc[72, 3]
soil_tst_s_land = slr_cst_sheet.iloc[73, 3]
hydro_reprt = slr_cst_sheet.iloc[74, 3]
pull_o_tsting = slr_cst_sheet.iloc[75, 3]
third_prty_astnc_oe = slr_cst_sheet.iloc[76, 3]

# K. Contingency
contgncy = slr_cst_sheet.iloc[79, 3]

# phasing inputs
fnl_module_prce = slr_cst_sheet.iloc[86, 10:].reset_index(drop=True)
fnl_mdule_tstng_prce = slr_cst_sheet.iloc[87, 10:].reset_index(drop=True)
fnl_mdule_logistcs = slr_cst_sheet.iloc[88, 10:].reset_index(drop=True)
fnl_lc_cst_mdule_pcrmnt = slr_cst_sheet.iloc[89, 10:].reset_index(drop=True)
ttl_ehv_cst = slr_cst_sheet.iloc[92, 10:].reset_index(drop=True)
ttl_bos_cst = slr_cst_sheet.iloc[93, 10:].reset_index(drop=True)
contgncy_prcnt = slr_cst_sheet.iloc[96, 10:].reset_index(drop=True)
ttl_apprvl_prmits = slr_cst_sheet.iloc[97, 10:].reset_index(drop=True)
ttl_thrd_party_esia = slr_cst_sheet.iloc[100, 10:].reset_index(drop=True)
ttl_thrd_party_lf_stdy = slr_cst_sheet.iloc[101, 10:].reset_index(drop=True)
lnd_delgnce_ttle_srch = slr_cst_sheet.iloc[102, 10:].reset_index(drop=True)
pd_expnses = slr_cst_sheet.iloc[103, 10:].reset_index(drop=True)
crtcal_tools_phasing = slr_cst_sheet.iloc[104, 10:].reset_index(drop=True)
lnd_cst_one_tme_brkrge = slr_cst_sheet.iloc[107, 10:].reset_index(drop=True)
lnd_cst_rnt = slr_cst_sheet.iloc[108, 10:].reset_index(drop=True)
na_conv_state_guidlns_phasing = slr_cst_sheet.iloc[109, 10:].reset_index(drop=True)

# WIND 1 site inputs
wtg_suply_w1 = wnd_cst_sheet1.iloc[4, 2]
uss_w1 = wnd_cst_sheet1.iloc[5, 2]
fndation_w1 = wnd_cst_sheet1.iloc[6, 2]
bop_trnky_w1 = wnd_cst_sheet1.iloc[9, 2]
lnd_cst_budgted_w1 = wnd_cst_sheet1.iloc[10, 2]
chnnl_prtnr_w1 = wnd_cst_sheet1.iloc[11, 2]
lnd_cst_w1 = wnd_cst_sheet1.iloc[14, 2]
ttl_pd_expnses_w1 = wnd_cst_sheet1.iloc[17, 2]
apprvls_w1 = wnd_cst_sheet1.iloc[20, 2]
contgncy_w1 = wnd_cst_sheet1.iloc[23, 2]
prlmmry_pero_exp_w1 = wnd_cst_sheet1.iloc[24, 2]
ot_mob_cst_w1 = wnd_cst_sheet1.iloc[25, 2]

# wtg supply percnetages inputs
wtg_supp_prcntge = wnd_cst_sheet1.iloc[22, 16]
wtg_adv_prcntge = wnd_cst_sheet1.iloc[23, 16]
wtg_supp_blade_prcntge = wnd_cst_sheet1.iloc[24, 16]
wtg_comm_prcntge = wnd_cst_sheet1.iloc[25, 16]

# logistics
logstcs_prcntge = wnd_cst_sheet1.iloc[27, 16]
dispatch_prcntge = wnd_cst_sheet1.iloc[28, 16]
delvry_prcntge = wnd_cst_sheet1.iloc[29, 16]

# civil works
civil_works_prcntge = wnd_cst_sheet1.iloc[31, 16]
civil_adv_prcntge = wnd_cst_sheet1.iloc[32, 16]
fondn_prcntge = wnd_cst_sheet1.iloc[33, 16]

# e&c
ec_prcntge = wnd_cst_sheet1.iloc[35, 16]
ec_adv_prcntge = wnd_cst_sheet1.iloc[36, 16]
ec_mob_prcntge = wnd_cst_sheet1.iloc[37, 16]
ec_instll_prcntge = wnd_cst_sheet1.iloc[38, 16]
ec_prfrmnce_prcntge = wnd_cst_sheet1.iloc[39, 16]

# electrica works
elec_prcntge = wnd_cst_sheet1.iloc[41, 16]
elec_adv_prcntge = wnd_cst_sheet1.iloc[42, 16]
elect_recipt_prcntge = wnd_cst_sheet1.iloc[43, 16]
elect_dp_yard_prcntge = wnd_cst_sheet1.iloc[44, 16]

# land arrangement
land_arr_prcntge = wnd_cst_sheet1.iloc[46, 16]
land_adv_prcntge = wnd_cst_sheet1.iloc[47, 16]
land_2mnths_prcntge = wnd_cst_sheet1.iloc[48, 16]
land_4mnths_prcntge = wnd_cst_sheet1.iloc[49, 16]
land_wtg_loc_prcntge = wnd_cst_sheet1.iloc[50, 16]
land_name_trnsfr_prcntge = wnd_cst_sheet1.iloc[51, 16]

# wind 1 phasing inputs
ntp_w1 = wnd_cst_sheet1.iloc[2, 16:].reset_index(drop=True)
lnd_aq_suzlon_w1 = wnd_cst_sheet1.iloc[3, 16:].reset_index(drop=True)
cvl_fndation_w1 = wnd_cst_sheet1.iloc[4, 16:].reset_index(drop=True)
wtg_suply_w1 = wnd_cst_sheet1.iloc[5, 16:].reset_index(drop=True)
instlation_wtg_w1 = wnd_cst_sheet1.iloc[6, 16:].reset_index(drop=True)
pr_33kv_line_w1 = wnd_cst_sheet1.iloc[7, 16:].reset_index(drop=True)
pre_cmsning_wtg_w1 = wnd_cst_sheet1.iloc[8, 16:].reset_index(drop=True)
cmsning_supprt_w1 = wnd_cst_sheet1.iloc[9, 16:].reset_index(drop=True)
per_cod_w1 = wnd_cst_sheet1.iloc[10, 16:].reset_index(drop=True)
bop_phasing_w1 = wnd_cst_sheet1.iloc[12, 16:].reset_index(drop=True)
pd_exp_phasing_w1 = wnd_cst_sheet1.iloc[13, 16:].reset_index(drop=True)
apprvls_phasing_w1 = wnd_cst_sheet1.iloc[14, 16:].reset_index(drop=True)
lnd_cst_phasing_w1 = wnd_cst_sheet1.iloc[15, 16:].reset_index(drop=True)
contgncy_phasing_w1 = wnd_cst_sheet1.iloc[16, 16:].reset_index(drop=True)
ot_mob_cst_phasing_w1 = wnd_cst_sheet1.iloc[17, 16:].reset_index(drop=True)  # calculated phasings for wind 1

# Wind 2 site inputs
w2_wtg_suply = wnd_cst_sheet2.iloc[4, 2]
w2_uss = wnd_cst_sheet2.iloc[5, 2]
w2_fndation = wnd_cst_sheet2.iloc[6, 2]
w2_bop_trnky = wnd_cst_sheet2.iloc[9, 2]
w2_lnd_cst_budgted = wnd_cst_sheet2.iloc[10, 2]
w2_chnnl_prtnr = wnd_cst_sheet2.iloc[11, 2]
w2_lnd_cst = wnd_cst_sheet2.iloc[14, 2]
w2_ttl_pd_expnses = wnd_cst_sheet2.iloc[17, 2]
w2_apprvls = wnd_cst_sheet2.iloc[20, 2]
w2_contgncy = wnd_cst_sheet2.iloc[23, 2]
w2_prlmmry_pero_exp = wnd_cst_sheet2.iloc[24, 2]
w2_ot_mob_cst = wnd_cst_sheet2.iloc[25, 2]

# wtg supply percnetages inputs
w2_wtg_supp_prcntge = wnd_cst_sheet2.iloc[22, 16]
w2_wtg_adv_prcntge = wnd_cst_sheet2.iloc[23, 16]
w2_wtg_supp_blade_prcntge = wnd_cst_sheet2.iloc[24, 16]
w2_wtg_comm_prcntge = wnd_cst_sheet2.iloc[25, 16]

# logistics
w2_logstcs_prcntge = wnd_cst_sheet2.iloc[27, 16]
w2_dispatch_prcntge = wnd_cst_sheet2.iloc[28, 16]
w2_delvry_prcntge = wnd_cst_sheet2.iloc[29, 16]

# civil works
w2_civil_works_prcntge = wnd_cst_sheet2.iloc[31, 16]
w2_civil_adv_prcntge = wnd_cst_sheet2.iloc[32, 16]
w2_fondn_prcntge = wnd_cst_sheet2.iloc[33, 16]

# e&c
w2_ec_prcntge = wnd_cst_sheet2.iloc[35, 16]
w2_ec_adv_prcntge = wnd_cst_sheet2.iloc[36, 16]
w2_ec_mob_prcntge = wnd_cst_sheet2.iloc[37, 16]
w2_ec_instll_prcntge = wnd_cst_sheet2.iloc[38, 16]
w2_ec_prfrmnce_prcntge = wnd_cst_sheet2.iloc[39, 16]

# electrica works
w2_elec_prcntge = wnd_cst_sheet2.iloc[41, 16]
w2_elec_adv_prcntge = wnd_cst_sheet2.iloc[42, 16]
w2_elect_recipt_prcntge = wnd_cst_sheet2.iloc[43, 16]
w2_elect_dp_yard_prcntge = wnd_cst_sheet2.iloc[44, 16]

# land arrangement
w2_land_arr_prcntge = wnd_cst_sheet2.iloc[46, 16]
w2_land_adv_prcntge = wnd_cst_sheet2.iloc[47, 16]
w2_land_2mnths_prcntge = wnd_cst_sheet2.iloc[48, 16]
w2_land_4mnths_prcntge = wnd_cst_sheet2.iloc[49, 16]
w2_land_wtg_loc_prcntge = wnd_cst_sheet2.iloc[50, 16]
w2_land_name_trnsfr_prcntge = wnd_cst_sheet2.iloc[51, 16]

# wind 2 phasing inputs
ntp_w2 = wnd_cst_sheet2.iloc[2, 16:].reset_index(drop=True)
lnd_aq_suzlon_w2 = wnd_cst_sheet2.iloc[3, 16:].reset_index(drop=True)
cvl_fndation_w2 = wnd_cst_sheet2.iloc[4, 16:].reset_index(drop=True)
wtg_suply_w2 = wnd_cst_sheet2.iloc[5, 16:].reset_index(drop=True)
instlation_wtg_w2 = wnd_cst_sheet2.iloc[6, 16:].reset_index(drop=True)
pr_33kv_line_w2 = wnd_cst_sheet2.iloc[7, 16:].reset_index(drop=True)
pre_cmsning_wtg_w2 = wnd_cst_sheet2.iloc[8, 16:].reset_index(drop=True)
cmsning_supprt_w2 = wnd_cst_sheet2.iloc[9, 16:].reset_index(drop=True)
per_cod_w2 = wnd_cst_sheet2.iloc[10, 16:].reset_index(drop=True)
bop_phasing_w2 = wnd_cst_sheet2.iloc[12, 16:].reset_index(drop=True)
pd_exp_phasing_w2 = wnd_cst_sheet2.iloc[13, 16:].reset_index(drop=True)
apprvls_phasing_w2 = wnd_cst_sheet2.iloc[14, 16:].reset_index(drop=True)
lnd_cst_phasing_w2 = wnd_cst_sheet2.iloc[15, 16:].reset_index(drop=True)
contgncy_phasing_w2 = wnd_cst_sheet2.iloc[16, 16:].reset_index(drop=True)
ot_mob_cst_phasing_w2 = wnd_cst_sheet2.iloc[17, 16:].reset_index(drop=True)

# inputs : solar per mw and wind per mw cost
s_cpx_cst = float(main_sheet.iloc[13, 3])  # solar cost
w_cpx_cst = float(main_sheet.iloc[14, 3])  # wind cost

# other inputs
roi = main_sheet.iloc[21, 3]  # rate of interest
debt_per = main_sheet.iloc[22, 3]  # debvt percentage
equ_per = main_sheet.iloc[23, 3]  # equity percentage
up_equ_per = main_sheet.iloc[24, 3]  # up equity percentage

# dates
cons_date = main_sheet.iloc[9, 3]
cons_dur = main_sheet.iloc[10, 3]
opr_dur = main_sheet.iloc[11, 3]

p1_phasing = main_sheet.iloc[46, 3:].reset_index(drop=True)
p2_phasing = main_sheet.iloc[47, 3:].reset_index(drop=True)
p3_phasing = main_sheet.iloc[48, 3:].reset_index(drop=True)
p4_phasing = main_sheet.iloc[49, 3:].reset_index(drop=True)
p4_phasing = main_sheet.iloc[20, 3:].reset_index(drop=True)
p5_phasing = main_sheet.iloc[44, 3:].reset_index(drop=True)

ex_rate = main_sheet.iloc[42, 3]

# interest
interest_rate = interest.iloc[33, 3]
refinancing_charges = interest.iloc[34, 3]
refinancing_switch = interest.iloc[30, 3]
corporate_fees_per = interest.iloc[37, 3]
corporate_guar_switch = interest.iloc[36, 3]
refinancing_fee_applicable_date = interest.iloc[32, 3]
witholding_tax_interst = interest.iloc[20, 3]

# lender fee
# global_df['day_yr_ratio']
tra = lender_fee_input.iloc[1, 3]
trustee = lender_fee_input.iloc[2, 3]
rating_loan = lender_fee_input.iloc[3, 3]
lia = lender_fee_input.iloc[4, 3]
lie = lender_fee_input.iloc[5, 3]
site_visit = lender_fee_input.iloc[6, 3]
review_charges = lender_fee_input.iloc[7, 3]
# print(tra, trustee, rating_loan, lia, lie, site_visit, review_charges)

# DSRA
dsra_req = interest.iloc[13, 3]
cash_dsra = interest.iloc[15, 3]
bg_dsra = interest.iloc[16, 3]
dsra_bg_cost = interest.iloc[17, 3]
dsra_bg_margin = interest.iloc[18, 3]
interest_on_dsra = interest.iloc[19, 3]

# revenue : calculated monthly and then quarterly
gcc_switch = rev_input.iloc[1, 9]
emission_fac = rev_input.iloc[15, 9]
# tariff_lockin  = rev_input.iloc[18,9]
tariff_post_lockin = rev_input.iloc[20, 9]
merchant_tariff = rev_input.iloc[23, 9]
gcc_sell_price = rev_input.iloc[7, 9]
exchange_rate = rev_input.iloc[13, 9]
depre_gcc_rate = rev_input.iloc[14, 9]

power_sale_days = main_sheet.iloc[33, 3]
gcc_days = main_sheet.iloc[34, 3]
onm_adv_days = main_sheet.iloc[35, 3]
wc_margin = main_sheet.iloc[31, 3]
interest_wc_per = main_sheet.iloc[32, 3]

# global_df['day_yr_ratio']
tra = lender_fee_input.iloc[1, 3]
trustee = lender_fee_input.iloc[2, 3]
rating_loan = lender_fee_input.iloc[3, 3]
lia = lender_fee_input.iloc[4, 3]
lie = lender_fee_input.iloc[5, 3]
site_visit = lender_fee_input.iloc[6, 3]
review_charges = lender_fee_input.iloc[7, 3]

[352]
# Constraints
ci_max = 0.1
iex_sale_max = 0.2
min_electrolyzer_turndown = 0.2
ghs_max_tonnes = 40

s_cap = 328
w1_cap = 236
w2_cap = 236
bid_cap = 328
btry_cap = 10
banking_perc = 0.05
psp_trbne_capacity = 10
lcoe = 3.5
elz_capacity = 300

annual_nh3_production_kt = 200
elz_availability = 70

# annual_nh3_production_kt = float(input("Enter targeted NH3 production (ktpa) ")) # 200
# elz_availability = float(input("Enter electrolyzer availability ",)) # 70
# new variables
elz_specific_power = 5 / 0.09042  # how to make this dynamic
NH3_cap_TPD = math.ceil(
    (annual_nh3_production_kt * 1000 / 335) / 50) * 50  # take next highest round value with multiple of 50
max_NH3_TPH = NH3_cap_TPD * (1 + 0.1) / 24  # max_NH3_TPH=27.5
# NH3_H2_conversion=5.62
NH3_H2_conversion = 5.62376237623762  # FIXed input for time being
energy_per_kg_of_H2 = 55.3
power_to_NH3_plant = 25  # how can it make dynamic ?
GHS_threshhold = 31  # make it dynamic
# GHS_threshhold = float(input("Enter GHS threshold ")) # 40 ##MAKE IT INPUT LATER

# power_as_per_600TPD_NH3 = 246  # (600*55.3/(24*5.62))
elz_annual_degradation = 0.01
year_no_input = 1

power_required_for_H2 = 5 / 0.09042

# H2_NH3_multiplier = 34.08 / 6.06
H2_NH3_multiplier = NH3_H2_conversion
initial_H2_stock = 28  # check to make it dynamic
ttl_btry_capex = 1722.0  # check to make it dynamic
p4_cst = 115.6919200000  # p4 cost

# Given Values
annual_nh3_production_kt = 200
# HOURS_PER_YEAR = 8760
CO2_EMISSION_FACTOR = 0.71  # kg CO2 per kWh
NH3_TO_H2_CONVERSION = NH3_H2_conversion
annual_h2_production = annual_nh3_production_kt * 1000 / NH3_TO_H2_CONVERSION
annual_energy_required_mwh = annual_h2_production * energy_per_kg_of_H2
power_as_per_600TPD_NH3 = annual_energy_required_mwh / 8760

Constants
[353]
data = {
    'Month': ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"],
    'Days': [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
}
days = pd.DataFrame(data)
days.index = days.index + 1

#### Modified month and days
# added 0.01 in the formula to match the round function of excel with python(in python rounding of 28.5 was being taken as 28 instead of 29)
bnkng_days_df = pd.DataFrame({
    'Month': days['Month'],
    'Days': round(days['Days'].apply(lambda x: x * (1 - banking_perc) + 0.01))
})

#### Fixed CONSTANTS DATA INPUTS
firm_power = {
    1: 112,  # January
    2: 118,  # February
    3: 115,  # March
    4: 128,  # April
    5: 161,  # May
    6: 203,  # June
    7: 209,  # July
    8: 187,  # August
    9: 130,  # September
    10: 118,  # October
    11: 126,  # November
    12: 135  # December
}

Global
Functions
[354]


def categorize_hour(hour):
    if 7 <= hour <= 10 or 19 <= hour <= 22:  # 7AM to 10 AM
        return 'c1'
    elif 19 <= hour <= 22:  # 6 PM to 10 PM
        return 'c2'
    elif 11 <= hour < 19 or 6 <= hour < 7:  # 11 AM to 6 PM and 5 AM to 7 AM
        return 'c4'
    else:  # 10 PM to 5 AM
        return 'c5'


def month_end_dt(date):
    end_dt = date + pd.offsets.MonthEnd()
    return end_dt


# Function to calculate the quarter start date from a given date (quarter end date)
def quarter_start(date):
    # Ensure the input is a pandas Timestamp
    date = pd.to_datetime(date)
    start_date = date - pd.offsets.QuarterBegin(startingMonth=1)
    return start_date


def dys_in_mnth(date):
    dt = pd.Timestamp(date)
    return dt.days_in_month


def no_of_yr_pst_cod(date):
    exe_yr = constr_end_date.year
    if not oper_start_date <= date <= end_date:
        return 0
    else:
        return date.year - exe_yr


def op_flag(date):
    if oper_start_date <= date <= end_date:
        return 1
    else:
        return 0


def year_end(date):
    return date + pd.offsets.YearEnd()


# Function to calculate the start and end of the financial year
def financial_year_dates(date):
    if date.month >= 4:
        fy_start = pd.Timestamp(year=date.year, month=4, day=1)
        fy_end = pd.Timestamp(year=date.year + 1, month=3, day=31)
    else:
        fy_start = pd.Timestamp(year=date.year - 1, month=4, day=1)
        fy_end = pd.Timestamp(year=date.year, month=3, day=31)
    return fy_start, fy_end


# Function to calculate the number of days in the financial year for the given date
def days_in_financial_year(date):
    fy_start, fy_end = financial_year_dates(date)
    return (fy_end - fy_start).days + 1


def qaurter_end_date(date):
    end_date = date + pd.offsets.QuarterEnd()
    return end_date


def get_quarter_start(date):
    return (date - pd.offsets.QuarterBegin(startingMonth=1)).normalize()


def days_in_quarter(quarter_start_date):
    quarter_start_date = pd.Timestamp(quarter_start_date)
    quarter_end_date = (quarter_start_date + pd.offsets.QuarterEnd()).normalize()
    return (quarter_end_date - quarter_start_date).days + 1


def flag(date):
    if oper_start_date <= date <= oper_end_date:
        return 1
    else:
        return 0


def month_end_dt(date):
    return date + pd.offsets.MonthEnd()


def no_of_dys(date):
    return pd.Timestamp(date).days_in_month


def no_of_yr_pst_cod(date):
    exe_yr = constr_end_date.year
    if not oper_start_date <= date <= oper_end_date:
        return 0
    else:
        return date.year - exe_yr


def quat_end(date):
    return date + pd.offsets.QuarterEnd()


def calculate_days(row, oper_start_date, oper_end_date):
    if (row['fy_end'] < oper_start_date) or (row['fy_start'] > oper_end_date):
        return 0
    elif (row['fy_start'] < oper_start_date < row['fy_end']):
        return (row['fy_end'] - oper_start_date).days + 1
    elif oper_end_date < row['fy_end']:
        return (oper_end_date - row['fy_start']).days + 1
    else:
        # Entire period is after the operation start date
        return (row['fy_end'] - row['fy_start']).days + 1


Project
Timelines
[395]
constr_end_date = pd.to_datetime(const_date) + pd.DateOffset(months=constr_dur - 1)
oper_start_date = pd.to_datetime(const_date) + pd.DateOffset(months=constr_dur)
end_date = pd.to_datetime(oper_start_date) + pd.DateOffset(months=oper_period_in_mnth)
operation_end_date = pd.to_datetime(oper_start_date) + pd.DateOffset(months=oper_period_in_mnth)
oper_end_date = pd.to_datetime(oper_start_date) + pd.DateOffset(months=oper_period_in_mnth) + pd.Timedelta(days=30)
free_onm_prd = oper_start_date + pd.DateOffset(years=opex_sheet.iloc[48, 3]) - pd.DateOffset(months=1)
free_invrtr_amc = oper_start_date + pd.DateOffset(years=free_period_inv_amc) - pd.DateOffset(months=1)
invrtr_repl = oper_start_date + pd.DateOffset(years=10) - pd.DateOffset(
    months=1)  ## after 10 years of oper_start i.e 2028-01-# Dynamic flags created to mitigate dependency on flags data inputs

# Dynamic flags created to mitigate dependency on flags data inputs
global_df = pd.DataFrame()
global_df['month_start'] = pd.date_range(start=constr_date, end=operation_end_date + pd.DateOffset(years=1), freq='MS')
global_df['op_flag'] = global_df['month_start'].apply(op_flag)
global_df['no_of_yr_pst_cod'] = global_df['month_start'].apply(no_of_yr_pst_cod)
global_df['dys_in_prd'] = global_df['month_start'].apply(dys_in_mnth)
global_df['dys_in_fy'] = global_df['month_start'].apply(days_in_financial_year)

global_quat_df = pd.DataFrame()
global_quat_df['month_start'] = pd.date_range(start=constr_date, end=operation_end_date + pd.DateOffset(years=1),
                                              freq='QS')
global_quat_df['op_flag'] = global_quat_df['month_start'].apply(op_flag)
global_quat_df['no_of_yr_pst_cod'] = global_quat_df['month_start'].apply(no_of_yr_pst_cod)
global_quat_df['days_in_quarter_prd'] = global_quat_df['month_start'].apply(days_in_quarter)
global_quat_df['days_in_quarter_prd'] = global_quat_df['days_in_quarter_prd'] * global_quat_df['op_flag']
global_quat_df['days_in_fy'] = global_quat_df['month_start'].apply(days_in_financial_year)

Timestamp('2053-04-01 00:00:00')
Supplu
calc
[402]


# def supply_calc(gen_profile):
def supply_calc(s_cap, w1_cap, w2_cap, btry_cap, banking_perc, psp_trbne_capacity):
    global pump_capacity, psp_energy_rating, incident_power_threshold, useable_bat_enrgy_rting
    # calculated parameters
    pump_capacity = psp_trbne_capacity * (1750 / 1680)  # calculted parameter # arun : constant values
    psp_energy_rating = psp_trbne_capacity * charging_discharing_cycle  # calcultaed paarmeter : arun : constant valeus pciked uop
    incident_power_threshold = psp_inputs.iloc[6, 3] * psp_trbne_capacity  ###### same here also , calculated paramter
    useable_bat_enrgy_rting = btry_cap * charging_discharing_cycle * (1 - btry_dpt_of_dschrg) / (
                1 + btry_other_losses)  #### here charging discharging was hard coded 6 before (made it duynmacis -7th june)

    daily_gen = gen_profile[['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4']].iloc[8:]
    daily_gen.columns = ['wind_cap_1', 'wind_cap_2', 's_cap']
    daily_gen.reset_index(inplace=True, drop=True)
    daily_gen['s_cap'] = daily_gen['s_cap'] * s_cap
    daily_gen['wind_cap_1'] = daily_gen['wind_cap_1'] * w1_cap
    daily_gen['wind_cap_2'] = daily_gen['wind_cap_2'] * w2_cap
    daily_gen['total_gen'] = daily_gen[['s_cap', 'wind_cap_1', 'wind_cap_2']].sum(axis=1)
    daily_gen["dmd_srvcd"] = np.minimum(bid_cap, daily_gen['total_gen'])
    # date range for hourly frequency
    daily_gen['datetime'] = pd.date_range(start='2023-01-01', end='2023-12-31 23:00:00', freq='H')
    # Extract day of the year, month, and hour
    daily_gen['day_of_year'] = daily_gen['datetime'].dt.dayofyear
    daily_gen['day_of_month'] = daily_gen['datetime'].dt.day
    daily_gen['month'] = daily_gen['datetime'].dt.month
    daily_gen['hour'] = daily_gen['datetime'].dt.hour + 1
    daily_gen['min_p_eltzr'] = daily_gen['month'].map(
        firm_power)  # ( Total supply should be respective to this minimum power to electrolyzer)
    daily_gen['total_supply'] = daily_gen.apply(
        lambda row: row['total_gen'] + (row['min_p_eltzr'] - row['total_gen']) if row['total_gen'] < row[
            'min_p_eltzr'] else (row['total_gen'] if row['total_gen'] <= 250 else 250), axis=1)
    daily_gen['category'] = daily_gen['hour'].apply(categorize_hour)
    daily_gen["rt_gen_bal_before_bat"] = daily_gen["total_gen"] - daily_gen["dmd_srvcd"]
    # Initializations
    daily_gen['cumm_drwn_frm_bnkng_c1'] = 0
    daily_gen['drwn_pwr_frm_bnkng_c1'] = 0
    daily_gen['cumm_drwn_frm_bnkng_c4'] = 0
    daily_gen['drwn_pwr_frm_bnkng_c4'] = 0
    daily_gen['cumm_drwn_frm_bnkng_c5'] = 0
    daily_gen['drwn_pwr_frm_bnkng_c5'] = 0
    daily_gen.at[0, 'drwn_pwr_frm_bnkng_c5'] = max(
        -(bid_cap * days.at[daily_gen.loc[0, 'month'], 'Days'] * banking_perc * 7 * (1 - banking_loss) -
          daily_gen.at[0, 'cumm_drwn_frm_bnkng_c5']),
        daily_gen.at[0, 'dmd_srvcd'] - daily_gen.at[0, 'min_p_eltzr']) if daily_gen.at[0, 'dmd_srvcd'] < daily_gen.at[
        0, 'min_p_eltzr'] else 0

    daily_gen['wtr_bal'] = 0
    daily_gen['btry_bal'] = 0

    daily_gen['psp_dschrgd'] = 0
    daily_gen.at[0, 'psp_dschrgd'] = min(daily_gen.at[0, 'wtr_bal'],
                                         (daily_gen.at[0, 'min_p_eltzr'] - daily_gen.at[0, 'dmd_srvcd'] +
                                          daily_gen.at[0, 'drwn_pwr_frm_bnkng_c1'] + daily_gen.at[
                                              0, 'drwn_pwr_frm_bnkng_c4'] +
                                          daily_gen.at[0, 'drwn_pwr_frm_bnkng_c5'])) if (daily_gen.at[0, 'dmd_srvcd'] -
                                                                                         daily_gen.at[
                                                                                             0, 'drwn_pwr_frm_bnkng_c1'] -
                                                                                         daily_gen.at[
                                                                                             0, 'drwn_pwr_frm_bnkng_c4'] -
                                                                                         daily_gen.at[
                                                                                             0, 'drwn_pwr_frm_bnkng_c5']) < \
                                                                                        daily_gen.at[
                                                                                            0, 'min_p_eltzr'] else 0
    daily_gen['btry_chrgd_b4_cycle_loss'] = 0
    # made change 600 = (btry_cap*6)
    daily_gen.at[0, 'btry_chrgd_b4_cycle_loss'] = min(daily_gen.at[0, 'rt_gen_bal_before_bat'],
                                                      ((btry_cap * 6) - (daily_gen.at[0, 'btry_bal'] * (
                                                                  1 + btry_other_losses)) / (
                                                                   1 - btry_dpt_of_dschrg)) / (1 - rnd_trp_losses),
                                                      btry_cap)

    daily_gen['btry_chrgd_aftr_cycle_loss'] = 0
    daily_gen.at[0, 'btry_chrgd_aftr_cycle_loss'] = daily_gen.at[0, 'btry_chrgd_b4_cycle_loss'] * (1 - rnd_trp_losses)
    daily_gen['rt_gen_bal_aftr_bat'] = 0
    daily_gen.at[0, 'rt_gen_bal_aftr_bat'] = daily_gen.at[0, 'rt_gen_bal_before_bat'] - daily_gen.at[
        0, 'btry_chrgd_b4_cycle_loss']

    daily_gen['btry_dschrgd'] = 0
    daily_gen.at[0, 'btry_dschrgd'] = min(daily_gen.at[0, 'btry_bal'],
                                          (daily_gen.at[0, 'min_p_eltzr'] - daily_gen.at[0, 'dmd_srvcd'] +
                                           daily_gen.loc[0, 'drwn_pwr_frm_bnkng_c1'] + daily_gen.loc[
                                               0, 'drwn_pwr_frm_bnkng_c4'] +
                                           daily_gen.loc[0, 'drwn_pwr_frm_bnkng_c5'] - daily_gen.at[
                                               0, 'psp_dschrgd'])) if (daily_gen.at[0, 'dmd_srvcd'] -
                                                                       daily_gen.loc[0, 'drwn_pwr_frm_bnkng_c1'] -
                                                                       daily_gen.loc[0, 'drwn_pwr_frm_bnkng_c4'] -
                                                                       daily_gen.loc[0, 'drwn_pwr_frm_bnkng_c5'] +
                                                                       daily_gen.at[0, 'psp_dschrgd']) < daily_gen.at[
                                                                          0, 'min_p_eltzr'] else 0

    daily_gen['cumm_banked_c1'] = 0
    daily_gen['bnkd_pwr_c1'] = 0
    daily_gen['cumm_banked_c4'] = 0
    daily_gen['bnkd_pwr_c4'] = 0
    daily_gen['cumm_banked_c5'] = 0
    daily_gen['bnkd_pwr_c5'] = 0
    daily_gen.at[0, 'bnkd_pwr_c5'] = min(bid_cap, daily_gen.at[0, 'rt_gen_bal_aftr_bat'],
                                         ((bid_cap * days.loc[daily_gen.loc[0, 'month'], 'Days'] * banking_perc * 7) -
                                          daily_gen.at[0, 'cumm_banked_c5'])) if daily_gen.at[0, 'cumm_banked_c5'] < (
            bid_cap * days.loc[daily_gen.loc[0, 'month'], 'Days'] * banking_perc * 7
    ) else 0

    daily_gen['bnkd_pwr_avl_fr_frcd_use'] = 0
    daily_gen['rt_gen_bal_b4_psp'] = 0
    daily_gen.at[0, 'rt_gen_bal_b4_psp'] = (daily_gen.at[0, 'total_gen'] - daily_gen.at[0, 'dmd_srvcd'] -
                                            daily_gen.at[0, 'btry_chrgd_b4_cycle_loss'] - daily_gen.at[
                                                0, 'bnkd_pwr_c1'] -
                                            daily_gen.at[0, 'bnkd_pwr_c4'] - daily_gen.at[0, 'bnkd_pwr_c5'] +
                                            daily_gen.at[0, 'bnkd_pwr_avl_fr_frcd_use'])

    daily_gen['psp_chrgd_b4_cycle_loss'] = 0
    daily_gen.at[0, 'psp_chrgd_b4_cycle_loss'] = 0 if min(daily_gen.at[0, 'rt_gen_bal_b4_psp'],
                                                          (pump_capacity / (1 - ists_losses)),
                                                          ((psp_energy_rating - daily_gen.at[0, 'wtr_bal']) / (
                                                                      1 - roundtrip_ists_losses))) < incident_power_threshold else min(
        daily_gen.at[0, 'rt_gen_bal_b4_psp'],
        (pump_capacity / (1 - ists_losses)),
        ((psp_energy_rating - daily_gen.at[0, 'wtr_bal']) / (1 - roundtrip_ists_losses)))

    daily_gen['psp_chrgd_aftr_cycle_loss'] = 0
    daily_gen.at[0, 'psp_chrgd_aftr_cycle_loss'] = daily_gen.at[0, 'psp_chrgd_b4_cycle_loss'] * (
                1 - roundtrip_ists_losses)

    # water balance closing
    daily_gen['wtr_clsng_bal'] = 0
    daily_gen.at[0, 'wtr_clsng_bal'] = daily_gen.at[0, 'wtr_bal'] - daily_gen.at[0, 'psp_dschrgd'] + daily_gen.at[
        0, 'psp_chrgd_aftr_cycle_loss']

    daily_gen['rt_gen_bal_aftr_psp'] = 0
    daily_gen.at[0, 'rt_gen_bal_aftr_psp'] = daily_gen.at[0, 'rt_gen_bal_b4_psp'] - daily_gen.at[
        0, 'psp_chrgd_b4_cycle_loss']

    daily_gen['btry_clsng_bal'] = 0
    daily_gen.at[0, 'btry_clsng_bal'] = min(
        (daily_gen.at[0, 'btry_bal'] + daily_gen.at[0, 'btry_chrgd_aftr_cycle_loss'] - daily_gen.at[0, 'btry_dschrgd']),
        useable_bat_enrgy_rting)
    exe_month = 1
    ex_month = 1
    for index, row in daily_gen.iloc[1:].iterrows():
        if exe_month != row['month']:
            daily_gen.loc[index, 'cumm_drwn_frm_bnkng_c1'] = 0
            daily_gen.loc[index, 'cumm_drwn_frm_bnkng_c4'] = 0
            daily_gen.loc[index, 'cumm_drwn_frm_bnkng_c5'] = 0

        else:
            daily_gen.loc[index, 'cumm_drwn_frm_bnkng_c1'] = (
                        daily_gen.loc[index - 1, 'cumm_drwn_frm_bnkng_c1'] + daily_gen.loc[
                    index - 1, 'drwn_pwr_frm_bnkng_c1'])
            daily_gen.loc[index, 'cumm_drwn_frm_bnkng_c4'] = (
                        daily_gen.loc[index - 1, 'cumm_drwn_frm_bnkng_c4'] + daily_gen.loc[
                    index - 1, 'drwn_pwr_frm_bnkng_c4'])
            daily_gen.loc[index, 'cumm_drwn_frm_bnkng_c5'] = (
                        daily_gen.loc[index - 1, 'cumm_drwn_frm_bnkng_c5'] + daily_gen.loc[
                    index - 1, 'drwn_pwr_frm_bnkng_c5'])
        exe_month = row['month']
        if (row['category'] == 'c1') & (row['dmd_srvcd'] < row['min_p_eltzr']) & (
                daily_gen.at[index, 'cumm_drwn_frm_bnkng_c1'] > (
        -(bid_cap * days.at[row['month'], 'Days'] * banking_perc * 8 * (1 - banking_loss)))):
            daily_gen.at[index, 'drwn_pwr_frm_bnkng_c1'] = max(
                -(bid_cap * days.at[row['month'], 'Days'] * banking_perc * 8 * (1 - banking_loss)) - daily_gen.loc[
                    index, 'cumm_drwn_frm_bnkng_c1'], row['dmd_srvcd'] - row['min_p_eltzr'])

        if (row['category'] == 'c4') & (row['dmd_srvcd'] < row['min_p_eltzr']) & (
                daily_gen.at[index, 'cumm_drwn_frm_bnkng_c4'] > (
        -(bid_cap * days.at[row['month'], 'Days'] * banking_perc * 9 * (1 - banking_loss)))):
            daily_gen.at[index, 'drwn_pwr_frm_bnkng_c4'] = max(
                -(bid_cap * days.at[row['month'], 'Days'] * banking_perc * 9 * (1 - banking_loss)) - daily_gen.loc[
                    index, 'cumm_drwn_frm_bnkng_c4'], row['dmd_srvcd'] - row['min_p_eltzr'])

        if (row['category'] == 'c5') & (row['dmd_srvcd'] < row['min_p_eltzr']) & (
                daily_gen.at[index, 'cumm_drwn_frm_bnkng_c5'] > (
        -(bid_cap * days.at[row['month'], 'Days'] * banking_perc * 7 * (1 - banking_loss)))):
            daily_gen.at[index, 'drwn_pwr_frm_bnkng_c5'] = max(
                -(bid_cap * days.at[row['month'], 'Days'] * banking_perc * 7 * (1 - banking_loss)) - daily_gen.loc[
                    index, 'cumm_drwn_frm_bnkng_c5'], row['dmd_srvcd'] - row['min_p_eltzr'])

        daily_gen.at[index, 'wtr_bal'] = daily_gen.at[index - 1, 'wtr_clsng_bal']
        daily_gen.at[index, 'btry_bal'] = daily_gen.at[index - 1, 'btry_clsng_bal']
        daily_gen.at[index, 'psp_dschrgd'] = min(daily_gen.at[index, 'wtr_bal'], (
                    daily_gen.at[index, 'min_p_eltzr'] - daily_gen.at[index, 'dmd_srvcd'] +
                    daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c1'] + daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c4'] +
                    daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c5'])) if (daily_gen.at[index, 'dmd_srvcd'] -
                                                                        daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c1'] -
                                                                        daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c4'] -
                                                                        daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c5']) < \
                                                                       daily_gen.at[index, 'min_p_eltzr'] else 0
        # changed btry_dpt_of_dschrg to (1-btry_dpt_of_dschrg)
        daily_gen.at[index, 'btry_chrgd_b4_cycle_loss'] = min(daily_gen.at[index, 'rt_gen_bal_before_bat'],
                                                              ((btry_cap * 6) - (daily_gen.at[index, 'btry_bal'] * (
                                                                          1 + btry_other_losses)) / (
                                                                           1 - btry_dpt_of_dschrg)) / (
                                                                          1 - rnd_trp_losses),
                                                              btry_cap)
        daily_gen.at[index, 'btry_chrgd_aftr_cycle_loss'] = daily_gen.at[index, 'btry_chrgd_b4_cycle_loss'] * (
                    1 - rnd_trp_losses)
        daily_gen.at[index, 'rt_gen_bal_aftr_bat'] = daily_gen.at[index, 'rt_gen_bal_before_bat'] - daily_gen.at[
            index, 'btry_chrgd_b4_cycle_loss']
        daily_gen.at[index, 'btry_dschrgd'] = min(daily_gen.at[index, 'btry_bal'], (
                    daily_gen.at[index, 'min_p_eltzr'] - daily_gen.at[index, 'dmd_srvcd'] +
                    daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c1'] + daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c4'] +
                    daily_gen.loc[index, 'drwn_pwr_frm_bnkng_c5'] - daily_gen.at[index, 'psp_dschrgd'])) if (
                                                                                                                        daily_gen.at[
                                                                                                                            index, 'dmd_srvcd'] -
                                                                                                                        daily_gen.loc[
                                                                                                                            index, 'drwn_pwr_frm_bnkng_c1'] -
                                                                                                                        daily_gen.loc[
                                                                                                                            index, 'drwn_pwr_frm_bnkng_c4'] -
                                                                                                                        daily_gen.loc[
                                                                                                                            index, 'drwn_pwr_frm_bnkng_c5'] +
                                                                                                                        daily_gen.at[
                                                                                                                            index, 'psp_dschrgd']) < \
                                                                                                            daily_gen.at[
                                                                                                                index, 'min_p_eltzr'] else 0

        if ex_month != row['month']:
            daily_gen.loc[index, 'cumm_banked_c1'] = 0
            daily_gen.loc[index, 'cumm_banked_c4'] = 0
            daily_gen.loc[index, 'cumm_banked_c5'] = 0

        else:
            daily_gen.loc[index, 'cumm_banked_c1'] = (
                        daily_gen.loc[index - 1, 'cumm_banked_c1'] + daily_gen.loc[index - 1, 'bnkd_pwr_c1'])
            daily_gen.loc[index, 'cumm_banked_c4'] = (
                        daily_gen.loc[index - 1, 'cumm_banked_c4'] + daily_gen.loc[index - 1, 'bnkd_pwr_c4'])
            daily_gen.loc[index, 'cumm_banked_c5'] = (
                        daily_gen.loc[index - 1, 'cumm_banked_c5'] + daily_gen.loc[index - 1, 'bnkd_pwr_c5'])
        ex_month = row['month']

        if (row['category'] == 'c1') & (
                daily_gen.at[index, 'cumm_banked_c1'] < (bid_cap * days.at[row['month'], 'Days'] * banking_perc * 8)):
            daily_gen.at[index, 'bnkd_pwr_c1'] = min(bid_cap, daily_gen.at[index, 'rt_gen_bal_aftr_bat'],
                                                     (bid_cap * days.at[row['month'], 'Days'] * banking_perc * 8) -
                                                     daily_gen.at[index, 'cumm_banked_c1'])

        if (row['category'] == 'c4') & (
                daily_gen.at[index, 'cumm_banked_c4'] < (bid_cap * days.at[row['month'], 'Days'] * banking_perc * 9)):
            daily_gen.at[index, 'bnkd_pwr_c4'] = min(bid_cap, daily_gen.at[index, 'rt_gen_bal_aftr_bat'],
                                                     (bid_cap * days.at[row['month'], 'Days'] * banking_perc * 9) -
                                                     daily_gen.at[index, 'cumm_banked_c4'])

        if (row['category'] == 'c5') & (
                daily_gen.at[index, 'cumm_banked_c5'] < (bid_cap * days.at[row['month'], 'Days'] * banking_perc * 7)):
            daily_gen.at[index, 'bnkd_pwr_c5'] = min(bid_cap, daily_gen.at[index, 'rt_gen_bal_aftr_bat'],
                                                     (bid_cap * days.at[row['month'], 'Days'] * banking_perc * 7) -
                                                     daily_gen.at[index, 'cumm_banked_c5'])

        if (row['month'] in bnkng_days_df.index) & (row['day_of_month'] == bnkng_days_df.loc[row['month'], 'Days']) & (
                row['hour'] == 24):
            daily_gen.at[index, 'bnkd_pwr_avl_fr_frcd_use'] = ((daily_gen.at[index, 'cumm_banked_c1'] + (
                        daily_gen.at[index, 'cumm_drwn_frm_bnkng_c1'] / (1 - banking_loss))) +
                                                               (daily_gen.at[index, 'cumm_banked_c4'] + (daily_gen.at[
                                                                                                             index, 'cumm_drwn_frm_bnkng_c4'] / (
                                                                                                                     1 - banking_loss))) +
                                                               (daily_gen.at[index, 'cumm_banked_c5'] + (daily_gen.at[
                                                                                                             index, 'cumm_drwn_frm_bnkng_c5'] / (
                                                                                                                     1 - banking_loss))))
        if daily_gen.at[index, 'bnkd_pwr_avl_fr_frcd_use'] < 0:
            daily_gen.at[index, 'bnkd_pwr_avl_fr_frcd_use'] = 0

        daily_gen.at[index, 'rt_gen_bal_b4_psp'] = (
                    daily_gen.at[index, 'total_gen'] - daily_gen.at[index, 'dmd_srvcd'] - daily_gen.at[
                index, 'btry_chrgd_b4_cycle_loss'] -
                    daily_gen.at[index, 'bnkd_pwr_c1'] - daily_gen.at[index, 'bnkd_pwr_c4'] - daily_gen.at[
                        index, 'bnkd_pwr_c5'] + daily_gen.at[index, 'bnkd_pwr_avl_fr_frcd_use'])
        daily_gen.at[index, 'psp_chrgd_b4_cycle_loss'] = 0 if min(daily_gen.at[index, 'rt_gen_bal_b4_psp'],
                                                                  (pump_capacity / (1 - ists_losses)), ((
                                                                                                                    psp_energy_rating -
                                                                                                                    daily_gen.at[
                                                                                                                        index, 'wtr_bal']) / (
                                                                                                                    1 - roundtrip_ists_losses))) < incident_power_threshold else min(
            daily_gen.at[index, 'rt_gen_bal_b4_psp'], (pump_capacity / (1 - ists_losses)),
            ((psp_energy_rating - daily_gen.at[index, 'wtr_bal']) / (1 - roundtrip_ists_losses)))
        daily_gen.at[index, 'psp_chrgd_aftr_cycle_loss'] = daily_gen.at[index, 'psp_chrgd_b4_cycle_loss'] * (
                    1 - roundtrip_ists_losses)
        daily_gen.at[index, 'wtr_clsng_bal'] = daily_gen.at[index, 'wtr_bal'] - daily_gen.at[index, 'psp_dschrgd'] + \
                                               daily_gen.at[index, 'psp_chrgd_aftr_cycle_loss']
        daily_gen.at[index, 'rt_gen_bal_aftr_psp'] = daily_gen.at[index, 'rt_gen_bal_b4_psp'] - daily_gen.at[
            index, 'psp_chrgd_b4_cycle_loss']
        daily_gen.at[index, 'btry_clsng_bal'] = min((daily_gen.at[index, 'btry_bal'] + daily_gen.at[
            index, 'btry_chrgd_aftr_cycle_loss'] - daily_gen.at[index, 'btry_dschrgd']), useable_bat_enrgy_rting)

    daily_gen['cumm_bnkd'] = daily_gen['cumm_banked_c1'] + daily_gen['cumm_banked_c4'] + daily_gen['cumm_banked_c5']

    daily_gen['cumm_drwn'] = daily_gen['cumm_drwn_frm_bnkng_c1'] + daily_gen['cumm_drwn_frm_bnkng_c4'] + daily_gen[
        'cumm_drwn_frm_bnkng_c5']

    daily_gen['dmd_srvd_thrgh_gen'] = daily_gen['dmd_srvcd'] - daily_gen['drwn_pwr_frm_bnkng_c1'] - daily_gen[
        'drwn_pwr_frm_bnkng_c4'] - daily_gen['drwn_pwr_frm_bnkng_c5'] + daily_gen['psp_dschrgd'] + daily_gen[
                                          'btry_dschrgd']

    ### Calculations for DI,CA column(IEX sale) w.r.t (NH3 & H2)
    daily_gen['supplement_supply'] = np.where(daily_gen['dmd_srvd_thrgh_gen'] < daily_gen['min_p_eltzr'],
                                              daily_gen['min_p_eltzr'] - daily_gen['dmd_srvd_thrgh_gen'], 0)
    daily_gen['resultant_supply'] = daily_gen['dmd_srvd_thrgh_gen'] + daily_gen['supplement_supply']
    pivot_daily_gen = daily_gen.pivot_table(index='day_of_year', columns='hour', values='resultant_supply')
    pivot_daily_gen['average_power'] = pivot_daily_gen.mean(axis=1)

    # *************************NOTE: variables are given in hardcode form from SME team(same implemented in code)

    pivot_daily_gen['power_for_H2'] = pivot_daily_gen['average_power'] - power_to_NH3_plant
    pivot_daily_gen['H2_gen_TPH'] = pivot_daily_gen['power_for_H2'] * (elz_availability / elz_specific_power)
    pivot_daily_gen['NH3_prod_TPH'] = np.where(pivot_daily_gen['H2_gen_TPH'] * NH3_H2_conversion > max_NH3_TPH,
                                               max_NH3_TPH, pivot_daily_gen['H2_gen_TPH'] * NH3_H2_conversion)
    ### adding NH3_prod_TPH to original yearly dataframe
    # Repeating 'NH3_prod_TPH' values for each hour of the day
    nh3_values = pivot_daily_gen['NH3_prod_TPH'].values.repeat(24)

    # Reshaping the pivot table back to the original dataframe format
    daily_gen_original_format = pivot_daily_gen.drop(
        columns=['NH3_prod_TPH', 'average_power', 'power_for_H2', 'H2_gen_TPH']).stack().reset_index()
    daily_gen_original_format.columns = ['day_of_year', 'hour', 'NH3_prod_TPH']
    daily_gen_original_format['NH3_prod_TPH'] = nh3_values
    daily_gen['NH3_prod_TPH'] = daily_gen_original_format['NH3_prod_TPH']

    ### CX column calculations(Power_for_H2_MW)

    # some variables assumed

    daily_gen['Power_for_H2_MW'] = 0
    daily_gen['H2_stock_tonne'] = 0
    daily_gen['H2_generation_TPH'] = 0
    daily_gen['H2_Required_TPH'] = 0
    daily_gen['H2_to_Store_Tonne'] = 0

    daily_gen.loc[0, 'Power_for_H2_MW'] = daily_gen.loc[0, 'resultant_supply'] - power_to_NH3_plant
    daily_gen.loc[0, 'H2_generation_TPH'] = (daily_gen.loc[0, 'Power_for_H2_MW'] * elz_availability * (
                (1 - elz_annual_degradation) ** (year_no_input - 1)) / power_required_for_H2)
    daily_gen.loc[0, 'H2_Required_TPH'] = daily_gen.loc[0, 'NH3_prod_TPH'] / H2_NH3_multiplier
    daily_gen.loc[0, 'H2_to_Store_Tonne'] = daily_gen.loc[0, 'H2_generation_TPH'] - daily_gen.loc[0, 'H2_Required_TPH']
    daily_gen.loc[0, 'H2_stock_tonne'] = daily_gen.loc[0, 'H2_to_Store_Tonne'] + initial_H2_stock

    for n in range(1, 8760):  # Assuming n ranges from 1 to 8759
        if (daily_gen.loc[n - 1, 'H2_stock_tonne'] > GHS_threshhold) and (
                (daily_gen.loc[n, 'resultant_supply'] - power_to_NH3_plant) > power_as_per_600TPD_NH3):
            daily_gen.loc[n, 'Power_for_H2_MW'] = power_as_per_600TPD_NH3
        else:
            daily_gen.loc[n, 'Power_for_H2_MW'] = daily_gen.loc[n, 'resultant_supply'] - power_to_NH3_plant

        ###CY column
        daily_gen.loc[n, 'H2_generation_TPH'] = (daily_gen.loc[n, 'Power_for_H2_MW'] * elz_availability * (
                    (1 - elz_annual_degradation) ** (year_no_input - 1)) / power_required_for_H2)
        daily_gen.loc[n, 'H2_Required_TPH'] = daily_gen.loc[n, 'NH3_prod_TPH'] / H2_NH3_multiplier
        daily_gen.loc[n, 'H2_to_Store_Tonne'] = daily_gen.loc[n, 'H2_generation_TPH'] - daily_gen.loc[
            n, 'H2_Required_TPH']

        daily_gen.loc[n, 'H2_stock_tonne'] = daily_gen.loc[n - 1, 'H2_stock_tonne'] + daily_gen.loc[
            n, 'H2_to_Store_Tonne']

    daily_gen['excess_power_IEX_sale_after_H2'] = daily_gen['resultant_supply'] - daily_gen[
        'Power_for_H2_MW'] - power_to_NH3_plant
    daily_gen['iex_sale'] = daily_gen['rt_gen_bal_aftr_psp'] + daily_gen['excess_power_IEX_sale_after_H2']
    daily_gen["iex_pur"] = daily_gen["dmd_srvcd"] - daily_gen["drwn_pwr_frm_bnkng_c1"] - daily_gen[
        "drwn_pwr_frm_bnkng_c4"] - daily_gen["drwn_pwr_frm_bnkng_c5"] + daily_gen["btry_dschrgd"] + daily_gen[
                               "psp_dschrgd"]
    daily_gen["iex_pur"] = daily_gen.apply(
        lambda row: row["min_p_eltzr"] - row["iex_pur"] if row["iex_pur"] < row["min_p_eltzr"] else 0, axis=1)

    return daily_gen


# Monthly SUPPLY
def monthly_dataa(daily_gen):
    # *******************Monthly dataframe in the supply calcs : Automation
    mnthly_data = pd.DataFrame()
    mnthly_data['cumm_drawn_during_c1_(MWh)'] = daily_gen[(daily_gen['month'].isin(days.index)) & (
                daily_gen['day_of_month'] == days.loc[daily_gen['month'].values, 'Days'].values) & (
                                                                      daily_gen['hour'] == 24)][
                                                    'cumm_drwn_frm_bnkng_c1'] * -1
    mnthly_data['cumm_banked_during_c1_(MWh)'] = daily_gen[(daily_gen['month'].isin(days.index)) & (
                daily_gen['day_of_month'] == days.loc[daily_gen['month'].values, 'Days'].values) & (
                                                                       daily_gen['hour'] == 24)]['cumm_banked_c1']
    mnthly_data['cumm_drawn_during_c4_(MWh)'] = daily_gen[(daily_gen['month'].isin(days.index)) & (
                daily_gen['day_of_month'] == days.loc[daily_gen['month'].values, 'Days'].values) & (
                                                                      daily_gen['hour'] == 24)][
                                                    'cumm_drwn_frm_bnkng_c4'] * -1
    mnthly_data['cumm_banked_during_c4_(MWh)'] = daily_gen[(daily_gen['month'].isin(days.index)) & (
                daily_gen['day_of_month'] == days.loc[daily_gen['month'].values, 'Days'].values) & (
                                                                       daily_gen['hour'] == 24)]['cumm_banked_c4']
    mnthly_data['cumm_drawn_during_c5_(MWh)'] = daily_gen[(daily_gen['month'].isin(days.index)) & (
                daily_gen['day_of_month'] == days.loc[daily_gen['month'].values, 'Days'].values) & (
                                                                      daily_gen['hour'] == 24)][
                                                    'cumm_drwn_frm_bnkng_c5'] * -1
    mnthly_data['cumm_banked_during_c5_(MWh)'] = daily_gen[(daily_gen['month'].isin(days.index)) & (
                daily_gen['day_of_month'] == days.loc[daily_gen['month'].values, 'Days'].values) & (
                                                                       daily_gen['hour'] == 24)]['cumm_banked_c5']
    mnthly_data['excess_drawn_in_c1_(MWh)'] = mnthly_data['cumm_drawn_during_c1_(MWh)'] - mnthly_data[
        'cumm_banked_during_c1_(MWh)']
    mnthly_data['excess_drawn_in_c4_(MWh)'] = mnthly_data['cumm_drawn_during_c4_(MWh)'] - mnthly_data[
        'cumm_banked_during_c4_(MWh)']
    mnthly_data['excess_drawn_in_c5_(MWh)'] = mnthly_data['cumm_drawn_during_c5_(MWh)'] - mnthly_data[
        'cumm_banked_during_c5_(MWh)']
    condition = ((mnthly_data['excess_drawn_in_c5_(MWh)'] > 0) &
                 (mnthly_data['excess_drawn_in_c1_(MWh)'] < 0) &
                 (np.maximum(mnthly_data['excess_drawn_in_c1_(MWh)'],
                             -(mnthly_data['excess_drawn_in_c5_(MWh)']))))
    mnthly_data['c1_adjustment_in_c5'] = np.where(condition, np.maximum(mnthly_data['excess_drawn_in_c1_(MWh)'],
                                                                        -(mnthly_data['excess_drawn_in_c5_(MWh)'])), 0)
    condition_1 = (mnthly_data['excess_drawn_in_c4_(MWh)'] > 0) & (
                (mnthly_data['excess_drawn_in_c1_(MWh)'] + mnthly_data['c1_adjustment_in_c5']) < 0) & (
                      np.maximum((mnthly_data['excess_drawn_in_c1_(MWh)'] - mnthly_data['c1_adjustment_in_c5']),
                                 -(mnthly_data['excess_drawn_in_c4_(MWh)'])))
    mnthly_data['c1_adjustment_in_c4'] = np.where(condition_1,
                                                  np.maximum((mnthly_data['excess_drawn_in_c1_(MWh)'] - mnthly_data[
                                                      'c1_adjustment_in_c5']),
                                                             - (mnthly_data['excess_drawn_in_c4_(MWh)'])), 0)
    mnthly_data['excess_drawn_in_c1_(MWh)_post_c1_adjustment'] = (mnthly_data['excess_drawn_in_c1_(MWh)'] -
                                                                  mnthly_data['c1_adjustment_in_c5'] - mnthly_data[
                                                                      'c1_adjustment_in_c4'])
    mnthly_data['excess_drawn_in_c4_(MWh)_post_c1_adjustment'] = mnthly_data['excess_drawn_in_c4_(MWh)'] + mnthly_data[
        'c1_adjustment_in_c4']
    mnthly_data['excess_drawn_in_c5_(MWh)_post_c1_adjustment'] = mnthly_data['excess_drawn_in_c5_(MWh)'] + mnthly_data[
        'c1_adjustment_in_c5']
    condition_2 = ((mnthly_data['excess_drawn_in_c5_(MWh)_post_c1_adjustment'] > 0) &
                   (mnthly_data['excess_drawn_in_c4_(MWh)_post_c1_adjustment'] < 0) &
                   (np.maximum(-(mnthly_data['excess_drawn_in_c5_(MWh)_post_c1_adjustment']),
                               mnthly_data['excess_drawn_in_c4_(MWh)_post_c1_adjustment'])))
    mnthly_data['c4_adjustment_in_c5'] = np.where(condition_2, np.maximum(
        -(mnthly_data['excess_drawn_in_c5_(MWh)_post_c1_adjustment']),
        mnthly_data['excess_drawn_in_c4_(MWh)_post_c1_adjustment']), 0)
    mnthly_data['final_excess_drawn_in_c1_and_c2_(MWh)_post_all_adjustments'] = (
                mnthly_data['excess_drawn_in_c1_(MWh)'] -
                mnthly_data['c1_adjustment_in_c5'] -
                mnthly_data['c1_adjustment_in_c4'])
    mnthly_data['final_excess_drawn_in_c4(MWh)_post_all_adjustments'] = (
                mnthly_data['excess_drawn_in_c4_(MWh)_post_c1_adjustment'] -
                mnthly_data['c4_adjustment_in_c5'])
    mnthly_data['final_excess_drawn_in_c5(MWh)_post_all_adjustments'] = (
                mnthly_data['excess_drawn_in_c5_(MWh)_post_c1_adjustment'] +
                mnthly_data['c4_adjustment_in_c5'])
    mnthly_data['cumm_drawn_frm_bnkng_(KWh)'] = -(daily_gen[(daily_gen['month'].isin(days.index)) & (
                daily_gen['day_of_month'] == days.loc[daily_gen['month'].values, 'Days'].values) & (
                                                                        daily_gen['hour'] == 24)]['cumm_drwn']) * 1000
    mnthly_data = mnthly_data.reset_index(drop=True)

    cumm_drawn_frm_bnkng = mnthly_data['cumm_drawn_frm_bnkng_(KWh)'].tolist()
    mnthly_data['final_excess_drawn_in_c1_and_c2_(MWh)_post_all_adjustments'] = np.where(
        mnthly_data['final_excess_drawn_in_c1_and_c2_(MWh)_post_all_adjustments'] < 0, 0,
        mnthly_data['final_excess_drawn_in_c1_and_c2_(MWh)_post_all_adjustments'])
    mnthly_data['final_excess_drawn_in_c4(MWh)_post_all_adjustments'] = np.where(
        mnthly_data['final_excess_drawn_in_c4(MWh)_post_all_adjustments'] < 0, 0,
        mnthly_data['final_excess_drawn_in_c4(MWh)_post_all_adjustments'])
    mnthly_data['final_excess_drawn_in_c5(MWh)_post_all_adjustments'] = np.where(
        mnthly_data['final_excess_drawn_in_c5(MWh)_post_all_adjustments'] < 0, 0,
        mnthly_data['final_excess_drawn_in_c5(MWh)_post_all_adjustments'])

    final_excess_drawn_in_c1_post_all_adjustments = mnthly_data[
        'final_excess_drawn_in_c1_and_c2_(MWh)_post_all_adjustments'].to_list()
    final_excess_drawn_in_c4_post_all_adjustments = mnthly_data[
        'final_excess_drawn_in_c4(MWh)_post_all_adjustments'].to_list()
    final_excess_drawn_in_c5_post_all_adjustments = mnthly_data[
        'final_excess_drawn_in_c5(MWh)_post_all_adjustments'].to_list()
    # mnthly_data.sum(numeric_only=True)
    return mnthly_data


# YEARLY SUPPLY
def macro_call(global_df, daily_gen, s_cap, w1_cap, w2_cap):
    degradation_rates = macro_tab.iloc[1:, 1]
    global_df['day_yr_ratio'] = global_df['dys_in_prd'] / global_df['dys_in_fy']
    daily_gen.drop('datetime', axis=1, inplace=True)
    daily_gen_sum = daily_gen.sum()
    # re_bid_mus = daily_gen_sum['total_supply'] / 1000 # total supply changed to resultant supply for matching re_bid_mus in  in macro_calc  dataframe
    re_bid_mus = daily_gen_sum['resultant_supply'] / 1000
    iex_sale_prcnt = daily_gen_sum['iex_sale'] / daily_gen_sum['total_gen']
    wind_gen_sum = (daily_gen_sum['wind_cap_1'] + daily_gen_sum['wind_cap_2']) * (1 - iex_sale_prcnt) / 1000
    solar_gen_sum = daily_gen_sum['s_cap'] * (1 - iex_sale_prcnt) / 1000
    supplement_supply = daily_gen_sum['iex_pur'] / 1000
    re_sale_mus = daily_gen_sum['iex_sale'] / 1000
    # Calculate static values for 25 years
    macro_cal = pd.DataFrame({
        'year': range(1, 26),
        're_bid_mus': re_bid_mus,
        'wind_gen_mus': wind_gen_sum,
        'solar_gen_mus': solar_gen_sum,
        'supplement_supply': supplement_supply,
        're_sale_mus': re_sale_mus,
        'iex_rev_inr': re_sale_mus * iex_sale_price,
    })
    degradation_rates = np.array(degradation_rates)
    # Pre-calculate Solar degradation
    macro_cal["solar_deg_per"] = degradation_rates
    macro_cal["aug_deg_solar"] = s_cap * macro_cal['solar_deg_per']

    degradation_solar = []
    s_capacity = [s_cap]
    for deg_rate in macro_cal["solar_deg_per"]:
        degradation = s_capacity[-1] * deg_rate
        new_capacity = s_capacity[-1] + degradation
        s_capacity.append(new_capacity)
        degradation_solar.append(degradation)
    macro_cal['s_capacity'] = s_capacity[1:]
    macro_cal['degradation_solar'] = degradation_solar
    return macro_cal


# capacity supply
def cap_supplyy(daily_gen):
    cap_supply = pd.DataFrame()
    cap_supply = daily_gen.copy()

    ##### following is being taken for the sake of months ( year does not matter here as these are design values given by ETS TEAM)
    date_range = pd.date_range(start='1/1/2026', end='31/12/2026 23:00', freq='H')
    cap_supply['date_time'] = date_range

    cap_supply['month'] = cap_supply['date_time'].dt.month
    cap_supply['day'] = cap_supply['date_time'].dt.day
    cap_supply['hour'] = cap_supply['date_time'].dt.hour
    cap_supply['year'] = cap_supply['date_time'].dt.year
    cap_supply.drop('date_time', axis=1, inplace=True)
    cap_supply['real_time_gen'] = daily_gen['total_gen']
    cap_supply['demand_service_gen'] = daily_gen["dmd_srvd_thrgh_gen"]
    cap_supply['ppa_exchange'] = cap_supply['demand_service_gen'] + daily_gen['iex_sale']
    return cap_supply


cap_supply = cap_supplyy(daily_gen)


# # MONTHLY PERCENTAGE CALCULATIONS OF SUPPLY
def monthly_call(cap_supplyy, s_cap, w1_cap, w2_cap):
    monthly_cal = cap_supplyy.groupby('month').agg(
        {'demand_service_gen': 'sum', 'ppa_exchange': 'sum', 'iex_pur': 'sum', 'wind_cap_1': 'sum', 'wind_cap_2': 'sum',
         's_cap': 'sum'}) / 1000
    monthly_cal['wind_gen'] = monthly_cal['wind_cap_1'] + monthly_cal['wind_cap_2']
    grand_total = monthly_cal.sum()

    monthly_cal.reset_index(inplace=True)
    monthly_cal['solar_pr'] = monthly_cal['s_cap'] / grand_total['s_cap']
    monthly_cal['wind_gen_pr'] = monthly_cal['wind_gen'] / grand_total['wind_gen']
    monthly_cal['re_power_pr'] = (monthly_cal['demand_service_gen'] / grand_total['demand_service_gen'])
    monthly_cal['re_exchange_pr'] = (monthly_cal['ppa_exchange'] / grand_total['ppa_exchange'])
    monthly_cal["wind_month_ratio"] = (monthly_cal["wind_cap_1"] + monthly_cal["wind_cap_2"]) / (
                monthly_cal["wind_cap_1"].sum() + monthly_cal["wind_cap_2"].sum())
    monthly_cal["solar_month_ratio"] = monthly_cal["s_cap"] / monthly_cal["s_cap"].sum()
    return monthly_cal


def batt_maintenance_cstt(global_df):
    bat_opex = pd.DataFrame()
    bat_opex['month_start'] = global_df['month_start']
    bat_opex['op_flag'] = global_df['op_flag']
    bat_opex['no_of_yr_pst_cod'] = global_df['no_of_yr_pst_cod']
    batt_energy_rting = btry_cap * charg_dischrg_cycle
    maintenance_chrgs = annual_maintenance_chrgs * ex_rate * 1000 / 10 ** 6
    batt_maintenance_cst = ((maintenance_chrgs * batt_energy_rting) / 12 * bat_opex['op_flag'] * battery_op_flag * (
                1 + bat_escalation) ** (bat_opex['no_of_yr_pst_cod'] - 1))
    return batt_maintenance_cst


# BANKING OPEX
def final_row_dff(global_df, mnthly_data):
    bnkng_op_flag = global_df['op_flag'].tolist()[::12]
    no_of_yrs_pst_cod = global_df['no_of_yr_pst_cod'].tolist()[::12]
    cumm_drawn_frm_bnkng = mnthly_data['cumm_drawn_frm_bnkng_(KWh)'].tolist()
    final_excess_drawn_in_c1_post_all_adjustments = mnthly_data[
        'final_excess_drawn_in_c1_and_c2_(MWh)_post_all_adjustments'].to_list()
    final_excess_drawn_in_c4_post_all_adjustments = mnthly_data[
        'final_excess_drawn_in_c4(MWh)_post_all_adjustments'].to_list()
    final_excess_drawn_in_c5_post_all_adjustments = mnthly_data[
        'final_excess_drawn_in_c5(MWh)_post_all_adjustments'].to_list()
    bnkd_pwr_drwl_cst = [0 if x == 0 else y * (banking_drawal_per_unit_charges / 10 ** 6) *
                                          (1 + banking_drawal_per_unit_charges_escalation) ** (x - 1) for x in
                         no_of_yrs_pst_cod for y in cumm_drawn_frm_bnkng]

    additional_c1_withdrawal_unit_charges = [((b * 1000) / 10 ** 6) * aditnl_c1_wdrwl_unit_chrges *
                                             (1 + additional_peak_pwr_wthdrwl_unt_chrgs_c1) **
                                             (0 if no_of_yrs_pst_cod[x] <= 5 else no_of_yrs_pst_cod[x] -
                                                                                  5) *
                                             bnkng_op_flag[x] for x in range(len(no_of_yrs_pst_cod))
                                             for b in final_excess_drawn_in_c1_post_all_adjustments]
    additional_c4_withdrawal_unit_charges = [((b * 1000) / 10 ** 6) * aditnl_c4_wdrwl_unit_chrges *
                                             (1 + additional_peak_pwr_wthdrwl_unt_chrgs_c4) **
                                             (0 if no_of_yrs_pst_cod[x] <= 5 else no_of_yrs_pst_cod[x] -
                                                                                  5) *
                                             bnkng_op_flag[x] for x in range(len(no_of_yrs_pst_cod))
                                             for b in final_excess_drawn_in_c4_post_all_adjustments]

    additional_c5_withdrawal_unit_charges = [((b * 1000) / 10 ** 6) * aditnl_c5_wdrwl_unit_chrges *
                                             (1 + additional_peak_pwr_wthdrwl_unt_chrgs_c5) **
                                             (0 if no_of_yrs_pst_cod[x] <= 5 else no_of_yrs_pst_cod[x] -
                                                                                  5) *
                                             bnkng_op_flag[x] for x in range(len(no_of_yrs_pst_cod))
                                             for b in final_excess_drawn_in_c5_post_all_adjustments]

    row_df = pd.DataFrame({
        'bnkd_pwr_drwl_cst': bnkd_pwr_drwl_cst,
        'additional_c1_withdrawal_unit_charges': additional_c1_withdrawal_unit_charges,
        'additional_c4_withdrawal_unit_charges': additional_c4_withdrawal_unit_charges,
        'additional_c5_withdrawal_unit_charges': additional_c5_withdrawal_unit_charges,
    })

    final_row_df = row_df.transpose()
    # row_df.sum()
    return final_row_df, no_of_yrs_pst_cod, bnkd_pwr_drwl_cst, additional_c1_withdrawal_unit_charges, additional_c4_withdrawal_unit_charges, additional_c5_withdrawal_unit_charges


# PSP Opex
def ops_op_flagg(global_df, psp_trbne_capacity, strage_rntl_cst_pr_yr):
    ops_op_flag = global_df['op_flag'].tolist()
    pump_strage = [psp_trbne_capacity * (strage_rntl_cst_pr_yr / 12) * op_flag * psp_op_flag for op_flag in ops_op_flag]
    return pump_strage


[403]
daily_gen = supply_calc(s_cap, w1_cap, w2_cap, btry_cap, banking_perc, psp_trbne_capacity)
mnthly_data = monthly_dataa(daily_gen)
macro_call = macro_call(global_df, daily_gen, s_cap, w1_cap, w2_cap)
batt_maintenance_cost = batt_maintenance_cstt(global_df)
final_row_dff = final_row_dff(global_df, mnthly_data)
pump_storage = ops_op_flagg(global_df, psp_trbne_capacity, strage_rntl_cst_pr_yr)
[404]


def solar_capex():
    dc_s_cap = s_cap * (1 + s_ovrld)
    # A.  module cost
    lnd_mod_price = (module_prce - non_usd_m_prce) * eff_exh_rate + non_usd_m_prce * exh_rate
    # module testing
    mod_test_cst = m_testing * eff_exh_rate
    # C. Turn key BOS
    trnky_bos_cst = turnky_bos_cst * (1 + gst)
    if 200 < s_cap <= 300:
        pss = 1178.036607314
    else:
        pss = pss_input
    # E. External Evacuation System
    ehv_line_cst = ehv_line_cost / dc_s_cap
    # G. Approvals and Permits
    conn_bank_grntee_chrgs = (5000000 + 30000000 + (200000 * s_cap)) * 0.01 * 2 * (1 + 0.18) / 1000000
    app_chrgs = conn_bank_grntee_chrgs + otr_than_bg_cst  # *********** being calculated using above two components (change)

    fnl_mod_price = lnd_mod_price * dc_s_cap * (1 + m_breakage_conti)

    f_mod_test_price = mod_test_cst * dc_s_cap * (1 + m_breakage_conti)

    f_mod_logstcs = m_logistcs * dc_s_cap

    f_lc_cst = lc_cst_module_pcmnt * dc_s_cap

    t_ehv_line_cst = ehv_line_cst * dc_s_cap

    cal_bos_cst = bos_cst * dc_s_cap + pss  # calculating using inputs
    t_bos_cst = (cal_bos_cst + trnky_bos_cst)

    t_appr_permits = app_chrgs + stge_connec_approvl + gna_app + rldc_reg_chrgs + conn_modeling + remote_end_mtr_tst + plant_end_mtr_tst + sna_reg

    t_thrd_prty_esia = thrd_party_rsrce_asmnt + thrd_party_esia

    t_thrd_prty_load_flow = thrd_party_lf_stdy + soil_tst_cntr_srvy * dc_s_cap + markting_exp + site_topo_ttl_stion + soil_tst_s_land + hydro_reprt + pull_o_tsting + third_prty_astnc_oe

    land_dilgnce = land_due_gdlines + title_srch * dc_s_cap

    ###################################NEW CHANGE (multiplied with 0) ########################################
    t_pd_exp = insurnce * s_cap * 0 + pd_exp * dc_s_cap

    crtcl_tools = crtcal_tools_req_cod

    land_cst_one_tme_brkge = bkrage_cst * dc_s_cap * lnd_req_pr_mwp

    land_cst_rent = (ttl_land_cst * dc_s_cap - land_cst_one_tme_brkge) * ((t_cnstrucn_perd / 12) - 1)

    na_conversion = na_convn_state_gdlines

    contngncy_cst = contgncy * (
                fnl_mod_price + f_mod_test_price + f_mod_logstcs + f_lc_cst + t_ehv_line_cst + t_bos_cst + t_appr_permits + t_thrd_prty_esia + t_thrd_prty_load_flow + land_dilgnce + t_pd_exp + crtcl_tools + land_cst_one_tme_brkge + land_cst_rent + na_conversion)

    s_phasing = pd.DataFrame()
    s_phasing["fnl_module_prce"] = fnl_module_prce * fnl_mod_price
    s_phasing["fnl_mdule_tstng_prce"] = fnl_mdule_tstng_prce * f_mod_test_price
    s_phasing["fnl_mdule_logistcs"] = fnl_mdule_logistcs * f_mod_logstcs
    s_phasing["fnl_lc_cst_mdule_pcrmnt"] = fnl_lc_cst_mdule_pcrmnt * f_lc_cst
    s_phasing["ttl_ehv_cst"] = ttl_ehv_cst * t_ehv_line_cst
    s_phasing["ttl_bos_cst"] = ttl_bos_cst * t_bos_cst
    s_phasing["contgncy_prcnt"] = contgncy_prcnt * contngncy_cst
    s_phasing["ttl_apprvl_prmits"] = ttl_apprvl_prmits * t_appr_permits
    s_phasing["ttl_thrd_party_esia"] = ttl_thrd_party_esia * t_thrd_prty_esia
    s_phasing["ttl_thrd_party_lf_stdy"] = ttl_thrd_party_lf_stdy * t_thrd_prty_load_flow
    s_phasing["lnd_delgnce_ttle_srch"] = lnd_delgnce_ttle_srch * land_dilgnce
    s_phasing["pd_expnses"] = pd_expnses * t_pd_exp
    s_phasing["crtcal_tools_phasing"] = crtcal_tools_phasing * crtcl_tools
    s_phasing["lnd_cst_one_tme_brkrge"] = lnd_cst_one_tme_brkrge * land_cst_one_tme_brkge
    s_phasing["lnd_cst_rnt"] = lnd_cst_rnt * land_cst_rent
    s_phasing["na_conv_state_guidlns_phasing"] = na_conv_state_guidlns_phasing * na_conversion
    s_phasing["s_capx"] = s_phasing.sum(axis=1)
    return s_phasing


s_phasing = solar_capex()
s_phasing.columns
Index(['fnl_module_prce', 'fnl_mdule_tstng_prce', 'fnl_mdule_logistcs',
       'fnl_lc_cst_mdule_pcrmnt', 'ttl_ehv_cst', 'ttl_bos_cst',
       'contgncy_prcnt', 'ttl_apprvl_prmits', 'ttl_thrd_party_esia',
       'ttl_thrd_party_lf_stdy', 'lnd_delgnce_ttle_srch', 'pd_expnses',
       'crtcal_tools_phasing', 'lnd_cst_one_tme_brkrge', 'lnd_cst_rnt',
       'na_conv_state_guidlns_phasing', 's_capx'],
      dtype='object')
[405]


def wind1_capex():
    # total oem scope
    ##############################changed to 4
    turbine_no = 4
    total_oem_scope = (wtg_suply_w1 + uss_w1 + fndation_w1) * w1_cap / turbine_no
    total_oem_scope

    # calculated components
    # wtg supply
    wtg_supp = wtg_supp_prcntge * total_oem_scope
    wtg_adv = wtg_adv_prcntge * wtg_supp
    wtg_blade_supp = wtg_supp_blade_prcntge * wtg_supp
    wtg_commsn = wtg_comm_prcntge * wtg_supp

    # logistics
    logstcs = logstcs_prcntge * total_oem_scope
    logstcs_dispatch = dispatch_prcntge * logstcs
    logstcs_delvry = delvry_prcntge * logstcs

    # civil works
    cw = civil_works_prcntge * total_oem_scope
    cw_adv = civil_adv_prcntge * cw
    cw_fondn = fondn_prcntge * cw

    # E&C
    ec = ec_prcntge * total_oem_scope
    ec_adv = ec_adv_prcntge * ec
    ec_mob = ec_mob_prcntge * ec
    ec_instll = ec_instll_prcntge * ec
    ec_perfmnce = ec_prfrmnce_prcntge * ec

    # Electrical work
    elec_wrk = elec_prcntge * total_oem_scope
    elect_adv = elec_adv_prcntge * elec_wrk
    elec_recipt = elect_recipt_prcntge * elec_wrk
    elec_dp_yard = elect_dp_yard_prcntge * elec_wrk

    # Land Arrnagement
    land_arr = land_arr_prcntge * total_oem_scope
    land_adv = land_adv_prcntge * land_arr
    land_2mnths = land_2mnths_prcntge * land_arr
    land_4mnths = land_4mnths_prcntge * land_arr
    land_wtg_loc = land_wtg_loc_prcntge * land_arr
    land_name_trnsfr = land_name_trnsfr_prcntge * land_arr

    # other calucalted parameters
    total_bop_cst = (bop_trnky_w1 + lnd_cst_budgted_w1 + chnnl_prtnr_w1) * w1_cap
    total_pd_cst = ttl_pd_expnses_w1 * w1_cap
    total_approval_cst = apprvls_w1
    total_land_cst = lnd_cst_w1 * w1_cap
    total_contngncy_cst = contgncy_w1 * w1_cap
    total_one_time_moblztn = ot_mob_cst_w1

    # WIND CAPEX
    w1_phasing = pd.DataFrame()
    w1_phasing["wtg_advance"] = wtg_adv * ntp_w1
    w1_phasing["wtg_blade_nacelle_supply"] = wtg_blade_supp * wtg_suply_w1
    w1_phasing["wth_commissioning"] = wtg_commsn * per_cod_w1
    w1_phasing["logistics_prior_to_dispatch"] = logstcs_dispatch * wtg_suply_w1
    w1_phasing["logistics_on_delivery"] = logstcs_delvry * wtg_suply_w1
    w1_phasing["civil_works_advance"] = cw_adv * ntp_w1
    w1_phasing["civil_works_foundation"] = cw_fondn * cvl_fndation_w1
    w1_phasing["ec_advance"] = ec_adv * ntp_w1
    w1_phasing["ec_mobilisation"] = ec_mob * wtg_suply_w1
    w1_phasing["ec_installation"] = ec_instll * instlation_wtg_w1
    w1_phasing["ec_performance_test"] = ec_perfmnce * per_cod_w1
    w1_phasing["electrical_work_advance"] = elect_adv * ntp_w1
    w1_phasing["electrical_receipt"] = elec_recipt * pr_33kv_line_w1
    w1_phasing["electrical_dp_yard"] = elec_dp_yard * pr_33kv_line_w1
    w1_phasing["land_arrangement_advance"] = land_adv * ntp_w1
    w1_phasing["land_arrangement_wtg_location"] = land_wtg_loc * lnd_aq_suzlon_w1
    w1_phasing["land_arrangement_name_transfer_sgil"] = land_name_trnsfr * per_cod_w1
    w1_phasing["total_bop_cost"] = total_bop_cst * bop_phasing_w1
    w1_phasing["total_pd_cost"] = total_pd_cst * pd_exp_phasing_w1
    w1_phasing["total_approval_cst"] = total_approval_cst * apprvls_phasing_w1
    w1_phasing["total_land_cst"] = total_land_cst * lnd_cst_phasing_w1
    w1_phasing["total_contingency_cst"] = total_contngncy_cst * contgncy_phasing_w1
    w1_phasing["total_one_time_mobilization"] = total_one_time_moblztn * ot_mob_cst_phasing_w1
    w1_phasing["w1_capx"] = w1_phasing.sum(axis=1)
    return w1_phasing


w1_phasing = wind1_capex()
w1_phasing.columns
Index(['wtg_advance', 'wtg_blade_nacelle_supply', 'wth_commissioning',
       'logistics_prior_to_dispatch', 'logistics_on_delivery',
       'civil_works_advance', 'civil_works_foundation', 'ec_advance',
       'ec_mobilisation', 'ec_installation', 'ec_performance_test',
       'electrical_work_advance', 'electrical_receipt', 'electrical_dp_yard',
       'land_arrangement_advance', 'land_arrangement_wtg_location',
       'land_arrangement_name_transfer_sgil', 'total_bop_cost',
       'total_pd_cost', 'total_approval_cst', 'total_land_cst',
       'total_contingency_cst', 'total_one_time_mobilization', 'w1_capx'],
      dtype='object')
[335]


def wind2_capex():
    # total oem scope
    w2_turbine_no = 3.3
    w2_total_oem_scope = (w2_wtg_suply + w2_uss + w2_fndation) * w2_cap / w2_turbine_no
    w2_total_oem_scope

    # wtg supply
    w2_wtg_supp = w2_wtg_supp_prcntge * w2_total_oem_scope
    w2_wtg_adv = w2_wtg_adv_prcntge * w2_wtg_supp
    w2_wtg_blade_supp = w2_wtg_supp_blade_prcntge * w2_wtg_supp
    w2_wtg_commsn = w2_wtg_comm_prcntge * w2_wtg_supp

    # logistics
    w2_logstcs = w2_logstcs_prcntge * w2_total_oem_scope
    w2_logstcs_dispatch = w2_dispatch_prcntge * w2_logstcs
    w2_logstcs_delvry = w2_delvry_prcntge * w2_logstcs

    # civil works
    w2_cw = w2_civil_works_prcntge * w2_total_oem_scope
    w2_cw_adv = w2_civil_adv_prcntge * w2_cw
    w2_cw_fondn = w2_fondn_prcntge * w2_cw

    # E&C
    w2_ec = w2_ec_prcntge * w2_total_oem_scope
    w2_ec_adv = w2_ec_adv_prcntge * w2_ec
    w2_ec_mob = w2_ec_mob_prcntge * w2_ec
    w2_ec_instll = w2_ec_instll_prcntge * w2_ec
    w2_ec_perfmnce = w2_ec_prfrmnce_prcntge * w2_ec

    # Electrical work
    w2_elec_wrk = w2_elec_prcntge * w2_total_oem_scope
    w2_elect_adv = w2_elec_adv_prcntge * w2_elec_wrk
    w2_elec_recipt = w2_elect_recipt_prcntge * w2_elec_wrk
    w2_elec_dp_yard = w2_elect_dp_yard_prcntge * w2_elec_wrk

    # Land Arrnagement
    w2_land_arr = w2_land_arr_prcntge * w2_total_oem_scope
    w2_land_adv = w2_land_adv_prcntge * w2_land_arr
    w2_land_2mnths = w2_land_2mnths_prcntge * w2_land_arr
    w2_land_4mnths = w2_land_4mnths_prcntge * w2_land_arr
    w2_land_wtg_loc = w2_land_wtg_loc_prcntge * w2_land_arr
    w2_land_name_trnsfr = w2_land_name_trnsfr_prcntge * w2_land_arr

    # other calucalted parameters
    w2_total_bop_cst = (w2_bop_trnky + w2_lnd_cst_budgted + w2_chnnl_prtnr) * w2_cap
    w2_total_pd_cst = w2_ttl_pd_expnses * w2_cap
    w2_total_approval_cst = w2_apprvls
    w2_total_land_cst = w2_lnd_cst * w2_cap
    w2_total_contngncy_cst = w2_contgncy * w2_cap
    w2_total_one_time_moblztn = w2_ot_mob_cst

    # WIND 2 CAPEX
    w2_phasing = pd.DataFrame()
    w2_phasing["wtg_advance"] = w2_wtg_adv * ntp_w2
    w2_phasing["wtg_blade_nacelle_supply"] = w2_wtg_blade_supp * wtg_suply_w2
    w2_phasing["wth_commissioning"] = w2_wtg_commsn * per_cod_w2
    w2_phasing["logistics_prior_to_dispatch"] = w2_logstcs_dispatch * wtg_suply_w2
    w2_phasing["logistics_on_delivery"] = w2_logstcs_delvry * wtg_suply_w2
    w2_phasing["civil_works_advance"] = w2_cw_adv * ntp_w2
    w2_phasing["civil_works_foundation"] = w2_cw_fondn * cvl_fndation_w2
    w2_phasing["ec_advance"] = w2_ec_adv * ntp_w2
    w2_phasing["ec_mobilisation"] = w2_ec_mob * wtg_suply_w2
    w2_phasing["ec_installation"] = w2_ec_instll * instlation_wtg_w2
    w2_phasing["ec_performance_test"] = w2_ec_perfmnce * per_cod_w2
    w2_phasing["electrical_work_advance"] = w2_elect_adv * ntp_w2
    w2_phasing["electrical_receipt"] = w2_elec_recipt * pr_33kv_line_w2
    w2_phasing["electrical_dp_yard"] = w2_elec_dp_yard * pr_33kv_line_w2
    w2_phasing["land_arrangement_advance"] = w2_land_adv * ntp_w2
    w2_phasing["land_arrangement_wtg_location"] = w2_land_wtg_loc * lnd_aq_suzlon_w2
    w2_phasing["land_arrangement_name_transfer_sgil"] = w2_land_name_trnsfr * per_cod_w2
    w2_phasing["total_bop_cost"] = w2_total_bop_cst * bop_phasing_w2
    w2_phasing["total_pd_cost"] = w2_total_pd_cst * pd_exp_phasing_w2
    w2_phasing["total_approval_cst"] = w2_total_approval_cst * apprvls_phasing_w2
    w2_phasing["total_land_cst"] = w2_total_land_cst * lnd_cst_phasing_w2
    w2_phasing["total_contingency_cst"] = w2_total_contngncy_cst * contgncy_phasing_w2
    w2_phasing["total_one_time_mobilization"] = w2_total_one_time_moblztn * ot_mob_cst_phasing_w2
    w2_phasing["w2_capx"] = w2_phasing.sum(axis=1)
    return w2_phasing


w2_phasing = wind2_capex()
w2_phasing.columns
Index(['wtg_advance', 'wtg_blade_nacelle_supply', 'wth_commissioning',
       'logistics_prior_to_dispatch', 'logistics_on_delivery',
       'civil_works_advance', 'civil_works_foundation', 'ec_advance',
       'ec_mobilisation', 'ec_installation', 'ec_performance_test',
       'electrical_work_advance', 'electrical_receipt', 'electrical_dp_yard',
       'land_arrangement_advance', 'land_arrangement_wtg_location',
       'land_arrangement_name_transfer_sgil', 'total_bop_cost',
       'total_pd_cost', 'total_approval_cst', 'total_land_cst',
       'total_contingency_cst', 'total_one_time_mobilization', 'w2_capx'],
      dtype='object')
[336]


def cumm(lst):
    cnt = Counter(lst)
    cum_sum = [lst[0]]
    for i in range(1, len(lst)):
        cum_sum.append(cum_sum[i - 1] + lst[i])
    return cum_sum


def pp_capex():
    p4_cst = 115.6919200000
    phasing = pd.DataFrame()
    p1 = (((5000000 + 30000000 + (200000 * w1_cap)) * 0.01 * 2 * (1 + 0.18) / 1000000) + (
                (5000000 + 30000000 + (200000 * w2_cap)) * 0.01 * 2 * (1 + 0.18) / 1000000))
    p2 = (0.5 * 1.18) * 2
    p3 = (0.5 * 1.18) * 2
    p4 = 0.235 * w1_cap * 1.18 + 0.235 * w2_cap * 1.18
    pp1 = p1_phasing * p1
    pp2 = p2_phasing * p2
    pp3 = p3_phasing * p3
    pp4 = p4_phasing * p4
    phasing["pp4_phasing"] = pp1 + pp2 + pp3 + pp4  # updated formula(9-10-23)
    phasing["pp5_phasing"] = 0  # intially
    phasing["pp4_5_phasing"] = phasing["pp4_phasing"].replace(np.nan, 0) + phasing["pp5_phasing"].replace(np.nan, 0)
    # phasing = phasing.fillna(0)
    return phasing


phasing = pp_capex()


# phasing

def battery_capex():
    batt_energy_rting = btry_cap * charg_dischrg_cycle

    usable_bat_engy = batt_energy_rting * (1 - batt_depth_dschrge) / (1 + batt_other_losses)

    batt_capex_cost = batt_capex_cost_ip * 1000 * ex_rate / 10 ** 6

    batt_capex = batt_capex_cost * batt_energy_rting

    batt_phasing = batt_capex_phasing * batt_capex

    batt_phasing = pd.to_numeric(batt_phasing, errors='coerce')
    zero_series = pd.Series([0])
    batt_phasing = pd.concat([batt_phasing, zero_series], ignore_index=True)
    btry_cpx = batt_phasing.tolist()

    phasing["btry_cpx"] = btry_cpx
    ttl_btry_capex = phasing["btry_cpx"].sum()
    return btry_cpx


btry_cpx = battery_capex()
# btry_cpx
[337]


def capex_logic(mnthly_cpx, capex):
    # dates
    cons_date = main_sheet.iloc[9, 3]
    cons_dur = main_sheet.iloc[10, 3]
    opr_dur = main_sheet.iloc[11, 3]
    comm_date = pd.to_datetime(cons_date) + pd.DateOffset(months=cons_dur)
    # comm_date
    # First day of month
    month_start = pd.date_range(cons_date, comm_date, freq='MS').to_pydatetime().tolist()
    # Last day of month
    month_end = pd.date_range(cons_date, comm_date + relativedelta(months=1), freq='M').to_pydatetime().tolist()

    idc_l = [0] * constr_dur + [0]  ##### make this dynamic as per cons duration
    while True:
        cumm_capx = cumm(mnthly_cpx)  # calling cumm fucntion

        # 30% of cumm capex
        cumm_capx_30_per = []
        for i in cumm_capx:
            l2 = equ_per * i  ######### its not 30 % of cumm capex, rather its
            cumm_capx_30_per.append(l2)

        equity = equ_per * capex  # (30% of capex including pp)
        up_equity = up_equ_per * equity  # 50 % of equity
        lft_equity = up_equ_per * equity
        debt = debt_per * capex  # 70% of capex including pp

        u_e = []
        l_e = []
        for (mnth_dmd, cumm_capx_30) in zip(mnthly_cpx, cumm_capx_30_per):
            up_equ = min(mnth_dmd, (up_equity - sum(u_e))) if sum(
                u_e) < up_equity else 0  # Min(mnth_dmd, up_equity - sum(u_e)) else 0
            lft_equ = cumm_capx_30 - (up_equity + sum(l_e)) if cumm_capx_30 > (up_equity + sum(l_e)) else 0
            u_e.append(up_equ)
            l_e.append(lft_equ)

        # making dataframe for the same
        df = pd.DataFrame()
        pd.set_option('display.max_columns', None)
        df["month_start"] = month_start
        df["month_end"] = month_end
        df["mntly_cpx"] = mnthly_cpx
        df["cum_cpx"] = np.round(cumm_capx, 2)
        df["30_cum cpx"] = np.round(cumm_capx_30_per, 2)
        df["up_equ_dis"] = u_e
        df["lft_equ_dis"] = l_e
        df["idc"] = idc_l  # setting idc to 0 initially
        df["equ_infused"] = df["up_equ_dis"] + df["lft_equ_dis"]
        df["debt"] = df["mntly_cpx"] + df["idc"] - df["equ_infused"]  # adding idc into debt
        df = df.replace(np.nan, 0)
        df.T

        cumm_debt = cumm(df["debt"])
        df["cumm_debt"] = cumm_debt

        # mov _avg
        df["mov_avg"] = df['cumm_debt'].rolling(2).mean()

        df["days_in_mnth"] = df["month_start"].apply(dys_in_mnth)

        condition = df["month_end"] < comm_date

        df["idc"] = 0  # Setting idc to 0 initially
        # #### make 365 dynamic
        dys_in_yr = 365
        df.loc[condition, "idc"] = df["mov_avg"] * (roi / dys_in_yr) * df["days_in_mnth"]

        res = pd.concat([phasing.T, df.T], axis=0)
        res
        # calculating phasing 5th component
        phasing["pp5_phasing"] = p5_phasing * 0.0085 * equity
        phasing["mnthly_cpx"] = phasing["s_capx"] + phasing["w1_capx"] + phasing["w2_capx"] + phasing["pp4_phasing"] + \
                                phasing["pp5_phasing"].replace(np.nan, 0) + batt_phasing
        mnthly_cpx = phasing["mnthly_cpx"].values.tolist()
        phasing.T

        # capex = sum of monthly capex
        upd_capex = phasing["mnthly_cpx"].sum() + df["idc"].sum()

        if abs(upd_capex - capex) == 0:
            break
        capex = upd_capex
        idc_l = df["idc"].values.tolist()

    new_idc_l = df["idc"].fillna(0).to_list()
    #### 1st FINAL DISTRIBUTION CODE
    a = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).tolist()
    cumm_capx = cumm(a)
    capex = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).sum()
    # print("capex", capex)
    equity = capex * equ_per
    # print("equity", equity)

    # 30% of cumm capex
    cumm_capx_30_per = []
    for i in cumm_capx:
        l2 = equ_per * i
        cumm_capx_30_per.append(l2)
    # equity debt (70, 30 distribution)
    equity = equ_per * capex  # (30% of capex including pp)
    up_equity = up_equ_per * equity  # 50 % of equity
    lft_equity = up_equ_per * equity
    debt = debt_per * capex  # 70% of capex including pp
    u_e = []
    l_e = []
    for (mnth_dmd, cumm_capx_30) in zip(mnthly_cpx, cumm_capx_30_per):
        up_equ = min(mnth_dmd, (up_equity - sum(u_e))) if sum(
            u_e) < up_equity else 0  # Min(mnth_dmd, up_equity - sum(u_e)) else 0
        lft_equ = cumm_capx_30 - (up_equity + sum(l_e)) if cumm_capx_30 > (up_equity + sum(l_e)) else 0
        u_e.append(up_equ)
        l_e.append(lft_equ)
    # making dataframe for the same
    df = pd.DataFrame()
    pd.set_option('display.max_columns', None)
    df["mntly_cpx"] = mnthly_cpx
    df["cum_cpx"] = np.round(cumm_capx, 2)
    df["30_cum cpx"] = np.round(cumm_capx_30_per, 2)
    df["month_start"] = month_start
    df["month_end"] = month_end
    df["up_equ_dis"] = u_e
    df["lft_equ_dis"] = l_e
    df["equ_infused"] = df["up_equ_dis"] + df["lft_equ_dis"]
    df["s_idc"] = new_idc_l
    df["debt"] = df["mntly_cpx"] + df["s_idc"] - df["equ_infused"]
    df.T

    cumm_debt = cumm(df["debt"])
    df["cumm_debt"] = cumm_debt
    df["mov_avg"] = df['cumm_debt'].rolling(2).mean()

    df["days_in_mnth"] = df["month_start"].apply(dys_in_mnth)
    df["idc"] = 0  # Setting idc to 0 initially
    df.loc[condition, "idc"] = df["mov_avg"] * (roi / dys_in_yr) * df["days_in_mnth"]
    # combining phasings and distributions, idc
    res = pd.concat([phasing.T, df.T], axis=0)
    res.fillna(0, inplace=True)
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()
    # print("final capex including idc ",final_capex)
    res.T["idc"].fillna(0).sum()
    res.T["mntly_cpx"].fillna(0).sum()
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()
    final_capex

    new_idc_l = df["idc"].fillna(0).to_list()
    a = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).tolist()
    cumm_capx = cumm(a)
    capex = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).sum()
    equity = capex * equ_per

    # 30% of cumm capex
    cumm_capx_30_per = []
    for i in cumm_capx:
        l2 = equ_per * i
        cumm_capx_30_per.append(l2)

    # equity debt (70, 30 distribution)
    equity = equ_per * capex  # (30% of capex including pp)
    up_equity = up_equ_per * equity  # 50 % of equity
    lft_equity = up_equ_per * equity
    debt = debt_per * capex  # 70% of capex including pp

    u_e = []
    l_e = []
    for (mnth_dmd, cumm_capx_30) in zip(mnthly_cpx, cumm_capx_30_per):
        up_equ = min(mnth_dmd, (up_equity - sum(u_e))) if sum(
            u_e) < up_equity else 0  # Min(mnth_dmd, up_equity - sum(u_e)) else 0
        lft_equ = cumm_capx_30 - (up_equity + sum(l_e)) if cumm_capx_30 > (up_equity + sum(l_e)) else 0
        u_e.append(up_equ)
        l_e.append(lft_equ)

    # making dataframe for the same
    df = pd.DataFrame()
    pd.set_option('display.max_columns', None)
    df["mntly_cpx"] = mnthly_cpx
    df["cum_cpx"] = np.round(cumm_capx, 2)
    df["30_cum cpx"] = np.round(cumm_capx_30_per, 2)
    df["month_start"] = month_start
    df["month_end"] = month_end
    df["up_equ_dis"] = u_e
    df["lft_equ_dis"] = l_e
    df["equ_infused"] = df["up_equ_dis"] + df["lft_equ_dis"]
    df["s_idc"] = new_idc_l
    df["debt"] = df["mntly_cpx"] + df["s_idc"] - df["equ_infused"]
    df.T

    cumm_debt = cumm(df["debt"])
    df["cumm_debt"] = cumm_debt

    df["mov_avg"] = df['cumm_debt'].rolling(2).mean()

    df["days_in_mnth"] = df["month_start"].apply(dys_in_mnth)

    # Using the boolean mask to update the "idc" column
    df["idc"] = 0  # Setting idc to 0 initially
    df.loc[condition, "idc"] = df["mov_avg"] * (roi / 365) * df["days_in_mnth"]

    # combining phasings and distributions, idc
    res = pd.concat([phasing.T, df.T], axis=0)
    res.fillna(0, inplace=True)
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()
    print("final capex including idc ", final_capex)

    res.T["idc"].fillna(0).sum()
    res.T["mntly_cpx"].fillna(0).sum()
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()

    capex_monthly = pd.DataFrame()
    capex_monthly['Month Start Date flag'] = global_df['month_start']
    capex_monthly['capex_month'] = res.T['mntly_cpx'] + res.T['idc'].fillna(0)
    capex_monthly['equity_draw'] = res.T['equ_infused']
    capex_monthly['debt_draw'] = res.T['debt']
    capex_monthly['idc_quat'] = res.T['idc'].fillna(0)
    capex_monthly.fillna(0, inplace=True)
    # capex_monthly
    capex_quat = capex_monthly
    capex_quat.set_index('Month Start Date flag', inplace=True)
    capex_quat = capex_monthly.resample('Q').sum()
    capex_quat = capex_quat.reset_index(drop=True)
    # capex_quat
    return final_capex, capex_monthly, capex_quat


def re_fm():
    s_phasing = solar_capex()
    w1_phasing = wind1_capex()
    w2_phasing = wind2_capex()
    pp_phasing = pp_capex()
    btry_cpx = battery_capex()
    phasing = pd.DataFrame()
    phasing["mnthly_cpx"] = phasing["s_capx"] + phasing["w1_capx"] + phasing["w2_capx"] + phasing["pp4_phasing"] + \
                            phasing["pp5_phasing"].replace(np.nan, 0) + batt_phasing
    re_cpx = s_phasing['s_capx'] + w1_phasing['w1_capx'] + w2_phasing['w2_capx'] + pp_phasing[
        'pp4_5_phasing'] + btry_cpx
    re_cpx = re_cpx.fillna(0)
    mnthly_cpx = re_cpx.values.tolist()
    capex = re_cpx.sum()
    final_capex = capex_logic(mnthly_cpx, capex)
    return final_capex[0]


re_fm()
---------------------------------------------------------------------------
KeyError
Traceback(most
recent
call
last)
Cell
In[337], line
234
231
final_capex = capex_logic(mnthly_cpx, capex)
232
return final_capex[0] --> 234
re_fm()
Cell
In[337], line
226, in re_fm()
224
btry_cpx = battery_capex()
225
phasing = pd.DataFrame() --> 226
phasing["mnthly_cpx"] = phasing["s_capx"] + phasing["w1_capx"] + phasing["w2_capx"] + phasing["pp4_phasing"] + phasing[
    "pp5_phasing"].replace(np.nan, 0) + batt_phasing
227
re_cpx = s_phasing['s_capx'] + w1_phasing['w1_capx'] + w2_phasing['w2_capx'] + pp_phasing['pp4_5_phasing'] + btry_cpx
228
re_cpx = re_cpx.fillna(0)
File
C:\ProgramData\anaconda3\Lib\site - packages\pandas\core\frame.py: 3893, in DataFrame.__getitem__(self, key)
3891
if self.columns.nlevels > 1: 3892
return self._getitem_multilevel(key) -> 3893
indexer = self.columns.get_loc(key)
3894
if is_integer(indexer): 3895
indexer = [indexer]
File
C:\ProgramData\anaconda3\Lib\site - packages\pandas\core\indexes\range.py: 418, in RangeIndex.get_loc(self, key)
416
raise KeyError(key) from err
417
if isinstance(key, Hashable): --> 418
raise KeyError(key)
419
self._check_indexing_error(key)
420
raise KeyError(key)
KeyError: 's_capx'
Flags
[388]
# Flag inputs
flag = pd.read_excel(inputs_xlsx, sheet_name='Flags').fillna(0).T
t_m = 360
flag = flag.iloc[4:(6 + t_m), 5:]
flag.reset_index(drop=True, inplace=True)
flag = flag.drop(1)
flag.columns = flag.iloc[0]
flag = flag.drop(0)
flag.reset_index(drop=True, inplace=True)

updated
gh2_nh3
[406]


def upd_fm_gh2_nh3(s_cap, w1_cap, w2_cap, btry_cap, elz_capacity, GHS_capacity):
    macro_cal = macro_call
    batt_maintenance_cst = batt_maintenance_cost
    final_row_df = final_row_dff
    pump_strage = pump_storage

    # flag1 = pd.read_excel(inputs_xlsx, sheet_name='Flags').fillna('').T
    # t_m = 360
    # flag1 = flag1.iloc[4:(6+t_m), 5:]
    # flag1.reset_index(drop=True, inplace=True)
    # flag1 = flag1.drop(1)
    # flag1.columns = flag1.iloc[0]
    # flag1 = flag1.drop(0)
    # flag1.reset_index(drop=True, inplace=True)
    # DC Capacity
    dc_s_cap = s_cap * (1 + s_ovrld)

    # A.  module cost
    lnd_mod_price = (module_prce - non_usd_m_prce) * eff_exh_rate + non_usd_m_prce * exh_rate

    # module testing
    mod_test_cst = m_testing * eff_exh_rate

    # C. Turn key BOS
    trnky_bos_cst = turnky_bos_cst * (1 + gst)

    if 200 < s_cap <= 300:
        pss = 1178.036607314
    else:
        pss = pss_input

    # E. External Evacuation System
    ehv_line_cst = ehv_line_cost / dc_s_cap

    # G. Approvals and Permits
    conn_bank_grntee_chrgs = (5000000 + 30000000 + (200000 * s_cap)) * 0.01 * 2 * (1 + 0.18) / 1000000
    app_chrgs = conn_bank_grntee_chrgs + otr_than_bg_cst  # *********** being calculated using above two components (change)

    fnl_mod_price = lnd_mod_price * dc_s_cap * (1 + m_breakage_conti)

    f_mod_test_price = mod_test_cst * dc_s_cap * (1 + m_breakage_conti)

    f_mod_logstcs = m_logistcs * dc_s_cap

    f_lc_cst = lc_cst_module_pcmnt * dc_s_cap

    t_ehv_line_cst = ehv_line_cst * dc_s_cap

    cal_bos_cst = bos_cst * dc_s_cap + pss  # calculating using inputs
    t_bos_cst = (cal_bos_cst + trnky_bos_cst)

    t_appr_permits = app_chrgs + stge_connec_approvl + gna_app + rldc_reg_chrgs + conn_modeling + remote_end_mtr_tst + plant_end_mtr_tst + sna_reg

    t_thrd_prty_esia = thrd_party_rsrce_asmnt + thrd_party_esia

    t_thrd_prty_load_flow = thrd_party_lf_stdy + soil_tst_cntr_srvy * dc_s_cap + markting_exp + site_topo_ttl_stion + soil_tst_s_land + hydro_reprt + pull_o_tsting + third_prty_astnc_oe

    land_dilgnce = land_due_gdlines + title_srch * dc_s_cap

    ###################################NEW CHANGE (multiplied with 0) ########################################
    t_pd_exp = insurnce * s_cap * 0 + pd_exp * dc_s_cap

    crtcl_tools = crtcal_tools_req_cod

    land_cst_one_tme_brkge = bkrage_cst * dc_s_cap * lnd_req_pr_mwp

    land_cst_rent = (ttl_land_cst * dc_s_cap - land_cst_one_tme_brkge) * ((t_cnstrucn_perd / 12) - 1)

    na_conversion = na_convn_state_gdlines

    contngncy_cst = contgncy * (
                fnl_mod_price + f_mod_test_price + f_mod_logstcs + f_lc_cst + t_ehv_line_cst + t_bos_cst + t_appr_permits + t_thrd_prty_esia + t_thrd_prty_load_flow + land_dilgnce + t_pd_exp + crtcl_tools + land_cst_one_tme_brkge + land_cst_rent + na_conversion)

    # total oem scope
    ##############################changed to 4
    turbine_no = 4
    total_oem_scope = (wtg_suply_w1 + uss_w1 + fndation_w1) * w1_cap / turbine_no
    total_oem_scope

    # calculated components
    # wtg supply
    wtg_supp = wtg_supp_prcntge * total_oem_scope
    wtg_adv = wtg_adv_prcntge * wtg_supp
    wtg_blade_supp = wtg_supp_blade_prcntge * wtg_supp
    wtg_commsn = wtg_comm_prcntge * wtg_supp

    # logistics
    logstcs = logstcs_prcntge * total_oem_scope
    logstcs_dispatch = dispatch_prcntge * logstcs
    logstcs_delvry = delvry_prcntge * logstcs

    # civil works
    cw = civil_works_prcntge * total_oem_scope
    cw_adv = civil_adv_prcntge * cw
    cw_fondn = fondn_prcntge * cw

    # E&C
    ec = ec_prcntge * total_oem_scope
    ec_adv = ec_adv_prcntge * ec
    ec_mob = ec_mob_prcntge * ec
    ec_instll = ec_instll_prcntge * ec
    ec_perfmnce = ec_prfrmnce_prcntge * ec

    # Electrical work
    elec_wrk = elec_prcntge * total_oem_scope
    elect_adv = elec_adv_prcntge * elec_wrk
    elec_recipt = elect_recipt_prcntge * elec_wrk
    elec_dp_yard = elect_dp_yard_prcntge * elec_wrk

    # Land Arrnagement
    land_arr = land_arr_prcntge * total_oem_scope
    land_adv = land_adv_prcntge * land_arr
    land_2mnths = land_2mnths_prcntge * land_arr
    land_4mnths = land_4mnths_prcntge * land_arr
    land_wtg_loc = land_wtg_loc_prcntge * land_arr
    land_name_trnsfr = land_name_trnsfr_prcntge * land_arr

    # other calucalted parameters
    total_bop_cst = (bop_trnky_w1 + lnd_cst_budgted_w1 + chnnl_prtnr_w1) * w1_cap
    total_pd_cst = ttl_pd_expnses_w1 * w1_cap
    total_approval_cst = apprvls_w1
    total_land_cst = lnd_cst_w1 * w1_cap
    total_contngncy_cst = contgncy_w1 * w1_cap
    total_one_time_moblztn = ot_mob_cst_w1

    # total oem scope
    w2_turbine_no = 3.3
    w2_total_oem_scope = (w2_wtg_suply + w2_uss + w2_fndation) * w2_cap / turbine_no
    w2_total_oem_scope

    # wtg supply
    w2_wtg_supp = w2_wtg_supp_prcntge * w2_total_oem_scope
    w2_wtg_adv = w2_wtg_adv_prcntge * w2_wtg_supp
    w2_wtg_blade_supp = w2_wtg_supp_blade_prcntge * w2_wtg_supp
    w2_wtg_commsn = w2_wtg_comm_prcntge * w2_wtg_supp

    # logistics
    w2_logstcs = w2_logstcs_prcntge * w2_total_oem_scope
    w2_logstcs_dispatch = w2_dispatch_prcntge * w2_logstcs
    w2_logstcs_delvry = w2_delvry_prcntge * w2_logstcs

    # civil works
    w2_cw = w2_civil_works_prcntge * w2_total_oem_scope
    w2_cw_adv = w2_civil_adv_prcntge * w2_cw
    w2_cw_fondn = w2_fondn_prcntge * w2_cw

    # E&C
    w2_ec = w2_ec_prcntge * w2_total_oem_scope
    w2_ec_adv = w2_ec_adv_prcntge * w2_ec
    w2_ec_mob = w2_ec_mob_prcntge * w2_ec
    w2_ec_instll = w2_ec_instll_prcntge * w2_ec
    w2_ec_perfmnce = w2_ec_prfrmnce_prcntge * w2_ec

    # Electrical work
    w2_elec_wrk = w2_elec_prcntge * w2_total_oem_scope
    w2_elect_adv = w2_elec_adv_prcntge * w2_elec_wrk
    w2_elec_recipt = w2_elect_recipt_prcntge * w2_elec_wrk
    w2_elec_dp_yard = w2_elect_dp_yard_prcntge * w2_elec_wrk

    # Land Arrnagement
    w2_land_arr = w2_land_arr_prcntge * w2_total_oem_scope
    w2_land_adv = w2_land_adv_prcntge * w2_land_arr
    w2_land_2mnths = w2_land_2mnths_prcntge * w2_land_arr
    w2_land_4mnths = w2_land_4mnths_prcntge * w2_land_arr
    w2_land_wtg_loc = w2_land_wtg_loc_prcntge * w2_land_arr
    w2_land_name_trnsfr = w2_land_name_trnsfr_prcntge * w2_land_arr

    # other calucalted parameters
    w2_total_bop_cst = (w2_bop_trnky + w2_lnd_cst_budgted + w2_chnnl_prtnr) * w2_cap
    w2_total_pd_cst = w2_ttl_pd_expnses * w2_cap
    w2_total_approval_cst = w2_apprvls
    w2_total_land_cst = w2_lnd_cst * w2_cap
    w2_total_contngncy_cst = w2_contgncy * w2_cap
    w2_total_one_time_moblztn = w2_ot_mob_cst

    # SOLAR CAPEX
    s_phasing = pd.DataFrame()
    s_phasing["fnl_module_prce"] = fnl_module_prce * fnl_mod_price
    s_phasing["fnl_mdule_tstng_prce"] = fnl_mdule_tstng_prce * f_mod_test_price
    s_phasing["fnl_mdule_logistcs"] = fnl_mdule_logistcs * f_mod_logstcs
    s_phasing["fnl_lc_cst_mdule_pcrmnt"] = fnl_lc_cst_mdule_pcrmnt * f_lc_cst
    s_phasing["ttl_ehv_cst"] = ttl_ehv_cst * t_ehv_line_cst
    s_phasing["ttl_bos_cst"] = ttl_bos_cst * t_bos_cst
    s_phasing["contgncy_prcnt"] = contgncy_prcnt * contngncy_cst
    s_phasing["ttl_apprvl_prmits"] = ttl_apprvl_prmits * t_appr_permits
    s_phasing["ttl_thrd_party_esia"] = ttl_thrd_party_esia * t_thrd_prty_esia
    s_phasing["ttl_thrd_party_lf_stdy"] = ttl_thrd_party_lf_stdy * t_thrd_prty_load_flow
    s_phasing["lnd_delgnce_ttle_srch"] = lnd_delgnce_ttle_srch * land_dilgnce
    s_phasing["pd_expnses"] = pd_expnses * t_pd_exp
    s_phasing["crtcal_tools_phasing"] = crtcal_tools_phasing * crtcl_tools
    s_phasing["lnd_cst_one_tme_brkrge"] = lnd_cst_one_tme_brkrge * land_cst_one_tme_brkge
    s_phasing["lnd_cst_rnt"] = lnd_cst_rnt * land_cst_rent
    s_phasing["na_conv_state_guidlns_phasing"] = na_conv_state_guidlns_phasing * na_conversion

    s_phasing["s_capx"] = s_phasing.sum(axis=1)

    # WIND CAPEX
    w1_phasing = pd.DataFrame()
    w1_phasing["wtg_advance"] = wtg_adv * ntp_w1
    w1_phasing["wtg_blade_nacelle_supply"] = wtg_blade_supp * wtg_suply_w1
    w1_phasing["wth_commissioning"] = wtg_commsn * per_cod_w1
    w1_phasing["logistics_prior_to_dispatch"] = logstcs_dispatch * wtg_suply_w1
    w1_phasing["logistics_on_delivery"] = logstcs_delvry * wtg_suply_w1
    w1_phasing["civil_works_advance"] = cw_adv * ntp_w1
    w1_phasing["civil_works_foundation"] = cw_fondn * cvl_fndation_w1
    w1_phasing["ec_advance"] = ec_adv * ntp_w1
    w1_phasing["ec_mobilisation"] = ec_mob * wtg_suply_w1
    w1_phasing["ec_installation"] = ec_instll * instlation_wtg_w1
    w1_phasing["ec_performance_test"] = ec_perfmnce * per_cod_w1
    w1_phasing["electrical_work_advance"] = elect_adv * ntp_w1
    w1_phasing["electrical_receipt"] = elec_recipt * pr_33kv_line_w1
    w1_phasing["electrical_dp_yard"] = elec_dp_yard * pr_33kv_line_w1
    w1_phasing["land_arrangement_advance"] = land_adv * ntp_w1

    w1_phasing["land_arrangement_wtg_location"] = land_wtg_loc * lnd_aq_suzlon_w1
    w1_phasing["land_arrangement_name_transfer_sgil"] = land_name_trnsfr * per_cod_w1
    w1_phasing["total_bop_cost"] = total_bop_cst * bop_phasing_w1
    w1_phasing["total_pd_cost"] = total_pd_cst * pd_exp_phasing_w1
    w1_phasing["total_approval_cst"] = total_approval_cst * apprvls_phasing_w1
    w1_phasing["total_land_cst"] = total_land_cst * lnd_cst_phasing_w1
    w1_phasing["total_contingency_cst"] = total_contngncy_cst * contgncy_phasing_w1
    w1_phasing["total_one_time_mobilization"] = total_one_time_moblztn * ot_mob_cst_phasing_w1

    w1_phasing["w1_capx"] = w1_phasing.sum(axis=1)

    # WIND 2 CAPEX
    w2_phasing = pd.DataFrame()
    w2_phasing["wtg_advance"] = w2_wtg_adv * ntp_w2
    w2_phasing["wtg_blade_nacelle_supply"] = w2_wtg_blade_supp * wtg_suply_w2
    w2_phasing["wth_commissioning"] = w2_wtg_commsn * per_cod_w2
    w2_phasing["logistics_prior_to_dispatch"] = w2_logstcs_dispatch * wtg_suply_w2
    w2_phasing["logistics_on_delivery"] = w2_logstcs_delvry * wtg_suply_w2
    w2_phasing["civil_works_advance"] = w2_cw_adv * ntp_w2
    w2_phasing["civil_works_foundation"] = w2_cw_fondn * cvl_fndation_w2
    w2_phasing["ec_advance"] = w2_ec_adv * ntp_w2
    w2_phasing["ec_mobilisation"] = w2_ec_mob * wtg_suply_w2
    w2_phasing["ec_installation"] = w2_ec_instll * instlation_wtg_w2
    w2_phasing["ec_performance_test"] = w2_ec_perfmnce * per_cod_w2
    w2_phasing["electrical_work_advance"] = w2_elect_adv * ntp_w2
    w2_phasing["electrical_receipt"] = w2_elec_recipt * pr_33kv_line_w2
    w2_phasing["electrical_dp_yard"] = w2_elec_dp_yard * pr_33kv_line_w2
    w2_phasing["land_arrangement_advance"] = w2_land_adv * ntp_w2
    w2_phasing["land_arrangement_wtg_location"] = w2_land_wtg_loc * lnd_aq_suzlon_w2
    w2_phasing["land_arrangement_name_transfer_sgil"] = w2_land_name_trnsfr * per_cod_w2
    w2_phasing["total_bop_cost"] = w2_total_bop_cst * bop_phasing_w2
    w2_phasing["total_pd_cost"] = w2_total_pd_cst * pd_exp_phasing_w2
    w2_phasing["total_approval_cst"] = w2_total_approval_cst * apprvls_phasing_w2
    w2_phasing["total_land_cst"] = w2_total_land_cst * lnd_cst_phasing_w2
    w2_phasing["total_contingency_cst"] = w2_total_contngncy_cst * contgncy_phasing_w2
    w2_phasing["total_one_time_mobilization"] = w2_total_one_time_moblztn * ot_mob_cst_phasing_w2

    # calculaing wind 1 phasings
    w2_phasing["w2_capx"] = w2_phasing.sum(axis=1)

    comm_date = pd.to_datetime(cons_date) + pd.DateOffset(months=cons_dur)

    month_start = pd.date_range(cons_date, comm_date, freq='MS').to_pydatetime().tolist()
    month_end = pd.date_range(cons_date, comm_date + relativedelta(months=1), freq='M').to_pydatetime().tolist()

    s_capex = s_phasing["s_capx"]
    w1_capex = w1_phasing["w1_capx"]
    w2_capex = w2_phasing["w2_capx"]
    wind_capex = w1_capex + w2_capex
    # wind_capex.sum()

    # P4 Cost
    p4_cst = 115.6919200000  # p4 cost

    # cummulative function
    def cumm(lst):
        cnt = Counter(lst)
        cum_sum = [lst[0]]
        for i in range(1, len(lst)):
            cum_sum.append(cum_sum[i - 1] + lst[i])
        return cum_sum

    # calculating phasings
    phasing = pd.DataFrame()

    p1 = (((5000000 + 30000000 + (200000 * w1_cap)) * 0.01 * 2 * (1 + 0.18) / 1000000) + (
                (5000000 + 30000000 + (200000 * w2_cap)) * 0.01 * 2 * (1 + 0.18) / 1000000))
    p2 = (0.5 * 1.18) * 2
    p3 = (0.5 * 1.18) * 2
    p4 = 0.235 * w1_cap * 1.18 + 0.235 * w2_cap * 1.18

    pp1 = p1_phasing * p1
    pp2 = p2_phasing * p2
    pp3 = p3_phasing * p3
    pp4 = p4_phasing * p4

    phasing["pp4_phasing"] = pp1 + pp2 + pp3 + pp4  # updated formula(9-10-23)

    phasing["pp5_phasing"] = 0  # intially
    phasing["s_capx"] = s_phasing["s_capx"]
    phasing["w1_capx"] = w1_phasing["w1_capx"]
    phasing["w2_capx"] = w2_phasing["w2_capx"]
    phasing = phasing.fillna(0)

    batt_energy_rting = btry_cap * charg_dischrg_cycle

    usable_bat_engy = batt_energy_rting * (1 - batt_depth_dschrge) / (1 + batt_other_losses)

    batt_capex_cost = batt_capex_cost_ip * 1000 * ex_rate / 10 ** 6

    batt_capex = batt_capex_cost * batt_energy_rting

    batt_phasing = batt_capex_phasing * batt_capex

    batt_phasing = pd.to_numeric(batt_phasing, errors='coerce')
    zero_series = pd.Series([0])
    batt_phasing = pd.concat([batt_phasing, zero_series], ignore_index=True)
    btry_cpx = batt_phasing.tolist()

    phasing["btry_cpx"] = btry_cpx
    ttl_btry_capex = phasing["btry_cpx"].sum()

    electrolyzer = elz_capacity * input.electrolyzer_capex * 1000 * input.exchange_rate_usdinr / 10 ** 6
    BOP = (elz_capacity * input.bop_plant_incl_demineralized_water * 1000 * input.exchange_rate_usdinr) / 10 ** 6
    storage_h2_plant = GHS_capacity * input.storage_h2_plant
    one_time_land_development_cost = input.one_time_landdevelopment_cost
    port_infra_and_transport_related_capex = input.port_infra_transport_related_capex_h2
    land_purchase_cost = input.land_purchase_cost
    construction_cy_start_flag1 = pd.DataFrame(index=['construction_cy_start_flag1'],
                                               columns=list(range(1, input.total_construction_period + 1)))
    construction_cy_start_flag1[:] = 0
    construction_cy_start_flag1.iloc[:, np.arange(0, construction_cy_start_flag1.shape[1], 12)] = 1
    flag1_calender_years_post_construction_start = flag1['Calender Years Post Construction Start'].iloc[
                                                   :input.total_construction_period].T
    flag1_calender_years_post_construction_start.index += 1
    land_lease_cost = input.land_required_electrolyzer * input.annual_rent_land_required_electrolyzer * construction_cy_start_flag1 * (
                1 + input.annual_land_lease_escalation_land_required_electrolyzer) ** (
                                  flag1_calender_years_post_construction_start - 1) * input.gh2_switch
    land_lease_cost = land_lease_cost.rename(index={'construction_cy_start_flag1': 'land_lease_cost'})
    gh2_phasings = main_sheet_gh2.iloc[12:18, 1:]
    gh2_phasings.drop(columns=gh2_phasings.columns[1],
                      inplace=True)  # .set_index(gh2_phasings.columns[0], inplace =True)
    gh2_phasings.set_index(gh2_phasings.columns[0], inplace=True)
    gh2_phasings.columns = range(1, int(gh2_phasings.shape[1] + 1))
    calculated_variables_gh2 = [electrolyzer, BOP, storage_h2_plant, one_time_land_development_cost,
                                port_infra_and_transport_related_capex]
    gh2_phasings.iloc[:(gh2_phasings.shape[0] - 1)] = gh2_phasings.iloc[:(gh2_phasings.shape[0] - 1)].multiply(
        calculated_variables_gh2, axis=0)
    gh2_phasings = gh2_phasings.fillna(0)
    gh2_phasings = gh2_phasings.T
    gh2_phasings['land_lease_cost'] = land_lease_cost.T
    gh2_phasings = gh2_phasings.T
    capex_nh3 = input.nh3_capex * input.exchange_rate_usdinr
    capex_n2 = input.capex_n2
    initial_h2_stock_expenses = (
                                            input.initial_h2_stock_cost * input.initial_h2_stock * input.exchange_rate_usdinr) * 1000 / pow(
        10, 6)  #### Multiplied by 1000as missing in formulae,it should be 1000/10^6
    port_infra_and_transport_related_capex_nh3 = input.port_infra_transport_related_capex_nh3
    nh3_phasings = main_sheet_nh3.iloc[8:13, 1:]
    nh3_phasings.drop(columns=nh3_phasings.columns[1],
                      inplace=True)  # .set_index(nh3_phasings.columns[0], inplace =True)
    nh3_phasings.set_index(nh3_phasings.columns[0], inplace=True)
    nh3_phasings.columns = range(1, int(nh3_phasings.shape[1] + 1))
    contingency_nh3 = 0
    calculated_variables_nh3 = [capex_nh3, capex_n2, initial_h2_stock_expenses,
                                port_infra_and_transport_related_capex_nh3, contingency_nh3]
    nh3_phasings = nh3_phasings.fillna(0)
    nh3_phasings.iloc[:nh3_phasings.shape[0]] = nh3_phasings.iloc[:nh3_phasings.shape[0]].multiply(
        calculated_variables_nh3, axis=0)

    #  GH2 - contingency
    gh2_cost = gh2_phasings.T[['Electrolyzer CapEx Phasing',
                               'BOP Plant incl. demineralized water Phasing', 'Storage of H2 at Plant Phasing',
                               'Port Infra & Transport related Capex']].sum().sum()
    contingency_gh2 = input.contingencynh3 * gh2_cost
    total_hard_cst_gh2 = gh2_cost + gh2_phasings.T[
        ['One Time Land Development Cost', 'land_lease_cost']].sum().sum() + contingency_gh2  # H2 CAPEX

    #  nh3 - contingency
    nh3_cost = nh3_phasings.T[['Capex NH3', 'Capex N2', 'Initial H2 Stock Expenses',
                               'Port Infra & Transport related Capex']].sum().sum()
    contingency_nh3 = input.contingencynh3 * nh3_cost
    total_hard_cst_nh3 = nh3_cost + contingency_nh3  # NH3 CAPEX

    # overall contingency
    cntgncy = input.contingencynh3 * (gh2_cost + nh3_cost)  # single value
    contingency = gh2_phasings.loc['Contingency-GH2'] * cntgncy
    nh3_phasings = nh3_phasings.T
    nh3_phasings["contingency"] = contingency
    nh3_phasings = nh3_phasings.T
    # total gh2 nh3 capex
    gh2_nh3_capex = pd.concat([gh2_phasings, nh3_phasings])
    gh2_nh3_capex.drop(["Contingency-GH2", "Contingency-NH3"], inplace=True)
    gh2_nh3_capex = gh2_nh3_capex.T
    gh2_nh3_capex["total_gh2_nh3_capex"] = gh2_nh3_capex.sum(axis=1)

    # adidng it into phasing
    # phasing = phasing[:-1] # dropping last row
    g_n_capx = gh2_nh3_capex["total_gh2_nh3_capex"].tolist() + [0]
    phasing["gh2_nh3_capex"] = g_n_capx
    phasing["mnthly_cpx"] = phasing["s_capx"] + phasing["w1_capx"] + phasing["w2_capx"] + phasing["pp4_phasing"] + \
                            phasing["pp5_phasing"].replace(np.nan, 0) + batt_phasing
    mnthly_cpx = phasing["mnthly_cpx"].values.tolist()

    capex = phasing["mnthly_cpx"].sum()

    total_gh2_capex = 29831.8

    hrs_of_dy = 24
    el_cpx = sum(gh2_phasings.T['Electrolyzer CapEx Phasing'].fillna(0).tolist())
    cpx_nh3 = sum(nh3_phasings.T['Capex NH3'].fillna(0).tolist())

    # el = electrolyzer
    # repl = replacement
    rplcmnt_cpx_gh2 = pd.DataFrame()
    rplcmnt_cpx_gh2['month_start'] = global_df['month_start']
    rplcmnt_cpx_gh2['month_end'] = global_df['month_start'].apply(month_end_dt)
    rplcmnt_cpx_gh2['dys_in_mnth'] = rplcmnt_cpx_gh2['month_start'].apply(no_of_dys)
    rplcmnt_cpx_gh2['flag'] = global_df['op_flag']
    rplcmnt_cpx_gh2['hr_avail'] = hrs_of_dy * rplcmnt_cpx_gh2['dys_in_mnth'] * rplcmnt_cpx_gh2['flag']
    rplcmnt_cpx_gh2['el_avail'] = rplcmnt_cpx_gh2['hr_avail'] * el_avail
    rplcmnt_cpx_gh2['cumm_usge_el'] = rplcmnt_cpx_gh2['el_avail'].cumsum()
    rplcmnt_cpx_gh2['repl_count'] = rplcmnt_cpx_gh2['cumm_usge_el'] / el_stk_lf
    rplcmnt_cpx_gh2['repl_count'] = rplcmnt_cpx_gh2['repl_count'].astype(int)
    rplcmnt_cpx_gh2['no_of_yr_pst_cod'] = rplcmnt_cpx_gh2['month_start'].apply(no_of_yr_pst_cod)
    x = rplcmnt_cpx_gh2[rplcmnt_cpx_gh2['cumm_usge_el'] >= el_stk_lf].index[0]
    y = rplcmnt_cpx_gh2[rplcmnt_cpx_gh2['cumm_usge_el'] >= el_stk_lf * 2].index[0]
    rplcmnt_cpx_gh2['repl_cpx_1'] = 0
    rplcmnt_cpx_gh2.loc[x, 'repl_cpx_1'] = el_repl_cpx_1 * el_cpx * (1 + gh2_inflsn) ** (
                rplcmnt_cpx_gh2.loc[x, 'no_of_yr_pst_cod'] - 1)
    rplcmnt_cpx_gh2['repl_cpx_2'] = 0
    rplcmnt_cpx_gh2.loc[y, 'repl_cpx_2'] = el_repl_cpx_2 * el_cpx * (1 + gh2_inflsn) ** (
                rplcmnt_cpx_gh2.loc[y, 'no_of_yr_pst_cod'] - 1)
    z = rplcmnt_cpx_gh2[rplcmnt_cpx_gh2['month_start'] == oper_start_date + pd.DateOffset(years=gh2_plnt_lf)].index[0]
    print(z)
    rplcmnt_cpx_gh2['repl_plnt_cpx'] = 0
    rplcmnt_cpx_gh2.loc[z, 'repl_plnt_cpx'] = BOP * (1 + gh2_inflsn) ** (rplcmnt_cpx_gh2.loc[z, 'no_of_yr_pst_cod'] - 1)
    rplcmnt_cpx_gh2['repl_cpx_btry'] = bat_enrg_rtng * ((bat_repl_chrgs * 1000 * ex_rate) / 10 ** 6) * rplcmnt_cpx_gh2[
        'flag'] * ((1 + bat_inflation_perc) ** (rplcmnt_cpx_gh2['no_of_yr_pst_cod'] - 1))
    rplcmnt_cpx_gh2.drop(['flag', 'no_of_yr_pst_cod'], axis=1, inplace=True)  #### change 1

    ### Replacement Capex Of NH3 (Monthly)
    rplcmnt_cpx_nh3 = rplcmnt_cpx_gh2[['month_start', 'month_end']]
    rplcmnt_cpx_nh3['no_of_yr_pst_cod'] = rplcmnt_cpx_nh3['month_start'].apply(no_of_yr_pst_cod)
    # rplcmnt_cpx_nh3['cpx_nh3'] = cpx_nh3 + [0]*(len(rplcmnt_cpx_nh3)-len(cpx_nh3))
    rplcmnt_cpx_nh3['repl_nh3_cpx'] = 0
    w = rplcmnt_cpx_nh3[rplcmnt_cpx_nh3['month_start'] == oper_start_date + pd.DateOffset(years=nh3_plnt_lf)].index[0]
    rplcmnt_cpx_nh3.loc[w, 'repl_nh3_cpx'] = cpx_nh3 * (1 + nh3_inflsn) ** (
                rplcmnt_cpx_nh3.loc[w, 'no_of_yr_pst_cod'] - 1)
    rplcmnt_cpx_nh3.drop(['no_of_yr_pst_cod'], axis=1, inplace=True)

    ### Replacement Capex Of GH2 (Quarterly)
    quat_repl_cpx_gh2 = rplcmnt_cpx_gh2[
        ['month_start', 'el_avail', 'repl_cpx_1', 'repl_cpx_2', 'repl_plnt_cpx', 'repl_cpx_btry']]
    quat_repl_cpx_gh2.set_index('month_start', inplace=True)
    quat_repl_cpx_gh2 = quat_repl_cpx_gh2.resample('QS').sum(numeric_only=True)
    quat_repl_cpx_gh2.reset_index(inplace=True)
    quat_repl_cpx_gh2.rename(columns={'month_start': 'quat_start'}, inplace=True)
    quat_repl_cpx_gh2.insert(1, 'quat_end', quat_repl_cpx_gh2['quat_start'].apply(quat_end))
    quat_repl_cpx_gh2['cumm_usge_el'] = quat_repl_cpx_gh2['el_avail'].cumsum()
    quat_repl_cpx_gh2.insert(2, 'quat_flag', global_quat_df['op_flag'])

    ### Replacement Capex Of NH3 (Quarterly)
    quat_repl_cpx_nh3 = rplcmnt_cpx_nh3
    quat_repl_cpx_nh3.set_index('month_start', inplace=True)
    quat_repl_cpx_nh3 = quat_repl_cpx_nh3.resample('QS').sum(numeric_only=True)
    quat_repl_cpx_nh3.reset_index(inplace=True)
    quat_repl_cpx_nh3.rename(columns={'month_start': 'quat_start'}, inplace=True)
    quat_repl_cpx_nh3.insert(1, 'quat_end', quat_repl_cpx_nh3['quat_start'].apply(quat_end))
    quat_repl_cpx_nh3.insert(2, 'quat_flag', global_quat_df['op_flag'])

    ### Replacement Capex Of GH2 (Yearly)
    fy_repl_cpx_gh2 = pd.DataFrame()
    fy_repl_cpx_gh2 = quat_repl_cpx_gh2[['cumm_usge_el', 'repl_cpx_1', 'repl_cpx_2', 'repl_plnt_cpx', 'repl_cpx_btry']]
    fy_repl_cpx_gh2.insert(0, 'fy_start', quat_repl_cpx_gh2['quat_start'].apply(lambda x: financial_year_dates(x)[0]))
    fy_repl_cpx_gh2.insert(1, 'fy_end', quat_repl_cpx_gh2['quat_start'].apply(lambda x: financial_year_dates(x)[1]))
    fy_repl_cpx_gh2 = fy_repl_cpx_gh2.groupby(['fy_start', 'fy_end']).sum().reset_index()

    ### Replacement Capex Of NH3 (Yearly)
    fy_repl_cpx_nh3 = pd.DataFrame()
    fy_repl_cpx_nh3 = quat_repl_cpx_nh3[['repl_nh3_cpx']]
    fy_repl_cpx_nh3.insert(0, 'fy_start', quat_repl_cpx_nh3['quat_start'].apply(lambda x: financial_year_dates(x)[0]))
    fy_repl_cpx_nh3.insert(1, 'fy_end', quat_repl_cpx_nh3['quat_start'].apply(lambda x: financial_year_dates(x)[1]))
    fy_repl_cpx_nh3 = fy_repl_cpx_nh3.groupby(['fy_start', 'fy_end']).sum().reset_index()

    idc_l = [0] * constr_dur + [0]  ##### make this dynamic as per cons duration
    while True:
        cumm_capx = cumm(mnthly_cpx)  # calling cumm fucntion

        # 30% of cumm capex
        cumm_capx_30_per = []
        for i in cumm_capx:
            l2 = equ_per * i  ######### its not 30 % of cumm capex, rather its
            cumm_capx_30_per.append(l2)

        equity = equ_per * capex  # (30% of capex including pp)
        up_equity = up_equ_per * equity  # 50 % of equity
        lft_equity = up_equ_per * equity
        debt = debt_per * capex  # 70% of capex including pp

        u_e = []
        l_e = []
        for (mnth_dmd, cumm_capx_30) in zip(mnthly_cpx, cumm_capx_30_per):
            up_equ = min(mnth_dmd, (up_equity - sum(u_e))) if sum(
                u_e) < up_equity else 0  # Min(mnth_dmd, up_equity - sum(u_e)) else 0
            lft_equ = cumm_capx_30 - (up_equity + sum(l_e)) if cumm_capx_30 > (up_equity + sum(l_e)) else 0
            u_e.append(up_equ)
            l_e.append(lft_equ)

        # making dataframe for the same
        df = pd.DataFrame()
        pd.set_option('display.max_columns', None)
        df["month_start"] = month_start
        df["month_end"] = month_end
        df["mntly_cpx"] = mnthly_cpx
        df["cum_cpx"] = np.round(cumm_capx, 2)
        df["30_cum cpx"] = np.round(cumm_capx_30_per, 2)
        df["up_equ_dis"] = u_e
        df["lft_equ_dis"] = l_e
        df["idc"] = idc_l  # setting idc to 0 initially
        df["equ_infused"] = df["up_equ_dis"] + df["lft_equ_dis"]
        df["debt"] = df["mntly_cpx"] + df["idc"] - df["equ_infused"]  # adding idc into debt
        df = df.replace(np.nan, 0)
        df.T

        cumm_debt = cumm(df["debt"])
        df["cumm_debt"] = cumm_debt

        # mov _avg
        df["mov_avg"] = df['cumm_debt'].rolling(2).mean()

        df["days_in_mnth"] = df["month_start"].apply(dys_in_mnth)

        condition = df["month_end"] < comm_date

        df["idc"] = 0  # Setting idc to 0 initially
        # #### make 365 dynamic
        dys_in_yr = 365
        df.loc[condition, "idc"] = df["mov_avg"] * (roi / dys_in_yr) * df["days_in_mnth"]

        res = pd.concat([phasing.T, df.T], axis=0)
        res
        # calculating phasing 5th component
        phasing["pp5_phasing"] = p5_phasing * 0.0085 * equity
        phasing["mnthly_cpx"] = phasing["s_capx"] + phasing["w1_capx"] + phasing["w2_capx"] + phasing["pp4_phasing"] + \
                                phasing["pp5_phasing"].replace(np.nan, 0) + batt_phasing
        mnthly_cpx = phasing["mnthly_cpx"].values.tolist()
        phasing.T

        # capex = sum of monthly capex
        upd_capex = phasing["mnthly_cpx"].sum() + df["idc"].sum()

        if abs(upd_capex - capex) == 0:
            break
        capex = upd_capex
        idc_l = df["idc"].values.tolist()

    new_idc_l = df["idc"].fillna(0).to_list()
    #### 1st FINAL DISTRIBUTION CODE
    a = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).tolist()
    cumm_capx = cumm(a)
    capex = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).sum()
    # print("capex", capex)
    equity = capex * equ_per
    # print("equity", equity)

    # 30% of cumm capex
    cumm_capx_30_per = []
    for i in cumm_capx:
        l2 = equ_per * i
        cumm_capx_30_per.append(l2)
    # equity debt (70, 30 distribution)
    equity = equ_per * capex  # (30% of capex including pp)
    up_equity = up_equ_per * equity  # 50 % of equity
    lft_equity = up_equ_per * equity
    debt = debt_per * capex  # 70% of capex including pp
    u_e = []
    l_e = []
    for (mnth_dmd, cumm_capx_30) in zip(mnthly_cpx, cumm_capx_30_per):
        up_equ = min(mnth_dmd, (up_equity - sum(u_e))) if sum(
            u_e) < up_equity else 0  # Min(mnth_dmd, up_equity - sum(u_e)) else 0
        lft_equ = cumm_capx_30 - (up_equity + sum(l_e)) if cumm_capx_30 > (up_equity + sum(l_e)) else 0
        u_e.append(up_equ)
        l_e.append(lft_equ)
    # making dataframe for the same
    df = pd.DataFrame()
    pd.set_option('display.max_columns', None)
    df["mntly_cpx"] = mnthly_cpx
    df["cum_cpx"] = np.round(cumm_capx, 2)
    df["30_cum cpx"] = np.round(cumm_capx_30_per, 2)
    df["month_start"] = month_start
    df["month_end"] = month_end
    df["up_equ_dis"] = u_e
    df["lft_equ_dis"] = l_e
    df["equ_infused"] = df["up_equ_dis"] + df["lft_equ_dis"]
    df["s_idc"] = new_idc_l
    df["debt"] = df["mntly_cpx"] + df["s_idc"] - df["equ_infused"]
    df.T

    cumm_debt = cumm(df["debt"])
    df["cumm_debt"] = cumm_debt
    df["mov_avg"] = df['cumm_debt'].rolling(2).mean()

    df["days_in_mnth"] = df["month_start"].apply(dys_in_mnth)
    df["idc"] = 0  # Setting idc to 0 initially
    df.loc[condition, "idc"] = df["mov_avg"] * (roi / dys_in_yr) * df["days_in_mnth"]
    # combining phasings and distributions, idc
    res = pd.concat([phasing.T, df.T], axis=0)
    res.fillna(0, inplace=True)
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()
    # print("final capex including idc ",final_capex)
    res.T["idc"].fillna(0).sum()
    res.T["mntly_cpx"].fillna(0).sum()
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()
    final_capex

    new_idc_l = df["idc"].fillna(0).to_list()
    a = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).tolist()
    cumm_capx = cumm(a)
    capex = (res.T["mntly_cpx"] + res.T["idc"].fillna(0)).sum()
    equity = capex * equ_per

    # 30% of cumm capex
    cumm_capx_30_per = []
    for i in cumm_capx:
        l2 = equ_per * i
        cumm_capx_30_per.append(l2)

    # equity debt (70, 30 distribution)
    equity = equ_per * capex  # (30% of capex including pp)
    up_equity = up_equ_per * equity  # 50 % of equity
    lft_equity = up_equ_per * equity
    debt = debt_per * capex  # 70% of capex including pp

    u_e = []
    l_e = []
    for (mnth_dmd, cumm_capx_30) in zip(mnthly_cpx, cumm_capx_30_per):
        up_equ = min(mnth_dmd, (up_equity - sum(u_e))) if sum(
            u_e) < up_equity else 0  # Min(mnth_dmd, up_equity - sum(u_e)) else 0
        lft_equ = cumm_capx_30 - (up_equity + sum(l_e)) if cumm_capx_30 > (up_equity + sum(l_e)) else 0
        u_e.append(up_equ)
        l_e.append(lft_equ)

    # making dataframe for the same
    df = pd.DataFrame()
    pd.set_option('display.max_columns', None)
    df["mntly_cpx"] = mnthly_cpx
    df["cum_cpx"] = np.round(cumm_capx, 2)
    df["30_cum cpx"] = np.round(cumm_capx_30_per, 2)
    df["month_start"] = month_start
    df["month_end"] = month_end
    df["up_equ_dis"] = u_e
    df["lft_equ_dis"] = l_e
    df["equ_infused"] = df["up_equ_dis"] + df["lft_equ_dis"]
    df["s_idc"] = new_idc_l
    df["debt"] = df["mntly_cpx"] + df["s_idc"] - df["equ_infused"]
    df.T

    cumm_debt = cumm(df["debt"])
    df["cumm_debt"] = cumm_debt

    df["mov_avg"] = df['cumm_debt'].rolling(2).mean()

    df["days_in_mnth"] = df["month_start"].apply(dys_in_mnth)

    # Using the boolean mask to update the "idc" column
    df["idc"] = 0  # Setting idc to 0 initially
    df.loc[condition, "idc"] = df["mov_avg"] * (roi / 365) * df["days_in_mnth"]

    # combining phasings and distributions, idc
    res = pd.concat([phasing.T, df.T], axis=0)
    res.fillna(0, inplace=True)
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()
    print("final capex including idc ", final_capex)

    res.T["idc"].fillna(0).sum()
    res.T["mntly_cpx"].fillna(0).sum()
    final_capex = res.T["mntly_cpx"].fillna(0).sum() + res.T["idc"].fillna(0).sum()

    capex_monthly = pd.DataFrame()
    capex_monthly['Month Start Date flag'] = global_df['month_start']
    capex_monthly['capex_month'] = res.T['mntly_cpx'] + res.T['idc'].fillna(0)
    capex_monthly['equity_draw'] = res.T['equ_infused']
    capex_monthly['debt_draw'] = res.T['debt']
    capex_monthly['idc_quat'] = res.T['idc'].fillna(0)
    capex_monthly.fillna(0, inplace=True)
    # capex_monthly
    capex_quat = capex_monthly
    capex_quat.set_index('Month Start Date flag', inplace=True)
    capex_quat = capex_monthly.resample('Q').sum()
    capex_quat = capex_quat.reset_index(drop=True)
    # capex_quat

    target_irr = 12  # Target IRR value

    macro_cal['h2_generated_tons'] = 0
    macro_cal.loc[0, 'h2_generated_tons'] = daily_gen['H2_generation_TPH'].sum()
    for i, row in macro_cal.iloc[1:].iterrows():
        if (row['year'] - 1) % (
        round(el_stk_lf / 8760)) == 0:  ########## round taken self,as without it ((input.electrolyzer_stack_life/8760 will never be zero---- 80000/8760)
            macro_cal.at[i, 'h2_generated_tons'] = daily_gen['H2_generation_TPH'].sum()
        else:
            macro_cal.at[i, 'h2_generated_tons'] = macro_cal.at[i - 1, 'h2_generated_tons'] * (
                        1 - elz_annual_degradation)

    macro_cal['nh3_generated_tons'] = macro_cal['h2_generated_tons'] * 5.6238

    sum_h2_nh3_generation_tph = pd.DataFrame()
    sum_h2_nh3_generation_tph['H2_generation_TPH'] = cap_supply.groupby('month')[
        ['H2_generation_TPH']].sum().reset_index().drop(columns='month')
    sum_h2_nh3_generation_tph['NH3_prod_TPH'] = cap_supply.groupby('month')[['NH3_prod_TPH']].sum().reset_index().drop(
        columns='month')

    monthly_cal['h2'] = 0
    monthly_cal['h2'] = sum_h2_nh3_generation_tph['H2_generation_TPH'] / 1000
    monthly_cal['nh3'] = sum_h2_nh3_generation_tph['NH3_prod_TPH'] / 1000

    monthly_cal['h2%'] = (monthly_cal['h2'] * 100) / monthly_cal['h2'].sum()
    monthly_cal['nh3%'] = (monthly_cal['nh3'] * 100) / monthly_cal['nh3'].sum()

    def fm(lcoe):
        lcoe = np.round(lcoe, 2)
        tariff_lockin = lcoe
        dsm_penalties = pd.DataFrame()
        repeated_DSM_penalties_wind = DSM_penalties_wind + [DSM_penalties_wind[-1]] * 20
        repeated_DSM_penalties_solar = DSM_penalties_solar + [DSM_penalties_solar[-1]] * 20
        dsm_penalties['Month Start'] = global_df['month_start']
        req_condition = (constr_end_date < dsm_penalties['Month Start']) & (
                    dsm_penalties['Month Start'] <= operation_end_date)
        cost_supp_supply = (np.tile(macro_cal['supplement_supply'], 12)) * (
            np.tile(monthly_cal["re_power_pr"], 25)) * iex_pur_price
        solar_dsm_penalities = (np.tile(repeated_DSM_penalties_solar, 12)) * (
            np.tile(macro_cal['solar_gen_mus'], 12)) * (np.tile(monthly_cal['solar_month_ratio'], 25)) * lcoe
        wind_dsm_penalities = (np.tile(repeated_DSM_penalties_wind, 12)) * (np.tile(macro_cal['wind_gen_mus'], 12)) * (
            np.tile(monthly_cal['wind_month_ratio'], 25)) * lcoe
        dsm_penalties['cost_supp_supply'] = np.where(req_condition, np.tile(cost_supp_supply, len(dsm_penalties) // len(
            cost_supp_supply) + 1)[:len(dsm_penalties)], 0)
        dsm_penalties["solar_dsm_penalities"] = np.where(req_condition, np.tile(solar_dsm_penalities,
                                                                                len(dsm_penalties) // len(
                                                                                    solar_dsm_penalities) + 1)[
                                                                        :len(dsm_penalties)], 0)
        dsm_penalties["wind_dsm_penalities"] = np.where(req_condition, np.tile(wind_dsm_penalities,
                                                                               len(dsm_penalties) // len(
                                                                                   wind_dsm_penalities) + 1)[
                                                                       :len(dsm_penalties)], 0)
        dsm_penalties['wind_dsm_penalities'].sum()

        #### quarter dsm

        dsm_penalties_quat = dsm_penalties[['cost_supp_supply', 'Month Start']]
        dsm_penalties_quat['cost_supp_supply'] = pd.to_numeric(dsm_penalties_quat['cost_supp_supply'], errors='coerce')
        dsm_penalties_quat.set_index('Month Start', inplace=True)
        dsm_penalties_quat = dsm_penalties_quat.resample('QS').sum(numeric_only=True)
        dsm_penalties_quat.reset_index(inplace=True)
        dsm_penalties_quat.rename(columns={'Month Start': 'Quarter Start'}, inplace=True)
        dsm_penalties_quat['Quarter End'] = dsm_penalties_quat['Quarter Start'].apply(qaurter_end_date)
        dsm_penalties_quat = dsm_penalties_quat[['Quarter Start', 'Quarter End', 'cost_supp_supply']]

        #### wind onm

        wind_site = {'wind_1_site_loctaion':
                         {1: 'Hanamsagar Envision',
                          2: 'Hanamsagar Sany',
                          3: 'Krishnapur Envision',
                          4: 'Krishnapur Sany'},
                     'wind_2_site_location':
                         {1: 'Hanamsagar Envision',
                          2: 'Hanamsagar Sany',
                          3: 'Krishnapur Envision',
                          4: 'Krishnapur Sany'},
                     'Envision':
                         {'turbine_capcity': 3.3,
                          'land_req': envi_land_req,
                          'land_lease_values': {
                              'fst_instlment': envi_fst_instlment,
                              'scnd_instlment': envi_scnd_instlment
                          }},
                     'Sany':
                         {'turbine_capcity': 4,
                          'land_req': sany_land_req,
                          'land_lease_values': {
                              'fst_instlment': sany_fst_instlment,
                              'scnd_instlment': sany_scnd_instlment
                          }},
                     'land_lease_year':
                         {'first_instlmnt_yr': first_instlmnt_yr,
                          'scnd_instlmnt_yr': scnd_instlmnt_yr
                          }}

        wind_capacity = w1_cap + w2_cap
        wind_onm = pd.DataFrame()
        wind_onm['month_start'] = global_df['month_start']
        wind_onm['year_wind'] = global_df.apply(
            lambda row: 0 if row['no_of_yr_pst_cod'] < 2 else row['no_of_yr_pst_cod'] - 2, axis=1)
        wind_onm['wind_op_flag_day'] = wind_onm['month_start'].apply(dys_in_mnth)
        wind_onm['wind_op_flag_year'] = wind_onm['month_start'].apply(days_in_financial_year)
        wind_onm['operations_op_flag'] = global_df['op_flag']
        wind_onm['self_op_flag'] = np.where(
            ((wind_onm['month_start'] > free_onm_prd) & (wind_onm['month_start'] <= operation_end_date)), 1, 0)
        wind_onm['self_year'] = wind_onm['year_wind']
        wind_onm['days/year'] = (wind_onm['wind_op_flag_day'] / wind_onm['wind_op_flag_year']) * wind_onm[
            'self_op_flag']
        wind_onm['days/year_ratio'] = (wind_onm['wind_op_flag_day'] / wind_onm['wind_op_flag_year'])
        wind_onm['escalation'] = ((1 + escalation_self) ** (wind_onm['self_year'] - 1)) * wind_onm['self_op_flag']
        wind_onm['wind_self'] = onm_cost_self * wind_capacity * wind_switch * wind_onm['days/year'] * (
        wind_onm['escalation'])
        wind_onm['wind_free'] = wind_onm['operations_op_flag'] * 0
        wind_onm['wind_lockin'] = wind_onm['operations_op_flag'] * 0
        wind_onm["escalation_hanamsagar"] = np.where(global_df['no_of_yr_pst_cod'] >= 1,
                                                     (global_df['no_of_yr_pst_cod'] - 1) // 3, 0)
        wind_onm['year_count'] = global_df['no_of_yr_pst_cod']
        wind_onm['Hanamsagar Envision'] = 0
        wind_onm['Hanamsagar Sany'] = 0
        wind_onm['Krishnapur Envision'] = 0
        wind_onm['Krishnapur Sany'] = 0
        location = wind_site['wind_1_site_loctaion'][main_sheet.iloc[5, 3]].split()[0]  ## 'Krishnapur' 0r Hanamsagar
        turbine = wind_site['wind_1_site_loctaion'][main_sheet.iloc[5, 3]].split()[-1]
        first_instlmnt_dt = oper_start_date + pd.DateOffset(years=wind_site['land_lease_year']['first_instlmnt_yr'])
        scnd_instlmnt_dt = oper_start_date + pd.DateOffset(years=wind_site['land_lease_year']['scnd_instlmnt_yr'])
        if location == "Hanamsagar":
            wind_onm[wind_site['wind_1_site_loctaion'][main_sheet.iloc[5, 3]]] = pd.to_numeric(
                np.where(wind_onm['year_count'] > upfront_duration, ((land_lease_charges *
                                                                      wind_site[turbine]['land_req']) /
                                                                     wind_site[turbine]['turbine_capcity']) *
                         wind_capacity * ((1 + hanam_escalation) ** wind_onm["escalation_hanamsagar"]) *
                         wind_onm['days/year_ratio'] * global_df['op_flag'], 0))
        elif location == "Krishnapur":
            wind_onm.loc[wind_onm['month_start'] == first_instlmnt_dt, wind_site['wind_1_site_loctaion'][
                main_sheet.iloc[5, 3]]] = (wind_capacity / wind_site[turbine]['turbine_capcity']) * \
                                          wind_site[turbine]['land_lease_values']['fst_instlment']
            wind_onm.loc[wind_onm['month_start'] == scnd_instlmnt_dt, wind_site['wind_1_site_loctaion'][
                main_sheet.iloc[5, 3]]] = (wind_capacity / wind_site[turbine]['turbine_capcity']) * \
                                          wind_site[turbine]['land_lease_values']['scnd_instlment']
        wind_onm['total_hanam_krish'] = wind_onm['Hanamsagar Envision'] + wind_onm['Hanamsagar Sany'] + wind_onm[
            'Krishnapur Envision'] + wind_onm['Krishnapur Sany']

        wind_onm["wind_bop_cost"] = bop_cost * wind_capacity * wind_switch * wind_onm['days/year_ratio'] * (
                    (1 + bop_escalation) ** (
                np.where(global_df['no_of_yr_pst_cod'] > 0, global_df['no_of_yr_pst_cod'] - 1, 0))) * global_df[
                                        'op_flag']
        wind_onm["wind_ctu_onm"] = ctu_cost * wind_capacity * wind_switch * wind_onm['days/year_ratio'] * (
                    (1 + ctu_escalation) ** (
                np.where(global_df['no_of_yr_pst_cod'] > 0, global_df['no_of_yr_pst_cod'] - 1, 0))) * global_df[
                                       'op_flag']
        free_p = pd.to_numeric(np.where(wind_onm['month_start'] > free_onm_prd, 0, global_df['op_flag']),
                               errors='coerce')
        wind_onm['sgil_exp'] = (((emp_salary_wind / 12) * wind_switch * ((1 + sgil_escalation) ** (
            np.where(global_df['no_of_yr_pst_cod'] > 0, global_df['no_of_yr_pst_cod'] - 1, 0)))) * free_p) + (((
                                                                                                                           emp_salary_wind / 12) * wind_switch * (
                                                                                                                           (
                                                                                                                                       1 + sgil_escalation) ** (
                                                                                                                               np.where(
                                                                                                                                   global_df[
                                                                                                                                       'no_of_yr_pst_cod'] > 0,
                                                                                                                                   global_df[
                                                                                                                                       'no_of_yr_pst_cod'] - 1,
                                                                                                                                   0)))) * free_p)
        wind_onm["GP_taxes"] = GP_taxes_wind * wind_capacity * wind_switch * wind_onm['days/year_ratio'] * global_df[
            'op_flag']
        wind_onm["wind_insu_cost"] = wind_insurance * wind_capacity * wind_switch * wind_onm['days/year_ratio'] * (
                    (1 + escalation_insu) ** (
                np.where(global_df['no_of_yr_pst_cod'] > 0, global_df['no_of_yr_pst_cod'] - 1, 0))) * global_df[
                                         'op_flag']
        wind_onm['wind_onm_cost_total'] = wind_onm['wind_free'] + wind_onm['wind_lockin'] + wind_onm['wind_self'] + \
                                          wind_onm['wind_bop_cost'] + wind_onm['wind_ctu_onm'] + wind_onm['sgil_exp'] + \
                                          wind_onm['GP_taxes']
        wind_onm['wind_dsm_penalities'] = dsm_penalties['wind_dsm_penalities']
        columns_to_convert = ['wind_self', 'wind_free', 'wind_lockin', 'Krishnapur Envision', 'Krishnapur Sany',
                              'Hanamsagar Envision', 'Hanamsagar Sany', 'wind_dsm_penalities', 'wind_bop_cost',
                              'wind_ctu_onm', 'sgil_exp', 'GP_taxes', 'wind_insu_cost']
        wind_onm[columns_to_convert] = wind_onm[columns_to_convert].apply(pd.to_numeric, errors='coerce')

        #### quarter wind onm

        wind_onm_quat = wind_onm_quat = wind_onm[
            ['month_start', 'wind_self', 'wind_free', 'wind_lockin', 'Krishnapur Envision',
             'Krishnapur Sany', 'Hanamsagar Envision', 'Hanamsagar Sany', 'wind_bop_cost',
             'wind_ctu_onm', 'sgil_exp', 'GP_taxes', 'wind_insu_cost', 'total_hanam_krish',
             'wind_dsm_penalities']]
        wind_onm_quat.set_index('month_start', inplace=True)
        wind_onm_quat = wind_onm_quat.resample('QS').sum(numeric_only=True)
        wind_onm_quat.reset_index(inplace=True)
        total_windonm_col = ['wind_self', 'wind_free', 'wind_lockin', 'Krishnapur Envision', 'Krishnapur Sany',
                             'Hanamsagar Envision', 'Hanamsagar Sany', 'wind_bop_cost', 'wind_ctu_onm', 'sgil_exp',
                             'GP_taxes', 'wind_insu_cost',
                             'wind_dsm_penalities']
        wind_onm_quat['total_wind_onm'] = wind_onm_quat[total_windonm_col].sum(axis=1)
        # wind_onm_quat

        #### Solar onm

        solar_onm = wind_onm[['month_start', 'days/year_ratio']]
        solar_onm["solar_onm_cost"] = s_cap * onm_cost * (
                (1 + annual_escalation) ** (global_df['no_of_yr_pst_cod'] - 1)) * \
                                      solar_onm['days/year_ratio'] * global_df['op_flag'] * solar_switch
        solar_onm["solar_ctu_bay"] = s_cap * ctu_bay_charges * (1 + escalation_rate_ctu) ** (
                    global_df['no_of_yr_pst_cod'] - 1) * solar_onm['days/year_ratio'] * global_df[
                                         'op_flag'] * solar_switch
        escalation_year = np.where(global_df['no_of_yr_pst_cod'] > 3, (global_df['no_of_yr_pst_cod'] - 1) // 3, 0)
        solar_onm["land_lease_charges"] = land_lease_carges_pa * land_required * (s_cap * 1.25) * (
                    1 + land_lease_escalation) ** escalation_year * solar_onm['days/year_ratio'] * solar_switch * \
                                          global_df['op_flag']
        invrtr_rplcmnt_flg = np.where(global_df['month_start'] == invrtr_repl, 1, 0)
        solar_onm["inverter_replacement"] = cost_replacement * invrtr_rplcmnt_flg * (
                    s_cap * 1.25) * solar_switch * inverter_switch
        bird_flag = np.where(solar_onm['month_start'] > free_onm_prd, global_df['op_flag'], 0)

        bird_div_main = ((810000 * 1.185 * tl_length * 0.02) / 1000000) / s_cap
        solar_onm['year'] = global_df['no_of_yr_pst_cod']
        solar_onm["bird_escalation_year"] = np.where(solar_onm['year'] > 1, ((solar_onm['year'] + 2) // 5), 0)
        solar_onm["bird_diverter_amc"] = bird_div_main * s_cap * (
                (1 + bird_diverter_amc_escalation) ** (solar_onm["bird_escalation_year"] - 1)) * solar_onm[
                                             'days/year_ratio'] * solar_switch * global_df['op_flag'] * bird_flag
        inverter_flag = np.where(solar_onm['month_start'] > free_invrtr_amc, global_df['op_flag'], 0)
        solar_onm["amc_escalation_year"] = np.where(global_df['no_of_yr_pst_cod'] >= 6,
                                                    ((global_df['no_of_yr_pst_cod'] - 6) // 5), 0)
        solar_onm["inverter_amc"] = inverter_annual_maintenance * s_cap * (
                (1 + inverter_amc_escalation) ** solar_onm["amc_escalation_year"]) * solar_onm[
                                        'days/year_ratio'] * solar_switch * inverter_flag
        solar_percent = pd.DataFrame({
            'solar_percent': list(monthly_cal['solar_pr'][6:]) + list(monthly_cal['solar_pr'][:6])
        })
        result = np.outer(macro_cal['degradation_solar'], solar_percent['solar_percent']).flatten()
        solar_onm['rslt'] = 0
        solar_onm.loc[(solar_onm['month_start'] > constr_end_date) &
                      (solar_onm['month_start'] <= end_date), 'rslt'] = result
        solar_onm["aug_s_cap_cost"] = aug_s_cap_exp * solar_onm['rslt'] * solar_switch

        solar_onm["land_tax_raj"] = np.where(global_df['no_of_yr_pst_cod'] > free_period_land,
                                             land_tax_charges_raj * (s_cap * 1.25) * solar_switch *
                                             solar_onm['days/year_ratio'], 0)

        solar_onm["ists_charges_redf"] = (
                ists_charges * s_cap * solar_switch * solar_onm['days/year_ratio']
                * global_df['op_flag'])
        solar_onm["solar_insurance_cost"] = insurance_solar * (s_cap * 1.25) * solar_switch * solar_onm[
            'days/year_ratio'] * ((1 + escalation_insur) ** (global_df['no_of_yr_pst_cod'] - 1)) * global_df['op_flag']
        solar_onm.drop(columns=['rslt'], inplace=True)

        #### Solar Onm Quarterly

        slr_onm_quat = solar_onm[['month_start', 'solar_onm_cost', 'solar_ctu_bay', 'land_lease_charges',
                                  'inverter_replacement', 'bird_diverter_amc', 'inverter_amc',
                                  'aug_s_cap_cost', 'land_tax_raj', 'ists_charges_redf',
                                  'solar_insurance_cost']]
        slr_onm_quat['solar_dsm_penalities'] = dsm_penalties['solar_dsm_penalities']
        slr_onm_quat['solar_dsm_penalities'].fillna(0, inplace=True)
        columns = ['solar_onm_cost', 'solar_ctu_bay', 'land_lease_charges',
                   'inverter_replacement',
                   'bird_diverter_amc', 'inverter_amc', 'aug_s_cap_cost', 'land_tax_raj',
                   'ists_charges_redf', 'solar_insurance_cost', 'solar_dsm_penalities']
        slr_onm_quat[columns] = slr_onm_quat[columns].apply(pd.to_numeric, errors='coerce')
        slr_onm_quat.set_index('month_start', inplace=True)
        slr_onm_quat = slr_onm_quat.resample('Q').sum(numeric_only=True)
        slr_onm_quat.reset_index(inplace=True)
        total_solaronm_col = ['solar_onm_cost', 'solar_ctu_bay', 'land_lease_charges', 'inverter_replacement',
                              'bird_diverter_amc', 'inverter_amc', 'aug_s_cap_cost', 'land_tax_raj',
                              'ists_charges_redf', 'solar_insurance_cost', 'solar_dsm_penalities']

        slr_onm_quat['total_solar_onm'] = slr_onm_quat[total_solaronm_col].sum(axis=1)

        #### Stoarage Components

        strge_comps = pd.DataFrame()
        strge_comps["month_start"] = solar_onm["month_start"]
        strge_comps["batt_maintenance_cst"] = batt_maintenance_cst.astype(float)
        strge_comps["pump_strage"] = pump_strage
        strge_comps["bnkd_pwr_drwl_cst"] = final_row_dff[2]
        strge_comps["additional_c1_withdrawal_unit_charges"] = final_row_dff[3]
        strge_comps["additional_c4_withdrawal_unit_charges"] = final_row_dff[4]
        strge_comps["additional_c5_withdrawal_unit_charges"] = final_row_dff[5]
        strge_comps.sum(numeric_only=True)

        #### Quarterly calculations of storage components

        strge_comps.set_index('month_start', inplace=True)
        strge_comps = strge_comps.resample('Q').sum(numeric_only=True)
        strge_comps.reset_index(inplace=True)
        strge_comps_tb_added = ['batt_maintenance_cst', 'pump_strage', 'bnkd_pwr_drwl_cst',
                                'additional_c1_withdrawal_unit_charges',
                                'additional_c4_withdrawal_unit_charges',
                                'additional_c5_withdrawal_unit_charges']  #
        strge_comps["strge_comps_opex"] = strge_comps[strge_comps_tb_added].sum(axis=1)

        ####opex_gh2
        years_count = wind_onm['month_start'].dt.year.nunique()
        # input.recovery_price_switch
        percent_h2_production = pd.concat([monthly_cal['h2%']] * years_count, ignore_index=True)
        percent_h2_production = percent_h2_production * flag['Operations flag period']
        h2_nh3_production = pd.DataFrame()

        h2_nh3_production['percent_h2_production'] = percent_h2_production

        h2_nh3_production['h2_generated_tons'] = pd.Series(
            [0] * constr_dur + np.repeat(macro_cal['h2_generated_tons'].values, 12).tolist() + [
                0] * 12)  ##### 12 hardcode is month multiplier, [0]*12,,1 year taken as buffer period

        h2_nh3_production['h2_production'] = h2_nh3_production['h2_generated_tons'] * h2_nh3_production[
            'percent_h2_production'] / 100  ####### /100 to get exact percentage multiplication
        h2_nh3_production['h2_price'] = input.tariff_gh2 * (1 + input.escalation_gh2_price) * flag[
            'Operations flag period'] * input.exchange_rate_usdinr
        h2_nh3_production.T
        print(h2_nh3_production['h2_production'].dtype)

        h2_nh3_production['water_cost_gh2'] = (
                    h2_nh3_production['h2_production'] * input.water_consumption * input.cost_per_unit_water * (
                        1000 / 10 ** 6) * ((1 + input.inflation_gh2) ** (global_df['no_of_yr_pst_cod'] - 1)))
        h2_nh3_production['vbr_expense'] = np.where(flag['No. Of Years Post CoD'] > 1, ((
                                                                                                    input.vbr_expense * input.exchange_rate_usdinr * (
                                                                                                        1 + input.vbr_expense_escalation) ** (
                                                                                                                flag[
                                                                                                                    'No. Of Years Post CoD'] - 2)) / 12),
                                                    0)

        cy_start_flag = pd.DataFrame(index=['construction_cy_start_flag'], columns=list(
            range(0, (input.total_construction_period + (input.operations_period + 1) * 12))))

        cy_start_flag[:] = 0
        cy_start_flag.iloc[:, np.arange(0, cy_start_flag.shape[1], 12)] = 1
        cy_start_flag.loc[:, 347] = 1

        annual_rent_for_land_required_electrolyser_dur_const = input.annual_rent_land_required_electrolyzer * (
                    1 + input.annual_land_lease_escalation_land_required_electrolyzer) ** (constr_dur / 12)

        land_lease_charges_for_gh2 = annual_rent_for_land_required_electrolyser_dur_const * input.land_required_electrolyzer * cy_start_flag * (
                    (1 + input.annual_land_lease_escalation_land_required_electrolyzer) ** (
                        flag['No. Of Years Post CoD'] - 1)) * flag['Operations flag period'] * input.gh2_switch

        h2_nh3_production['land_lease_charges_for_gh2'] = land_lease_charges_for_gh2.T
        land_lease_charges_for_gh2.sum(axis=1)

        h2_nh3_production['onm_h2'] = (input.gh2_om_initial_capex / 12) * (electrolyzer + BOP) * (
                    (1 + input.inflation_gh2) ** (flag['No. Of Years Post CoD'] - 1)) * flag[
                                          'Operations flag period'] * input.gh2_switch

        #####opex_nh3
        input.recovery_price_switch = 1
        percent_nh3_production = pd.concat([monthly_cal['nh3%']] * years_count, ignore_index=True)
        percent_nh3_production = percent_nh3_production * flag['Operations flag period']

        h2_nh3_production['percent_nh3_production'] = percent_nh3_production
        h2_nh3_production['nh3_generated_tons'] = pd.Series(
            [0] * constr_dur + np.repeat(macro_cal['nh3_generated_tons'].values, 12).tolist() + [0] * 12)

        h2_nh3_production['nh3_production'] = h2_nh3_production['nh3_generated_tons'] * h2_nh3_production[
            'percent_nh3_production'] / 100  ######### /100 to get exact percentage     ########## macro_cal['nh3_generated_tons'] not matching exactly that flows down,minor mismatch
        h2_nh3_production['nh3_price'] = input.tariff_nh3 * (1 + input.escalation_nh3_price) * flag[
            'Operations flag period'] * input.exchange_rate_usdinr
        h2_nh3_production.T

        h2_nh3_production['onm_nh3'] = (input.nh3_om_initial_capex / 12) * capex_nh3 * (
                    (1 + input.inflation_nh3) ** (flag['No. Of Years Post CoD'] - 1)) * flag[
                                           'Operations flag period'] * input.nh3_switch

        # onm_nh3

        h2_nh3_production['onm_n2'] = (input.n2_om_initial_capex / 12) * capex_n2 * (
                    (1 + input.inflation_nh3) ** (flag['No. Of Years Post CoD'] - 1)) * flag[
                                          'Operations flag period'] * input.nh3_switch

        h2_nh3_production['labour_cost'] = np.nan
        h2_nh3_production['labour_cost'] = h2_nh3_production['labour_cost'].fillna(0)

        h2_nh3_production['nh3_transport_cost'] = None
        h2_nh3_production['nh3_transport_cost'] = h2_nh3_production['nh3_transport_cost'].fillna(0)  ### or np.nan

        gh2_nh3_onm_cost = h2_nh3_production['water_cost_gh2'] + h2_nh3_production['vbr_expense'] + h2_nh3_production[
            'land_lease_charges_for_gh2'] + h2_nh3_production['onm_h2'] + h2_nh3_production['onm_nh3'] + \
                           h2_nh3_production['onm_n2'] + h2_nh3_production['labour_cost'] + h2_nh3_production[
                               'nh3_transport_cost']

        #### Total Opex

        pwr_of_elz_n_nh3 = list(daily_gen.groupby('month')['resultant_supply'].sum() * 1000)
        elec_dty_chrgs = [(pwr * ed_chrgs * (0 if yr <= 5 else 1)) / 10 ** 6 for yr in no_of_yrs_pst_cod
                          for pwr in pwr_of_elz_n_nh3]
        elec_dty_chrgs_quarterly = [sum(elec_dty_chrgs[i:i + 3]) for i in range(0, len(elec_dty_chrgs), 3)]
        opex_oper = pd.DataFrame({
            'qtr_strt_dt': strge_comps['month_start'].apply(get_quarter_start),
            'qtr_end_dt': strge_comps['month_start'],
            'elec_dty_chrgs_quarterly': elec_dty_chrgs_quarterly
        })
        opex_oper['total_opex'] = slr_onm_quat['total_solar_onm'] + wind_onm_quat['total_wind_onm'] + \
                                  dsm_penalties_quat[
                                      'cost_supp_supply'] + strge_comps["strge_comps_opex"] + opex_oper[
                                      'elec_dty_chrgs_quarterly']
        opex_oper.sum(numeric_only=True)

        ### Depreciation

        #### Quarterly Depreciation

        qtrly_btry_depre = pd.DataFrame({
            'qtr_strt_dt': opex_oper['qtr_strt_dt'],
            'qtr_end_dt': opex_oper['qtr_end_dt'],
            'btry_rplcmnt_flg': global_quat_df['op_flag'],
        })
        # ttl_btry_capex need to dynamic when capex will be calculated
        qtrly_btry_depre.at[0, 'btry_orgnl_depre'] = np.minimum((ttl_btry_capex * btry_depre_rate) / 4,
                                                                (ttl_btry_capex - 0) * qtrly_btry_depre.at[
                                                                    0, 'btry_rplcmnt_flg'])
        for index, row in qtrly_btry_depre.iterrows():
            qtrly_btry_depre.at[index, 'btry_orgnl_depre'] = min((ttl_btry_capex * btry_depre_rate) / 4, (
                    ttl_btry_capex - (qtrly_btry_depre.loc[:index, 'btry_orgnl_depre']).sum()) * row[
                                                                     'btry_rplcmnt_flg'])
        qtrly_btry_depre

        #### FY battery depreciation

        yrly_btry_orgnl_depre_fy = pd.DataFrame({
            'fy_strt_dt': qtrly_btry_depre['qtr_strt_dt'].apply(lambda x: financial_year_dates(x)[0]),
            'fy_end_dt': qtrly_btry_depre['qtr_end_dt'].apply(lambda x: financial_year_dates(x)[1]),
            'yrly_btry_orgnl_depre_fy': qtrly_btry_depre['btry_orgnl_depre']
        })
        yrly_btry_orgnl_depre_fy = yrly_btry_orgnl_depre_fy.groupby(['fy_strt_dt', 'fy_end_dt']).sum().reset_index()
        yrly_btry_orgnl_depre_fy

        # flag

        capex = res.T["mnthly_cpx"] - res.T["btry_cpx"] + res.T["idc"].fillna(
            0)  # **************change made on 19 april 2024
        depre = pd.DataFrame()
        depre['date'] = pd.date_range(const_date, oper_start_date, freq='MS')
        depre['capex'] = capex
        depre['financial_year'] = depre['date'].apply(
            lambda x: f'{x.year}-{x.year + 1}' if x.month >= 4 else f'{x.year - 1}-{x.year}')
        depre = depre.groupby('financial_year').agg({'capex': 'sum'})
        depre.reset_index(inplace=True)
        new_rows = pd.DataFrame({'capex': np.zeros(41 - len(depre))})  ###### WHY 41 ONLY
        depre = pd.concat([depre, new_rows]).reset_index(drop=True)
        depre.drop(columns='financial_year', inplace=True)

        depre['opening_depre'] = 0
        depre.loc[1:, 'opening_depre'] = depre['capex'].cumsum().shift(1)[1:]
        depre['closing_bal'] = depre['capex'].cumsum()

        depre['dep_for_period'] = 0
        depre['book_dep_celing'] = 0

        depre["days_year_flag"] = flag['No. of Days in Operations'][1:42].values / flag['Number of Days in Year'][
                                                                                   1:42].values  ######3 CHECK INDEXING
        depre["operation_flag"] = flag['Operation Active Flag for dep'][1:42].values  # CHECK INDEXING
        btry_orgnl_depre_fy = qtrly_btry_depre['btry_orgnl_depre'].tolist()

        ############3 book depreciation
        for i in range(len(depre)):
            if i == 0:
                depre.loc[i, 'book_dep_celing_dm'] = depre['capex'].sum() * max_dep_value - depre.loc[
                    i, 'dep_for_period']
                depre.loc[i, 'dep_for_period'] = 0
            else:
                depre.loc[i, 'book_dep_celing_dm'] = depre.loc[i - 1, 'book_dep_celing_dm'] - depre.loc[
                    i - 1, 'dep_for_period']
                ############formula change (on 23th may 2024)
                ######## swap closing balance with ceiling
                depre.loc[i, 'dep_for_period'] = np.minimum(book_dep_rate * depre.loc[i, 'closing_bal'],
                                                            depre.loc[i, 'book_dep_celing_dm']) * \
                                                 depre["operation_flag"][i] * depre["days_year_flag"][i]
        depre['book_dep_celing'] = np.append(depre['book_dep_celing_dm'][1:], 0)
        depre['cummu_dep_period'] = depre['dep_for_period'].cumsum()
        depre['net_asset_val'] = np.maximum(0, (depre['closing_bal'] - depre['cummu_dep_period']))

        depre['tax_depre_flag'] = flag['Tax Depreciation To Be Considered Flag'][1:42].values

        ######################333333 SLM DEPRECIATION
        for i in range(len(depre)):
            if i == 0:
                depre.loc[i, 'dep_slm_cummu'] = 0
                depre.loc[i, 'dep_period_slm'] = 0

            else:

                depre.loc[i, 'dep_period_slm'] = depre['tax_depre_flag'][i] * np.minimum(
                    tax_rate_slm * depre.loc[i, 'closing_bal'],
                    depre.loc[i, 'closing_bal'] - depre.loc[i - 1, 'dep_slm_cummu'])
                depre.loc[i, 'dep_slm_cummu'] = depre.loc[i - 1, 'dep_slm_cummu'] + depre.loc[i, 'dep_period_slm']

        depre.loc[0, 'dep_wdv_cummu'] = 0
        depre.loc[0, 'dep_period_wdv'] = 0
        depre.loc[0, 'net_asset_wdv'] = depre.loc[0, 'closing_bal'] - depre.loc[0, 'dep_wdv_cummu']

        for i in range(1, len(depre)):
            depre.loc[i, 'dep_period_wdv'] = depre['tax_depre_flag'][i] * tax_rate_wdv * depre.loc[
                i - 1, 'net_asset_wdv']
            depre.loc[i, 'dep_wdv_cummu'] = depre.loc[i - 1, 'dep_wdv_cummu'] + depre.loc[i, 'dep_period_wdv']
            depre.loc[i, 'net_asset_wdv'] = depre.loc[i, 'closing_bal'] - depre.loc[i, 'dep_wdv_cummu']

        # to make this first column
        flag['FY Start Date'] = pd.to_datetime(flag['FY Start Date'])
        fy_end_dates = flag['FY Start Date'][1:42].reset_index(drop=True)
        depre.insert(0, 'FY Start Date', fy_end_dates)

        # ***************** BATTERY DEPRECIATION IT - WDV method (newly added on 8th may 2024)
        wdv_max_deprec_val_battery = depre_sheet.iloc[25, 3]
        wdv_rate_battery = depre_sheet.iloc[26, 3]
        depre['operations_year_count'] = depre['operation_flag'].cumsum()
        depre['operations_year_count'] = depre['operations_year_count'].mask(depre['operation_flag'] == 0,
                                                                             0)  # in place of mask,counter can be used if operation year becomes zero in between of operations
        depre['battery_tax_depreciation_wdv_method'] = np.nan
        cumulative_sum = 0
        for i in range(len(depre)):
            if (depre.loc[i, 'operations_year_count'] == 1) and (depre.loc[i, 'days_year_flag'] > 0.5):
                depre.loc[i, 'battery_tax_depreciation_wdv_method'] = sum(btry_orgnl_depre_fy) * wdv_rate_battery
            elif depre.loc[i, 'operations_year_count'] == 1:
                depre.loc[i, 'battery_tax_depreciation_wdv_method'] = sum(btry_orgnl_depre_fy) * wdv_rate_battery / 2
            else:
                depre.loc[i, 'battery_tax_depreciation_wdv_method'] = (
                                                                              sum(btry_orgnl_depre_fy) * wdv_max_deprec_val_battery - cumulative_sum
                                                                      ) * wdv_rate_battery * depre.loc[
                                                                          i, 'operation_flag']

            # Updating cumulative sum
            cumulative_sum += depre.loc[i, 'battery_tax_depreciation_wdv_method']

        depre["dep_period_wdv"] += depre["battery_tax_depreciation_wdv_method"]
        depre["dep_for_period"] += yrly_btry_orgnl_depre_fy["yrly_btry_orgnl_depre_fy"]
        active_flag_df = pd.DataFrame(flag[['Quarter Start Date for DSRA', 'Operation Active Flag']][:120])
        active_flag_df = active_flag_df.set_index('Quarter Start Date for DSRA')
        active_flag_df['quarter'] = active_flag_df.index.to_period('Q-DEC').shift(-1)
        active_flag_df['Operation Active Flag'] = active_flag_df['Operation Active Flag'].astype('int')
        active_flag_df['quarter'] = active_flag_df['quarter'].astype(str)

        depre['year'] = depre['FY Start Date'].dt.year
        active_flag_df.reset_index(inplace=True)

        depre["fy_strt_dt"] = yrly_btry_orgnl_depre_fy["fy_strt_dt"]
        depre["fy_end_dt"] = yrly_btry_orgnl_depre_fy["fy_end_dt"]
        depre["yrly_btry_orgnl_depre_fy"] = yrly_btry_orgnl_depre_fy["yrly_btry_orgnl_depre_fy"]

        new_list = [x for x in depre['dep_for_period'].tolist() for _ in range(4)][:-4]
        depre = depre[depre['FY Start Date'] < operation_end_date]
        # depre

        ### Depre Quarterly

        quarterly_depre = pd.DataFrame()
        quarterly_depre['qtr_strt_dt'] = qtrly_btry_depre['qtr_strt_dt']
        quarterly_depre['qtr_end_dt'] = qtrly_btry_depre['qtr_end_dt']
        quarterly_depre['days_in_prd'] = days_in_prd.tolist()[:120]
        quarterly_depre['days_in_fy'] = days_in_fy.tolist()[:120]
        quarterly_depre['dep_for_period'] = new_list[:120]
        # quarterly_depre
        quarterly_depre['dep_for_period'] = quarterly_depre['dep_for_period'].shift(-3).fillna(0.0)
        quarterly_depre['dep_for_period'].loc[[13, 14, 15]] = 0.0
        quarterly_depre.loc[quarterly_depre['qtr_strt_dt'] > oper_start_date, 'dep_for_period'] = (quarterly_depre[
                                                                                                       'dep_for_period'] *
                                                                                                   quarterly_depre[
                                                                                                       'days_in_prd']) / \
                                                                                                  quarterly_depre[
                                                                                                      'days_in_fy']
        qtr_aftr_oper_end_date = oper_end_date + timedelta(days=1)
        quarterly_depre.loc[quarterly_depre['qtr_end_dt'] == 'qtr_aftr_oper_end_date', 'dep_for_period'] = \
        quarterly_depre['dep_for_period'] / 3
        quarterly_depre.loc[(quarterly_depre['qtr_strt_dt'] >= '2053-04-01') & (
                    quarterly_depre['qtr_end_dt'] <= oper_end_date), 'dep_for_period'] = quarterly_depre[
            'dep_for_period']
        quarterly_depre["dep_for_period"].sum()  ################# TO BE CORRECTED ( ARUN) : 7TH JUNE
        # quarterly_depre

        #####Depreciation of GH2 by Equipment Usage
        dep_eq_usge_gh2 = pd.DataFrame()
        dep_eq_usge_gh2['quat_start'] = quat_repl_cpx['quat_start']  # .apply(lambda x: financial_year_dates(x)[0])
        dep_eq_usge_gh2['quat_end'] = quat_repl_cpx['quat_end']  # .apply(lambda x: financial_year_dates(x)[1])
        dep_eq_usge_gh2['cumm_usge_el'] = quat_repl_cpx['cumm_usge_el']
        dep_eq_usge_gh2.loc[0, 'el_orgnl'] = np.minimum(
            el_cpx * ((quat_repl_cpx.at[0, 'cumm_usge_el'] - 0) / el_stk_lf),
            (el_cpx - 0) * quat_repl_cpx.at[0, 'quat_flag'])  # initializing the column's value
        ttl_repl_cpx_1 = quat_repl_cpx['repl_cpx_1'].sum()
        ttl_repl_cpx_2 = quat_repl_cpx['repl_cpx_2'].sum()
        dep_eq_usge_gh2['el_repl_1'] = 0
        dep_eq_usge_gh2['el_repl_2'] = 0
        for index, row in quat_repl_cpx.iloc[1:].iterrows():
            dep_eq_usge_gh2.at[index, 'el_orgnl'] = np.minimum(el_cpx * ((quat_repl_cpx.at[index, 'cumm_usge_el'] -
                                                                          quat_repl_cpx.at[
                                                                              index - 1, 'cumm_usge_el']) / el_stk_lf) *
                                                               quat_repl_cpx.at[index, 'quat_flag'], (
                                                                           el_cpx - dep_eq_usge_gh2.loc[:index - 1,
                                                                                    'el_orgnl'].sum()) *
                                                               quat_repl_cpx.at[index, 'quat_flag'])
            if (quat_repl_cpx.at[index, 'cumm_usge_el'] > el_stk_lf < (2 * el_stk_lf)):
                dep_eq_usge_gh2.at[index, 'el_repl_1'] = np.minimum(quat_repl_cpx_gh2['repl_cpx_1'].sum() * ((
                                                                                                                         quat_repl_cpx.at[
                                                                                                                             index, 'cumm_usge_el'] -
                                                                                                                         quat_repl_cpx.at[
                                                                                                                             index - 1, 'cumm_usge_el']) / el_stk_lf),
                                                                    (quat_repl_cpx_gh2[
                                                                         'repl_cpx_1'].sum() - dep_eq_usge_gh2.loc[
                                                                                               :index - 1,
                                                                                               'el_repl_1'].sum()) *
                                                                    quat_repl_cpx.at[index, 'quat_flag'])
            if quat_repl_cpx.at[index, 'cumm_usge_el'] > (2 * el_stk_lf):
                dep_eq_usge_gh2.at[index, 'el_repl_2'] = np.minimum(quat_repl_cpx_gh2['repl_cpx_2'].sum() * ((
                                                                                                                         quat_repl_cpx.at[
                                                                                                                             index, 'cumm_usge_el'] -
                                                                                                                         quat_repl_cpx.at[
                                                                                                                             index - 1, 'cumm_usge_el']) / el_stk_lf),
                                                                    (quat_repl_cpx_gh2[
                                                                         'repl_cpx_2'].sum() - dep_eq_usge_gh2.loc[
                                                                                               :index - 1,
                                                                                               'el_repl_2'].sum()) *
                                                                    quat_repl_cpx.at[index, 'quat_flag'])

        #####Book Depreciation(FY) - GH2/BATTERY

        oper_minus_1_yr = oper_end_dt - pd.DateOffset(years=1)  #### operations till minus 1 years
        bk_dep_sch_gh2 = pd.DataFrame()
        bk_dep_sch_gh2 = dep_eq_usge_gh2[['cumm_usge_el', 'el_orgnl', 'el_repl_1', 'el_repl_2']]
        bk_dep_sch_gh2.insert(0, 'fy_start', dep_eq_usge_gh2['quat_start'].apply(lambda x: financial_year_dates(x)[0]))
        bk_dep_sch_gh2.insert(1, 'fy_end', dep_eq_usge_gh2['quat_start'].apply(lambda x: financial_year_dates(x)[1]))
        bk_dep_sch_gh2 = bk_dep_sch_gh2.groupby(['fy_start', 'fy_end']).sum().reset_index()
        bk_dep_sch_gh2['flag'] = bk_dep_sch_gh2['fy_end'].apply(
            lambda yr: 0 if (yr < oper_start_date) or (yr > operation_end_date) else 1)
        bk_dep_sch_gh2['ttl_gh2_cpx'] = total_gh2_capex
        bk_dep_sch_gh2['no_f_dys_prd'] = bk_dep_sch_gh2.apply(
            lambda row: calculate_days(row, oper_start_date, oper_end_date), axis=1)
        bk_dep_sch_gh2['no_f_dys_yr'] = bk_dep_sch_gh2['fy_start'].apply(days_in_financial_year)
        bk_dep_sch_gh2['ini_cpx'] = 0
        bk_dep_sch_gh2['acc_wdv_ini_cpx'] = 0
        for idx, row in bk_dep_sch_gh2.iterrows():
            if (row['fy_end'] > oper_start_date) & (row['fy_end'] < oper_end_dt):
                bk_dep_sch_gh2.loc[idx, 'ini_cpx'] = np.minimum(
                    total_gh2_capex * max_depre_val * bk_depre_rt_gh2 * (row['no_f_dys_prd'] / row['no_f_dys_yr']),
                    (total_gh2_capex * max_depre_val) - bk_dep_sch_gh2['ini_cpx'].sum() * row['flag'])

            if oper_end_date < row['fy_end'] < operation_end_date:
                bk_dep_sch_gh2.loc[idx, 'ini_cpx'] = total_gh2_capex * max_depre_val - bk_dep_sch_gh2['ini_cpx'].sum()

            if (row['fy_start'] < oper_start_date < row['fy_end']):
                if row['no_f_dys_prd'] > 182:  #### 182 taken hard coded as per formula
                    bk_dep_sch_gh2.loc[idx, 'acc_wdv_ini_cpx'] = total_gh2_capex * wdv_rt_gh2
                else:
                    bk_dep_sch_gh2.loc[idx, 'acc_wdv_ini_cpx'] = ((total_gh2_capex * wdv_rt_gh2) / 2) * row['flag']

            elif (row['fy_start'] > oper_start_date) & (row['fy_start'] < oper_end_date):
                # np.nan
                bk_dep_sch_gh2.loc[idx, 'acc_wdv_ini_cpx'] = ((total_gh2_capex * max_depre_val - bk_dep_sch_gh2.loc[
                                                                                                 :idx - 1,
                                                                                                 'acc_wdv_ini_cpx'].sum()) * wdv_rt_gh2 *
                                                              row['flag'])

        bk_dep_sch_gh2['depre_repl_cpx'] = bk_dep_sch_gh2['el_repl_1'] + bk_dep_sch_gh2['el_repl_2']
        bk_dep_sch_gh2['ttl_bk_depre'] = bk_dep_sch_gh2['ini_cpx'] + bk_dep_sch_gh2['depre_repl_cpx']
        bk_dep_sch_gh2['depre_repl_cpx_btry_slm'] = np.where(bk_dep_sch_gh2['flag'] < 2, 0,
                                                             (fy_repl_cpx_gh2['repl_cpx_btry'] * bk_depre_rt_btry) / 4)
        bk_dep_sch_gh2['ttl_bk_depre_btry_slm'] = depre['yrly_btry_orgnl_depre_fy'] + bk_dep_sch_gh2[
            'depre_repl_cpx_btry_slm']

        ##### Income tax depreciation schedule - WDV - GH2

        bk_dep_sch_gh2['incm_tx_gh2_depre_repl_cpx'] = bk_dep_sch_gh2['el_repl_1'] + bk_dep_sch_gh2['el_repl_2']
        bk_dep_sch_gh2['ttl_wdv_gh2'] = bk_dep_sch_gh2['acc_wdv_ini_cpx'] + bk_dep_sch_gh2['incm_tx_gh2_depre_repl_cpx']

        ##### Income tax depreciation schedule - WDV - Battery

        bk_dep_sch_gh2['incm_tx_btry_depre_repl_cpx'] = np.where(bk_dep_sch_gh2['flag'] < 2, 0, (
                    fy_repl_cpx_gh2['repl_cpx_btry'] * bk_depre_rt_btry) / 4)
        # bk_dep_sch_gh2['ttl_wdv_btry'] = bk_dep_sch_gh2['acc_wdv_ini_cpx'] + bk_dep_sch_gh2['incm_tx_btry_depre_repl_cpx']
        bk_dep_sch_gh2['ttl_wdv_btry'] = depre['battery_tax_depreciation_wdv_method'] + bk_dep_sch_gh2[
            'incm_tx_btry_depre_repl_cpx']

        print(bk_dep_sch_gh2)
        depre_quat_nh3 = pd.DataFrame()
        depre_quat_nh3['qtr_strt_dt'] = qtrly_btry_depre['qtr_strt_dt']
        depre_quat_nh3['qtr_end_dt'] = qtrly_btry_depre['qtr_end_dt']

        operations = global_df['op_flag']
        gcc_flag = flag['GCC Flag']  # .loc[:360]
        no_years_post_cod = global_df['no_of_yr_pst_cod']
        depre_gcc = (1 + depre_gcc_rate) ** no_years_post_cod

        revenue = pd.DataFrame()
        # revenue['month_start'] = wind_onm['month_start']
        revenue['month_start'] = wind_onm[
            'month_start']  # pd.date_range(start=constr_date, end=operation_end_date + pd.DateOffset(years=1), freq='MS')
        # Total number of years
        years_count = revenue[
            'month_start'].dt.year.nunique()  ######### converting date range to year count,month count,quarter count to use in revenue['per_gen']
        # Total number of months
        months_count = revenue['month_start'].nunique()
        # Total number of quarters
        quarters_count = revenue['month_start'].dt.to_period('Q').nunique()

        revenue['per_gen'] = np.tile(monthly_cal['re_power_pr'], years_count) * operations  #### 40 changed to 30

        def outer_and_select(first, second, start=constr_dur, end=348):  ######### take care of this part 348
            zeros = np.zeros(months_count)
            zeros[start:end] = np.outer(first, second).flatten()[:end - start]
            return zeros * operations

        revenue['supp_u_bid'] = outer_and_select(macro_cal['re_bid_mus'], monthly_cal['re_power_pr'])

        revenue['merchant_sale_mus'] = outer_and_select(macro_cal['re_sale_mus'], monthly_cal['re_power_pr'])
        revenue['gcc_gen'] = (revenue['supp_u_bid'] + revenue[
            'merchant_sale_mus']) * gcc_flag * gcc_switch * emission_fac
        revenue['month_start'] = pd.to_datetime(revenue['month_start'])
        revenue['bid_tariff'] = 0

        revenue.loc[(revenue['month_start'] >= pd.Timestamp(oper_start_date)) & (
                    revenue['month_start'] <= pd.Timestamp(oper_end_date)), 'bid_tariff'] = tariff_lockin

        revenue['merchant_tariff'] = merchant_tariff * operations
        revenue["gcc_price"] = gcc_sell_price * exchange_rate * depre_gcc * gcc_flag
        revenue['payment_bid'] = revenue['supp_u_bid'] * revenue['bid_tariff']
        revenue['merchant_rev'] = revenue['merchant_sale_mus'] * revenue['merchant_tariff']
        revenue['gcc_rev'] = (revenue['gcc_gen'] * revenue['gcc_price']) / 1000
        revenue['gcc_rev'] = revenue['gcc_rev'].astype(float)

        #########*******************************CHANGE ALL QUARTERLTLY CALCULATIONS IN A BETTER WAY : CODE
        # revenue quaterly
        revenue_quat = pd.DataFrame()
        revenue_quat = revenue[['month_start', 'payment_bid', 'merchant_rev', 'gcc_rev']].copy()

        revenue_quat['month_start'] = pd.to_datetime(revenue_quat['month_start'])
        revenue_quat.set_index('month_start', inplace=True)
        revenue_quat = revenue_quat.resample('Q').sum()
        revenue_quat.reset_index(inplace=True)
        revenue_quat.rename(columns={'month_start': 'quarter_end'}, inplace=True)
        revenue_quat.insert(1, 'quarter_start', revenue_quat['quarter_end'].apply(quarter_start))
        revenue_quat['total_revenue_quat'] = revenue_quat['payment_bid'] + revenue_quat['merchant_rev'] + revenue_quat[
            'gcc_rev']

        revenue_quat['merchant_rev'].sum()

        #### revenue_gh2

        h2_nh3_production['h2'] = (h2_nh3_production['h2_production'] * h2_nh3_production['h2_price']) * 1000 / 10 ** 6
        extra_months = 3  # hardcoded to get 3 months extra to get 15,27...)
        h2_nh3_production['h2_recovery_revenue'] = 0
        h2_nh3_production['h2_recovery_revenue'].iloc[constr_dur + (1 * 12 + extra_months) - 1] = h2_nh3_production[
                                                                                                      'h2_production'].iloc[
                                                                                                  constr_dur:(
                                                                                                              constr_dur + 1 * 12)].sum() * input.recovery_price_h2_production_y1 * (
                                                                                                              1000 / 10 ** 6) * input.recovery_price_switch
        h2_nh3_production['h2_recovery_revenue'].iloc[constr_dur + (2 * 12 + extra_months) - 1] = h2_nh3_production[
                                                                                                      'h2_production'].iloc[
                                                                                                  (
                                                                                                              constr_dur + 1 * 12):(
                                                                                                              constr_dur + 2 * 12)].sum() * input.recovery_price_h2_production_y2 * (
                                                                                                              1000 / 10 ** 6) * input.recovery_price_switch
        h2_nh3_production['h2_recovery_revenue'].iloc[constr_dur + (3 * 12 + extra_months) - 1] = h2_nh3_production[
                                                                                                      'h2_production'].iloc[
                                                                                                  (
                                                                                                              constr_dur + 2 * 12):(
                                                                                                              constr_dur + 3 * 12)].sum() * input.recovery_price_h2_production_y3 * (
                                                                                                              1000 / 10 ** 6) * input.recovery_price_switch

        #### revenue_nh3
        input.recovery_price_switch = 1

        h2_nh3_production['nh3'] = (h2_nh3_production['nh3_production'] * h2_nh3_production['nh3_price']) / 10 ** 6

        #### since allocations of 1st,2nd,3rd of oper. year in 15,27,39th month
        extra_months = 3  # hardcoded to get 3 months extra to get 15,27...)

        h2_nh3_production['nh3_recovery_revenue'] = 0
        h2_nh3_production['nh3_recovery_revenue'].iloc[constr_dur + (1 * 12 + extra_months) - 1] = h2_nh3_production[
                                                                                                       'nh3_production'].iloc[
                                                                                                   constr_dur:(
                                                                                                               constr_dur + 1 * 12)].sum() * input.recovery_price_nh3_production_y1 * (
                                                                                                               1000 / 10 ** 6) * input.recovery_price_switch
        h2_nh3_production['nh3_recovery_revenue'].iloc[constr_dur + (2 * 12 + extra_months) - 1] = h2_nh3_production[
                                                                                                       'nh3_production'].iloc[
                                                                                                   (
                                                                                                               constr_dur + 1 * 12):(
                                                                                                               constr_dur + 2 * 12)].sum() * input.recovery_price_nh3_production_y2 * (
                                                                                                               1000 / 10 ** 6) * input.recovery_price_switch
        h2_nh3_production['nh3_recovery_revenue'].iloc[constr_dur + (3 * 12 + extra_months) - 1] = h2_nh3_production[
                                                                                                       'nh3_production'].iloc[
                                                                                                   (
                                                                                                               constr_dur + 2 * 12):(
                                                                                                               constr_dur + 3 * 12)].sum() * input.recovery_price_nh3_production_y3 * (
                                                                                                               1000 / 10 ** 6) * input.recovery_price_switch

        ebitda = pd.DataFrame()
        ebit = pd.DataFrame()

        ebitda['year'] = quarterly_depre['qtr_strt_dt']
        ebitda['EBITDA'] = revenue_quat['total_revenue_quat'].reset_index(drop=True) - opex_oper[
            'total_opex'].reset_index(
            drop=True)  ################# here in opex_oper['total_opex'],thare is NAN value after 115 index,which is not in current code.making NAN in ebitda['EBITDA'] for time being.

        ebitda['EBITDA'] = pd.to_numeric(ebitda['EBITDA'], errors='coerce')
        ebitda['EBITDA'].iloc[116:] = np.nan  ############### added to match values.
        ebit['ebitda'] = ebitda['EBITDA']
        # ebit['depreciation'] = quarterly_depre['dep_for_period']
        ebit['EBIT'] = ebitda['EBITDA'].reset_index(drop=True) - quarterly_depre['dep_for_period'].reset_index(
            drop=True)
        # print(ebit['EBIT'].sum())
        total_onm_opex = pd.DataFrame()
        total_onm_opex['month_start'] = revenue_quat['quarter_end']
        total_onm_opex['onm_ex_supp'] = slr_onm_quat['total_solar_onm'] + wind_onm_quat['total_wind_onm']

        # revenue_quat.reset_index(inplace=True)
        recievables_power = pd.DataFrame()
        recievables_power['month_start'] = revenue_quat['quarter_end']

        recievables_power['operations'] = flag['Operations Flag for WC'][
                                          0:quarters_count]  ####################### flag changed to 30 years as per considering operation(160--> 120)
        recievables_power['days for wc'] = flag['Number of Days of Operations in Quarter for WC'][0:quarters_count]
        recievables_power['power_bid_cummu'] = revenue_quat['payment_bid'].cumsum()
        recievables_power['total_rev_ex_gcc'] = revenue_quat['payment_bid']

        mask = (revenue_quat['quarter_end'] == pd.Timestamp(oper_end_date)) | (recievables_power['operations'] == 0)
        recievables_power.loc[mask, 'revenue_power_bid'] = 0
        valid_rows = ~mask
        recievables_power.loc[valid_rows, 'revenue_power_bid'] = (revenue_quat.loc[valid_rows, 'payment_bid'] / (
        recievables_power.loc[valid_rows, 'days for wc']) * power_sale_days)

        recievables_power['revenue_power_bid'].fillna(0, inplace=True)

        recievables_power['recivables_from_power'] = np.minimum(recievables_power['power_bid_cummu'],
                                                                recievables_power['revenue_power_bid'])
        recievables_power['gcc_rev_cummu'] = revenue_quat['gcc_rev'].cumsum()

        mask = (revenue_quat['quarter_end'] == pd.Timestamp(oper_end_date)) | (recievables_power['operations'] == 0)
        recievables_power.loc[mask, 'revenue_gcc'] = 0
        valid_rows = ~mask
        recievables_power.loc[valid_rows, 'revenue_gcc'] = (revenue_quat.loc[valid_rows, 'gcc_rev'] / (
        recievables_power.loc[valid_rows, 'operations']) * gcc_days)

        recievables_power['revenue_gcc'].fillna(0, inplace=True)
        recievables_power['recievable_sale_gcc'] = np.minimum(recievables_power['gcc_rev_cummu'],
                                                              recievables_power['revenue_gcc'])
        total_onm_opex.reset_index(inplace=True)
        recievables_power['onm_ex_supp_cumsum'] = total_onm_opex['onm_ex_supp'].cumsum()

        mask = (total_onm_opex['month_start'] == pd.Timestamp(oper_end_date)) | (
                    recievables_power['operations'] == 0) | (onm_adv_days == 0)
        recievables_power.loc[mask, 'onm_opex'] = 0
        valid_rows = ~mask
        recievables_power.loc[valid_rows, 'onm_opex'] = (total_onm_opex.loc[valid_rows, 'onm_ex_supp'] /
                                                         recievables_power.loc[valid_rows, 'operations']) * onm_adv_days

        recievables_power['onm_opex'].fillna(0, inplace=True)
        recievables_power['advance_opex'] = np.minimum(recievables_power['onm_ex_supp_cumsum'],
                                                       recievables_power['onm_opex'])
        recievables_power['total_net_wc'] = recievables_power['recivables_from_power'] + recievables_power[
            'recievable_sale_gcc'] - recievables_power['advance_opex']
        recievables_power['power_bid_gcc'] = recievables_power['recivables_from_power'] + recievables_power[
            'recievable_sale_gcc']
        recievables_power['change_in_recievables'] = recievables_power['power_bid_gcc'].diff().fillna(0)
        recievables_power['change_in_payable'] = recievables_power['advance_opex'].diff().fillna(0)
        recievables_power['change_in_wc'] = (
                    recievables_power['change_in_recievables'] + recievables_power['change_in_payable'])

        recievables_power['beginning_bal'] = 0
        recievables_power['wc_drawdown'] = recievables_power['change_in_wc'] * (1 - wc_margin)
        recievables_power['ending_bal'] = 0
        recievables_power['interest_on_wc'] = 0

        for i in range(len(recievables_power)):
            if i == 0:
                recievables_power.loc[i, 'ending_bal'] = recievables_power.loc[i, 'wc_drawdown']
            else:
                recievables_power.loc[i, 'beginning_bal'] = recievables_power.loc[i - 1, 'ending_bal']
                #         recievables_power['wc_drawdown'] = recievables_power['change_in_wc'] * (1-wc_margin)
                recievables_power.loc[i, 'ending_bal'] = recievables_power.loc[i, 'beginning_bal'] + \
                                                         recievables_power.loc[i, 'wc_drawdown']
                # recievables_power.loc[i, 'interest_on_wc'] = ((recievables_power.loc[i, 'beginning_bal'] + recievables_power.loc[i, 'ending_bal']) / 2) * interest_wc_per * (global_quat_df['days_in_quarter_prd'][i]/global_df['dys_in_fy'][0:160][i])
                recievables_power.loc[i, 'interest_on_wc'] = ((recievables_power.loc[i, 'beginning_bal'] +
                                                               recievables_power.loc[
                                                                   i, 'ending_bal']) / 2) * interest_wc_per * (flag[
                                                                                                                   'Number of Days of Operations in Quarter for WC'][
                                                                                                               0:quarters_count][
                                                                                                                   i] /
                                                                                                               flag[
                                                                                                                   'Days in Current FY'][
                                                                                                               0:quarters_count][
                                                                                                                   i])  ###### total quarters 120(earlier t_q changed to quarters count created in revenue segment)

        # recievables_power

        a = pd.DataFrame()
        a['x'] = ebitda['EBITDA'].reset_index(drop=True)
        a['y'] = quarterly_depre['dep_for_period'].reset_index(drop=True)
        a['z'] = ebit['EBIT']

        columns_to_sum = recievables_power.drop(['month_start'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)

        def days_in_quarter(quarter_start_date):
            quarter_start_date = pd.Timestamp(quarter_start_date)
            quarter_end_date = (quarter_start_date + pd.offsets.QuarterEnd()).normalize()
            return (quarter_end_date - quarter_start_date).days + 1

        revenue_quat['Days in Period'] = revenue_quat['quarter_start'].apply(days_in_quarter)
        revenue_quat['Days in Current FY'] = revenue_quat['quarter_start'].apply(days_in_financial_year)

        def add_zero_rows(df,
                          target_length):  ############ removing concat from above function, new way to add_zero_rows function.(however i don't see any use of this function as its output not used anywhere in code.)
            if target_length <= len(df):
                return df
            # Create an empty DataFrame of the target length filled with zeros
            new_df = pd.DataFrame(0, index=np.arange(target_length), columns=df.columns)
            # Copy the original DataFrame's data into the new DataFrame
            new_df.iloc[:len(df)] = df.values
            return new_df

        def get_principal_outstanding_end_year(financial_year):
            end_year = int(financial_year.split('-')[1])
            end_year_date = pd.Timestamp(f"{end_year}-03-31")
            return mapping_dict.get(end_year_date, np.nan)

        data = capex_quat['debt_draw']
        capex_df = pd.DataFrame()
        capex_df['debt_idc'] = res.T['debt']

        debt_sch = pd.DataFrame({
            'quarter_start': revenue_quat['quarter_start'],
            'quarter_end': revenue_quat['quarter_end'],
            'debt_drawn': data,
            'debt_repayment': (capex_df['debt_idc'].sum()) * flag['Principal Repayment Factor'][0:quarters_count]
            ####### newly changed t_q(120) changed to quarters count
        })

        debt_sch['principal_outstanding'] = debt_sch['debt_drawn'].cumsum() - debt_sch['debt_repayment'].cumsum()
        # print(debt_sch['debt_drawn'].cumsum())

        debt_sch['opening_debt'] = [0] + list(debt_sch['principal_outstanding'].shift(1)[1:])
        debt_sch['days_pr_quarter'] = (debt_sch['quarter_end'] - debt_sch['quarter_start']).dt.days + 1
        # debt_sch['interest_repay'] = debt_sch['opening_debt'] * (flag['Days in Period for debt'][0:160])/(flag['Days in Current FY'][0:160]) * flag['Interest Repayment Flag'] * interest_rate
        debt_sch['interest_repay'] = debt_sch['opening_debt'] * (revenue_quat['Days in Period']) / (
        wind_onm['wind_op_flag_year'][0:quarters_count]) * flag[
                                         'Interest Repayment Flag'] * interest_rate  ######## hereflag['Days in Current FY'][0:t_q] is monthly flag(for full year) sliced for 120  is  equivalent to  wind_onm['wind_flag_year']
        debt_sch["withholding_tax_on_interest"] = debt_sch['interest_repay'] * witholding_tax_interst
        corporate_switch = corporate_guar_switch

        condition = (
                (round(debt_sch['opening_debt'], 5) > 0) &
                (flag['Corporate Guarantee Flag'].iloc[
                 0:quarters_count]) &  ####### newly changed t_q(120) changed to quarters count
                (corporate_switch == 1)
        )

        debt_sch['corporate_gua_flag'] = condition.astype(int)

        debt_sch['refinancing_fee'] = 0.0
        debt_sch.loc[
            debt_sch['quarter_end'] == refinancing_fee_applicable_date, 'refinancing_fee'] = refinancing_charges * \
                                                                                             res.T[
                                                                                                 'debt'].sum() * refinancing_switch  # date made dynamic
        debt_sch["principle_interest_repay"] = debt_sch['debt_repayment'] + debt_sch['interest_repay']
        debt_sch['corporate_guar_fees'] = (corporate_fees_per / 4) * debt_sch['corporate_gua_flag'] * debt_sch[
            'opening_debt']
        debt_sch['financial_year'] = debt_sch['quarter_start'].apply(
            lambda x: f'{x.year}-{x.year + 1}' if x.month >= 4 else f'{x.year - 1}-{x.year}')
        debt_sch_annual = debt_sch.groupby('financial_year').agg(
            {'principle_interest_repay': 'sum', 'debt_repayment': 'sum', 'interest_repay': 'sum'}).reset_index()

        mapping_dict = debt_sch.set_index('quarter_end')['principal_outstanding'].to_dict()

        debt_sch_annual['debt_for_debt/ebitda'] = debt_sch_annual['financial_year'].apply(
            get_principal_outstanding_end_year)
        debt_sch_annual = debt_sch_annual.iloc[2:-1].reset_index(drop=True)

        debt_sch_annual = add_zero_rows(debt_sch_annual, years_count)  ########### t_y changed to years_count as 30.

        debt_sch_annual

        columns_to_sum = debt_sch.drop(['quarter_start', 'quarter_end'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)
        column_sums

        ### Lender Fee

        wind_onm['month_end'] = wind_onm['month_start'] + pd.offsets.MonthEnd(
            0)  ##### newly added during optimisation to get month end from wind_onm['month_start']

        # lender fee

        lender_fee = pd.DataFrame()

        lender_fee['month_start'] = wind_onm['month_start']
        lender_fee['month_end'] = wind_onm['month_end']
        lender_fee['day_yr_ratio'] = wind_onm['days/year_ratio']

        lender_fee['lender_fees_flag'] = flag["Lender Fees Flag"]

        # lender_fee['tra_total'] = flag['day_yr_ratio'] * lender_fee['lender_fees_flag'] * tra        ################## like this in below all set of code, flag['day_yr_ratio'] replaced with lender_fee['day_yr_ratio']
        lender_fee['tra_total'] = lender_fee['day_yr_ratio'] * lender_fee['lender_fees_flag'] * tra
        lender_fee['trustee_total'] = lender_fee['day_yr_ratio'] * lender_fee['lender_fees_flag'] * trustee
        lender_fee['rating_total'] = lender_fee['day_yr_ratio'] * lender_fee['lender_fees_flag'] * rating_loan
        lender_fee['lia_total'] = lender_fee['day_yr_ratio'] * lender_fee['lender_fees_flag'] * lia
        lender_fee['lie_total'] = lender_fee['day_yr_ratio'] * lender_fee['lender_fees_flag'] * lie
        lender_fee['site_visit_lender'] = lender_fee['day_yr_ratio'] * lender_fee['lender_fees_flag'] * site_visit
        lender_fee['review_charges'] = lender_fee['day_yr_ratio'] * lender_fee['lender_fees_flag'] * review_charges
        lender_fee['lender_fees_total'] = lender_fee['tra_total'] + lender_fee['trustee_total'] + lender_fee[
            'rating_total'] + lender_fee['lia_total'] + lender_fee['lie_total'] + lender_fee['site_visit_lender'] + \
                                          lender_fee['review_charges']
        lender_fee['tra_total'] + lender_fee['trustee_total'] + lender_fee['rating_total'] + lender_fee['lia_total'] + \
        lender_fee['lie_total'] + lender_fee['site_visit_lender'] + lender_fee['review_charges']

        # lender fee quarterly calculations
        lender_fee_quaterly = pd.DataFrame()
        lender_fee.set_index('month_start', inplace=True)
        lender_fee_quaterly['lender_fees'] = lender_fee['lender_fees_total'].resample('Q').sum()
        lender_fee.reset_index(inplace=True)
        lender_fee_quaterly.reset_index(inplace=True)
        lender_fee_quaterly

        columns_to_sum = lender_fee.drop(['month_start', 'month_end'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)

        dsra = pd.DataFrame()
        dsra['quarter_start'] = revenue_quat[
            'quarter_start']  #######  flag removed from flag['Quarter Start Date for DSRA'][:160]  to revenue_quat['quarter_start']

        dsra_req_list = (debt_sch['principle_interest_repay'].shift(-1)[:-1] if dsra_req == 1 else debt_sch[
                                                                                                       'principle_interest_repay'].shift(
            -1)[:-2] + debt_sch['principle_interest_repay'].shift(-2)[:-2]).tolist()

        # dsra_req_list.append(0)
        dsra['dsra_req'] = pd.Series(dsra_req_list) * flag[
            'DSRA Flag']  # multiplication with flag as it was missing from our end
        dsra['dsra_cash_bal'] = flag['DSRA Flag'] * dsra['dsra_req']  # need to be checked at excel model end
        dsra['cash_dsra_req'] = dsra[
                                    'dsra_cash_bal'] * cash_dsra  # cash dsra need to be checked in excel model as its 0 in excel and 1 in input file
        dsra['bg_req_dsra'] = dsra['dsra_req'] * bg_dsra
        dsra['change_cash_dsra'] = dsra['cash_dsra_req'].diff().fillna(0)
        revenue_quat['Operational Days in Period'] = revenue_quat['Days in Period'] * flag[
            'DSRA Flag']  ########### new columns for operational days hasbeeen created to remove dependency from flag
        number_of_days = (revenue_quat['Operational Days in Period']) / (
        wind_onm['wind_op_flag_year'][0:quarters_count])  ########## independent of flag made.

        dsra['dsra_bg_charges'] = dsra['bg_req_dsra'] * dsra_bg_cost * number_of_days
        dsra['dsra_bg_margin'] = dsra['bg_req_dsra'] * dsra_bg_margin
        dsra['change_dsra_bg_margin'] = dsra['dsra_bg_margin'].diff().fillna(0)
        dsra['interest_cash_dsra'] = interest_on_dsra * (
                    dsra['cash_dsra_req'] + dsra['dsra_bg_margin']) * number_of_days

        columns_to_sum = dsra.drop(['quarter_start'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)
        # column_sums

        # PBT
        pbt = pd.DataFrame()
        corporate_tax_rate = main_sheet.iloc[36, 3]
        # pbt['month_start'] = flag['Quarter Start Date for DSRA'][:160] # chnage these
        pbt['month_start'] = revenue_quat['quarter_start']
        pbt['profit_b_tax'] = ebit['EBIT'] - (
                    lender_fee_quaterly['lender_fees'] + debt_sch['refinancing_fee'] + debt_sch['corporate_guar_fees'] +
                    dsra['dsra_bg_charges'] + recievables_power['interest_on_wc'] + debt_sch['interest_repay'] +
                    debt_sch["withholding_tax_on_interest"]) + dsra['interest_cash_dsra']

        pbt.set_index('month_start', inplace=True)

        pbt_annual = pbt.resample('A-MAR').sum()  ############# REMOVE THESE AND MAKE THE ALLOCATION DYNAMIC
        # pbt_annual = pbt_annual[:-1]
        pbt_annual.reset_index(inplace=True)
        pbt_annual = pbt_annual.drop('month_start', axis=1)
        yearly_dates = depre[
            "FY Start Date"]  ####### above code was not including financial year 2023,so used depre["FY Start Date"]

        pbt_annual.insert(0, 'year_start', yearly_dates)

        pbt_annual['tax_profit'] = pbt_annual['profit_b_tax'] + depre["dep_for_period"] - depre['dep_period_wdv']
        pbt_annual['bal_loss_carry_forward'] = 0
        pbt_annual['loss_carry_forward'] = 0

        for i in range(len(pbt_annual)):

            pbt_annual.loc[i, 'loss_carry_forward'] = np.where(
                pbt_annual.loc[i, 'tax_profit'] < 0,
                pbt_annual.loc[i, 'tax_profit'],
                np.minimum(pbt_annual.loc[i, 'tax_profit'],
                           -pbt_annual.loc[i - 1, 'bal_loss_carry_forward'] if i > 0 else 0)
            )

            if i > 0:
                pbt_annual.loc[i, 'bal_loss_carry_forward'] = pbt_annual.loc[i - 1, 'bal_loss_carry_forward'] + \
                                                              pbt_annual.loc[i, 'loss_carry_forward']

        pbt_annual['taxable_profit'] = pbt_annual['tax_profit'] - pbt_annual['loss_carry_forward']
        pbt_annual['tax_pay_wo_80'] = corporate_tax_rate * pbt_annual['taxable_profit']

        # pbt_annual

        columns_to_sum = pbt_annual.drop(['year_start'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)
        column_sums  # validated

        deff_tax = pd.DataFrame()
        deff_tax['month_start'] = depre["FY Start Date"]  # should be dynamic later)
        deff_tax['current_tax_quat'] = pbt_annual['tax_pay_wo_80']
        deff_tax['diff_book_tax_dep'] = (depre['dep_period_wdv'] - depre['dep_for_period'])
        deff_tax['diff_book_tax_dep_cumsum'] = depre['dep_period_wdv'].cumsum() - depre['dep_for_period'].cumsum()
        deff_tax['temp_diff_a'] = deff_tax['diff_book_tax_dep_cumsum']
        deff_tax['temp_diff_b'] = -pbt_annual['bal_loss_carry_forward']
        temp_a_b = (deff_tax['temp_diff_a'] - deff_tax['temp_diff_b']).fillna(0)
        deff_tax['net_temp_diff'] = np.where(temp_a_b > 0, temp_a_b, 0)
        deff_tax['total_dtl_pend'] = deff_tax['net_temp_diff'] * corporate_tax_rate
        deff_tax['dtl_charged_pnl'] = deff_tax['total_dtl_pend'].diff().fillna(0)
        deff_tax.set_index('month_start', inplace=True)
        deff_tax[
            deff_tax.index > oper_end_date] = 0  ####### removed pd.todatetime as not needed as already in timestamp
        deff_tax.reset_index(inplace=True)
        deff_tax['year'] = deff_tax['month_start'].dt.year

        columns_to_sum = deff_tax.drop(['month_start', 'year'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)

        final_quarterly_df = pd.DataFrame()

        for idx, row in active_flag_df.iterrows():
            quarter = row['quarter']
            year = int(quarter[:4])

            yearly_data = deff_tax[deff_tax['year'] == year]

            if row['Operation Active Flag'] == 1 and not yearly_data.empty:
                yearly_data_divided = yearly_data.copy()
                active_quarters = active_flag_df[(active_flag_df['quarter'].str.startswith(str(year))) &
                                                 (active_flag_df['Operation Active Flag'] == 1)].shape[0]
                for column in ["current_tax_quat", 'diff_book_tax_dep', 'diff_book_tax_dep_cumsum', 'temp_diff_a',
                               'temp_diff_b',
                               'net_temp_diff', 'total_dtl_pend', 'dtl_charged_pnl']:
                    yearly_data_divided[column] /= active_quarters

                final_quarterly_df = pd.concat([final_quarterly_df, yearly_data_divided], ignore_index=True)
            else:
                nan_row = pd.DataFrame([[np.nan for _ in range(final_quarterly_df.shape[1])]],
                                       columns=final_quarterly_df.columns)
                final_quarterly_df = pd.concat([final_quarterly_df, nan_row], ignore_index=True)

        # final_quarterly_df['Quarter Start Date for DSRA'] = active_flag_df['Quarter Start Date for DSRA'].values
        final_quarterly_df['Quarter Start Date for DSRA'] = revenue_quat[
            'quarter_start'].values  ########### active_flag_df['Quarter Start Date for DSRA'] replaced with  revenue_quat['quarter_start'] (removing dependency on flags)

        quarter_start_date = final_quarterly_df['Quarter Start Date for DSRA']
        final_quarterly_df.drop(columns=['Quarter Start Date for DSRA'], inplace=True)
        final_quarterly_df.drop(columns=['year'], inplace=True)

        final_quarterly_df.insert(0, 'quarter_start', quarter_start_date)
        final_quarterly_df.fillna(0, inplace=True)
        final_quarterly_df

        sum1 = final_quarterly_df.drop(['quarter_start', 'month_start'], axis=1)
        sum2 = sum1.sum(axis=0)

        csr_df = pbt.reset_index()  ####### directly made equivalent because dependency on pbt columns.

        def add_financial_year(df, date_col,
                               output_col='financial_year'):  ########## new function added to remove the below set of code,and this function will be used multiple times to get financial year in code. also used in DSCR
            df[output_col] = df[date_col].dt.year
            df.loc[df[date_col].dt.month >= 4, output_col] += 1
            return df

        csr_df = add_financial_year(csr_df, 'month_start')

        sum_by_year = csr_df.groupby('financial_year')['profit_b_tax'].sum().reset_index()

        sum_by_year['rolling_mean'] = sum_by_year['profit_b_tax'].rolling(window=3).mean()
        # Calculate the 'cs' column based on the rolling mean, shifted by 1 position
        sum_by_year['csr_expenses'] = (sum_by_year['rolling_mean'].shift(1) / 4) * csr_per
        # Drop the intermediate 'rolling_mean' column
        sum_by_year = sum_by_year.drop(columns=['rolling_mean'])
        # sum_by_year=sum_by_year.fillna(0)
        csr_quat = pd.merge(csr_df, sum_by_year[['financial_year', 'csr_expenses']], on='financial_year')
        csr_quat['csr_expenses'] = csr_quat['csr_expenses'] * flag["Operations Flag for CSR"][
                                                              :quarters_count]  ################flag quarters changed as per operation 25 years(160--120,30 year consideration)
        csr_quat = csr_quat.fillna(0)
        csr_quat
        csr_quat[['csr_expenses', 'profit_b_tax']].sum()

        ### PAT

        profit_after_tax = pd.DataFrame()
        profit_after_tax['month_start'] = revenue_quat[
            'quarter_start']  ########### removed flag dependency & used  revenue_quat['quarter_start']
        profit_after_tax['PAT'] = (pbt['profit_b_tax'].reset_index(drop=True)) - (
                    csr_quat['csr_expenses'] + final_quarterly_df['current_tax_quat'] + final_quarterly_df[
                'dtl_charged_pnl'])
        profit_after_tax["PAT"].sum()

        ### DSCR

        dscr_quat = pd.DataFrame()
        dscr_quat['month_start'] = revenue_quat[
            'quarter_start']  #### year changed to month_start & annual date_changed to financial year     ########## removed flag dependency & used  revenue_quat['quarter_start']

        # interest cash dsra is interest_income
        dscr_quat['ebitda_for_dscr'] = ebitda['EBITDA'].reset_index(drop=True) + dsra['interest_cash_dsra'].reset_index(
            drop=True) - final_quarterly_df['current_tax_quat'].reset_index(drop=True)
        dscr_quat['interest_repay'] = debt_sch['interest_repay']
        dscr_quat['debt_repay'] = debt_sch['debt_repayment']

        dscr_quat = add_financial_year(dscr_quat,
                                       'month_start')  ############### above function hasbeen used ,already being used in CSR

        dscr_annual = dscr_quat.groupby('financial_year')[
            ['ebitda_for_dscr', 'interest_repay', 'debt_repay']].sum().reset_index()
        dscr_annual['DSCR'] = dscr_annual.apply(
            lambda x: x['ebitda_for_dscr'] / (x['interest_repay'] + x['debt_repay']) if (x['interest_repay'] + x[
                'debt_repay']) != 0 else 0, axis=1)
        dscr_annual = dscr_annual.fillna(0).replace(-np.inf, 0)

        dscr_annual.sum(axis=0)

        debt_sch['withholding_tax_on_interest'].sum()

        # cash flow calculations
        cash_flow_stat = pd.DataFrame()

        cash_flow_stat["qtr_strt_dt"] = revenue_quat['quarter_start']
        cash_flow_stat["qtr_end_dt"] = revenue_quat['quarter_end']

        ebitda['EBITDA'].reset_index(drop=True, inplace=True)
        revenue_quat['total_revenue_quat'].reset_index(drop=True, inplace=True)

        cash_flow_stat['Ebitda_margin'] = (
                    ebitda['EBITDA'].fillna(0) / revenue_quat['total_revenue_quat'].astype(float)).fillna(0)
        cash_flow_stat['Ebit_margin'] = (
                    ebit['EBIT'].fillna(0) / revenue_quat['total_revenue_quat'].astype(float)).fillna(0)
        cash_flow_stat = cash_flow_stat.replace(-np.inf, 0)
        pat_np = profit_after_tax['PAT'].to_numpy()
        revenue_np = revenue_quat['total_revenue_quat'].to_numpy()

        net_margin_np = np.divide(pat_np, revenue_np, out=np.zeros_like(pat_np), where=revenue_np != 0)
        cash_flow_stat['net_margin'] = net_margin_np

        pbt_quat = final_quarterly_df['current_tax_quat'].to_numpy()

        pbt.fillna(0, inplace=True)
        pbt_eff = pbt['profit_b_tax'].to_numpy()
        # print(pbt_quat.shape)
        eff_tax_rate = np.divide(pbt_quat.astype(float), pbt_eff.astype(float), out=np.zeros_like(pbt_quat),
                                 where=pbt_eff != 0)

        cash_flow_stat['eff_tax_rate'] = eff_tax_rate
        cash_flow_stat['tax_sheild_financing'] = ((lender_fee_quaterly['lender_fees'] + debt_sch['refinancing_fee'] +
                                                   debt_sch['corporate_guar_fees'] + dsra['dsra_bg_charges'] +
                                                   recievables_power['interest_on_wc'] + debt_sch['interest_repay']) -
                                                  dsra['interest_cash_dsra'] + debt_sch[
                                                      'withholding_tax_on_interest']) * eff_tax_rate
        cash_flow = pd.concat([ebitda, csr_quat['csr_expenses'], final_quarterly_df['current_tax_quat'],
                               recievables_power['change_in_wc']], axis=1)
        cash_flow_stat['cash_flow_oper'] = cash_flow['EBITDA'] - cash_flow['csr_expenses'] - cash_flow[
            'current_tax_quat'] - cash_flow['change_in_wc']

        cash_flow_stat['cash_flow_investing_capex'] = -capex_quat['capex_month']
        cash_flow_stat['equity_drawdown'] = capex_quat['equity_draw']
        cash_flow_stat['debt_drawdown'] = capex_quat['debt_draw']
        cash_flow_stat['wc_drawdown/repayment'] = recievables_power["wc_drawdown"]
        cash_flow_stat['lender_fees'] = lender_fee_quaterly['lender_fees']
        cash_flow_stat['refinancing_fees'] = debt_sch['refinancing_fee']
        cash_flow_stat['corporate_gua_fees'] = debt_sch['corporate_guar_fees']
        cash_flow_stat['principle_repayment'] = debt_sch['debt_repayment']
        cash_flow_stat['interest_repayment'] = debt_sch['interest_repay']
        cash_flow_stat['withholding_tax_on_interest'] = debt_sch['withholding_tax_on_interest']
        cash_flow_stat['interest_wc'] = recievables_power['interest_on_wc']
        cash_flow_stat['interest_income'] = dsra['interest_cash_dsra']
        cash_flow_stat['change_cash_dsra'] = -dsra['change_cash_dsra']
        cash_flow_stat['change_dsra_bgmargin'] = dsra['change_dsra_bg_margin']
        cash_flow_stat['dsra_bg_charges'] = dsra['dsra_bg_charges']

        cols_add_net_cash_senior_facility = ['cash_flow_oper', 'cash_flow_investing_capex', 'equity_drawdown',
                                             'debt_drawdown', 'wc_drawdown/repayment']
        cash_flow_stat['net_cash_senior_facility'] = cash_flow_stat[cols_add_net_cash_senior_facility].sum(axis=1) * \
                                                     flag['Operation Active Flag'][:quarters_count]

        # should be true but all are false
        numer = cash_flow_stat['net_cash_senior_facility'].values
        denom = debt_sch['principle_interest_repay'].values
        result = np.zeros_like(numer)
        mask_non_zero = denom != 0
        result[mask_non_zero] = numer[mask_non_zero] / denom[mask_non_zero]
        # cash_flow_stat['dscr_quat_lvl'] = np.where(result>10000, 0, result* flag['Operation Active Flag'][:160])
        cash_flow_stat['dscr_quat_lvl'] = np.where(result > 10000, 0, result * flag['Operation Active Flag'][
                                                                               :quarters_count])  #####changed as per flag operation year considered 25 years(160-->120)

        cash_retention = main_sheet.iloc[41, 3]
        cust_equity = main_sheet.iloc[40, 3]
        min_dscr = main_sheet.iloc[38, 3]
        min_debt_ety = main_sheet.iloc[39, 3]

        cash_flow_stat['opening_cash_bal'] = 0

        for i in range(len(cash_flow_stat)):

            if i == 0:
                cash_flow_stat.loc[i, 'opening_cash_bal'] = 0
                cash_flow_stat.loc[i, 'opening_reserve'] = 0
                cash_flow_stat.loc[i, 'flag_div_dist'] = 0

            else:

                cols_add_net_cash_flow_dist = ['opening_cash_bal', 'cash_flow_oper', 'cash_flow_investing_capex',
                                               'equity_drawdown', 'debt_drawdown', 'wc_drawdown/repayment',
                                               'interest_income', 'change_cash_dsra', 'change_dsra_bgmargin']
                cols_subtract_net_cash_flow_dist = ['lender_fees', 'refinancing_fees', 'corporate_gua_fees',
                                                    'principle_repayment', 'interest_repayment',
                                                    'withholding_tax_on_interest', 'interest_wc', 'dsra_bg_charges']
                # cash_flow_stat.loc[i-1, 'net_cash_flow_dist'] = (cash_flow_stat[cols_add_net_cash_flow_dist].loc[i-1].sum()  - cash_flow_stat[cols_subtract_net_cash_flow_dist].loc[i-1].sum()) * flag['Operation Active Flag'][:160][i-1]
                cash_flow_stat.loc[i - 1, 'net_cash_flow_dist'] = (cash_flow_stat[cols_add_net_cash_flow_dist].loc[
                                                                       i - 1].sum() -
                                                                   cash_flow_stat[cols_subtract_net_cash_flow_dist].loc[
                                                                       i - 1].sum()) * \
                                                                  flag['Operation Active Flag'][:quarters_count][
                                                                      i - 1]  #####changed as per flag operation year considered 25 years(160-->120)

                # equity_flag = cash_flow_stat['equity_drawdown'].sum() + cash_flow_stat['opening_reserve'][i-1]
                equity_flag = cash_flow_stat['equity_drawdown'].cumsum() + cash_flow_stat['opening_reserve'][
                    i - 1]  # new update taking cummulative sum than simple sum
                debt_flag = debt_sch['principal_outstanding'].values[i - 1]

                debt_equity_ratio = debt_flag / equity_flag

                condition = (cash_flow_stat.loc[i - 1, 'dscr_quat_lvl'] >= min_dscr) and (
                            debt_equity_ratio <= min_debt_ety)

                flag_division_dis = np.where(condition, 1, 0)

                cash_flow_stat.loc[i - 1, 'net_profit'] = profit_after_tax.loc[i - 1, 'PAT'] * \
                                                          flag['Operation Active Flag'][:quarters_count][i - 1]

                dividend = (max(min(cash_flow_stat.loc[i - 1, 'net_profit'],
                                    cash_flow_stat.loc[i - 1, 'opening_reserve'],
                                    cash_flow_stat.loc[i - 1, 'net_cash_flow_dist'] * (1 - cash_retention)), 0))
                new_condition = (cash_flow_stat["qtr_end_dt"] > pd.to_datetime(refinancing_fee_applicable_date)).astype(
                    int)
                cash_flow_stat["new_condition"] = new_condition
                # cash_flow_stat["final"] = flag_division_dis *flag['Principal Payment Flag'][:160].astype(float) * flag["Operation Active Flag"][:160].astype(float) *  cash_flow_stat["new_condition"]
                cash_flow_stat["final"] = flag_division_dis * flag['Principal Payment Flag'][:quarters_count].astype(
                    float) * flag["Operation Active Flag"][:quarters_count].astype(float) * cash_flow_stat[
                                              "new_condition"]  #####changed as per flag operation year considered 25 years(160-->120)

                # cash_flow_stat.loc[i-1, 'dividend'] = dividend * cash_flow_stat['flag_div_dist'].iloc[i-1] * flag['Principal Payment Flag'][:160].iloc[i-1] * flag['Operation Active Flag'][:160][i-1]  * cash_flow_stat["new_condition"].astype(float)
                cash_flow_stat.loc[i - 1, 'dividend'] = dividend * cash_flow_stat["final"].iloc[i - 1]
                # cash_flow_stat.loc[i-1, 'closing_reserve'] = (cash_flow_stat.loc[i-1, 'opening_reserve'] + cash_flow_stat.loc[i-1, 'net_profit'] - cash_flow_stat.loc[i-1, 'dividend'])* flag['Operation Active Flag'][:160][i-1]
                cash_flow_stat.loc[i - 1, 'closing_reserve'] = (cash_flow_stat.loc[i - 1, 'opening_reserve'] +
                                                                cash_flow_stat.loc[i - 1, 'net_profit'] -
                                                                cash_flow_stat.loc[i - 1, 'dividend']) * \
                                                               flag['Operation Active Flag'][:quarters_count][
                                                                   i - 1]  #####changed as per flag operation year considered 25 years(160-->120)

                cash_flow_stat.loc[i, 'opening_reserve'] = cash_flow_stat.loc[i - 1, 'closing_reserve'] * \
                                                           flag['Operation Active Flag'][:quarters_count][
                                                               i - 1]  #####changed as per flag operation year considered 25 years(160-->120)
                cash_flow_stat.loc[i - 1, 'cash_flow_financing'] = (
                            cash_flow_stat.loc[i - 1, 'equity_drawdown'] + cash_flow_stat.loc[i - 1, 'debt_drawdown'] +
                            cash_flow_stat.loc[i - 1, 'wc_drawdown/repayment'] - cash_flow_stat.loc[
                                i - 1, 'lender_fees'] - cash_flow_stat.loc[i - 1, 'refinancing_fees'] -
                            cash_flow_stat.loc[i - 1, 'corporate_gua_fees'] - cash_flow_stat.loc[
                                i - 1, 'principle_repayment'] - cash_flow_stat.loc[i - 1, 'interest_repayment'] -
                            cash_flow_stat.loc[i - 1, 'withholding_tax_on_interest'] - cash_flow_stat.loc[
                                i - 1, 'interest_wc'] + cash_flow_stat.loc[i - 1, 'interest_income'] +
                            cash_flow_stat.loc[i - 1, 'change_cash_dsra'] + cash_flow_stat.loc[
                                i - 1, 'change_dsra_bgmargin'] - cash_flow_stat.loc[i - 1, 'dsra_bg_charges'] -
                            cash_flow_stat.loc[i - 1, 'dividend'])
                cash_flow_stat.loc[i - 1, 'net_cash_inflow/outflow'] = (cash_flow_stat.loc[i - 1, 'cash_flow_oper'] +
                                                                        cash_flow_stat.loc[
                                                                            i - 1, 'cash_flow_investing_capex'] +
                                                                        cash_flow_stat.loc[
                                                                            i - 1, 'cash_flow_financing']) * \
                                                                       flag['Operation Active Flag'][:quarters_count][
                                                                           i - 1]
                cash_flow_stat.loc[i - 1, 'cash_flow_end_period'] = (cash_flow_stat.loc[i - 1, 'opening_cash_bal'] +
                                                                     cash_flow_stat.loc[
                                                                         i - 1, 'net_cash_inflow/outflow']) * \
                                                                    flag['Operation Active Flag'][:quarters_count][
                                                                        i - 1]
                cash_flow_stat.loc[i, 'opening_cash_bal'] = cash_flow_stat.loc[i - 1, 'cash_flow_end_period'] * \
                                                            flag['Operation Active Flag'][:quarters_count][i]

        cash_flow_stat.fillna(0, inplace=True)

        cols_subtract_net_cash_debt_srvc = ['lender_fees', 'refinancing_fees', 'corporate_gua_fees',
                                            'principle_repayment', 'interest_repayment', 'withholding_tax_on_interest',
                                            'interest_wc']
        cols_add_net_cash_debt_srvc = ['opening_cash_bal', 'net_cash_senior_facility', 'interest_income']
        # cash_flow_stat['net_cash_debt_srvc'] = (cash_flow_stat[cols_add_net_cash_debt_srvc].sum(axis=1) - cash_flow_stat[cols_subtract_net_cash_debt_srvc].sum(axis=1)) * flag['Operation Active Flag'][:160]
        cash_flow_stat['net_cash_debt_srvc'] = (cash_flow_stat[cols_add_net_cash_debt_srvc].sum(axis=1) -
                                                cash_flow_stat[cols_subtract_net_cash_debt_srvc].sum(axis=1)) * flag[
                                                                                                                    'Operation Active Flag'][
                                                                                                                :quarters_count]  #####changed as per flag operation year considered 25 years(160-->120)

        columns_to_sum = cash_flow.drop(['year'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)
        column_sums

        columns_to_sum = cash_flow_stat.drop(['qtr_strt_dt', 'qtr_end_dt'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)
        # balance sheet
        # current asset
        current_asset = pd.DataFrame()

        current_asset['qtr_strt_dt'] = revenue_quat['quarter_start']
        current_asset['qtr_end_dt'] = revenue_quat["quarter_end"]

        # current_asset['month_start'] = flag['Quarter Start Date for WC'][:160]
        current_asset['cash_equi'] = cash_flow_stat['cash_flow_end_period']
        current_asset['trade_recievable'] = recievables_power['recivables_from_power'] + recievables_power[
            'recievable_sale_gcc']
        current_asset['advances'] = recievables_power['advance_opex']

        # non current asset
        current_asset['nca_dsra'] = dsra['cash_dsra_req'] + dsra['dsra_bg_margin']
        current_asset['gross_fixed'] = cash_flow_stat['cash_flow_investing_capex'].cumsum()
        current_asset['acc_depriciation'] = quarterly_depre['dep_for_period'].cumsum()
        current_asset['total_assets'] = current_asset['cash_equi'] + current_asset['trade_recievable'] + current_asset[
            'advances'] + current_asset['nca_dsra'] + (-current_asset['gross_fixed']) - current_asset[
                                            'acc_depriciation']

        # equity calculations
        current_asset['equity_shareholder_capital'] = cash_flow_stat[
            'equity_drawdown'].cumsum()  # new change - take cumm than simple

        # liabilities
        current_asset['wc_borrowings'] = cash_flow_stat[
            'wc_drawdown/repayment'].cumsum()  # take cumsum here also (new chnage )
        current_asset['long_term_borrowings'] = (cash_flow_stat['debt_drawdown'] - cash_flow_stat[
            'principle_repayment']).cumsum()  # take cumm here aslo (new change)
        # also subtract now as both were positive in python and we have to subtract it (new change) , earlier formula was to add

        current_asset['deff_tax_lia'] = final_quarterly_df['dtl_charged_pnl'].cumsum()
        current_asset['dividend_customer'] = cash_flow_stat['dividend'] * cust_equity
        current_asset.fillna(0, inplace=True)
        current_asset['reserve_surplus'] = cash_flow_stat['closing_reserve']
        current_asset['totl_sharehldr_ety_lia'] = current_asset['equity_shareholder_capital'] + current_asset[
            'wc_borrowings'] + current_asset['long_term_borrowings'] + current_asset['deff_tax_lia'] + current_asset[
                                                      'reserve_surplus']
        current_asset['total_assets'] == current_asset['totl_sharehldr_ety_lia']

        current_asset = current_asset.iloc[:117]  # take only upto 2052 last quarter as project duration is 25 uears

        columns_to_sum = current_asset.drop(['qtr_strt_dt', 'qtr_end_dt'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)
        column_sums

        envi_make = 3.3
        sany_make = 4
        turbine_cap_acc_make = {1: envi_make, 2: sany_make, 3: envi_make, 4: sany_make}

        button_wind2 = 4
        solar_terminal_value = 0
        wind1_terminal_value = ((1.4 * w1_cap) / turbine_cap_acc_make.get(button_wind1, 1)) * (
                    1 + 0.03) ** 25  ############********1 taken as default value to aviod zero division error
        wind2_terminal_value = ((1.4 * w1_cap) / turbine_cap_acc_make.get(button_wind2, 1)) * (1 + 0.03) ** 25
        total_terminal_value = solar_terminal_value + wind1_terminal_value + wind2_terminal_value
        total_terminal_value

        terminal_value_date = oper_end_date + pd.Timedelta(days=1)
        terminal_value_date

        current_asset["terminal_value"] = np.where(current_asset["qtr_strt_dt"] == terminal_value_date,
                                                   total_terminal_value, 0)

        # fcff
        fcff = pd.DataFrame()
        fcff['month_start'] = flag['Quarter Start Date for WC'][:quarters_count]
        fcff["month_end"] = flag['Quarter End Date for WC'][:quarters_count]
        # fcff['month_start'] = revenue_quat['quarter_start']
        # # fcff["month_end"] = revenue_quat["quarter_end"]
        fcff['EBITDA'] = ebitda['EBITDA']
        fcff['csr_expenses'] = csr_quat['csr_expenses']
        fcff['current_tax_quat'] = final_quarterly_df['current_tax_quat']
        fcff['tax_sheild_financing'] = cash_flow_stat['tax_sheild_financing']
        fcff['change_in_wc'] = recievables_power['change_in_wc']
        fcff["terminal_value"] = current_asset["terminal_value"]

        capex_monthlyy = capex_monthly.drop(columns=['level_0'], errors='ignore')
        capex_monthlyy = capex_monthlyy.reset_index()
        capex_monthlyy["month_end"] = flag["Month End Date flag"]

        # capex_monthly
        capex_fcff = pd.DataFrame(capex_monthlyy[::])
        capex_fcff = capex_fcff[capex_fcff['Month Start Date flag'] < oper_start_date]
        capex_fcff.rename(columns={'Month Start Date flag': 'month_start'}, inplace=True)
        fcff['month_start'] = pd.to_datetime(fcff['month_start'])
        fcff = fcff[fcff[
                        'month_start'] >= oper_start_date]  ##################### hardcode '2027-10-01 00:00:00' chnaged with oper_start_date

        fcff.reset_index(drop=True, inplace=True)
        final_fcff = pd.merge(capex_fcff, fcff, on='month_start', how='outer')  # combining construction and oepratioos
        final_fcff.fillna(0, inplace=True)
        final_fcff["month_end"] = final_fcff["month_end_x"].astype(str) + final_fcff["month_end_y"].astype(str)
        # final_fcff["month_end"] = pd.to_datetime(final_fcff["month_end"])   ############## COMMENTED OUT THGIS FOR DIFFERENT INNPUT FILE CHECK WITH DIFFERENCE CONSTR STRAT DATE
        final_fcff = final_fcff.drop(columns=["month_end_x", "month_end_y"], axis=1)
        final_fcff['FCFF'] = (final_fcff['EBITDA'] - final_fcff['csr_expenses']
                              - final_fcff['current_tax_quat']
                              - final_fcff['tax_sheild_financing']
                              - final_fcff['change_in_wc']
                              - final_fcff['capex_month']
                              + final_fcff['idc_quat'] + final_fcff["terminal_value"])

        columns_to_sum = final_fcff.drop(['month_start', 'month_end'], axis=1)
        column_sums = columns_to_sum.sum(axis=0)

        ### FCFE

        fcfe = pd.DataFrame()
        fcfe['month_start'] = flag['Quarter Start Date for WC'][:quarters_count]
        fcfe["month_end"] = flag['Quarter End Date for WC'][:quarters_count]
        fcfe['tax_sheild_financing'] = cash_flow_stat['tax_sheild_financing']
        # fcfe['idc_quat'] = capex_quat['idc_quat']
        fcfe['lender_fees'] = -cash_flow_stat['lender_fees']
        fcfe['refinancing_fees'] = -cash_flow_stat['refinancing_fees']
        fcfe['corporate_gua_fees'] = -cash_flow_stat['corporate_gua_fees']
        fcfe['dsra_bg_charges'] = -cash_flow_stat['dsra_bg_charges']
        fcfe['interest_wc'] = -cash_flow_stat['interest_wc']
        fcfe['interest_senior_facilites'] = -cash_flow_stat['interest_repayment']
        fcfe['withholding_tax_on_interest'] = cash_flow_stat['withholding_tax_on_interest']
        fcfe['interest_income'] = cash_flow_stat['interest_income']
        fcfe['principle_repayment'] = -cash_flow_stat['principle_repayment']
        fcfe['wc_drawdown/repayment'] = cash_flow_stat['wc_drawdown/repayment']
        fcfe['change_cash_dsra'] = cash_flow_stat['change_cash_dsra']
        quarter_constr = int(main_sheet.iloc[10, 3] / 3)
        fcfe = fcfe[quarter_constr:]
        final_fcfe = pd.concat([capex_fcff, fcfe], axis=0, ignore_index=False)
        final_fcfe.fillna(0, inplace=True)
        final_fcfe = final_fcfe.reset_index(drop=True)
        final_fcfe['month_start'] = pd.to_datetime(final_fcfe['month_start'])
        final_fcfe['FCFF'] = final_fcff['FCFF']

        final_fcfe['FCFE'] = (
                    final_fcfe['FCFF'] + final_fcfe['tax_sheild_financing'] - final_fcff['idc_quat'] - final_fcfe[
                'withholding_tax_on_interest']
                    + final_fcfe['lender_fees'] + final_fcfe['refinancing_fees']
                    + final_fcfe['corporate_gua_fees'] + final_fcfe['dsra_bg_charges']
                    + final_fcfe['interest_wc'] + final_fcfe['interest_senior_facilites']
                    + final_fcfe['interest_income'] + final_fcfe['debt_draw']
                    + final_fcfe['principle_repayment'] + final_fcfe['wc_drawdown/repayment']
                    + final_fcfe['change_cash_dsra'])

        # final_fcfe['FCFE'] = pd.to_numeric(final_fcfe['FCFE'], errors='coerce')
        final_fcfe["month_end"] = pd.to_datetime(final_fcfe["month_end"])
        dates = pd.to_datetime(final_fcfe["month_start"] + (final_fcfe["month_end"] - final_fcfe["month_start"]) / 2)
        amounts = final_fcfe['FCFE']
        project_irr = xirr(pd.DataFrame({"dates": dates, "amounts": amounts})) * 100
        return project_irr - target_irr

    try:
        lcoe_value_hit_12 = brentq(fm, 4, 10)
        print(f"LCOE value where IRR first hits 12%: {lcoe_value_hit_12}")
    except ValueError:
        print("No LCOE value found where IRR hits 12%")
        lcoe_value_hit_12 = None

    # print("Project IRR is ", target_irr, "for ", lcoe_value_hit_12)

    # returning significant values
    # project_irr = (target_irr + fm(lcoe_value_hit_12))
    iex_pur = daily_gen['iex_pur'].sum()
    iex_pur = (iex_pur / (bid_cap * 8760))
    iex_sale = daily_gen["iex_sale"].sum()
    iex_sale = (iex_sale / (bid_cap * 8760))
    resultant_supply = daily_gen['total_supply'].sum()
    cuf = resultant_supply / (bid_cap * 8760)

    return lcoe_value_hit_12, target_irr, iex_pur, iex_sale, cuf


lcoe_value_hit_12 = upd_fm_gh2_nh3(s_cap, w1_cap, w2_cap, btry_cap, elz_capacity, GHS_capacity)

dt = financial_year_dates(operation_end_date + pd.DateOffset(years=1))[0]
Timestamp('2053-04-01 00:00:00')
