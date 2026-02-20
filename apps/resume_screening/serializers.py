"""
Serializers for resume screening API.
"""
from rest_framework import serializers


class ResumeUploadSerializer(serializers.Serializer):
    """Serializer for resume upload response."""
    
    id = serializers.UUIDField(read_only=True)
    filename = serializers.CharField(read_only=True)
    file_path = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class ResumeDetailSerializer(serializers.Serializer):
    """Serializer for resume detail response."""
    
    id = serializers.UUIDField(read_only=True)
    filename = serializers.CharField(read_only=True)
    file_path = serializers.CharField(read_only=True)
    raw_text = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
