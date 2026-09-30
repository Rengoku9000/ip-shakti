"""
Test Suite: Query Classifier (Phase 2B.1)
Tests intent classification, topic categorization, botanical/entity extraction,
formulation categorization, evidentiary basis assertion, and low-confidence handling.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from classification import (
    query_classifier,
    entity_extractor,
    formulation_classifier,
    QueryIntent,
    Topic,
    FormulationType,
    FormulationBasis,
    EntityType,
    JurisdictionChoice
)


class TestQueryClassifier(unittest.TestCase):
    def test_patentability_intent_and_botanical_extraction(self):
        """Verify patentability query extracts botanical and traditional knowledge topic without legal advice"""
        query = "Can Ashwagandha-based traditional formulations be patented under the Indian Patents Act?"
        res = query_classifier.classify(query)

        self.assertEqual(res.intent, QueryIntent.PATENTABILITY.value)
        self.assertIn(Topic.PATENT_LAW.value, res.topics)
        self.assertIn(Topic.TRADITIONAL_KNOWLEDGE.value, res.topics)
        self.assertEqual(res.jurisdiction.primary, JurisdictionChoice.INDIA.value)
        self.assertGreater(res.confidence, 0.85)

        # Check entity extraction and Latin normalization
        botanicals = [e for e in res.entities if e.entity_type == EntityType.BOTANICAL.value]
        self.assertGreater(len(botanicals), 0)
        self.assertEqual(botanicals[0].name.lower(), "ashwagandha")
        self.assertEqual(botanicals[0].normalized_name, "Withania somnifera")

        # Crucial safety check: Must not output legal conclusions
        explanation_text = " ".join(res.explanation).lower()
        self.assertNotIn("not patentable", explanation_text)
        self.assertNotIn("patent granted", explanation_text)
        self.assertNotIn("legally invalid", explanation_text)

    def test_pharmacopoeia_intent(self):
        """Verify pharmacopoeia and quality standards inquiries"""
        query = "What standards apply to an Ayurvedic single drug under the Ayurvedic Pharmacopoeia of India?"
        res = query_classifier.classify(query)

        self.assertEqual(res.intent, QueryIntent.PHARMACOPOEIA.value)
        self.assertIn(Topic.PHARMACOPOEIA.value, res.topics)
        self.assertIn(Topic.AYURVEDA_REGULATION.value, res.topics)
        self.assertEqual(res.jurisdiction.primary, JurisdictionChoice.INDIA.value)

    def test_abs_biodiversity_intent(self):
        """Verify ABS regulatory queries under the Biological Diversity Act"""
        query = "What are the mandatory approval requirements under Section 6 of the Biological Diversity Act for filing a patent?"
        res = query_classifier.classify(query)

        self.assertEqual(res.intent, QueryIntent.ABS.value)
        self.assertIn(Topic.ABS.value, res.topics)
        self.assertIn(Topic.BIOLOGICAL_RESOURCES.value, res.topics)
        self.assertEqual(res.jurisdiction.primary, JurisdictionChoice.INDIA.value)

    def test_international_ip_treaty_intent(self):
        """Verify international treaty inquiries (WIPO GRATK)"""
        query = "What are the mandatory patent disclosure requirements for genetic resources under the WIPO GRATK Treaty?"
        res = query_classifier.classify(query)

        self.assertEqual(res.intent, QueryIntent.INTERNATIONAL_IP.value)
        self.assertIn(Topic.INTERNATIONAL_TREATY.value, res.topics)
        self.assertIn(Topic.PATENT_LAW.value, res.topics)
        self.assertEqual(res.jurisdiction.primary, JurisdictionChoice.INTERNATIONAL.value)

    def test_regulatory_compliance_intent(self):
        """Verify manufacturing licensing and GMP inquiries"""
        query = "What are the manufacturing licensing requirements for classical formulations under Schedule T of Drugs and Cosmetics Rules in India?"
        res = query_classifier.classify(query)

        self.assertEqual(res.intent, QueryIntent.REGULATORY_COMPLIANCE.value)
        self.assertIn(Topic.AYURVEDA_REGULATION.value, res.topics)
        self.assertIn(Topic.LICENSING.value, res.topics)
        self.assertIn(Topic.GMP.value, res.topics)

    def test_formulation_classification_categories(self):
        """Verify distinct formulation categories and basis assignment"""
        # 1. Single drug
        res_single = query_classifier.classify("What testing standards apply to Withania somnifera single ingredient in India?")
        self.assertEqual(res_single.formulation.type, FormulationType.SINGLE_DRUG.value)
        self.assertEqual(res_single.formulation.basis, FormulationBasis.USER_ASSERTED.value)

        # 2. Classical formulation
        res_classical = query_classifier.classify("Are classical Ayurvedic formulations like Chyawanprash patentable in India?")
        self.assertEqual(res_classical.formulation.type, FormulationType.CLASSICAL_FORMULATION.value)
        self.assertEqual(res_classical.formulation.basis, FormulationBasis.USER_ASSERTED.value)

        # 3. Proprietary formulation
        res_prop = query_classifier.classify("Can a proprietary Ayurvedic medicine be licensed without clinical trials in India?")
        self.assertEqual(res_prop.formulation.type, FormulationType.PROPRIETARY_FORMULATION.value)
        self.assertEqual(res_prop.formulation.basis, FormulationBasis.USER_ASSERTED.value)

        # 4. Polyherbal formulation
        res_poly = query_classifier.classify("Can a synergistic formulation containing Haldi and Ginger be patented in India?")
        self.assertEqual(res_poly.formulation.type, FormulationType.POLYHERBAL_FORMULATION.value)

        # 5. Non-formulation / administrative
        res_admin = query_classifier.classify("What are the penalties under the Biological Diversity Act in India?")
        self.assertEqual(res_admin.formulation.type, FormulationType.NOT_APPLICABLE.value)
        self.assertFalse(res_admin.formulation.detected)

    def test_ambiguity_ayurvedic_medicine(self):
        """
        Verify Section 24: 'Ayurvedic medicine' alone should NOT automatically
        become CLASSICAL_FORMULATION.
        """
        res = query_classifier.classify("Ayurvedic medicine")
        self.assertNotEqual(res.formulation.type, FormulationType.CLASSICAL_FORMULATION.value)
        self.assertIn(res.formulation.type, [FormulationType.AYURVEDIC_FORMULATION.value, FormulationType.UNKNOWN.value])

    def test_formulation_signal_ashwagandha_churna(self):
        """Verify Section 24: 'Ashwagandha churna' produces AYURVEDIC_FORMULATION with dosage signal"""
        res = query_classifier.classify("Ashwagandha churna")
        self.assertEqual(res.formulation.type, FormulationType.AYURVEDIC_FORMULATION.value)
        self.assertIn("churna", res.formulation.dosage_forms)

    def test_evidentiary_basis_integrity(self):
        """Verify classifier never emits LEGAL_FACT or unverified authoritative validity"""
        queries = [
            "Classical Chyawanprash formulation",
            "Proprietary herbal syrup",
            "Ashwagandha extract",
            "Triphala churna"
        ]
        for q in queries:
            res = query_classifier.classify(q)
            self.assertNotEqual(res.formulation.basis, "LEGAL_FACT")
            self.assertIn(res.formulation.basis, [FormulationBasis.USER_ASSERTED.value, FormulationBasis.UNKNOWN.value])

    def test_negative_and_out_of_domain_queries(self):
        """Verify Section 23: Pure chit-chat / out-of-domain queries return UNKNOWN with low confidence"""
        negative_queries = [
            "What do you think about this?",
            "Tell me something interesting.",
            "Is this good?",
            "Hello there",
            "How are you?"
        ]
        for q in negative_queries:
            res = query_classifier.classify(q)
            self.assertEqual(res.intent, QueryIntent.UNKNOWN.value, f"Failed for negative query: '{q}'")
            self.assertLessEqual(res.confidence, 0.30)

    def test_explanation_present(self):
        """Every classification must provide human-readable explanation entries"""
        res = query_classifier.classify("Can Curcuma longa be patented under Indian law?")
        self.assertIsInstance(res.explanation, list)
        self.assertGreater(len(res.explanation), 0)
        self.assertTrue(any("curcuma longa" in exp.lower() for exp in res.explanation))


if __name__ == "__main__":
    unittest.main()
