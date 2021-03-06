import scrapy

from covid19datascrapper.items import Patient

PATIENT_FIELDS = [
    'patient_number', 'date_announced', 'date_added', 'age', 'gender', 
    'residence_district', 'detected_city', 'detected_district', 'status',
    'transmission_type', 'notes', 'related_patients', 'known_cluster',
    'dhs_orig_patient_number', 'origin_state', 'origin_country',
    'district_patient_number', 'city_patient_number', 'released',
    'recovery_time', 'deceased', 'sources'
]


class PatientsSpider(scrapy.Spider):

    """This spider crawls through the Google docs spreadsheet at given URL and
    collects necessary information regarding covid 19 patients of Kerala during
    the 2020 epidemic."""

    name = 'kerala_patients'
    allowed_domains = ['https://docs.google.com']
    start_urls = ['https://docs.google.com/spreadsheets/d/e/2PACX-1vQU9eLCMT0XwWnoxV_LkyCkxMcPYO7z7ULdODoUFgcdzp48pgGpGrVZFXvraXYvUioVRsQgQDU_pQyI/pubhtml']
    custom_settings = {
        'FEED_EXPORT_FIELDS' : PATIENT_FIELDS 
    }

    def __init__(self, pr_start=1, pr_end=0, **kwargs):
        """
        pr_start: Number of patient row where to begin with.
        pr_end: Number of the row where to end scrapping.

        For both numbers, start counting rows with first row as 1 (not 0).
        """
        self.pr_start = int(pr_start)
        self.pr_end = int(pr_end)
        super().__init__(**kwargs)

    def parse(self, response):
        """Parse the spreadsheet and yield all requested patient rows."""
        # All rows in the first tab, "Patient Data".
        rows = response.xpath('//div[@id="0"] //tr[@style="height:20px;"]')
        start = max(self.pr_start - 1, 0)
        end = self.pr_end or len(rows)
        patients = rows[start : end]
        for patient in patients:
            item = Patient()
            cols = patient.css('td')
            # If Patient Num is empty, we have reached the end. Break the loop.
            if not (cols and cols[0].css('::text').get()):
                break
            # 3rd col is empty, so insert a corresponding empty field name too.
            # This is done to keep both field-name and col iterations in sync.
            patient_fields = PATIENT_FIELDS[:2] + [''] + PATIENT_FIELDS[2:]
            for index, field in enumerate(patient_fields):
                # Third col is empty. Skip it.
                if index == 2:
                    continue
                elif index >= len(cols):
                    break
                value = cols[index].css('::text').get(default='')
                # Some of the cols are given as Unspecified. Make them empty.
                item[field] = value.strip() if value != "Unspecified" else ''
            yield item
        else:
            print("Scrapped", len(patients), "/", len(rows), "patient rows.")
