from rest_framework import serializers
from .models import *


class ProjectDeatailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDetail
        exclude = ['project_id', 'created_at']

    def create(self, validated_data):
        instance = self.Meta.objects.create(**validated_data)
        return instance


class InputParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputParameters
        exclude = ['processed']

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class Solar_AssumptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar_Assumptions
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class Wind_AssumptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wind_Assumptions
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class Battery_AssumptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Battery_Assumptions
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class Psp_AssumptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Psp_Assumptions
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class Plant_ShutdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant_Shutdown
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class Operational_InputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant_Shutdown
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class Nh3_H2_InputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nh3_H2_Inputs
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class ElectrolyzerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electrolyzer
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class ConstructionCostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionCosting
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class OperationalCostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalCosting
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class NH3_PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = NH3_Plant
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class SolarProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolarProfile
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class WindProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindProfile
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class OtherAttributeOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherAttributeOutput
        exclude = ['id', 'version', "created_at"]

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class SolarOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolarOutput
        exclude = ['id', 'otherattribute']

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class WindOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindOutput
        exclude = ['id', 'otherattribute']

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class ProjectAssumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAssumption
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class Solar_ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar_Profile
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance


class Wind_ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wind_Profile
        fields = '__all__'

        def create(self, validated_data):
            instance = self.Meta.model.objects.create(**validated_data)
            return instance