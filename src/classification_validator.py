# src/classification_validator.py
"""
Safety validation for classifications to prevent misclassification and misinformation.
Added this after realizing we needed better validation - had some issues with low confidence cases.
"""

from typing import Dict, List, Optional, Tuple


class ClassificationValidator:
    """
    Validates classifications to ensure accuracy and prevent errors.
    """
    
    # Minimum confidence thresholds
    MIN_CONFIDENCE_HIGH = 0.80
    MIN_CONFIDENCE_MEDIUM = 0.60
    MIN_CONFIDENCE_LOW = 0.40
    
    # Valid OWASP 2025 categories
    VALID_OWASP_2025_CATEGORIES = {
        "broken_access_control",
        "cryptographic_failures",
        "injection",
        "insecure_design",
        "security_misconfiguration",
        "vulnerable_components",
        "authentication_failures",
        "broken_authentication",
        "software_and_data_integrity_failures",
        "server_side_request_forgery",
        "ssrf",
        "other"
    }
    
    @staticmethod
    def validate_classification(classification: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a classification result.
        
        Returns:
            (is_valid, warnings)
        """
        warnings = []
        
        # Check required fields
        if "fine_label" not in classification:
            return False, ["Missing required field: fine_label"]
        
        if "confidence" not in classification:
            return False, ["Missing required field: confidence"]
        
        fine_label = classification.get("fine_label", "").lower().strip()
        confidence = float(classification.get("confidence", 0.0))
        
        # Validate label is a known OWASP category
        if fine_label not in ClassificationValidator.VALID_OWASP_2025_CATEGORIES:
            warnings.append(f"Unknown category: {fine_label}. May be misclassified.")
        
        # Validate confidence is reasonable
        if confidence < ClassificationValidator.MIN_CONFIDENCE_LOW:
            warnings.append(f"Very low confidence ({confidence:.0%}). High risk of misclassification.")
            return False, warnings
        
        if confidence < ClassificationValidator.MIN_CONFIDENCE_MEDIUM:
            warnings.append(f"Low confidence ({confidence:.0%}). Please verify classification.")
        
        if confidence < ClassificationValidator.MIN_CONFIDENCE_HIGH:
            warnings.append(f"Medium confidence ({confidence:.0%}). Review recommended before action.")
        
        # Check for suspicious patterns
        rationale = classification.get("rationale", "").lower()
        if "uncertain" in rationale or "unsure" in rationale or "might be" in rationale:
            warnings.append("Rationale indicates uncertainty. Verify classification.")
        
        # Check if label matches incident_type
        incident_type = classification.get("incident_type", "").lower()
        if incident_type and fine_label not in incident_type.lower():
            warnings.append("Label mismatch between fine_label and incident_type. Verify consistency.")
        
        return True, warnings
    
    @staticmethod
    def should_proceed_to_phase2(classification: Dict, min_confidence: float = 0.70) -> Tuple[bool, str]:
        """
        Determine if classification is safe to proceed to Phase-2.
        
        Returns:
            (should_proceed, reason)
        """
        is_valid, warnings = ClassificationValidator.validate_classification(classification)
        
        if not is_valid:
            return False, "Classification validation failed. " + "; ".join(warnings)
        
        confidence = float(classification.get("confidence", 0.0))
        
        if confidence < min_confidence:
            return False, f"Confidence too low ({confidence:.0%} < {min_confidence:.0%}). Need more information."
        
        if warnings:
            # Has warnings but might be okay - return with warning
            return True, "Proceeding with warnings: " + "; ".join(warnings)
        
        return True, "Classification validated successfully."
    
    @staticmethod
    def get_safety_disclaimer(classification: Dict) -> str:
        """
        Generate appropriate safety disclaimer based on classification confidence.
        """
        confidence = float(classification.get("confidence", 0.0))
        
        if confidence >= 0.90:
            return "✅ High confidence classification. Still recommend manual verification."
        elif confidence >= 0.80:
            return "⚠️ Good confidence, but please verify this classification matches your situation."
        elif confidence >= 0.65:
            return "⚠️ Medium confidence. Review recommended before taking action."
        else:
            return "⚠️ Low confidence. High risk of misclassification. Please provide more details or verify manually."

