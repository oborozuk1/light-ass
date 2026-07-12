
from light_ass import AssShape
from light_ass.types.ass_shape.command import LineCmd, MoveCmd


class TestAssShapeFromAss:
    def test_lazy_parsing(self):
        s = AssShape.from_ass("m 0 0 l 10 10 20 0")
        assert s._parsed is False

    def test_commands_triggers_parse(self):
        s = AssShape.from_ass("m 0 0 l 10 10 20 0")
        cmds = s.commands
        assert s._parsed is True
        assert len(cmds) == 2

    def test_move_command(self):
        s = AssShape.from_ass("m 0 0")
        cmds = s.commands
        assert isinstance(cmds[0], MoveCmd)
        assert cmds[0].point.x == 0
        assert cmds[0].point.y == 0

    def test_line_command(self):
        s = AssShape.from_ass("l 100 200")
        assert len(s.commands) == 0

    def test_multiple_commands(self):
        s = AssShape.from_ass("m 0 0 l 10 10")
        cmds = s.commands
        assert len(cmds) == 2
        assert [type(c) for c in cmds] == [MoveCmd, LineCmd]

    def test_negative_coords(self):
        s = AssShape.from_ass("m -10 -20 l -30 40")
        cmds = s.commands
        assert cmds[0].point.x == -10
        assert cmds[0].point.y == -20

    def test_float_coords(self):
        s = AssShape.from_ass("m 1.5 2.5")
        cmds = s.commands
        assert cmds[0].point.x == 1.5
        assert cmds[0].point.y == 2.5


class TestAssShapeToAss:
    def test_round_trip_simple(self):
        original = "m 0 0"
        s = AssShape.from_ass(original)
        result = s.to_ass(decimal=0)
        assert result == "m 0 0"

    def test_to_ass_with_decimal(self):
        s = AssShape.from_ass("m 1.5 2.5")
        assert s.to_ass(decimal=1) == "m 1.5 2.5"

    def test_no_decimal_trailing_zeros(self):
        s = AssShape.from_ass("m 1.500 2.500")
        s.commands
        assert s.to_ass() == "m 1.5 2.5"


class TestAssShapeScale:
    def test_scale_uniform(self):
        s = AssShape.from_ass("m 0 0")
        s.scale(2)
        cmds = s.commands
        assert cmds[0].point.x == 0
        assert cmds[0].point.y == 0

    def test_scale_xy(self):
        s = AssShape.from_ass("m 10 1")
        s.scale(2, 3)
        cmds = s.commands
        assert cmds[0].point.x == 20
        assert cmds[0].point.y == 3


class TestAssShapeRepr:
    def test_repr_unparsed(self):
        s = AssShape.from_ass("m 0 0")
        assert "unparsed" in repr(s)

    def test_repr_parsed(self):
        s = AssShape.from_ass("m 0 0")
        s.commands
        assert "1 command" in repr(s)

    def test_repr_parsed_multiple(self):
        s = AssShape.from_ass("m 0 0 l 10 10")
        s.commands
        assert "2 commands" in repr(s)
