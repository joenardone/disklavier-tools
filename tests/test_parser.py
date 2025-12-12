import pytest
from tools.convert_fil_to_mid import get_parser


def test_parser_accepts_preset_dkc900():
    parser = get_parser()
    args = parser.parse_args(['--preset', 'dkc900', 'sample.fil'])
    assert args.preset == 'dkc900'
