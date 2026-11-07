from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Certification, Experience


class CertificationSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Certification
        fields = [
            "id", "title", "description", "year", "is_highlight",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError(
                "Judul sertifikasi tidak boleh hanya berisi tag HTML"
            )
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError(
                "Deskripsi sertifikasi tidak boleh hanya berisi tag HTML"
            )
        return value

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    """Public experience fields; star information is computed for the session."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category", "thumbnail",
            "started_at", "ended_at", "is_ongoing", "star_count", "is_starred",
        ]
        read_only_fields = ["id", "started_at", "is_ongoing"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Judul pengalaman tidak boleh kosong setelah tag HTML dibersihkan.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Deskripsi pengalaman tidak boleh kosong setelah tag HTML dibersihkan.")
        return value

    def validate_thumbnail(self, value):
        if value and not value.lower().startswith(("https://", "http://")):
            raise serializers.ValidationError("URL gambar harus menggunakan HTTP atau HTTPS.")
        return value

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()
