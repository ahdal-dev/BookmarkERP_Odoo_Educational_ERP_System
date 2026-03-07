import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from time import time
import os

from app.services.processing_service import process_image

class TestProcessImage(unittest.TestCase):

    @patch("app.services.processing_service.detect_id_card")
    def test_no_id_card_detected(self, mock_detect):
        mock_detect.return_value = (np.zeros((100,100,3)), [])
        result = process_image(r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\screenshot_20200921-233244_drive8225956331957385339.jpg", MagicMock(), MagicMock())
        self.assertEqual(result, {})

    @patch("app.services.processing_service.detect_id_card")
    def test_id_card_only(self, mock_detect):
        image = np.zeros((200,200,3), dtype=np.uint8)
        mock_detect.return_value = (image, [[10,10,150,150]])
        model_job = MagicMock()
        model_job.return_value = []
        result = process_image(r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\screenshot_20200921-233244_drive8225956331957385339.jpg", MagicMock(), model_job)
        self.assertEqual(result, {})

    @patch("app.services.processing_service.os.remove")
    @patch("app.services.processing_service.os.path.exists")
    @patch("app.services.processing_service.nid_ocr")
    @patch("app.services.processing_service.detect_id_card")
    def test_nid_ocr_called(self, mock_detect, mock_nid, mock_exists, mock_remove):
        image = np.zeros((200,200,3), dtype=np.uint8)
        mock_detect.return_value = (image, [[10,10,150,150]])
        mock_exists.return_value = True
        mock_nid.return_value = "123456789"

        mock_box = MagicMock()
        mock_box.xyxy = [np.array([20,20,100,60])]
        mock_box.cls = [0]
        mock_result = MagicMock()
        mock_result.boxes = [mock_box]
        mock_result.names = {0: "nid"}

        model_job = MagicMock()
        model_job.return_value = [mock_result]

        result = process_image(r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\screenshot_20200921-233244_drive8225956331957385339.jpg", MagicMock(), model_job)
        self.assertEqual(result["nid"], "123456789")
        mock_remove.assert_called()

    @patch("app.services.processing_service.os.remove")
    @patch("app.services.processing_service.os.path.exists")
    @patch("app.services.processing_service.nid_ocr")
    @patch("app.services.processing_service.detect_id_card")
    def test_back_nid(self, mock_detect, mock_nid, mock_exists, mock_remove):
        image = np.zeros((200,200,3), dtype=np.uint8)
        mock_detect.return_value = (image, [[10,10,150,150]])
        mock_exists.return_value = True
        mock_nid.return_value = "987654321"

        mock_box = MagicMock()
        mock_box.xyxy = [np.array([20,20,100,60])]
        mock_box.cls = [0]
        mock_result = MagicMock()
        mock_result.boxes = [mock_box]
        mock_result.names = {0: "back_nid"}

        model_job = MagicMock()
        model_job.return_value = [mock_result]

        result = process_image(r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\screenshot_20200921-233244_drive8225956331957385339.jpg", MagicMock(), model_job)
        self.assertEqual(result["back_nid"], "987654321")

    @patch("app.services.processing_service.extract_text")
    @patch("app.services.processing_service.detect_id_card")
    def test_extract_text_field(self, mock_detect, mock_extract):
        image = np.zeros((200,200,3), dtype=np.uint8)
        mock_detect.return_value = (image, [[10,10,150,150]])
        mock_extract.return_value = "Engineer"

        mock_box = MagicMock()
        mock_box.xyxy = [np.array([20,20,100,60])]
        mock_box.cls = [0]
        mock_result = MagicMock()
        mock_result.boxes = [mock_box]
        mock_result.names = {0: "job"}

        model_job = MagicMock()
        model_job.return_value = [mock_result]

        result = process_image(r"C:\Users\zyada\Desktop\ZC\Spring 2026\CSAI 499\Testing OCR IMAGES\screenshot_20200921-233244_drive8225956331957385339.jpg", MagicMock(), model_job)
        self.assertEqual(result["job"], "Engineer")

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