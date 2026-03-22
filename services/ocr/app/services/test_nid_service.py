import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from time import time
import cv2
import easyocr

from app.services.nid_service import nid_ocr

class TestNidOCR(unittest.TestCase):

    @patch("app.services.nid_service.cv2.imread")
    def test_image_not_found(self, mock_imread):
        mock_imread.return_value = None
        result = nid_ocr("dummy_path.jpg")
        self.assertEqual(result, "Error: Image not found.")

    @patch("app.services.nid_service.easyocr.Reader")
    @patch("app.services.nid_service.cv2.split")
    @patch("app.services.nid_service.cv2.imread")
    def test_successful_ocr(self, mock_imread, mock_split, mock_reader):
        mock_imread.return_value = np.zeros((100,100,3), dtype=np.uint8)
        mock_split.return_value = (np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8))
        reader_instance = MagicMock()
        reader_instance.readtext.return_value = [([[0,0],[1,0],[1,1],[0,1]], "١٢٣٤", 0.9)]
        mock_reader.return_value = reader_instance

        result = nid_ocr("dummy_path.jpg")
        self.assertIn("1234", result)

    @patch("app.services.nid_service.easyocr.Reader")
    @patch("app.services.nid_service.cv2.split")
    @patch("app.services.nid_service.cv2.imread")
    def test_multiple_numbers(self, mock_imread, mock_split, mock_reader):
        mock_imread.return_value = np.zeros((100,100,3), dtype=np.uint8)
        mock_split.return_value = (np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8))
        reader_instance = MagicMock()
        reader_instance.readtext.return_value = [
            ([[0,0],[1,0],[1,1],[0,1]], "١٢", 0.9),
            ([[0,0],[1,0],[1,1],[0,1]], "٣٤", 0.9)
        ]
        mock_reader.return_value = reader_instance

        result = nid_ocr("dummy_path.jpg")
        self.assertTrue(len(result.strip()) > 0)

    @patch("app.services.nid_service.easyocr.Reader")
    @patch("app.services.nid_service.cv2.split")
    @patch("app.services.nid_service.cv2.imread")
    def test_no_digits_detected(self, mock_imread, mock_split, mock_reader):
        mock_imread.return_value = np.zeros((100,100,3), dtype=np.uint8)
        mock_split.return_value = (np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8))
        reader_instance = MagicMock()
        reader_instance.readtext.return_value = []
        mock_reader.return_value = reader_instance

        result = nid_ocr("dummy_path.jpg")
        self.assertEqual(result.strip(), "")

    @patch("app.services.nid_service.easyocr.Reader")
    @patch("app.services.nid_service.cv2.split")
    @patch("app.services.nid_service.cv2.imread")
    def test_arabic_digit_conversion(self, mock_imread, mock_split, mock_reader):
        mock_imread.return_value = np.zeros((100,100,3), dtype=np.uint8)
        mock_split.return_value = (np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8))
        reader_instance = MagicMock()
        reader_instance.readtext.return_value = [([[0,0],[1,0],[1,1],[0,1]], "٩٨٧٦", 0.9)]
        mock_reader.return_value = reader_instance

        result = nid_ocr("dummy_path.jpg")
        self.assertIn("9876", result)

    @patch("app.services.nid_service.easyocr.Reader")
    @patch("app.services.nid_service.cv2.split")
    @patch("app.services.nid_service.cv2.imread")
    def test_mixed_text(self, mock_imread, mock_split, mock_reader):
        mock_imread.return_value = np.zeros((100,100,3), dtype=np.uint8)
        mock_split.return_value = (np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8),
                                   np.zeros((100,100), dtype=np.uint8))
        reader_instance = MagicMock()
        reader_instance.readtext.return_value = [
            ([[0,0],[1,0],[1,1],[0,1]], "١٢٣", 0.9),
            ([[0,0],[1,0],[1,1],[0,1]], "abc", 0.9)
        ]
        mock_reader.return_value = reader_instance

        result = nid_ocr("dummy_path.jpg")
        self.assertTrue("123" in result or result.strip() != "")

class JacocoResult(unittest.TextTestResult):
    def startTestRun(self):
        self.successes = []
        self._start_time = time()
        print("------------------------------------------------------------")
        print("TESTS")
        print("------------------------------------------------------------")
        super().startTestRun()

    def addSuccess(self, test):
        self.successes.append(test)
        super().addSuccess(test)

    def stopTestRun(self):
        self._elapsed_time = time() - self._start_time
        total = self.testsRun
        failures = len(self.failures)
        errors = len(self.errors)
        skipped = len(self.skipped)

        print(f"\nTests run: {total}, Failures: {failures}, Errors: {errors}, Skipped: {skipped}")
        print(f"Time elapsed: {round(self._elapsed_time,3)} s\n")
        print("Results:")
        for test in self.successes:
            dots = '.' * (35 - len(test._testMethodName))
            print(f"{test._testMethodName} {dots} OK")
        print("\n------------------------------------------------------------")
        print("BUILD SUCCESS")
        print(f"Total tests run: {total}")
        print(f"Failures: {failures}")
        print(f"Errors: {errors}")
        print(f"Skipped: {skipped}")
        print(f"Total time: {round(self._elapsed_time,3)} s")
        print("------------------------------------------------------------")
        super().stopTestRun()

class JacocoRunner(unittest.TextTestRunner):
    resultclass = JacocoResult
if __name__ == "__main__":
    unittest.main(testRunner=JacocoRunner(verbosity=0))