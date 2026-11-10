import asyncio
from collections.abc import Callable
from typing import Any
from src.utility import is_valid


class UserIO:
    async def get_input(self, display: str = "") -> str:
        return ""

    def print(self, value: str):
        pass

    async def get_line(self, display: str):
        return await self.get_input(display + "\n")

    async def get_choice(
        self,
        prompt: str,
        options: list[str],
        returns_index=False,
        allows_free_form=False,
    ) -> str | int:
        while True:
            try:
                self.print(prompt)
                for index, option in enumerate(options):
                    self.print(f"{index + 1}. {option}")
                value = await self.get_input()
                number = int(value) - 1
                if 0 <= number < len(options):
                    if returns_index:
                        return number
                    return options[number]
            except KeyboardInterrupt:
                exit(0)
            except:
                if allows_free_form:
                    return value
            self.print("Try again")

    async def set_state_with_choice(
        self,
        instance: Any,
        path: str,
        prompt: str,
        options: list[str],
        skip_if_has_value=False,
    ):
        value = getattr(instance, path)
        if skip_if_has_value and value:
            return
        setattr(instance, path, await self.get_choice(prompt, options))

    async def set_state_with_number(
        self,
        instance: Any,
        path: str,
        prompt: str,
        validator: Callable[[int], bool],
        skip_if_has_value=False,
    ):
        value = getattr(instance, path)
        if skip_if_has_value and value:
            return
        setattr(instance, path, await self.get_number(prompt, validator))

    async def get_number(
        self, prompt: str, validator: Callable[[int], bool] = is_valid
    ) -> int:
        while True:
            self.print(prompt)
            try:
                number = int(await self.get_input())
                if validator(number):
                    return number
            except KeyboardInterrupt:
                exit(0)
                return
            except ValueError:
                pass
            self.print("Try again")

    async def set_state_with_line(
        self, instance: Any, path: str, prompt: str, skip_if_has_value=False
    ):
        value = getattr(instance, path)
        if skip_if_has_value and value:
            return
        setattr(instance, path, await self.get_line(prompt))

    async def set_state_with_list(
        self, instance: Any, path: str, prompt: str, skip_if_has_value=False
    ):
        value = getattr(instance, path)
        if skip_if_has_value and value:
            return
        line = " "
        self.print(prompt)
        list = []  # [conversation id]
        while line:
            line = await self.get_input()  #
            if line:
                list.append(line)
        setattr(instance, path, list)

    async def set_state_with_dict(
        self, instance: Any, path: str, prompt: str, skip_if_has_value=False
    ):
        existing_value = getattr(instance, path)
        if skip_if_has_value and existing_value:
            return
        self.print(prompt)
        dict = {}  # {"flag visible": False}
        while True:
            key = await self.get_input()  # "flag visible"
            if not key:
                break
            response = await self.get_input()
            value = response.lower() == "on"
            dict[key] = value
        setattr(instance, path, dict)


class ConsoleUserIO(UserIO):
    async def get_input(self, display="") -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, display)

    def print(self, value: str):
        print(value)


class TkUserIO(UserIO):
    async def get_input(self, display="") -> str:
        return ""

    def print(self, value):
        pass
