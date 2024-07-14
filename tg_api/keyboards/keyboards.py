from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class ButtonText:
    CONNECT_API_KEY = "⚙️ Профиль"
    INFO_COIN = "📖 Узнать текущую цену монеты"
    GET_INFO_SPECIFIC_COIN = "💵 Получить текущую цену монеты"
    MAKE_DEAL = "💰 Купить/продать монету"
    CANCEL = "Закончить!"
    MENU = "↩️ Вернуться в главное меню"
    ADD_API_KEYS = "✏️ Добавить ключи"
    REMOVE_API_KEYS = "🚫 Удалить ключи"
    GET_API_KEYS = "📖 Посмотреть мои ключи"
    YES = "✅ Да"
    NO = "❌ Нет"
    START_TRADING = "💰 Начать торговлю"
    GET_BALANCE = "🧾  Баланс USDT"
    GET_COIN_INFO = "🪙 Узнать состояние кошелька"
    GET_HISTORY_TRADE = "📜 Посмотреть историю сделок"
    BUY = "buy"
    SELL = "sell"
    MARKET = "market"
    LIMIT_ORD = "limit"
    CONFIRMATION = "✅ Подтверждаю"
    NON_CONFIRMATION = "❌ Отменить ордер"
    SELL_ALL = "Продать все монеты!"


class KB:
    @staticmethod
    def get_on_start_kb() -> ReplyKeyboardMarkup:
        """
        Кнопки начального меню
        """
        send_API_button = KeyboardButton(text=ButtonText.CONNECT_API_KEY)
        start_trading = KeyboardButton(text=ButtonText.START_TRADING)
        buttons_first_row = [send_API_button]
        button_third_row = [start_trading]

        markup = ReplyKeyboardMarkup(
            keyboard=[buttons_first_row, button_third_row], resize_keyboard=True
        )
        return markup

    @staticmethod
    def get_info_specific_coin() -> ReplyKeyboardMarkup:
        """
        Кнопки полученя информации по монете и кнопка меню
        """
        send_info_coin = KeyboardButton(text=ButtonText.GET_INFO_SPECIFIC_COIN)
        menu = KeyboardButton(text=ButtonText.MENU)
        button_first_row = [send_info_coin]
        button_second_row = [menu]
        markup = ReplyKeyboardMarkup(
            keyboard=[button_first_row, button_second_row], resize_keyboard=True
        )
        return markup

    @staticmethod
    def connection_API_keys() -> ReplyKeyboardMarkup:
        """
        Кнопки внутри меню Профиля
        """
        add_API_key = KeyboardButton(text=ButtonText.ADD_API_KEYS)
        get_API_keys = KeyboardButton(text=ButtonText.GET_API_KEYS)
        remove_API_key = KeyboardButton(text=ButtonText.REMOVE_API_KEYS)
        menu = KeyboardButton(text=ButtonText.MENU)
        button_first_row = [add_API_key]
        button_third_row = [get_API_keys]
        button_second_row = [remove_API_key]
        button_fourth_row = [menu]
        markup = ReplyKeyboardMarkup(
            keyboard=[
                button_first_row,
                button_second_row,
                button_third_row,
                button_fourth_row,
            ],
            resize_keyboard=True,
        )
        return markup

    @staticmethod
    def confirmation() -> ReplyKeyboardMarkup:
        kb = [[KeyboardButton(text=ButtonText.YES), KeyboardButton(text=ButtonText.NO)]]
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        return markup

    @staticmethod
    def trading_start() -> ReplyKeyboardMarkup:
        """
        Кнопки из меню "Начать торговлю"
        """
        get_wallet_balance = KeyboardButton(text=ButtonText.GET_BALANCE)
        get_coin_info_wallet = KeyboardButton(text=ButtonText.GET_COIN_INFO)
        send_info_coin = KeyboardButton(text=ButtonText.GET_INFO_SPECIFIC_COIN)
        get_trade_history = KeyboardButton(text=ButtonText.GET_HISTORY_TRADE)
        make_deal = KeyboardButton(text=ButtonText.MAKE_DEAL)
        menu = KeyboardButton(text=ButtonText.MENU)
        button_first_row = [get_wallet_balance]
        button_second_row = [get_coin_info_wallet]
        button_third_row = [get_trade_history]
        button_fourth_row = [make_deal]
        button_fifth_row = [send_info_coin]
        button_sixth_row = [menu]
        markup = ReplyKeyboardMarkup(
            keyboard=[
                button_first_row,
                button_second_row,
                button_third_row,
                button_fourth_row,
                button_fifth_row,
                button_sixth_row,
            ],
            resize_keyboard=True,
        )
        return markup

    @staticmethod
    def kb_buy_sell() -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text=ButtonText.BUY), KeyboardButton(text=ButtonText.SELL)]
        ]
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        return markup

    @staticmethod
    def order_type() -> ReplyKeyboardMarkup:
        kb = [
            [
                KeyboardButton(text=ButtonText.MARKET),
                KeyboardButton(text=ButtonText.LIMIT_ORD),
            ]
        ]
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        return markup

    @staticmethod
    def quantity_order_kb() -> ReplyKeyboardMarkup:
        kb = [
            [
                KeyboardButton(text=ButtonText.MARKET),
                KeyboardButton(text=ButtonText.LIMIT_ORD),
            ]
        ]
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        return markup

    @staticmethod
    def order_confirmation() -> ReplyKeyboardMarkup:
        kb = [
            [
                KeyboardButton(text=ButtonText.CONFIRMATION),
                KeyboardButton(text=ButtonText.NON_CONFIRMATION),
            ]
        ]
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        return markup

    @staticmethod
    def cancel() -> ReplyKeyboardMarkup:
        kb = [
            [
                KeyboardButton(text=ButtonText.CANCEL),
            ]
        ]
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        return markup
