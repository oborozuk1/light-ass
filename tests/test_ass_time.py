import pytest

from light_ass import AssTime


class TestAssTimeParse:
    def test_parse_simple(self):
        t = AssTime.parse("0:00:00.00")
        assert t.time == 0

    def test_parse_one_second(self):
        t = AssTime.parse("0:00:01.00")
        assert t.time == 1000

    def test_parse_one_minute(self):
        t = AssTime.parse("0:01:00.00")
        assert t.time == 60000

    def test_parse_one_hour(self):
        t = AssTime.parse("1:00:00.00")
        assert t.time == 3600000

    def test_parse_mixed(self):
        t = AssTime.parse("1:23:45.67")
        assert t.time == 5025670

    def test_parse_centiseconds(self):
        t = AssTime.parse("0:00:01.50")
        assert t.time == 1500

    def test_parse_single_digit_centiseconds(self):
        t = AssTime.parse("0:00:00.5")
        assert t.time == 500

    def test_parse_three_digit_ms(self):
        t = AssTime.parse("0:00:00.500")
        assert t.time == 500

    def test_parse_zero_padded_hours(self):
        t = AssTime.parse("00:00:05.00")
        assert t.time == 5000


class TestAssTimeToAss:
    def test_zero(self):
        assert AssTime(0).to_ass() == "0:00:00.00"

    def test_one_second(self):
        assert AssTime(1000).to_ass() == "0:00:01.00"

    def test_one_minute(self):
        assert AssTime(60000).to_ass() == "0:01:00.00"

    def test_one_hour(self):
        assert AssTime(3600000).to_ass() == "1:00:00.00"

    def test_mixed(self):
        assert AssTime(5025670).to_ass() == "1:23:45.67"

    def test_centiseconds_rounding(self):
        assert AssTime(1015).to_ass() == "0:00:01.02"

    def test_negative_becomes_zero(self):
        assert AssTime(-5000).to_ass() == "0:00:00.00"

    def test_round_trip(self):
        original = "1:12:34.56"
        assert AssTime.parse(original).to_ass() == original


class TestAssTimeArithmetic:
    def test_add_int(self):
        t = AssTime(1000) + 500
        assert t.time == 1500

    def test_add_ass_time(self):
        t = AssTime(1000) + AssTime(500)
        assert t.time == 1500

    def test_radd(self):
        t = 500 + AssTime(1000)
        assert t.time == 1500

    def test_sub_int(self):
        t = AssTime(1000) - 300
        assert t.time == 700

    def test_sub_ass_time(self):
        t = AssTime(1000) - AssTime(300)
        assert t.time == 700

    def test_rsub(self):
        t = 1000 - AssTime(300)
        assert t.time == 700

    def test_mul(self):
        t = AssTime(500) * 3
        assert t.time == 1500

    def test_rmul(self):
        t = 3 * AssTime(500)
        assert t.time == 1500

    def test_truediv(self):
        result = AssTime(1000) / 2
        assert result == 500.0

    def test_floordiv(self):
        t = AssTime(1000) // 3
        assert t.time == 333

    def test_iadd(self):
        t = AssTime(1000)
        t += 500
        assert t.time == 1500

    def test_isub(self):
        t = AssTime(1000)
        t -= 300
        assert t.time == 700

    def test_add_not_implemented(self):
        with pytest.raises(TypeError):
            AssTime(100) + "invalid"

    def test_sub_not_implemented(self):
        with pytest.raises(TypeError):
            AssTime(100) - "invalid"


class TestAssTimeComparison:
    def test_eq_same(self):
        assert AssTime(1000) == AssTime(1000)

    def test_eq_different(self):
        assert not (AssTime(1000) == AssTime(2000))

    def test_eq_int(self):
        assert AssTime(1000) == 1000

    def test_eq_float(self):
        assert AssTime(1000) == 1000.0

    def test_eq_not_implemented(self):
        assert not (AssTime(1000) == "invalid")

    def test_lt(self):
        assert AssTime(100) < AssTime(200)

    def test_lt_int(self):
        assert AssTime(100) < 200

    def test_le(self):
        assert AssTime(100) <= AssTime(100)

    def test_gt(self):
        assert AssTime(200) > AssTime(100)

    def test_gt_int(self):
        assert AssTime(200) > 100

    def test_ge(self):
        assert AssTime(200) >= AssTime(100)


class TestAssTimeDunder:
    def test_int(self):
        assert int(AssTime(5000)) == 5000

    def test_hash(self):
        assert hash(AssTime(5000)) == hash(5000)

    def test_repr(self):
        assert repr(AssTime(5000)) == "AssTime(5000)"

    def test_str(self):
        assert str(AssTime(5000)) == "0:00:05.00"

    def test_hash_equality(self):
        t1 = AssTime(5000)
        t2 = AssTime(5000)
        assert hash(t1) == hash(t2)
