from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from pybit.exceptions import FailedRequestError

from database.common.orm import OrmFunc
from site_api.site_api_handler import exchg_request, Account, Market, PlaceOrder
from tg_api.keyboards.keyboards import ButtonText, KB
from tg_api.commands.answer_text import AnswerText

router = Router()


class TradeOrder(StatesGroup):
    coin = State()
    side = State()
    orderType = State()
    qty = State()
    price = State()
    confirmation = State()


available_side_chosen = [ButtonText.BUY, ButtonText.SELL]
available_orderType_chosen = [ButtonText.LIMIT_ORD, ButtonText.MARKET]


@router.message(F.text == ButtonText.MENU)
async def get_back(message: types.Message, state: FSMContext):
    """Функция возврата в меню"""
    await message.answer(
        text=AnswerText.RETURN_TO_MENU, reply_markup=KB.get_on_start_kb()
    )
    await state.clear()


@router.message(F.text == ButtonText.START_TRADING)
async def start_trading(message: Message):
    """Выдает меню с кнопками для Начать торговлю"""
    await message.answer(
        text=AnswerText.START_TRADING_answer, reply_markup=KB.trading_start()
    )


@router.message(F.text == ButtonText.GET_BALANCE)
async def get_balance(message: Message):
    """Функция для вывода баланса кошелька(USDT only)"""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    session = exchg_request(api_pub, api_secret)
    try:
        get_blnc = Account.get_usdt_balance(session)
    except FailedRequestError:
        return message.answer(text=f"Не верные ключи API!")
    except UnicodeEncodeError:
        return message.answer(
            text=f"Не допустимые символы в API. Проверьте введенные вами данные!"
        )
    except PermissionError:
        return message.answer(text=AnswerText.NO_API)
    except Exception as e:
        return message.answer(text=f"{e}")
    blnc = float(get_blnc)
    result = f"Balance = {round(blnc, 2)} USDT"
    await message.answer(text=result)


@router.message(F.text == ButtonText.GET_COIN_INFO)
async def get_coin_balance(message: Message):
    """Выдает информацию о количестве монет в кошельке"""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    session = exchg_request(api_pub, api_secret)
    try:
        blnc = Account.get_all_coins_balance(session)
    except FailedRequestError:
        return message.answer(text=f"Не верные ключи API!")
    except UnicodeEncodeError:
        return message.answer(
            text=f"Не допустимые символы в API. Проверьте введенные вами данные!"
        )
    except PermissionError:
        return message.answer(text=AnswerText.NO_API)
    except Exception as e:
        return message.answer(text=f"{e}")
    dict_str = "\n".join(f"{key} - {value}" for key, value in blnc.items())
    await message.answer(text=dict_str)


@router.message(F.text == ButtonText.GET_HISTORY_TRADE)
async def trade_history(message: Message):
    """Выдает информацию о совершенных сделках"""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    session = exchg_request(api_pub, api_secret)
    try:
        trade_history = Account.get_trade_history(session)
    except FailedRequestError:
        return message.answer(text=f"Не верные ключи API!")
    except UnicodeEncodeError:
        return message.answer(
            text=f"Не допустимые символы в API. Проверьте введенные вами данные!"
        )
    except PermissionError:
        return message.answer(text=AnswerText.NO_API)
    except Exception as e:
        return message.answer(text=f"{e}")
    await message.answer(text=trade_history)


