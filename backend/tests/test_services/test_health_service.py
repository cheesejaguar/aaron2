from app.services.health_service import bp_status


class TestBPStatus:
    def test_normal(self):
        assert bp_status(115, 75) == "normal"

    def test_normal_boundary(self):
        assert bp_status(119, 79) == "normal"

    def test_elevated(self):
        assert bp_status(125, 78) == "elevated"

    def test_elevated_boundary(self):
        assert bp_status(129, 79) == "elevated"

    def test_high_stage_1_systolic(self):
        assert bp_status(135, 78) == "high_stage_1"

    def test_high_stage_1_diastolic(self):
        assert bp_status(115, 85) == "high_stage_1"

    def test_high_stage_2_systolic(self):
        assert bp_status(145, 78) == "high_stage_2"

    def test_high_stage_2_diastolic(self):
        assert bp_status(115, 95) == "high_stage_2"

    def test_high_stage_2_both(self):
        assert bp_status(155, 100) == "high_stage_2"

    def test_crisis_systolic(self):
        assert bp_status(185, 75) == "crisis"

    def test_crisis_diastolic(self):
        assert bp_status(115, 125) == "crisis"
