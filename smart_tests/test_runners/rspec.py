from . import smart_tests

subset = smart_tests.CommonSubsetImpls(__name__).scan_files('*_spec.rb')
record_tests = smart_tests.CommonRecordTestImpls(__name__).report_files()
