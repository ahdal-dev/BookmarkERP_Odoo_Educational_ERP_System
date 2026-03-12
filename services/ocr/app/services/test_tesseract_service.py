import unittest
from unittest.mock import patch
import numpy as np
from time import time

from app.services.tesseract_service import extract_text

class TestExtractText(unittest.TestCase):

    @patch("app.services.tesseract_service.pytesseract.image_to_string")
    @patch("app.services.tesseract_service.cv2.cvtColor")
    @patch("app.services.tesseract_service.cv2.threshold")
    def test_extract_text_normal(self, mock_threshold, mock_cvtColor, mock_tesseract):
        image = np.zeros((100,100,3), dtype=np.uint8)
        bbox = [10,10,50,50]
        mock_cvtColor.return_value = np.zeros((40,40), dtype=np.uint8)
        mock_threshold.return_value = (0, np.zeros((40,40), dtype=np.uint8))
        mock_tesseract.return_value = "مرحبا"
        self.assertEqual(extract_text(image, bbox), "مرحبا")

    @patch("app.services.tesseract_service.pytesseract.image_to_string")
    @patch("app.services.tesseract_service.cv2.cvtColor")
    @patch("app.services.tesseract_service.cv2.threshold")
    def test_extract_text_empty(self, mock_threshold, mock_cvtColor, mock_tesseract):
        image = np.zeros((100,100,3), dtype=np.uint8)
        bbox = [0,0,50,50]
        mock_cvtColor.return_value = np.zeros((50,50), dtype=np.uint8)
        mock_threshold.return_value = (0, np.zeros((50,50), dtype=np.uint8))
        mock_tesseract.return_value = ""
        self.assertEqual(extract_text(image, bbox), "")

    @patch("app.services.tesseract_service.pytesseract.image_to_string")
    @patch("app.services.tesseract_service.cv2.cvtColor")
    @patch("app.services.tesseract_service.cv2.threshold")
    def test_extract_text_different_bbox(self, mock_threshold, mock_cvtColor, mock_tesseract):
        image = np.zeros((200,200,3), dtype=np.uint8)
        bbox = [20,30,120,130]
        mock_cvtColor.return_value = np.zeros((100,100), dtype=np.uint8)
        mock_threshold.return_value = (0, np.zeros((100,100), dtype=np.uint8))
        mock_tesseract.return_value = "اختبار"
        self.assertEqual(extract_text(image, bbox), "اختبار")

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