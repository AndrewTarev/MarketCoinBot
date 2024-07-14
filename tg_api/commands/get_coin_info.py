from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.common.orm import OrmFunc
from site_api.site_api_handler import Market, exchg_request
from tg_api.commands.answer_text import AnswerText
from tg_api.keyboards.keyboards import ButtonText, KB

router = Router()


class FindCoin(StatesGroup):
    """Для хранения состояний. Список имеющихся хранилищ FSM"""

    coins_name = State()


@router.message(F.text == ButtonText.CANCEL)
async def cancel_func(message: Message, state: FSMContext):
    """Функция для прекращения получения данных по ценам монет"""
    await message.answer(
        text=AnswerText.RETURN_TO_MENU, reply_markup=KB.trading_start()
    )
    await state.clear()


@router.message(F.text == ButtonText.GET_INFO_SPECIFIC_COIN)
async def cmd_coin(message: types.Message, state: FSMContext):
    """Запрос на ввод наименования интересующей монеты"""
    await message.answer(text=AnswerText.INPUT_COINS_NAME, reply_markup=KB.cancel())
    await state.set_state(FindCoin.coins_name)


@router.message(FindCoin.coins_name)
async def coin_chosen(message: Message, state: FSMContext):
    """Функция возвращающая цену монеты"""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    session = exchg_request(api_pub, api_secret)

    if not message.text:
        await message.answer(text=AnswerText.WHAT_IS_IT)
    coin_data = await state.update_data(coins_name=message.text.upper())
    coins_name = coin_data["coins_name"]

    if not coins_name.endswith("USDT"):
        coins_name += "USDT"
    try:
        coin_price = Market.get_tickers(coins_name, session)
    except Exception:
        return message.answer(text="Такой монеты не существует!")

    await message.answer(
        text=coin_price,
    )
