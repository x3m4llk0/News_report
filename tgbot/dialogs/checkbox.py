from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent
from aiogram_dialog.widgets.kbd import Button, Checkbox, ManagedCheckboxAdapter
from aiogram_dialog.widgets.text import Const


class CheckBoxDialog(StatesGroup):
    state = State()



async def exit(c: CallbackQuery, _: Button, manager: DialogManager):
    await c.message.delete()
    await manager.done()


async def check_changed(event: ChatEvent, checkbox: ManagedCheckboxAdapter, manager: DialogManager):
    checkbox.is_checked()


main_window = Dialog(
    Window(
        Const("Сделай все по порядку"),
        Checkbox(
            checked_text=Const("✅ Проверил орфограцию"),
            unchecked_text=Const('❌ Орфография через "Рецензирование" или F7'),
            id="is_fixed",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил окончания"),
            unchecked_text=Const("❌ Окончания в нужном падеже и тся/ться"),
            id="is_fixed1",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил вложения"),
            unchecked_text=Const("❌ Открывается корректное вложение"),
            id="is_fixed4",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил ссылки в excel"),
            unchecked_text=Const("❌ Проверь ссылки в excel"),
            id="is_fixed2",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил ссылки в pdf"),
            unchecked_text=Const("❌ Проверь ссылки в pdf"),
            id="is_fixed3",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил"),
            unchecked_text=Const("❌ Нужно ли вносить инфо еще где-то(БЗ/ПЗ)?"),
            id="is_fixed5",
            default=False,
            on_state_changed=check_changed
        ),
        Button(Const("Закрыть"), id="test_button", on_click=exit),

        state=CheckBoxDialog.state,
    ),
)




class RelizDialog(StatesGroup):
    state_reliz = State()

    async def exit(c: CallbackQuery, _: Button, manager: DialogManager):
        await c.message.delete()
        await manager.done()

    async def check_changed(event: ChatEvent, checkbox: ManagedCheckboxAdapter, manager: DialogManager):
        checkbox.is_checked()

reliz_window = Dialog(
    Window(
        Const("<b>Перед направлением релиза обязательно проверь наличие задач на почте❗</b>\n\n"
              "При отсутствии задач, откладывающих отправку релиза проверь:"),
        Checkbox(
            checked_text=Const("✅ Проверил"),
            unchecked_text=Const('❌ Корректность получателей'),
            id="is_fixed",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил"),
            unchecked_text=Const("❌ Корректность темы письма"),
            id="is_fixed1",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил"),
            unchecked_text=Const("❌ Наличие файла/ов с релизом"),
            id="is_fixed4",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил"),
            unchecked_text=Const("❌ Убрать подпись"),
            id="is_fixed2",
            default=False,
            on_state_changed=check_changed
        ),
        Checkbox(
            checked_text=Const("✅ Проверил"),
            unchecked_text=Const("❌ Отправка с почты СОП"),
            id="is_fixed3",
            default=False,
            on_state_changed=check_changed
        ),
        Button(Const("Закрыть"), id="test_button", on_click=exit),

        state=RelizDialog.state_reliz,
    ),
)