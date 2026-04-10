from rest_framework import serializers


class DynamicFieldsSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request:
            fields = request.query_params.get('fields')
            if fields:
                allowed = set(fields.split(','))
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)
