from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status, generics
import sys
from .bd_portal import *
from multiprocessing import Process, Manager
import logging
from django.shortcuts import render


class CreateProject(generics.GenericAPIView):
    serializer_class = ProjectDeatailSerializer

    def post(self, request):
        try:
            if not request.data['project_name']:
                return Response("Please enter a Project Name to proceed.",
                                status=status.HTTP_400_BAD_REQUEST)
            if ProjectDetail.objects.filter(project_name=request.data['project_name']).exists():
                return Response(f"{request.data['project_name']} already exists.",
                                status=status.HTTP_409_CONFLICT)
            project = ProjectDetail.objects.create(project_name=request.data['project_name'],
                                                   description=request.data['Description'])
            serializer = self.get_serializer(project)
            return Response({'message': f"Project {project.project_name} created successfully!",
                             'status': status.HTTP_201_CREATED,
                             'data': serializer.data})
        except Exception as err:
            return Response({"error": f"{type(err).__name__} was raised: {err} Error on line " + format(
                sys.exc_info()[-1].tb_lineno)})


class ExcelImport(generics.GenericAPIView):
    serializer_class = InputParameterSerializer
    queryset = InputParameters.objects.all()

    def get(self, request):
        project_list = list(ProjectDetail.objects.values_list('project_name', flat=True))
        return Response({'project_name': project_list}, status=status.HTTP_200_OK)

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
        try:
            existing_data = InputParameters.objects.filter(
                target_nh3_production_ktpa=request.data['target_nh3_production_ktpa'],
                max_iex_sale_perc=request.data['max_iex_sale_perc'],
                max_ci_kg_CO2_kg_H2=request.data['max_ci_kg_CO2_kg_H2'],
                max_ci_t_CO2_t_NH3=request.data['max_ci_t_CO2_t_NH3'],
                number_of_solar_sites=request.data['number_of_solar_sites'],
                number_of_wind_sites=request.data['number_of_wind_sites'],
                excel_file=filepath.name,
                project__project_name=request.data['project_name']
            ).first()

            if existing_data:
                if existing_data.processed:
                    return Response({"message": "Data with the same parameters already exists."},
                                    status=status.HTTP_409_CONFLICT)
                else:
                    project_id = existing_data.id
                    processes = [
                        # Process(target=project_assumption, args=(filepath, project_id, error_dict)),
                        Process(target=requrired_data, args=(filepath, project_id, error_dict)),
                        # Process(target=solar_profile, args=(filepath, project_id, error_dict)),
                        # Process(target=wind_profile, args=(filepath, project_id, error_dict)),
                        Process(target=project_assump, args=(filepath, project_id, error_dict)),
                        Process(target=solarprofile, args=(filepath, project_id, error_dict)),
                        Process(target=windprofile, args=(filepath, project_id, error_dict))

                    ]

                    for p in processes:
                        p.start()
                    for p in processes:
                        p.join()
                    if error_dict:
                        error_messages = [f"{key}: {msg}" for key, msg in error_dict.items()]
                        print(error_messages)
                        return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    df = main_func(project_id, error_dict)
                    create_output = OtherAttributeOutput.objects.create(
                        ghs_capacity_tonnes=round(random.uniform(0, 50), 2),
                        electrolyser_capacity_mw=round(random.uniform(0, 50), 2),
                        bid_capacity_mw=round(random.uniform(0, 50), 2),
                        nh3_production_tonnes=round(random.uniform(0, 50), 2),
                        carbon_intensity_h2=round(random.uniform(0, 50), 2),
                        carbon_intensity_nh3=round(random.uniform(0, 50), 2),
                        iex_sale_percentage=round(random.uniform(0, 50), 2),
                        version_id=project_id
                    )
                    s_w_o_t = output(int(existing_data.number_of_solar_sites), int(existing_data.number_of_wind_sites),
                                     create_output.id)
                    InputParameters.objects.filter(id=project_id).update(processed=1)
                    serializer = self.get_serializer(existing_data)
                    input_dict = serializer.data
                    output_dict = {
                        'ghs_capacity_tonnes': create_output.ghs_capacity_tonnes,
                        'electrolyser_capacity_mw': create_output.electrolyser_capacity_mw,
                        'bid_capacity_mw': create_output.bid_capacity_mw,
                        'nh3_production_tonnes': create_output.nh3_production_tonnes,
                        'carbon_intensity_h2': create_output.carbon_intensity_h2,
                        'carbon_intensity_nh3': create_output.carbon_intensity_nh3,
                        'iex_sale_percentage': create_output.iex_sale_percentage,
                        'solar_value': ", ".join(map(str, s_w_o_t[0])),
                        'wind_value': ", ".join(map(str, s_w_o_t[1]))
                    }
                    input_dict.update(output_dict)

                    return Response({'message': 'Output data stored successfully',
                                     'status': status.HTTP_201_CREATED,
                                     'data': input_dict})
            project = ProjectDetail.objects.get(project_name=request.data['project_name'])
            create_param = InputParameters.objects.create(
                target_nh3_production_ktpa=request.data['target_nh3_production_ktpa'],
                max_iex_sale_perc=request.data['max_iex_sale_perc'],
                max_ci_kg_CO2_kg_H2=request.data['max_ci_kg_CO2_kg_H2'],
                max_ci_t_CO2_t_NH3=request.data['max_ci_t_CO2_t_NH3'],
                number_of_solar_sites=request.data['number_of_solar_sites'],
                number_of_wind_sites=request.data['number_of_wind_sites'],
                excel_file=filepath.name,
                project=project
            )
            project_id = create_param.id
            processes = [
                # Process(target=project_assumption, args=(filepath, project_id, error_dict)),
                Process(target=requrired_data, args=(filepath, project_id, error_dict)),
                # Process(target=solar_profile, args=(filepath, project_id, error_dict)),
                # Process(target=wind_profile, args=(filepath, project_id, error_dict)),
                Process(target=project_assump, args=(filepath, project_id, error_dict)),
                Process(target=solarprofile, args=(filepath, project_id, error_dict)),
                Process(target=windprofile, args=(filepath, project_id, error_dict))
            ]

            for p in processes:
                p.start()
            for p in processes:
                p.join()
            if error_dict:
                error_messages = [f"{key}: {msg}" for key, msg in error_dict.items()]
                print(error_messages)
                return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            df = main_func(project_id, error_dict)
            create_output = OtherAttributeOutput.objects.create(
                ghs_capacity_tonnes=round(random.uniform(0, 50), 2),
                electrolyser_capacity_mw=round(random.uniform(0, 50), 2),
                bid_capacity_mw=round(random.uniform(0, 50), 2),
                nh3_production_tonnes=round(random.uniform(0, 50), 2),
                carbon_intensity_h2=round(random.uniform(0, 50), 2),
                carbon_intensity_nh3=round(random.uniform(0, 50), 2),
                iex_sale_percentage=round(random.uniform(0, 50), 2),
                version_id=project_id
            )
            s_w_o_t = output(int(create_param.number_of_solar_sites), int(create_param.number_of_wind_sites),
                             create_output.id)
            InputParameters.objects.filter(id=project_id).update(processed=1)
            serializer = self.get_serializer(create_param)
            input_dict = serializer.data
            output_dict = {
                'ghs_capacity_tonnes': create_output.ghs_capacity_tonnes,
                'electrolyser_capacity_mw': create_output.electrolyser_capacity_mw,
                'bid_capacity_mw': create_output.bid_capacity_mw,
                'nh3_production_tonnes': create_output.nh3_production_tonnes,
                'carbon_intensity_h2': create_output.carbon_intensity_h2,
                'carbon_intensity_nh3': create_output.carbon_intensity_nh3,
                'iex_sale_percentage': create_output.iex_sale_percentage,
                'solar_value': ", ".join(map(str, s_w_o_t[0])),
                'wind_value': ", ".join(map(str, s_w_o_t[1]))
            }
            input_dict.update(output_dict)
            return Response({'message': 'Output data stored successfully',
                             'status': status.HTTP_201_CREATED,
                             'data': input_dict})

        except ProjectDetail.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND,
                             'message': f"Project {request.data['project_name']} doesnot exists."},
                            status=status.HTTP_404_NOT_FOUND)


