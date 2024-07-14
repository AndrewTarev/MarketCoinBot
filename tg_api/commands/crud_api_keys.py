from aiogram import F, types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from database.common.orm import OrmFunc
from tg_api.keyboards.keyboards import ButtonText, KB
from tg_api.commands.answer_text import AnswerText

router = Router()


class AddApiKeys(StatesGroup):
    """Для хранения состояний. Список имеющихся хранилищ FSM"""

    api_pub = State()
    api_secret = State()


class ConfirmationRemove(StatesGroup):
    yes_or_no = State()


@router.message(F.text == ButtonText.MENU)
async def get_back(message: types.Message, state: FSMContext):
    """Функция возврата в меню"""
    await message.answer(
        text=AnswerText.RETURN_TO_MENU, reply_markup=KB.get_on_start_kb()
    )
    await state.clear()


@router.message(F.text == ButtonText.CONNECT_API_KEY)
async def connection_API(message: types.Message):
    """Меню Профиля"""
    await message.answer(
        text=AnswerText.CONNECTION_API_KEYS,
        reply_markup=KB.connection_API_keys(),
    )


@router.message(F.text == ButtonText.ADD_API_KEYS, StateFilter(None))
async def add_key(message: types.Message, state: FSMContext):
    """Входим в состояние ввода публичного ключа"""
    await message.answer(
        text=AnswerText.INPUT_API_PUB, reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddApiKeys.api_pub)  # Устанавливаем пользователю состояние


@router.message(AddApiKeys.api_pub)
async def add_key_finished(message: Message, state: FSMContext):
    """Сохраняем публичный ключ в хранилище и запрашиваем API secret"""
    if not message.text:
        await message.answer(text=AnswerText.FILTER_TEXT)
    else:
        await state.update_data(
            api_pub=message.text
        )  # Здесь записываем в хронилище его ответ
        user_data = await state.get_data()
        OrmFunc.add_api_pub_DB(message.from_user.id, user_data.get("api_pub"))
        await message.answer(
            text=AnswerText.INPUT_API_SECRET,
        )
        await state.set_state(AddApiKeys.api_secret)


@router.message(AddApiKeys.api_secret)
async def key_is_recorded(message: Message, state: FSMContext):
    """Сохраняем API secret"""
    if not message.text:
        await message.answer(text=AnswerText.FILTER_TEXT)
    else:
        await state.update_data(api_secret=message.text)
        user_data = await state.get_data()
        OrmFunc.add_api_secret_DB(message.from_user.id, user_data.get("api_secret"))
        await message.answer(
            text=AnswerText.KEY_IS_RECORDED, reply_markup=KB.connection_API_keys()
        )
        # Сброс состояния и сохранённых данных у пользователя
        await state.clear()


@router.message(F.text == ButtonText.GET_API_KEYS)
async def get_key(message: Message):
    """Получаем наши ключи"""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    if api_pub == None or api_secret is None:
        await message.answer(text=AnswerText.ADD_THE_KEY)
    else:
        await message.answer(
            text=f"api_pub: ***{api_pub[-4:]}\napi_secret: ***{api_secret[-4:]}"
        )


@router.message(F.text == ButtonText.REMOVE_API_KEYS)
async def remove_key(message: Message, state: FSMContext):
    """Запрос на удаление ключей из БД"""
    await message.answer(text=AnswerText.DELETE_KEYS, reply_markup=KB.confirmation())
    await state.set_state(ConfirmationRemove.yes_or_no)


@router.message(ConfirmationRemove.yes_or_no)
async def confirmation_remove(message: Message, state: FSMContext):
    """Подтверждение на удаление ключей"""
    await state.update_data(yes_or_no=message.text)
    answer = await state.get_data()
    if answer.get("yes_or_no") == ButtonText.YES:
        OrmFunc.remove_api_keys(message.from_user.id)
        await message.answer(
            text=AnswerText.KEY_IS_REMOVED, reply_markup=KB.get_on_start_kb()
        )
        await state.clear()
    elif answer.get("yes_or_no") == ButtonText.NO:
        await message.answer(
            text=AnswerText.I_STILL_HAVE_THE_KEY, reply_markup=KB.connection_API_keys()
        )
        await state.clear()
    else:
        await message.answer(
            text=AnswerText.UNKNOWN_COMMAND, reply_markup=KB.confirmation()
        )
