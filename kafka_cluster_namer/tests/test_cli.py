from kafka_namer.cli import main


def test_default_prints_one_name(capsys):
    assert main([]) == 0
    assert len(capsys.readouterr().out.strip().splitlines()) == 1


def test_count_prints_that_many_names(capsys):
    assert main(["-n", "5"]) == 0
    assert len(capsys.readouterr().out.strip().splitlines()) == 5


def test_seed_is_reproducible(capsys):
    main(["--seed", "7", "-n", "3"])
    first = capsys.readouterr().out
    main(["--seed", "7", "-n", "3"])
    assert capsys.readouterr().out == first


def test_zero_count_is_an_error(capsys):
    assert main(["-n", "0"]) == 2
    assert "error" in capsys.readouterr().err
