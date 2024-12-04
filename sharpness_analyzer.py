import cv2
import numpy as np
from typing import Dict


class SharpnessAnalyzer:
    """
    Implements various methods for analyzing image sharpness.
    All methods return normalized scores on a 1-100 scale.
    """

    @staticmethod
    def normalize_score(value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a score to a 1-100 scale using predetermined ranges for each method.

        Args:
            value: Raw score value
            min_val: Expected minimum value for this method
            max_val: Expected maximum value for this method

        Returns:
            Normalized score between 1 and 100
        """
        normalized = ((value - min_val) / (max_val - min_val)) * 99 + 1
        return np.clip(normalized, 1, 100)

    def laplacian_variance(self, image: np.ndarray) -> float:
        """
        Calculate normalized image sharpness using Laplacian variance method.
        Higher values indicate sharper edges.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        raw_score = laplacian.var()
        return self.normalize_score(raw_score, 0, 500)

    def sobel_gradient(self, image: np.ndarray) -> float:
        """
        Calculate normalized image sharpness using Sobel gradient method.
        Measures edge strength in both horizontal and vertical directions.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        raw_score = np.sqrt(sobelx ** 2 + sobely ** 2).mean()
        return self.normalize_score(raw_score, 0, 50)

    def tenengrad(self, image: np.ndarray) -> float:
        """
        Calculate normalized image sharpness using Tenengrad algorithm.
        Uses thresholded Sobel gradients for noise-resistant edge detection.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        tenengrad = np.sqrt(sobelx ** 2 + sobely ** 2)
        threshold = 0.1 * tenengrad.max()
        raw_score = np.mean(tenengrad[tenengrad > threshold])
        return self.normalize_score(raw_score, 0, 100)