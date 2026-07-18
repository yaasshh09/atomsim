import pytest

from atomsim.atoms import (
    ATOM_KEYS,
    atom_for_key,
    aufbau_configuration,
    element_by_symbol,
    format_config,
    is_atom_key,
    is_ground,
    parse_config,
    subshell_capacity,
    total_electrons,
    validate_config,
)


def test_subshell_capacity():
    assert subshell_capacity(0) == 2   # s
    assert subshell_capacity(1) == 6   # p
    assert subshell_capacity(2) == 10  # d


@pytest.mark.parametrize("z,expected", [
    (1, "1s1"),
    (2, "1s2"),
    (6, "1s2 2s2 2p2"),      # carbon
    (10, "1s2 2s2 2p6"),     # neon
    (11, "1s2 2s2 2p6 3s1"), # sodium
    (18, "1s2 2s2 2p6 3s2 3p6"),  # argon
])
def test_aufbau_matches_known_configs(z, expected):
    assert format_config(aufbau_configuration(z)) == expected


def test_config_roundtrip_and_count():
    cfg = parse_config("1s2 2s2 2p1")
    assert total_electrons(cfg) == 5
    assert format_config(cfg) == "1s2 2s2 2p1"


def test_is_ground():
    assert is_ground(aufbau_configuration(11)) is True
    assert is_ground(parse_config("1s2 2s2 2p6 3p1")) is False  # excited Na


def test_validate_rejects_overfill_and_bad_shell():
    with pytest.raises(ValueError, match="capacity"):
        validate_config(parse_config("1s3"))         # > 2 in s
    with pytest.raises(ValueError, match="n must be"):
        validate_config(((( 1, 1), 1),))              # 1p impossible (n<=l)


def test_atom_keys_cover_he_to_ar():
    assert ATOM_KEYS[0] == "he" and ATOM_KEYS[-1] == "ar"
    assert len(ATOM_KEYS) == 17
    assert is_atom_key("na") and not is_atom_key("h")
    assert atom_for_key("na").z == 11 and element_by_symbol("Na").z == 11
