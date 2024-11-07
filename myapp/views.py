from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status, generics
import sys
from .bd_portal import *
from multiprocessing import Process, Manager
import logging


class ExcelImport(generics.GenericAPIView):
    serializer_class = InputParameterSerializer
    queryset = InputParameters.objects.all()

    try:
        def post(self, request):
            manager = Manager()
            error_dict = manager.dict()
            required_fields = [
                'project_name',
                'target_nh3_production_ktpa',
                'max_iex_sale_perc',
                'max_ci_kg_CO2_kg_H2',
                'max_ci_t_CO2_t_NH3',
                'number_of_solar_sites',
                'number_of_wind_sites',
                'excel_file'
            ]
            missing_fields = [field for field in required_fields if
                              field not in request.data or not request.data[field]]

            if missing_fields:
                return Response({'error': f'Missing fields: {", ".join(missing_fields)}'},
                                status=status.HTTP_400_BAD_REQUEST)
            filepath = request.data['excel_file']
            if not request.data['excel_file'].name.endswith(('xlsx', 'xls')):
                return Response(
                    {"error": "Invalid file type. Please upload an Excel file with .xlsx or .xls extension."},
                    status=400)
            instance, creatproject = ProjectDetail.objects.get_or_create(project_name=request.data['project_name'])
            existing_data = InputParameters.objects.filter(
                target_nh3_production_ktpa=request.data['target_nh3_production_ktpa'],
                max_iex_sale_perc=request.data['max_iex_sale_perc'],
                max_ci_kg_CO2_kg_H2=request.data['max_ci_kg_CO2_kg_H2'],
                max_ci_t_CO2_t_NH3=request.data['max_ci_t_CO2_t_NH3'],
                number_of_solar_sites=request.data['number_of_solar_sites'],
                number_of_wind_sites=request.data['number_of_wind_sites'],
                excel_file=filepath.name,
                project=instance
            ).first()

            if existing_data:
                if existing_data.processed:
                    return Response({"message": "Data with the same parameters already exists."},
                                    status=status.HTTP_409_CONFLICT)
                else:
                    project_id = existing_data.id
                    processes = [
                        Process(target=project_assumption, args=(filepath, project_id, error_dict)),
                        Process(target=requrired_data, args=(filepath, project_id, error_dict)),
                        Process(target=solar_profile, args=(filepath, project_id, error_dict)),
                        Process(target=wind_profile, args=(filepath, project_id, error_dict))
                    ]

                    for p in processes:
                        p.start()
                    for p in processes:
                        p.join()
                    if error_dict:
                        error_messages = [f"{key}: {msg}" for key, msg in error_dict.items()]
                        print(error_messages)
                        return Response({"status": "error"})
                    create_output = OtherAttributeOutput.objects.create(
                        ghs_capacity_tonnes=random.uniform(0, 50),
                        electrolyser_capacity_mw=random.uniform(0, 50),
                        bid_capacity_mw=random.uniform(0, 50),
                        nh3_production_tonnes=random.uniform(0, 50),
                        carbon_intensity_h2=random.uniform(0, 50),
                        carbon_intensity_nh3=random.uniform(0, 50),
                        iex_sale_percentage=random.uniform(0, 50),
                        version_id=project_id
                    )
                    s_w_o_t = output(int(existing_data.number_of_solar_sites), int(existing_data.number_of_wind_sites), create_output.id)
                    InputParameters.objects.filter(id=project_id).update(processed=1)
                    # serializer = self.get_serializer(existing_data)

                    return Response({
                        'ghs_capacity_tonnes': create_output.ghs_capacity_tonnes,
                        'electrolyser_capacity_mw': create_output.electrolyser_capacity_mw,
                        'bid_capacity_mw': create_output.bid_capacity_mw,
                        'nh3_production_tonnes': create_output.nh3_production_tonnes,
                        'carbon_intensity_h2': create_output.carbon_intensity_h2,
                        'carbon_intensity_nh3': create_output.carbon_intensity_nh3,
                        'iex_sale_percentage': create_output.iex_sale_percentage,
                        'solar_value': s_w_o_t[0],
                        'wind_value': s_w_o_t[1]
                    }, status=status.HTTP_201_CREATED)

            create_param = InputParameters.objects.create(
                target_nh3_production_ktpa=request.data['target_nh3_production_ktpa'],
                max_iex_sale_perc=request.data['max_iex_sale_perc'],
                max_ci_kg_CO2_kg_H2=request.data['max_ci_kg_CO2_kg_H2'],
                max_ci_t_CO2_t_NH3=request.data['max_ci_t_CO2_t_NH3'],
                number_of_solar_sites=request.data['number_of_solar_sites'],
                number_of_wind_sites=request.data['number_of_wind_sites'],
                excel_file=filepath.name,
                project=instance
            )
            project_id = create_param.id
            processes = [
                Process(target=project_assumption, args=(filepath, project_id, error_dict)),
                Process(target=requrired_data, args=(filepath, project_id, error_dict)),
                Process(target=solar_profile, args=(filepath, project_id, error_dict)),
                Process(target=wind_profile, args=(filepath, project_id, error_dict))
            ]

            for p in processes:
                p.start()
            for p in processes:
                p.join()
            if error_dict:
                error_messages = [f"{key}: {msg}" for key, msg in error_dict.items()]
                print(error_messages)
                return Response({"status": "error"})
            create_output = OtherAttributeOutput.objects.create(
                ghs_capacity_tonnes=random.uniform(0, 50),
                electrolyser_capacity_mw=random.uniform(0, 50),
                bid_capacity_mw=random.uniform(0, 50),
                nh3_production_tonnes=random.uniform(0, 50),
                carbon_intensity_h2=random.uniform(0, 50),
                carbon_intensity_nh3=random.uniform(0, 50),
                iex_sale_percentage=random.uniform(0, 50),
                version_id=project_id
            )
            s_w_o_t = output(int(create_param.number_of_solar_sites), int(create_param.number_of_wind_sites),
                             create_output.id)
            InputParameters.objects.filter(id=project_id).update(processed=1)
            return Response({
                'ghs_capacity_tonnes': create_output.ghs_capacity_tonnes,
                'electrolyser_capacity_mw': create_output.electrolyser_capacity_mw,
                'bid_capacity_mw': create_output.bid_capacity_mw,
                'nh3_production_tonnes': create_output.nh3_production_tonnes,
                'carbon_intensity_h2': create_output.carbon_intensity_h2,
                'carbon_intensity_nh3': create_output.carbon_intensity_nh3,
                'iex_sale_percentage': create_output.iex_sale_percentage,
                'solar_value': s_w_o_t[0],
                'wind_value': s_w_o_t[1]
            }, status=status.HTTP_201_CREATED)

    except Exception as err:
        print({"error": f"{type(err).__name__} was raised: {err} Error on line " + format(
            sys.exc_info()[-1].tb_lineno)})