@router.message(F.text == ButtonText.MAKE_DEAL)
async def ticker_choice(message: Message, state: FSMContext):
    """Начало составления ордера. Запрос названия интересующей монеты"""
    await message.answer(
        text=AnswerText.INPUT_COINS_NAME, reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(TradeOrder.coin)


@router.message(TradeOrder.coin)
async def ticker_chosen(message: Message, state: FSMContext):
    """Проверка и сохранение в StorageMemory введеной монеты."""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    session = exchg_request(api_pub, api_secret)

    if not message.text:
        await message.answer(text=AnswerText.WHAT_IS_IT)

    msg = message.text.upper()

    if not msg.endswith("USDT"):
        msg += "USDT"

    coin_data = await state.update_data(coin=msg)
    coin = coin_data["coin"]

    try:
        coin_price = Market.get_tickers(coin, session)
    except Exception:
        return message.answer(text="Такой монеты не существует!")

    await message.answer(
        text=f"Вы выбрали {coin_price}.\n\nТеперь выберите направление: ",
        reply_markup=KB.kb_buy_sell(),
    )
    await state.set_state(TradeOrder.side)


@router.message(TradeOrder.side, F.text.in_(available_side_chosen))
async def side_chosen(message: Message, state: FSMContext):
    """Выбор направления сделки(покупка/продажа)"""
    await state.update_data(side=message.text.lower())
    await message.answer(
        text="Теперь выберите тип ордера:", reply_markup=KB.order_type()
    )
    await state.set_state(TradeOrder.orderType)


@router.message(TradeOrder.side)
async def side_chosen_incorrectly(message: Message):
    """Проверка на корректность ввода направления сделки"""
    await message.answer(text=AnswerText.INCORRECT_INPUT, reply_markup=KB.kb_buy_sell())


@router.message(TradeOrder.orderType, F.text.in_(available_orderType_chosen))
async def orderType_chosen(message: Message, state: FSMContext):
    """Запрос тип ордера(market/limit)"""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    session = exchg_request(api_pub, api_secret)

    await state.update_data(orderType=message.text)
    user_data = await state.get_data()
    coin = user_data["coin"]
    try:
        minQtyOrder = PlaceOrder.get_min_qtyOrder(
            session, coin
        )  # минимально возможный ордер
        maxQtyOrder = PlaceOrder.round_to_base_precision(session, coin)
    except FailedRequestError:
        await state.clear()
        return message.answer(
            text=f"Не верные ключи API!", reply_markup=KB.connection_API_keys()
        )
    except UnicodeEncodeError:
        await state.clear()
        return message.answer(
            text=f"Не допустимые символы в API. Проверьте введенные вами данные!",
            reply_markup=KB.connection_API_keys(),
        )
    except PermissionError:
        await state.clear()
        return message.answer(
            text=AnswerText.NO_API, reply_markup=KB.connection_API_keys()
        )
    except Exception as e:
        await state.clear()
        return message.answer(text=f"{e}")

    if user_data["side"] == ButtonText.BUY:  # Если покупаем, то:
        await message.answer(
            text=f"Введите сумму(в USDT) на которую желаете приобрести:",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(TradeOrder.qty)
    else:
        await message.answer(
            text=f"Введите количество монет для продажи\n"
            f"Минимально возможный размер ордера = {minQtyOrder}\n"
            f"Количество монет на вашем счету = {maxQtyOrder}",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(TradeOrder.qty)


@router.message(TradeOrder.orderType)
async def orderType_chosen_incorrectly(message: Message):
    """Проверка на корректность ввода типа ордера"""
    await message.answer(text=AnswerText.INCORRECT_INPUT, reply_markup=KB.order_type())


@router.message(TradeOrder.qty)
async def qty_chosen(message: Message, state: FSMContext):
    """Ввод колличества монет на продажу или покупку"""
    await state.update_data(qty=message.text)
    user_data = await state.get_data()

    if user_data["orderType"] == ButtonText.MARKET:
        await message.answer(
            text=f"Ваш ордер:\nsymbol - {user_data['coin']}\nside - {user_data['side']}\n"
            f"OrderType - {user_data['orderType']}\nQuantity - {user_data['qty']}\n"
            f"Подтвердите ордер для выполнения:",
            reply_markup=KB.order_confirmation(),
        )
        await state.set_state(TradeOrder.confirmation)

    elif user_data["orderType"] == ButtonText.LIMIT_ORD:
        await message.answer(
            text="Введите цену лимитного ордера:", reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(TradeOrder.price)


@router.message(TradeOrder.price)
async def price_chosen(message: Message, state: FSMContext):
    """Ввод цены по которой хотим выставить лимитный ордер"""
    await state.update_data(price=message.text)
    user_data = await state.get_data()
    await message.answer(
        text=f"Ваш ордер:\nsymbol - {user_data['coin']}\nside - {user_data['side']}\n"
        f"OrderType - {user_data['orderType']}\nQuantity - {user_data['qty']}\nPrice - {user_data['price']}\n"
        f"Подтвердите ордер для выполнения:",
        reply_markup=KB.order_confirmation(),
    )
    await state.set_state(TradeOrder.confirmation)


@router.message(TradeOrder.confirmation)
async def confirmation_chosen(message: Message, state: FSMContext):
    """Подтверждение составленного ордера и вывод его на биржу"""
    api_pub, api_secret = OrmFunc.get_api_keys(message.from_user.id)
    session = exchg_request(api_pub, api_secret)
    user_confirmation = await state.update_data(confirmation=message.text)
    user_data = await state.get_data()

    if user_confirmation["confirmation"] == ButtonText.NON_CONFIRMATION:
        await message.answer(text="Отменил!", reply_markup=KB.trading_start())
        await state.clear()

    elif user_confirmation["confirmation"] == ButtonText.CONFIRMATION:

        if user_data["orderType"] == ButtonText.MARKET:
            coin, side, orderType, qty = (
                user_data["coin"],
                user_data["side"],
                user_data["orderType"],
                user_data["qty"],
            )
            try:
                order = PlaceOrder.market_place_order(
                    session=session, coin=coin, side=side, orderType=orderType, qty=qty
                )
            except FailedRequestError:
                await state.clear()
                return message.answer(
                    text=f"Не верные ключи API!", reply_markup=KB.connection_API_keys()
                )
            except UnicodeEncodeError:
                await state.clear()
                return message.answer(
                    text=f"Не допустимые символы в API. Проверьте введенные вами данные!",
                    reply_markup=KB.connection_API_keys(),
                )
            except PermissionError:
                await state.clear()
                return message.answer(
                    text=AnswerText.NO_API, reply_markup=KB.connection_API_keys()
                )
            except Exception as e:
                await state.clear()
                return message.answer(text=f"{e}")
            await message.answer(text=f"{order}", reply_markup=KB.trading_start())

        elif user_data["orderType"] == ButtonText.LIMIT_ORD:
            coin, side, orderType, qty, price = (
                user_data["coin"],
                user_data["side"],
                user_data["orderType"],
                user_data["qty"],
                user_data["price"],
            )
            try:
                order = PlaceOrder.limit_place_order(
                    session=session,
                    coin=coin,
                    side=side,
                    orderType=orderType,
                    qty=qty,
                    price=price,
                )
            except FailedRequestError:
                await state.clear()
                return message.answer(
                    text=f"Не верные ключи API!", reply_markup=KB.connection_API_keys()
                )
            except UnicodeEncodeError:
                await state.clear()
                return message.answer(
                    text=f"Не допустимые символы в API. Проверьте введенные вами данные!",
                    reply_markup=KB.connection_API_keys(),
                )
            except PermissionError:
                await state.clear()
                return message.answer(
                    text=AnswerText.NO_API, reply_markup=KB.connection_API_keys()
                )
            except Exception as e:
                await state.clear()
                return message.answer(text=f"{e}")
            await message.answer(text=f"{order}", reply_markup=KB.trading_start())
