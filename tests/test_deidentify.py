"""
Use Philter-lite to replace PHI with ***'s.
"""
from importlib.resources import files

import philter_lite as philter

config_path = files('philter_lite.configs').joinpath('philter_delta.toml')
filters = philter.load_filters(config_path)


def test_deidentify_basic():
    text = """
    Patient Name: Susanne Samuelson
    Age: 99 years
    MRN: 1234567
    SSN: 219-68-3947
    Reason for Exam: Screening (asymptomatic).

    Bilateral CC and MLO views were obtained. Three-dimensional digital breast
    tomosynthesis views using CC and MLO planes.
    """
    include_map, exclude_map, data_tracker = philter.detect_phi(text, patterns=filters)
    deidentified_text = philter.transform_text_asterisk(text, include_map)

    assert "Susanne Samuelson" not in deidentified_text
    assert "Age: 99 years" not in deidentified_text
    assert "MRN: 1234567" not in deidentified_text
    assert "SSN: 219-68-3947" not in deidentified_text


def test_deidentify_age_and_time_spans():
    text = """
    Patient Name: Chan Han
    Age: 99 years
    MRN: 1234-7654-8787

    Patient has undergone hormone replacement therapy for 10 years. Patient is 99 years old.
    """
    include_map, exclude_map, data_tracker = philter.detect_phi(text, patterns=filters)
    deidentified_text = philter.transform_text_asterisk(text, include_map)

    assert "Age: 99 years" not in deidentified_text
    assert "Patient is 99 years old" not in deidentified_text
    assert "for 10 years" in deidentified_text


def test_deidentify_email_address_phone():
    text = """
    Patient Name: Daniela Martinez
    Age: 53 years
    Medical Record: 12345-567STC

    Get rid of PHI like emails, for example daniela.martinez@mydomain.com. Also,
    this patient lives at 1497 Marigold Drive, Seattle, WA. Some innocent text here.
    
    Her phone number is 206-943-1112. Please call on that number after 11am.
    """
    include_map, exclude_map, data_tracker = philter.detect_phi(text, patterns=filters)
    deidentified_text = philter.transform_text_asterisk(text, include_map)

    assert "12345-567STC" not in deidentified_text
    assert "Daniela Martinez" not in deidentified_text
    assert "daniela.martinez@mydomain.com" not in deidentified_text
    assert "1497 Marigold Drive" not in deidentified_text
    assert "206-943-1112" not in deidentified_text
