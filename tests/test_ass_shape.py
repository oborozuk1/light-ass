
from light_ass import AssShape


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
        assert cmds[0].cmd == "m"
        assert cmds[0].points[0].x == 0
        assert cmds[0].points[0].y == 0

    def test_line_command(self):
        s = AssShape.from_ass("l 100 200")
        cmds = s.commands
        assert cmds[0].cmd == "l"
        assert cmds[0].points[0].x == 100
        assert cmds[0].points[0].y == 200

    def test_multiple_commands(self):
        s = AssShape.from_ass("m 0 0 l 10 10")
        cmds = s.commands
        assert len(cmds) == 2
        assert [c.cmd for c in cmds] == ["m", "l"]

    def test_negative_coords(self):
        s = AssShape.from_ass("m -10 -20 l -30 40")
        cmds = s.commands
        assert cmds[0].points[0].x == -10
        assert cmds[0].points[0].y == -20

    def test_float_coords(self):
        s = AssShape.from_ass("m 1.5 2.5")
        cmds = s.commands
        assert cmds[0].points[0].x == 1.5
        assert cmds[0].points[0].y == 2.5


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
        assert s.to_ass() == "m 1.5 2.5"


class TestAssShapeScale:
    def test_scale_uniform(self):
        s = AssShape.from_ass("m 0 0")
        s.commands
        s.scale(2)
        cmds = s.commands
        assert cmds[0].points[0].x == 0
        assert cmds[0].points[0].y == 0

    def test_scale_xy(self):
        s = AssShape.from_ass("m 10 10")
        s.commands
        s.scale(2, 3)
        cmds = s.commands
        assert cmds[0].points[0].x == 20
        assert cmds[0].points[0].y == 30


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


class TestAssShapeSetter:
    def test_set_commands(self):
        s = AssShape.from_ass("m 0 0")
        from light_ass.types.ass_shape.shape import Command, Point

        new_cmds = [Command("l", [Point(5, 5)])]
        s.commands = new_cmds
        assert s._parsed is True
        assert len(s.commands) == 1
        assert s.commands[0].cmd == "l"