class Logs(generics.GenericAPIView):
    def get(self, request):
        queryset = ProjectDetail.objects.select_related(
            'inputparameters',
            'inputparameters__otherattributeoutput',
            'inputparameters__otherattributeoutput__solaroutput',
            'inputparameters__otherattributeoutput__windoutput'
        ).values(
            'project_name',
            'created_at',
            'inputparameters__target_nh3_production_ktpa',
            'inputparameters__max_iex_sale_perc',
            'inputparameters__max_ci_kg_CO2_kg_H2',
            'inputparameters__max_ci_t_CO2_t_NH3',
            'inputparameters__number_of_solar_sites',
            'inputparameters__number_of_wind_sites',
            'inputparameters__excel_file',
            'inputparameters__version',
            'inputparameters__otherattributeoutput__ghs_capacity_tonnes',
            'inputparameters__otherattributeoutput__electrolyser_capacity_mw',
            'inputparameters__otherattributeoutput__bid_capacity_mw',
            'inputparameters__otherattributeoutput__nh3_production_tonnes',
            'inputparameters__otherattributeoutput__carbon_intensity_h2',
            'inputparameters__otherattributeoutput__carbon_intensity_nh3',
            'inputparameters__otherattributeoutput__iex_sale_percentage',
            # 'inputparameters__otherattributeoutput__solaroutput__solar_value',
            # 'inputparameters__otherattributeoutput__windoutput__wind_value'  # Fixed reference to wind_value
        )

        records = []
        for record in queryset:
            if record['inputparameters__excel_file']:
                record['created_at'] = record['created_at'].date()
                records.append(record)

        return Response({'message': 'Logs Created Successfully',
                         'status': status.HTTP_201_CREATED,
                         'data': records})


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
            serializer = OtherAttributeOutputSerializer(query)
            dz_output = serializer.data
            dz_output['solar_value'] = list(solar_value)
            dz_output['wind_value'] = list(wind_value)

            return Response(dz_output, status=status.HTTP_200_OK)

        except InputParameters.DoesNotExist:
            return Response("Fields does not exist.")


logger = logging.getLogger(__name__)


class DelApi(generics.GenericAPIView):
    def delete(self, request, pk):
        logger.info("Delete request received")
        deleted, _ = ProjectDetail.objects.filter(project_id=pk).delete()
        if deleted:
            logger.info("Data deleted successfully")
            return Response({"message": "Data deleted"}, status=status.HTTP_200_OK)
        else:
            logger.info("No data found to delete")
            return Response({"message": "No data found"}, status=status.HTTP_404_NOT_FOUND)


class EmptyProjectTable(generics.GenericAPIView):
    def delete(self, request):
        logger.info("Delete request received")
        deleted = ProjectDetail.objects.all().delete()
        if deleted:
            logger.info("Data deleted successfully")
            return Response({"message": "Data deleted"}, status=status.HTTP_200_OK)
        else:
            logger.info("No data found to delete")
            return Response({"message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
