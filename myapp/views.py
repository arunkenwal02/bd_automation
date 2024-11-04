from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status, generics
import sys
from .bd_portal import *
from multiprocessing import Process, Manager


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
            missing_fields = [field for field in required_fields if field not in request.data]

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
                    print(project_id)
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
                    InputParameters.objects.filter(id=project_id).update(processed=1)
                    serializer = self.get_serializer(existing_data)

                    return Response({
                        'status': 'Success',
                        'message': 'existing excel data inserted successfully',
                        'data': serializer.data}, status=status.HTTP_201_CREATED)

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
            InputParameters.objects.filter(id=project_id).update(processed=1)
            serializer = self.get_serializer(create_param)
            return Response({
                'status': 'Success',
                'message': 'data inserted successfully',
                'data': serializer.data}, status=status.HTTP_201_CREATED)

    except Exception as err:
        print({"error": f"{type(err).__name__} was raised: {err} Error on line " + format(
            sys.exc_info()[-1].tb_lineno)})


class DelApi(generics.GenericAPIView):
    def delete(self, request):
        instance = ProjectDetail.objects.get(project_id=2)
        instance.delete()
        print('lll')
        return Response({"message": "data deleted"})
