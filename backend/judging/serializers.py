from rest_framework import serializers

from .models import JudgeAssignment, ProjectJudgeAssignment, Score


class JudgeAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = JudgeAssignment
        fields = "__all__"
        read_only_fields = ("assigned_at",)


class ProjectJudgeAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectJudgeAssignment
        fields = "__all__"
        read_only_fields = ("assigned_at",)


class ScoreSerializer(serializers.ModelSerializer):
    criterion_name = serializers.CharField(source="criterion.name", read_only=True)
    max_score = serializers.IntegerField(source="criterion.max_score", read_only=True)
    weight = serializers.FloatField(source="criterion.weight", read_only=True)

    class Meta:
        model = Score
        fields = (
            "id",
            "judge",
            "project",
            "criterion",
            "value",
            "comment",
            "criterion_name",
            "max_score",
            "weight",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ScoreUpsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ("project", "criterion", "value", "comment")

    def validate_value(self, value):
        if value is None:
            return 0
        if value < 0:
            return 0
        return value
