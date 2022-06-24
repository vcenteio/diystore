from ...application.dto import DTO


def generate_json_presentation(output_dto: DTO):
    return output_dto.json()
