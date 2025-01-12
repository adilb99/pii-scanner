from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class Processor:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        # self.extractor = PiiExtractor()
    
    def process_file(self, file_path: str) -> dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Use Presidio for analysis
            analyzer_results = self.analyzer.analyze(
                text=text,
                language='en'
            )
            
            # Use PII-Extract as backup
            # pii_results = self.extractor.extract(text)
            
            return {
                "presidio_findings": [
                    {
                        "entity_type": finding.entity_type,
                        "start": finding.start,
                        "end": finding.end,
                        "score": finding.score
                    }
                    for finding in analyzer_results
                ],
                "pii_extract_findings": []
            }
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise 