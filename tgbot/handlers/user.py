from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.markdown import hbold

from tgbot.keyboards.callback_data import ProductsCallback
from tgbot.keyboards.inline import rules_kb, menu_kb, product_kb, back_to_menu_kb
from tgbot.misc.platform_api import send_upd, send_to_api
from tgbot.misc.questions import products_questions
from tgbot.misc.states import dialog
from tgbot.models.db_commands import get_user, create_user, delete_user, get_session, create_session

user_router = Router()


@user_router.message(commands=["start"], state=None)
async def user_start(message: Message):
    user = await get_user(message.chat.id)
    if not user or not user.is_active:
        return await message.answer("Соглашаетесь ли в с правилами?", reply_markup=await rules_kb())
    await message.answer("Выберете один из пунктов меню 👇", reply_markup=await menu_kb())


@user_router.message(commands=["stop_dialog"])
async def stop_dialog(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Сессия завершена можете дальше пользоваться ботом")


@user_router.callback_query(text="accept_rules")
async def accept_rules(call: CallbackQuery):
    await create_user(call.message.chat.id, username=call.message.chat.username, is_active=True)
    await send_to_api(call.message.chat.id, title="Подтвердил правила", name="start")
    await call.message.edit_text("Выберете один из пунктов меню 👇", reply_markup=await menu_kb())


@user_router.callback_query(text="back_to_menu", state="*")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_to_api(call.message.chat.id)
    await call.message.edit_text("Выберете один из пунктов меню 👇", reply_markup=await menu_kb())


@user_router.callback_query(text="cancel_rules")
async def cancel_rules(call: CallbackQuery):
    await send_to_api(call.message.chat.id)
    await call.message.edit_text("Вы не согласились с правилами, для повторной регистрации выполните команду /start")


@user_router.callback_query(text="disable_bot")
async def cancel_rules(call: CallbackQuery):
    await delete_user(call.message.chat.id)
    await call.message.edit_text("Вы отписались от рассылки и ограничены в правах пользования ботом, "
                                 "для повторной регистрации выполните команду /start")


@user_router.callback_query(text="products")
async def products(call: CallbackQuery):
    await send_to_api(call.message.chat.id)
    await call.message.edit_text("Выберете один из пунктов меню 👇", reply_markup=await product_kb())


@user_router.callback_query(ProductsCallback.filter())
async def show_products(call: CallbackQuery, callback_data: ProductsCallback):
    questions_id = callback_data.id
    questions = products_questions()
    keys = list(questions.keys())
    await call.message.edit_text(
        text="\n".join(
            [
                hbold(keys[questions_id]),
                f'\n{questions[keys[questions_id]]}'
            ]
        ), reply_markup=await back_to_menu_kb()
    )


@user_router.callback_query(text="another_question")
async def another_question(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Напишите текст вопроса", reply_markup=await back_to_menu_kb())
    await state.set_state(dialog.session)


@user_router.message(state=dialog.session)
async def dialog_with_manager(message: Message, event_update: Update):
    session = await get_session(user_id=message.chat.id)
    await send_to_api(message.chat.id)
    if message.text:
        if message.text.startswith("/"):
            return message.answer(
                f"Команда {message.text} не доступна в сессии с менеджером, для завершения сессии используйте"
                f"используйте команду /stop_dialog")
    if session:
        await send_upd(event_update.json())
    else:
        await send_upd(event_update.json(), True)
        await create_session(user_id=message.chat.id)
    await message.answer("Ваше сообщение отправлено менеджеру, для остановки чата пропишите команду, /stop_dialog")