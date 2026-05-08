from rapidfuzz import distance
import sys
import re
import string
from src.logging.logger import get_logger

logger = get_logger(__name__)

class MetricsEvaluator:
    def _normalize(self, text):
        """
        Global normalization for DocVQA evaluation:
        1. Convert to lowercase
        2. Remove all punctuation
        3. Remove extra whitespace
        4. Strip leading/trailing spaces
        """
        if not text:
            return ""
        text = str(text).lower()
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Remove extra whitespace
        text = " ".join(text.split())
        return text.strip()

    def calculate_anls(self, ground_truth_list, prediction, threshold=0.5):
        """
        Average Normalized Levenshtein Similarity (ANLS)
        """
        try:
            if not ground_truth_list:
                return 0.0
            
            p = self._normalize(prediction)
            best_score = 0
            
            for gt in ground_truth_list:
                gt_norm = self._normalize(gt)
                if not gt_norm and not p:
                    score = 1.0
                elif not gt_norm or not p:
                    score = 0.0
                else:
                    d = distance.Levenshtein.distance(p, gt_norm)
                    max_len = max(len(p), len(gt_norm))
                    nl = d / max_len
                    score = 1 - nl if nl < threshold else 0
                
                if score > best_score:
                    best_score = score
                    
            return best_score
        except Exception as e:
            logger.error(f"ANLS calculation failed: {str(e)}")
            return 0.0

    def calculate_em(self, ground_truth_list, prediction):
        """
        Exact Match (EM)
        """
        try:
            p = self._normalize(prediction)
            for gt in ground_truth_list:
                if p == self._normalize(gt):
                    return 1.0
            return 0.0
        except Exception as e:
            logger.error(f"EM calculation failed: {str(e)}")
            return 0.0

    def calculate_f1(self, ground_truth_list, prediction):
        """
        Word-level F1 Score
        """
        try:
            p_norm = self._normalize(prediction)
            p_tokens = p_norm.split()
            best_f1 = 0
            
            for gt in ground_truth_list:
                gt_norm = self._normalize(gt)
                gt_tokens = gt_norm.split()
                
                common = set(p_tokens) & set(gt_tokens)
                num_same = len(common)
                
                if len(p_tokens) == 0 or len(gt_tokens) == 0:
                    f1 = 1.0 if p_tokens == gt_tokens else 0.0
                else:
                    precision = num_same / len(p_tokens)
                    recall = num_same / len(gt_tokens)
                    if precision + recall == 0:
                        f1 = 0.0
                    else:
                        f1 = (2 * precision * recall) / (precision + recall)
                
                if f1 > best_f1:
                    best_f1 = f1
                    
            return best_f1
        except Exception as e:
            logger.error(f"F1 calculation failed: {str(e)}")
            return 0.0