class RetrieveApi(generics.GenericAPIView):
    def post(self, request):
        required_field = ['project_id', 'version']
        missing_fields = [field for field in required_field if not request.data[field]]
        if missing_fields:
            return Response({'error': f"field missing {" ,".join(missing_fields)}"})
        project_id = request.data['project_id']
        version = request.data['version']
        try:
            version_query = InputParameters.objects.get(project_id=project_id, version=version).id
            query = OtherAttributeOutput.objects.filter(version_id=version_query).first()
            solar_value = SolarOutput.objects.filter(otherattribute_id=query.id).values_list('solar_value', flat=True)
            wind_value = WindOutput.objects.filter(otherattribute_id=query.id).values_list('wind_value', flat=True)
            print(solar_value)
            serializer = OtherAttributeOutputSerializer(query)
            dz_output = serializer.data
            dz_output['solar_value'] = list(solar_value)
            dz_output['wind_value'] = list(wind_value)

            return Response(dz_output, status=status.HTTP_200_OK)

        except InputParameters.DoesNotExist:
            return Response("Fields does not exist.")


logger = logging.getLogger(__name__)


class DelApi(generics.GenericAPIView):
    def delete(self, request):
        logger.info("Delete request received")
        deleted, _ = ProjectDetail.objects.filter(project_id=3).delete()
        if deleted:
            logger.info("Data deleted successfully")
            return Response({"message": "Data deleted"}, status=status.HTTP_200_OK)
        else:
            logger.info("No data found to delete")
            return Response({"message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
