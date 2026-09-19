import io


class FakeS3:
    """In-memory stand-in for the four boto3 calls landing uses."""

    def __init__(self, page_size: int = 1000) -> None:
        self.objects: dict[str, bytes] = {}
        self.put_order: list[str] = []
        self._page_size = page_size

    def put_object(self, **kwargs):
        self.objects[kwargs["Key"]] = kwargs["Body"]
        self.put_order.append(kwargs["Key"])

    def get_object(self, **kwargs):
        return {"Body": io.BytesIO(self.objects[kwargs["Key"]])}

    def list_objects_v2(self, **kwargs):
        keys = sorted(key for key in self.objects if key.startswith(kwargs["Prefix"]))
        start = int(kwargs.get("ContinuationToken", 0))
        page = keys[start : start + self._page_size]
        response = {"Contents": [{"Key": key} for key in page]}
        if start + self._page_size < len(keys):
            response["IsTruncated"] = True
            response["NextContinuationToken"] = str(start + self._page_size)
        return response

    def delete_objects(self, **kwargs):
        for item in kwargs["Delete"]["Objects"]:
            self.objects.pop(item["Key"], None)
