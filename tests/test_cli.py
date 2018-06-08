import pytest
import sys 
import os

sys.path.append(os.path.relpath("src/"))

from cli import create_parser, create_tournament

test_tournament='test'


@pytest.fixture
def parser():
    return create_parser()


class TestCli(object):    

    def test_parser_h(self, parser):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            parser.parse_args(['-h'])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_parser_v(self, parser):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            parser.parse_args(['-v'])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_parser_fail(self, parser):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            parser.parse_args(['--nonsense'])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code != 0

    def test_parser_create_tournament(self, parser):
        args = parser.parse_args([test_tournament, 'create-tournament'])
        print(args)
        assert args.func is create_tournament
        