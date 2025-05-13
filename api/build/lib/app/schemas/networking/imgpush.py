from pydantic import field_validator

from app.schemas.base import NetworkingBase


class ImgpushUploadResponse(NetworkingBase):
    filename: str

    @field_validator("filename")
    def validate_filename(cls, filename):  # noqa: N805
        if len(filename.split(".")) != 2:
            ValueError("Filename must have a be of the form 'xxx.jpeg'.")
        return filename

    @property
    def name(self):
        return self.filename.split(".")[0]

    @property
    def extension(self):
        return self.filename.split(".")[1]
