from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database.common.orm import OrmFunc
from tg_api.keyboards.keyboards import KB
from tg_api.commands.answer_text import AnswerText

router = Router()


@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    OrmFunc.add_user(message.from_user.id)
    await message.answer(
        text=f"Привет, {message.from_user.full_name}! 😊 {AnswerText.START}",
        reply_markup=KB.get_on_start_kb(),
    )
    await state.clear()


@router.message(Command("help"))
async def handle_help(message: types.Message, state: FSMContext):
    await message.answer(text=AnswerText.HELP)
    await state.clear()
