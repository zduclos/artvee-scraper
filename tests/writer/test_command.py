from command import Command, MacroCommand
from mockito import mock, verify, when


def test_macrocommand_execute():
    # Mock Command::execute
    command_mock = mock(Command)
    when(command_mock).execute().thenReturn(True, True)

    # Setup
    macroCmd = MacroCommand()
    macroCmd.add(command_mock)
    macroCmd.add(command_mock)

    # Test
    result = macroCmd.execute()

    # Validate
    assert result == True, "Macro command execute should succeed"
    verify(command_mock, times=2).execute()


def test_macrocommand_revert():
    # Mock Command::execute
    command_mock = mock(Command)
    when(command_mock).execute().thenReturn(True, True)
    # Mock Command::revert
    when(command_mock).revert().thenReturn(True, True)

    # Setup
    macroCmd = MacroCommand()
    macroCmd.add(command_mock)
    macroCmd.add(command_mock)
    macroCmd.execute()

    # Test
    result = macroCmd.revert()

    # Validate
    assert result == True, "Macro command revert should succeed"
    verify(command_mock, times=2).execute()
    verify(command_mock, times=2).revert()


def test_macrocommand_execute_fail_revert_succeeds():
    # Mock Command::execute
    command_mock = mock(Command)
    when(command_mock).execute().thenReturn(True, False)
    # Mock Command::revert
    when(command_mock).revert().thenReturn(True)

    # Setup
    macroCmd = MacroCommand()
    macroCmd.add(command_mock)
    macroCmd.add(command_mock)
    macroCmd.execute()

    # Test
    result = macroCmd.revert()

    # Validate
    assert result == True, "Macro command revert should succeed"
    verify(command_mock, times=2).execute()
    verify(command_mock, times=1).revert()


def test_macrocommand_retry():
    # Mock Command::execute
    command_mock = mock(Command)
    when(command_mock).execute().thenReturn(True, False, True, True)
    # Mock Command::revert
    when(command_mock).revert().thenReturn(True)

    # Setup
    macroCmd = MacroCommand()
    macroCmd.add(command_mock)
    macroCmd.add(command_mock)

    # Test
    if not macroCmd.execute():  # execution fails
        macroCmd.revert()  # reverting succeeds
    result = macroCmd.execute()  # execution retry succeeds

    # Validate
    assert result == True, "Macro command retry execute should succeed"
    verify(command_mock, times=4).execute()
    verify(command_mock, times=1).revert()


def test_macrocommand_execute_empty():
    # Setup
    macroCmd = MacroCommand()

    # Test
    result = macroCmd.execute()

    # Validate
    assert result == True, "Macro command execute should succeed"


def test_macrocommand_revert_empty():
    # Setup
    macroCmd = MacroCommand()

    # Test
    result = macroCmd.revert()

    # Validate
    assert result == True, "Macro command revert should succeed"
