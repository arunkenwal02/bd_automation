from django.db import models
from django.db.models import Max


class ProjectDetail(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class InputParameters(models.Model):
    id = models.AutoField(primary_key=True)
    target_nh3_production_ktpa = models.IntegerField(null=False, blank=False)
    max_iex_sale_perc = models.FloatField()
    max_ci_kg_CO2_kg_H2 = models.FloatField()
    max_ci_t_CO2_t_NH3 = models.FloatField()
    number_of_solar_sites = models.PositiveIntegerField()
    number_of_wind_sites = models.PositiveIntegerField()
    excel_file = models.CharField(max_length=100)
    version = models.PositiveIntegerField()
    project = models.ForeignKey(ProjectDetail, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        last_version = InputParameters.objects.filter(project=self.project).aggregate(Max('version'))[
                           'version__max'] or 0

        self.version = last_version + 1

        super().save()


class Solar_Assumptions(models.Model):
    id = models.AutoField(primary_key=True)
    solar_ehv_line_loss = models.FloatField()
    solar_plant_availability = models.FloatField()
    solar_grid_availability = models.FloatField()
    ctu_loss = models.FloatField()
    stu_loss = models.FloatField()
    loss_at_load_end = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class Wind_Assumptions(models.Model):
    id = models.AutoField(primary_key=True)
    ctu_loss = models.FloatField()
    stu_loss = models.FloatField()
    loss_at_load_end = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class Battery_Assumptions(models.Model):
    id = models.AutoField(primary_key=True)
    battery_capacity_power_rating = models.FloatField()
    battery_energy_rating = models.FloatField()
    roundtrip_loss_total = models.FloatField()
    roundtrip_efficiency_charging_leg = models.FloatField()
    roundtrip_efficiency_discharging_leg = models.FloatField()
    battery_discharge_depth = models.FloatField()
    battery_other_losses = models.FloatField()
    usable_battery_energy_rating = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class Psp_Assumptions(models.Model):
    id = models.AutoField(primary_key=True)
    psp_turbine_capacity_power_rating = models.FloatField()
    psp_energy_rating = models.FloatField()
    roundtrip_efficiency_charging_leg = models.FloatField()
    roundtrip_efficiency_discharging_leg = models.FloatField()
    pump_capacity = models.FloatField()
    incident_power_threshold_perc_charging = models.FloatField()
    incident_power_threshold_mw_charging = models.FloatField()
    incident_power_threshold_perc_discharging = models.FloatField()
    incident_power_threshold_mw_discharging = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class Plant_Shutdown(models.Model):
    id = models.AutoField(primary_key=True)
    no_of_days = models.IntegerField()
    month_of_shutdown = models.IntegerField()
    shutdown_from_day_of_month = models.IntegerField()
    shutdown_till_day_of_month = models.IntegerField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class Operational_Inputs(models.Model):
    id = models.AutoField(primary_key=True)
    elz_min_turndown = models.FloatField()
    elz_availability = models.FloatField()
    nh3_plant_availability = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class Nh3_H2_Inputs(models.Model):
    id = models.AutoField(primary_key=True)
    nh3_h2_multiplier = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class Electrolyzer(models.Model):
    id = models.AutoField(primary_key=True)
    lower_end_range_elz_loading = models.FloatField()
    specific_power_actual_generation_kwh_per_kg_h2 = models.FloatField()
    ac_dc_conversion_losses_perc = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class ConstructionCosting(models.Model):
    id = models.AutoField(primary_key=True)
    capex = models.CharField(max_length=100, blank=False, null=False)
    uom = models.CharField(max_length=100)
    value = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class OperationalCosting(models.Model):
    id = models.AutoField(primary_key=True)
    npv_of_opex = models.CharField(max_length=100, blank=False, null=False)
    uom = models.CharField(max_length=100)
    value = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class NH3_Plant(models.Model):
    id = models.AutoField(primary_key=True)
    nh3_tpd = models.FloatField()
    nh3_power_requirement_mw = models.FloatField()
    capex_usd_mn = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class SolarProfile(models.Model):
    id = models.AutoField(primary_key=True)
    day_of_year = models.IntegerField()
    time = models.IntegerField()
    unit = models.PositiveIntegerField(null=True)
    generation_value = models.FloatField()
    cuf = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class WindProfile(models.Model):
    id = models.AutoField(primary_key=True)
    day_of_year = models.IntegerField()
    time = models.IntegerField()
    unit = models.PositiveIntegerField(null=True)
    generation_value = models.FloatField()
    cuf = models.FloatField()
    mw_per_turbine = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)


class OtherAttributeOutput(models.Model):
    id = models.AutoField(primary_key=True)
    ghs_capacity_tonnes = models.FloatField()
    electrolyser_capacity_mw = models.FloatField()
    bid_capacity_mw = models.FloatField()
    nh3_production_tonnes = models.FloatField()
    carbon_intensity_h2 = models.FloatField()
    carbon_intensity_nh3 = models.FloatField()
    iex_sale_percentage = models.FloatField()
    version = models.ForeignKey(InputParameters, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)


class SolarOutput(models.Model):
    id = models.AutoField(primary_key=True)
    otherattribute = models.ForeignKey(OtherAttributeOutput, on_delete=models.CASCADE)
    solar_value = models.FloatField()


class WindOutput(models.Model):
    id = models.AutoField(primary_key=True)
    otherattribute = models.ForeignKey(OtherAttributeOutput, on_delete=models.CASCADE)
    wind_value = models.FloatField()

